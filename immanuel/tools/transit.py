"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module provides core transit calculation functionality using
Swiss Ephemeris high-precision functions for exact event timing.

"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import swisseph as swe

from immanuel.classes.transit_events import (
    TransitEvent,
    TransitPeriod,
    IntensityCurve,
    create_transit_event,
)
from immanuel.const import calc, chart, transits
from immanuel.tools import date, ephemeris


class TransitCalculator:
    """Core engine for calculating planetary transits with high precision."""

    def __init__(self, precision: str = transits.DEFAULT_PRECISION):
        self.precision = precision
        self.tolerance = self._get_tolerance()

    def _get_tolerance(self) -> float:
        """Get tolerance in Julian days based on precision level."""
        tolerances = {
            transits.PRECISION_MINUTE: 1.0 / 1440,  # 1 minute
            transits.PRECISION_SECOND: 1.0 / 86400,  # 1 second
            transits.PRECISION_HIGH: 1.0 / 864000,  # 0.1 second
        }
        return tolerances.get(self.precision, transits.CONVERGENCE_TOLERANCE)

    def normalize_interval(self, interval: transits.IntervalType) -> timedelta:
        """Convert interval specification to timedelta object."""
        if isinstance(interval, str):
            return transits.INTERVAL_MAPPINGS.get(interval, timedelta(days=1))
        elif isinstance(interval, timedelta):
            return interval
        elif isinstance(interval, (int, float)):
            return timedelta(seconds=interval)
        else:
            return timedelta(days=1)

    def find_planet_crossing(
        self, planet: int, target_longitude: float, start_jd: float, backwards: bool = False
    ) -> Optional[float]:
        """
        Find when a planet crosses a specific longitude using Swiss Ephemeris.
        Uses geocentric positions for all planets (consistent with natal chart).

        Args:
            planet: Planet constant (chart.SUN, chart.MOON, etc.)
            target_longitude: Target longitude in degrees (0-360)
            start_jd: Starting Julian day for search
            backwards: Search backwards in time

        Returns:
            Julian day of crossing, or None if not found
        """
        try:
            # Use Swiss Ephemeris direct functions for Sun and Moon
            if planet == chart.SUN:
                return swe.solcross_ut(target_longitude, start_jd)
            elif planet == chart.MOON:
                return swe.mooncross_ut(target_longitude, start_jd)
            else:
                # For other planets, manually search for geocentric crossings
                return self._find_geocentric_crossing(planet, target_longitude, start_jd, backwards)

        except swe.Error:
            # Handle cases where crossing not found in search period
            return None

    def _find_geocentric_crossing(
        self, planet: int, target_longitude: float, start_jd: float, backwards: bool = False
    ) -> Optional[float]:
        """
        Find geocentric longitude crossing using iterative search.
        This is needed because Swiss Ephemeris only has helio_cross_ut for planets.
        """
        # Search parameters based on actual orbital periods + padding
        orbital_periods = {
            chart.MERCURY: 88,  # 88 days
            chart.VENUS: 225,  # 225 days
            chart.MARS: 687,  # 687 days (~1.9 years)
            chart.JUPITER: 4333,  # 4333 days (~11.9 years)
            chart.SATURN: 10759,  # 10759 days (~29.5 years)
            chart.URANUS: 30687,  # 30687 days (~84 years)
            chart.NEPTUNE: 60190,  # 60190 days (~165 years)
            chart.PLUTO: 90560,  # 90560 days (~248 years)
        }

        # Use full orbital period + 20% padding to ensure we don't miss crossings
        base_period = orbital_periods.get(planet, 4333)  # Default to Jupiter if unknown
        max_search_days = int(base_period * 1.2)

        # Adjust initial step size based on orbital speed
        if base_period <= 365:  # Fast planets (Mercury, Venus)
            initial_step = 1.0
        elif base_period <= 2000:  # Medium planets (Mars)
            initial_step = 5.0
        elif base_period <= 15000:  # Slow planets (Jupiter, Saturn)
            initial_step = 15.0
        else:  # Very slow planets (Uranus, Neptune, Pluto)
            initial_step = 30.0

        precision_step = 0.001  # Final precision in days

        current_jd = start_jd
        step = initial_step if not backwards else -initial_step

        # Get initial planet position
        try:
            current_pos = ephemeris.get_planet(planet, current_jd)
            prev_lon = current_pos["lon"]
        except:
            return None

        # Coarse search to bracket the crossing
        days_searched = 0
        crossing_found = False
        bracket_start = None
        bracket_end = None

        while days_searched < max_search_days:
            current_jd += step
            days_searched += abs(step)

            try:
                current_pos = ephemeris.get_planet(planet, current_jd)
                current_lon = current_pos["lon"]

                # Check if we crossed the target longitude
                if self._longitude_crossed(prev_lon, current_lon, target_longitude):
                    bracket_start = current_jd - step
                    bracket_end = current_jd
                    crossing_found = True
                    break

                prev_lon = current_lon

            except:
                continue

        if not crossing_found:
            return None

        # Binary search for precise crossing time
        iterations = 0
        max_iterations = 50

        while (bracket_end - bracket_start) > precision_step and iterations < max_iterations:
            mid_jd = (bracket_start + bracket_end) / 2

            try:
                start_pos = ephemeris.get_planet(planet, bracket_start)
                mid_pos = ephemeris.get_planet(planet, mid_jd)

                if self._longitude_crossed(start_pos["lon"], mid_pos["lon"], target_longitude):
                    bracket_end = mid_jd
                else:
                    bracket_start = mid_jd

                iterations += 1

            except:
                break

        return (bracket_start + bracket_end) / 2

    def _longitude_crossed(self, lon1: float, lon2: float, target: float) -> bool:
        """Check if longitude crossing occurred between two positions."""
        # Normalize longitudes to 0-360
        lon1 = lon1 % 360
        lon2 = lon2 % 360
        target = target % 360

        # Handle wrapping around 0/360 degrees
        if abs(lon2 - lon1) > 180:
            # Crossing occurred around 0/360 degree point
            if lon1 > 180:
                lon1 -= 360
            if lon2 > 180:
                lon2 -= 360
            if target > 180:
                target -= 360

        # Check if target is between lon1 and lon2
        return (lon1 <= target <= lon2) or (lon2 <= target <= lon1)

    def find_sign_ingress(
        self, planet: int, target_sign: int, start_jd: float, backwards: bool = False
    ) -> Optional[TransitEvent]:
        """Find when a planet ingresses into a specific sign."""
        # Calculate target longitude for sign ingress
        target_longitude = (target_sign - 1) * 30  # Signs are 30 degrees each

        crossing_jd = self.find_planet_crossing(planet, target_longitude, start_jd, backwards)

        if crossing_jd:
            crossing_dt = date.to_datetime(crossing_jd)

            return create_transit_event(
                event_type=transits.EVENT_INGRESS_SIGN,
                date_time=crossing_dt,
                julian_date=crossing_jd,
                transiting_object=planet,
                longitude=target_longitude,
                from_position=target_sign - 1 if target_sign > 1 else 12,
                to_position=target_sign,
                exact=True,
                precision_achieved=self.precision,
            )

        return None

    def find_aspect_formation(
        self,
        transiting_planet: int,
        target_longitude: float,
        aspect_degrees: float,
        start_jd: float,
        backwards: bool = False,
    ) -> Optional[TransitEvent]:
        """Find when a transiting planet forms an aspect to a target longitude."""

        # Calculate the exact longitude where the aspect forms
        aspect_longitude = (target_longitude + aspect_degrees) % 360

        crossing_jd = self.find_planet_crossing(transiting_planet, aspect_longitude, start_jd, backwards)

        if crossing_jd:
            crossing_dt = date.to_datetime(crossing_jd)

            return create_transit_event(
                event_type=transits.EVENT_ASPECT,
                date_time=crossing_dt,
                julian_date=crossing_jd,
                transiting_object=transiting_planet,
                target_object=None,  # Will be set by caller
                aspect_type=aspect_degrees,  # Will be mapped to calc constant
                longitude=aspect_longitude,
                exact=True,
                orb=0.0,  # Exact by definition
                precision_achieved=self.precision,
            )

        return None

    def find_planetary_stations(self, planet: int, start_jd: float, end_jd: float) -> List[TransitEvent]:
        """Find all retrograde/direct stations for a planet in the given period."""
        stations = []
        current_jd = start_jd
        step_size = 1.0  # 1 day steps

        previous_speed = None

        while current_jd < end_jd:
            # Get planet position and speed
            try:
                pos_data = ephemeris.get_planet(planet, current_jd)
                current_speed = pos_data.get("speed", 0)

                # Check for speed sign change (station)
                if previous_speed is not None:
                    if (previous_speed > 0 and current_speed < 0) or (previous_speed < 0 and current_speed > 0):

                        # Refine station timing
                        station_jd = self._refine_station_timing(planet, current_jd - step_size, current_jd)

                        if station_jd:
                            station_dt = date.to_datetime(station_jd)
                            station_type = (
                                transits.STATION_RETROGRADE if previous_speed > 0 else transits.STATION_DIRECT
                            )

                            station_event = create_transit_event(
                                event_type=transits.EVENT_STATION,
                                date_time=station_dt,
                                julian_date=station_jd,
                                transiting_object=planet,
                                longitude=pos_data.get("lon", 0),
                                station_type=station_type,
                                speed_before=previous_speed,
                                speed_after=current_speed,
                                exact=True,
                                precision_achieved=self.precision,
                            )
                            stations.append(station_event)

                previous_speed = current_speed
                current_jd += step_size

            except Exception:
                current_jd += step_size
                continue

        return stations

    def _refine_station_timing(self, planet: int, start_jd: float, end_jd: float) -> Optional[float]:
        """Refine station timing using binary search to achieve target precision."""

        max_iterations = transits.MAX_ITERATIONS
        iteration = 0

        while (end_jd - start_jd) > self.tolerance and iteration < max_iterations:
            mid_jd = (start_jd + end_jd) / 2

            try:
                start_speed = ephemeris.get_planet(planet, start_jd).get("speed", 0)
                mid_speed = ephemeris.get_planet(planet, mid_jd).get("speed", 0)

                # Check which half contains the station
                if (start_speed > 0) == (mid_speed > 0):
                    start_jd = mid_jd
                else:
                    end_jd = mid_jd

                iteration += 1

            except Exception:
                break

        return (start_jd + end_jd) / 2

    def calculate_transit_timeline(
        self,
        objects: List[int],
        start_date: datetime,
        end_date: datetime,
        interval: transits.IntervalType = transits.DEFAULT_INTERVAL,
        latitude: float = 0.0,
        longitude: float = 0.0,
    ) -> TransitPeriod:
        """Calculate planetary positions at regular intervals over a time period."""

        period_interval = self.normalize_interval(interval)
        events = []

        current_dt = start_date
        while current_dt <= end_date:
            current_jd = date.to_jd(current_dt)

            # Get positions for all requested objects at this time
            for obj in objects:
                try:
                    pos_data = ephemeris.get_planet(obj, current_jd)

                    # Create a position event (not a crossing event)
                    position_event = TransitEvent(
                        event_type="position",  # Special type for timeline
                        date_time=current_dt,
                        julian_date=current_jd,
                        transiting_object=obj,
                        longitude=pos_data.get("lon", 0),
                        exact=False,
                        precision_achieved=self.precision,
                        metadata=pos_data,
                    )
                    events.append(position_event)

                except Exception:
                    continue

            current_dt += period_interval

        return TransitPeriod(start_date=start_date, end_date=end_date, events=events, interval=interval)

    def generate_intensity_curve(
        self,
        transiting_planet: int,
        target_object: int,
        aspect_type: int,
        natal_longitude: float,
        start_jd: float,
        end_jd: float,
        curve_orb: float = 8.0,
        sampling_interval: Union[str, timedelta] = "daily"
    ) -> Optional[IntensityCurve]:
        """
        Generate an intensity curve for a specific aspect between two objects.

        Args:
            transiting_planet: The transiting planet (chart constant)
            target_object: The target object (chart constant)
            aspect_type: The aspect type (calc constant)
            natal_longitude: The longitude of the target object
            start_jd: Start of the period to analyze
            end_jd: End of the period to analyze
            curve_orb: Maximum orb to include in curve (degrees)
            sampling_interval: How often to sample (string or timedelta)

        Returns:
            IntensityCurve object with time-series data, or None if no samples within orb
        """

        # Convert sampling interval to timedelta
        sample_delta = self.normalize_interval(sampling_interval)

        # Calculate aspect longitude target
        aspect_longitude = (natal_longitude + aspect_type) % 360

        # Initialize curve data
        samples = []
        event_id = f"{transiting_planet}_{target_object}_{aspect_type}_{int(start_jd)}"

        # Track retrograde sessions
        retrograde_sessions = []
        current_retrograde_session = 0
        previous_retrograde = None

        # Sampling loop
        current_jd = start_jd
        sample_count = 0
        max_samples = 10000  # Safety limit

        while current_jd <= end_jd and sample_count < max_samples:
            try:
                # Get transiting planet position
                planet_pos = ephemeris.get_planet(transiting_planet, current_jd)
                planet_lon = planet_pos['lon']
                planet_speed = planet_pos.get('speed', 0)

                # Calculate orb (angular distance from exact aspect)
                orb_value = self._calculate_orb(planet_lon, aspect_longitude)

                # Only include samples within the specified curve orb
                if orb_value <= curve_orb:
                    current_dt = date.to_datetime(current_jd)

                    # Determine if applying or separating
                    applying = self._is_aspect_applying(
                        transiting_planet, planet_lon, aspect_longitude, current_jd
                    )

                    # Track retrograde motion
                    is_retrograde = planet_speed < 0

                    # Detect retrograde session changes
                    if previous_retrograde is not None and previous_retrograde != is_retrograde:
                        if is_retrograde:
                            # Starting new retrograde session
                            current_retrograde_session += 1
                            retrograde_sessions.append({
                                'session_number': current_retrograde_session,
                                'start_jd': current_jd,
                                'station_retrograde_jd': current_jd,
                                'end_jd': None,
                                'station_direct_jd': None,
                                'multiple_exactness': False  # Will be calculated later
                            })
                        else:
                            # Ending retrograde session
                            if retrograde_sessions:
                                retrograde_sessions[-1]['end_jd'] = current_jd
                                retrograde_sessions[-1]['station_direct_jd'] = current_jd

                    previous_retrograde = is_retrograde

                    # Create sample data point
                    sample = {
                        'julian_date': current_jd,
                        'datetime': current_dt,
                        'orb_value': orb_value,
                        'applying': applying,
                        'retrograde': is_retrograde,
                        'retrograde_session': current_retrograde_session if is_retrograde else 0
                    }

                    samples.append(sample)

                # Adaptive sampling based on orb distance
                if orb_value <= 1.0:
                    # Within 1 degree - sample hourly
                    step_delta = timedelta(hours=1)
                elif orb_value <= 3.0:
                    # Within 3 degrees - sample every 6 hours
                    step_delta = timedelta(hours=6)
                elif orb_value <= 5.0:
                    # Within 5 degrees - use specified sampling interval
                    step_delta = sample_delta
                else:
                    # Beyond 5 degrees - sample weekly for efficiency
                    step_delta = timedelta(weeks=1)

                current_jd += step_delta.total_seconds() / 86400.0  # Convert to Julian days
                sample_count += 1

            except Exception as e:
                # Skip problematic dates and continue
                current_jd += sample_delta.total_seconds() / 86400.0
                sample_count += 1
                continue

        # If no samples within orb, return None
        if not samples:
            return None

        # Close any open retrograde session
        if retrograde_sessions and retrograde_sessions[-1]['end_jd'] is None:
            retrograde_sessions[-1]['end_jd'] = end_jd

        # Calculate metadata
        peak_sample = min(samples, key=lambda s: s['orb_value'])

        # Determine multiple exactness for retrograde sessions
        exact_threshold = 0.1  # Consider orb < 0.1° as "exact"
        exact_samples = [s for s in samples if s['orb_value'] < exact_threshold]

        for session in retrograde_sessions:
            session_samples = [s for s in exact_samples if s['retrograde_session'] == session['session_number']]
            if len(session_samples) > 1:
                session['multiple_exactness'] = True

        metadata = {
            'retrograde_sessions': retrograde_sessions,
            'peak_intensity': {
                'best_orb': peak_sample['orb_value'],
                'julian_date': peak_sample['julian_date'],
                'retrograde_session': peak_sample['retrograde_session']
            },
            'total_samples': len(samples),
            'time_span_days': end_jd - start_jd,
            'exact_moments': len(exact_samples)
        }

        sampling_config = {
            'curve_orb': curve_orb,
            'sampling_interval': str(sampling_interval),
            'adaptive_sampling': True,
            'start_jd': start_jd,
            'end_jd': end_jd
        }

        return IntensityCurve(
            transit_event_id=event_id,
            transiting_object=transiting_planet,
            target_object=target_object,
            aspect_type=aspect_type,
            samples=samples,
            sampling_config=sampling_config,
            metadata=metadata
        )

    def _calculate_orb(self, planet_lon: float, aspect_lon: float) -> float:
        """Calculate the orb (angular distance) between two longitudes."""
        diff = abs(planet_lon - aspect_lon)
        # Handle wraparound at 0/360 degrees
        if diff > 180:
            diff = 360 - diff
        return diff

    def _is_aspect_applying(self, planet: int, planet_lon: float, aspect_lon: float, jd: float) -> bool:
        """Determine if an aspect is applying (getting closer) or separating (moving away)."""
        try:
            # Get planet position slightly in the future
            future_jd = jd + 0.01  # ~15 minutes in the future
            future_pos = ephemeris.get_planet(planet, future_jd)
            future_lon = future_pos['lon']

            # Calculate current and future orbs
            current_orb = self._calculate_orb(planet_lon, aspect_lon)
            future_orb = self._calculate_orb(future_lon, aspect_lon)

            # If future orb is smaller, the aspect is applying
            return future_orb < current_orb

        except:
            # Fallback: assume applying if planet is moving forward
            try:
                pos_data = ephemeris.get_planet(planet, jd)
                speed = pos_data.get('speed', 0)
                return speed > 0  # Simple approximation
            except:
                return True  # Default to applying

    def find_solar_eclipses(
        self, start_jd: float, end_jd: float, latitude: float = 0.0, longitude: float = 0.0
    ) -> List[TransitEvent]:
        """Find all solar eclipses within the given time period.

        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            latitude: Observer latitude (for local visibility)
            longitude: Observer longitude (for local visibility)

        Returns:
            List of solar eclipse TransitEvent objects
        """
        eclipses = []
        current_jd = start_jd

        while current_jd < end_jd:
            try:
                # Find next solar eclipse globally
                eclipse_type, eclipse_times = swe.sol_eclipse_when_glob(
                    current_jd, swe.ECL_ALLTYPES_SOLAR, 0
                )

                if eclipse_times[0] <= end_jd:
                    eclipse_jd = eclipse_times[0]  # Maximum eclipse time
                    eclipse_dt = date.to_datetime(eclipse_jd)

                    # Get Sun position at eclipse time (eclipse longitude)
                    sun_position = ephemeris.get_planet(chart.SUN, eclipse_jd)
                    eclipse_longitude = sun_position['lon']

                    # Calculate house position if coordinates provided
                    eclipse_house = None
                    if latitude != 0.0 or longitude != 0.0:
                        try:
                            houses = ephemeris.get_houses(
                                jd=eclipse_jd,
                                lat=latitude,
                                lon=longitude,
                                house_system=settings.house_system
                            )
                            eclipse_house = self._get_house_for_longitude(eclipse_longitude, houses)
                        except:
                            pass

                    # Determine eclipse type
                    eclipse_subtype = transits.ECLIPSE_PARTIAL
                    if eclipse_type & swe.ECL_TOTAL:
                        eclipse_subtype = transits.ECLIPSE_TOTAL
                    elif eclipse_type & swe.ECL_ANNULAR:
                        eclipse_subtype = transits.ECLIPSE_ANNULAR

                    # Check local visibility if coordinates provided
                    visibility = True
                    if latitude != 0.0 or longitude != 0.0:
                        try:
                            local_type, local_times, local_attr = swe.sol_eclipse_when_loc(
                                current_jd, latitude, longitude, 0
                            )
                            visibility = bool(local_type & swe.ECL_VISIBLE)
                        except:
                            visibility = False

                    eclipse_event = create_transit_event(
                        event_type=transits.EVENT_ECLIPSE,
                        date_time=eclipse_dt,
                        julian_date=eclipse_jd,
                        transiting_object=chart.SUN,  # Solar eclipse
                        target_object=chart.MOON,      # Moon blocks Sun
                        longitude=eclipse_longitude,
                        house=eclipse_house,
                        exact=True,
                        eclipse_type=eclipse_subtype,  # total, partial, annular
                        visibility_info={'visible_from_location': visibility},
                        magnitude=1.0,  # Can be calculated from eclipse_times if needed
                        precision_achieved=self.precision,
                        metadata={
                            'eclipse_times': eclipse_times,
                            'eclipse_type_flags': eclipse_type,
                            'eclipse_category': transits.ECLIPSE_SOLAR,
                            'global_eclipse': True,
                        }
                    )
                    eclipses.append(eclipse_event)

                    # Move to next search point
                    current_jd = eclipse_jd + 1.0  # Move past this eclipse
                else:
                    break

            except swe.Error:
                # No more eclipses found in range
                break

        return eclipses

    def find_lunar_eclipses(
        self, start_jd: float, end_jd: float, latitude: float = 0.0, longitude: float = 0.0
    ) -> List[TransitEvent]:
        """Find all lunar eclipses within the given time period.

        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            latitude: Observer latitude (for local visibility)
            longitude: Observer longitude (for local visibility)

        Returns:
            List of lunar eclipse TransitEvent objects
        """
        eclipses = []
        current_jd = start_jd

        while current_jd < end_jd:
            try:
                # Find next lunar eclipse
                eclipse_type, eclipse_times = swe.lun_eclipse_when(
                    current_jd, swe.ECL_ALLTYPES_LUNAR, 0
                )

                if eclipse_times[0] <= end_jd:
                    eclipse_jd = eclipse_times[0]  # Maximum eclipse time
                    eclipse_dt = date.to_datetime(eclipse_jd)

                    # Get Moon position at eclipse time (eclipse longitude)
                    moon_position = ephemeris.get_planet(chart.MOON, eclipse_jd)
                    eclipse_longitude = moon_position['lon']

                    # Calculate house position if coordinates provided
                    eclipse_house = None
                    if latitude != 0.0 or longitude != 0.0:
                        try:
                            houses = ephemeris.get_houses(
                                jd=eclipse_jd,
                                lat=latitude,
                                lon=longitude,
                                house_system=settings.house_system
                            )
                            eclipse_house = self._get_house_for_longitude(eclipse_longitude, houses)
                        except:
                            pass

                    # Determine eclipse type
                    eclipse_subtype = transits.ECLIPSE_PARTIAL
                    if eclipse_type & swe.ECL_TOTAL:
                        eclipse_subtype = transits.ECLIPSE_TOTAL
                    elif eclipse_type & swe.ECL_PENUMBRAL:
                        eclipse_subtype = transits.ECLIPSE_PENUMBRAL

                    # Check local visibility if coordinates provided
                    visibility = True
                    if latitude != 0.0 or longitude != 0.0:
                        try:
                            local_type, local_times, local_attr = swe.lun_eclipse_when_loc(
                                current_jd, latitude, longitude, 0
                            )
                            visibility = bool(local_type & swe.ECL_VISIBLE)
                        except:
                            visibility = False

                    eclipse_event = create_transit_event(
                        event_type=transits.EVENT_ECLIPSE,
                        date_time=eclipse_dt,
                        julian_date=eclipse_jd,
                        transiting_object=chart.MOON,  # Lunar eclipse
                        target_object=chart.SUN,       # Earth's shadow
                        longitude=eclipse_longitude,
                        house=eclipse_house,
                        exact=True,
                        eclipse_type=eclipse_subtype,  # total, partial, penumbral
                        visibility_info={'visible_from_location': visibility},
                        magnitude=1.0,  # Can be calculated from eclipse_times if needed
                        precision_achieved=self.precision,
                        metadata={
                            'eclipse_times': eclipse_times,
                            'eclipse_type_flags': eclipse_type,
                            'eclipse_category': transits.ECLIPSE_LUNAR,
                            'global_eclipse': True,
                        }
                    )
                    eclipses.append(eclipse_event)

                    # Move to next search point
                    current_jd = eclipse_jd + 1.0  # Move past this eclipse
                else:
                    break

            except swe.Error:
                # No more eclipses found in range
                break

        return eclipses

    def find_all_eclipses(
        self, start_jd: float, end_jd: float, latitude: float = 0.0, longitude: float = 0.0
    ) -> List[TransitEvent]:
        """Find all eclipses (solar and lunar) within the given time period.

        Args:
            start_jd: Starting Julian day
            end_jd: Ending Julian day
            latitude: Observer latitude (for local visibility)
            longitude: Observer longitude (for local visibility)

        Returns:
            List of all eclipse TransitEvent objects, sorted by date
        """
        all_eclipses = []

        # Find solar eclipses
        solar_eclipses = self.find_solar_eclipses(start_jd, end_jd, latitude, longitude)
        all_eclipses.extend(solar_eclipses)

        # Find lunar eclipses
        lunar_eclipses = self.find_lunar_eclipses(start_jd, end_jd, latitude, longitude)
        all_eclipses.extend(lunar_eclipses)

        # Sort by date
        all_eclipses.sort(key=lambda e: e.julian_date)
        return all_eclipses

    def _get_house_for_longitude(self, longitude: float, houses: dict) -> Optional[int]:
        """Determine which house a given longitude falls into.

        Args:
            longitude: The ecliptic longitude in degrees
            houses: Dictionary of house cusps from ephemeris.get_houses()

        Returns:
            House number (1-12) or None if cannot be determined
        """
        if not houses:
            return None

        try:
            # Get house cusps (1st house cusp, 2nd house cusp, etc.)
            cusps = []
            for house_num in range(1, 13):
                if house_num in houses:
                    cusps.append((house_num, houses[house_num]['lon']))

            if not cusps:
                return None

            # Sort cusps by longitude
            cusps.sort(key=lambda x: x[1])

            # Find which house the longitude falls into
            longitude = longitude % 360

            for i, (house_num, cusp_lon) in enumerate(cusps):
                next_cusp_lon = cusps[(i + 1) % 12][1]

                # Handle wrap-around at 0/360 degrees
                if cusp_lon <= next_cusp_lon:
                    if cusp_lon <= longitude < next_cusp_lon:
                        return house_num
                else:  # Wrap around case
                    if longitude >= cusp_lon or longitude < next_cusp_lon:
                        return house_num

            # Fallback - should not happen
            return 1

        except:
            return None
