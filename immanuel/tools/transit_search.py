"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides specialized transit search functionality for finding
    specific transit events within date ranges with high precision.

"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import swisseph as swe

from immanuel.classes.transit_events import (
    TransitEvent,
    create_transit_event,
)
from immanuel.const import calc, chart, transits
from immanuel.setup import settings
from immanuel.tools import date, ephemeris, transit
from immanuel.tools.transit import TransitCalculator


class TransitSearch:
    """Advanced transit search functionality for finding specific events."""

    def __init__(
        self,
        natal_chart: Optional['Chart'] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        precision: str = transits.DEFAULT_PRECISION,
    ):
        self.natal_chart = natal_chart
        self.start_date = start_date or datetime.now()
        self.end_date = end_date or (datetime.now() + timedelta(days=365))
        self.calculator = TransitCalculator(precision=precision)

    def find_aspects(
        self,
        transiting_planet: int,
        natal_planet: int,
        aspect: int,
        max_orb: float = 1.0,
        backwards: bool = False,
    ) -> List[TransitEvent]:
        """
        Find all aspects between a transiting planet and natal planet.

        Args:
            transiting_planet: Planet constant for transiting planet
            natal_planet: Planet constant for natal planet
            aspect: Aspect constant (calc.CONJUNCTION, calc.OPPOSITION, etc.)
            max_orb: Maximum orb to consider (degrees)
            backwards: Search backwards in time

        Returns:
            List of TransitEvent objects for found aspects
        """
        if not self.natal_chart:
            raise ValueError("Natal chart required for aspect search")

        aspects_found = []

        # Get natal planet position
        natal_object = self.natal_chart._objects.get(natal_planet)
        if not natal_object:
            return aspects_found

        natal_longitude = natal_object['lon']

        # Calculate target longitudes for the aspect (most aspects have two positions)
        aspect_longitudes = []

        # Add the forward aspect (e.g., +60° for sextile)
        aspect_longitudes.append((natal_longitude + aspect) % 360)

        # Add the backward aspect for non-conjunction/opposition aspects
        if aspect != 0 and aspect != 180:  # Not conjunction or opposition
            aspect_longitudes.append((natal_longitude - aspect) % 360)

        # Search for crossings within the time period
        current_jd = date.to_jd(self.start_date)
        end_jd = date.to_jd(self.end_date)

        # Use a sequential search approach to find ALL crossings
        found_dates = set()  # Track found dates to prevent duplicates

        # Search for each aspect longitude
        for aspect_longitude in aspect_longitudes:
            current_jd = date.to_jd(self.start_date)  # Reset for each aspect longitude

            while current_jd < end_jd:
                try:
                    # Find next crossing of the aspect longitude
                    crossing_jd = self.calculator.find_planet_crossing(
                        transiting_planet, aspect_longitude, current_jd, backwards
                    )

                    if crossing_jd and crossing_jd <= end_jd:
                        # Create a unique key for this event (rounded to avoid tiny differences)
                        event_key = round(crossing_jd, 4)

                        if event_key not in found_dates:
                            # Verify the aspect is within orb
                            crossing_pos = ephemeris.get_planet(transiting_planet, crossing_jd)
                            actual_distance = abs(crossing_pos['lon'] - aspect_longitude)

                            # Handle longitude wrapping (e.g., 359° vs 1°)
                            if actual_distance > 180:
                                actual_distance = 360 - actual_distance

                            if actual_distance <= max_orb:
                                found_dates.add(event_key)
                                crossing_dt = date.to_datetime(crossing_jd)

                                aspect_event = create_transit_event(
                                    event_type=transits.EVENT_ASPECT,
                                    date_time=crossing_dt,
                                    julian_date=crossing_jd,
                                    transiting_object=transiting_planet,
                                    target_object=natal_planet,
                                    aspect_type=aspect,
                                    orb=actual_distance,
                                    exact=(actual_distance < 0.1),  # Within 0.1 degrees
                                    longitude=crossing_pos['lon'],
                                    precision_achieved=self.calculator.precision
                                )
                                aspects_found.append(aspect_event)

                        # Move search forward past this event
                        current_jd = crossing_jd + 5.0  # 5 days forward
                    else:
                        # No more crossings found, exit
                        break

                except Exception:
                    # Move forward and try again
                    current_jd += 30.0

        return aspects_found

    def find_sign_ingresses(
        self,
        planet: int,
        target_signs: Optional[List[int]] = None,
    ) -> List[TransitEvent]:
        """
        Find all sign ingresses for a planet within the search period.

        Args:
            planet: Planet constant
            target_signs: List of sign numbers to search for (1-12), or None for all

        Returns:
            List of TransitEvent objects for found ingresses
        """
        ingresses_found = []
        found_dates = set()  # Track found dates to prevent duplicates
        signs_to_search = target_signs or list(range(1, 13))

        current_jd = date.to_jd(self.start_date)
        end_jd = date.to_jd(self.end_date)

        # Search for the next ingress for each sign from the current position
        for sign in signs_to_search:
            search_jd = current_jd

            while search_jd < end_jd:
                ingress_event = self.calculator.find_sign_ingress(
                    planet, sign, search_jd
                )

                if ingress_event and ingress_event.julian_date <= end_jd:
                    # Create a unique key for this event (rounded to avoid tiny differences)
                    event_key = (sign, round(ingress_event.julian_date, 4))

                    if event_key not in found_dates:
                        found_dates.add(event_key)
                        ingresses_found.append(ingress_event)
                        # Move search forward past this event
                        search_jd = ingress_event.julian_date + 1.0
                    else:
                        break  # Already found this ingress
                else:
                    break  # No more ingresses found for this sign

        # Sort by date
        ingresses_found.sort(key=lambda e: e.julian_date)
        return ingresses_found

    def find_stations(
        self,
        planet: int,
        station_type: Optional[str] = None,
    ) -> List[TransitEvent]:
        """
        Find all retrograde/direct stations for a planet.

        Args:
            planet: Planet constant
            station_type: 'retrograde', 'direct', or None for both

        Returns:
            List of TransitEvent objects for found stations
        """
        stations = self.calculator.find_planetary_stations(
            planet,
            date.to_jd(self.start_date),
            date.to_jd(self.end_date)
        )

        if station_type:
            stations = [s for s in stations
                        if s.metadata.get('station_type') == station_type]

        return stations

    def find_planetary_return(
        self,
        planet: int,
    ) -> Optional[TransitEvent]:
        """
        Find the next planetary return (planet returning to natal position).

        Args:
            planet: Planet constant

        Returns:
            TransitEvent for the planetary return, or None if not found
        """
        if not self.natal_chart:
            raise ValueError("Natal chart required for planetary return search")

        # Get natal planet position
        natal_object = self.natal_chart._objects.get(planet)
        if not natal_object:
            return None

        natal_longitude = natal_object['lon']

        # Find when transiting planet returns to natal longitude
        current_jd = date.to_jd(self.start_date)

        return_jd = self.calculator.find_planet_crossing(
            planet, natal_longitude, current_jd
        )

        if return_jd:
            return_dt = date.to_datetime(return_jd)

            return create_transit_event(
                event_type=transits.EVENT_PLANETARY_RETURN,
                date_time=return_dt,
                julian_date=return_jd,
                transiting_object=planet,
                target_object=planet,  # Returning to itself
                aspect_type=calc.CONJUNCTION,  # Return is a conjunction
                orb=0.0,  # Exact by definition
                exact=True,
                longitude=natal_longitude,
                precision_achieved=self.calculator.precision
            )

        return None

    def find_lunar_phases(
        self,
        phase_types: Optional[List[int]] = None,
    ) -> List[TransitEvent]:
        """
        Find lunar phases (New Moon, Full Moon, quarters) within the period.

        Args:
            phase_types: List of phase constants to search for, or None for all

        Returns:
            List of TransitEvent objects for found phases
        """
        phases_found = []
        phases_to_search = phase_types or [0, 90, 180, 270]  # Major phases

        current_jd = date.to_jd(self.start_date)
        end_jd = date.to_jd(self.end_date)

        while current_jd < end_jd:
            try:
                # Get Sun and Moon positions
                sun_pos = ephemeris.get_planet(chart.SUN, current_jd)
                moon_pos = ephemeris.get_planet(chart.MOON, current_jd)

                # Calculate phase angle
                phase_angle = (moon_pos['lon'] - sun_pos['lon']) % 360

                # Check if we're near a target phase
                for target_phase in phases_to_search:
                    angle_diff = abs(phase_angle - target_phase)
                    if angle_diff <= 1.0:  # Within 1 degree
                        phase_dt = date.to_datetime(current_jd)

                        phase_event = create_transit_event(
                            event_type="lunar_phase",
                            date_time=phase_dt,
                            julian_date=current_jd,
                            transiting_object=chart.MOON,
                            target_object=chart.SUN,
                            aspect_type=target_phase,
                            orb=angle_diff,
                            exact=(angle_diff < 0.1),
                            longitude=moon_pos['lon'],
                            precision_achieved=self.calculator.precision
                        )
                        phases_found.append(phase_event)

                current_jd += 1.0  # Check daily

            except Exception:
                current_jd += 1.0

        return phases_found

    def search_comprehensive(
        self,
        include_aspects: bool = True,
        include_ingresses: bool = True,
        include_stations: bool = True,
        include_returns: bool = False,
        planets: Optional[List[int]] = None,
    ) -> Dict[str, List[TransitEvent]]:
        """
        Perform a comprehensive search for multiple types of transit events.

        Args:
            include_aspects: Search for aspects to natal chart
            include_ingresses: Search for sign ingresses
            include_stations: Search for planetary stations
            include_returns: Search for planetary returns
            planets: List of planets to search, or None for default set

        Returns:
            Dictionary with event types as keys and lists of events as values
        """
        results = {}
        search_planets = planets or [
            chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
            chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO
        ]

        if include_aspects and self.natal_chart:
            results['aspects'] = []
            for t_planet in search_planets:
                for n_planet in search_planets:
                    for aspect in settings.aspects:
                        aspects = self.find_aspects(t_planet, n_planet, aspect)
                        results['aspects'].extend(aspects)

        if include_ingresses:
            results['ingresses'] = []
            for planet in search_planets:
                ingresses = self.find_sign_ingresses(planet)
                results['ingresses'].extend(ingresses)

        if include_stations:
            results['stations'] = []
            # Stations only relevant for outer planets
            station_planets = [chart.MERCURY, chart.VENUS, chart.MARS,
                               chart.JUPITER, chart.SATURN, chart.URANUS,
                               chart.NEPTUNE, chart.PLUTO]
            for planet in station_planets:
                if planet in search_planets:
                    stations = self.find_stations(planet)
                    results['stations'].extend(stations)

        if include_returns and self.natal_chart:
            results['returns'] = []
            for planet in search_planets:
                if planet != chart.SUN and planet != chart.MOON:  # Exclude Sun/Moon
                    return_event = self.find_planetary_return(planet)
                    if return_event:
                        results['returns'].append(return_event)

        return results