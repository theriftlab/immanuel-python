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
