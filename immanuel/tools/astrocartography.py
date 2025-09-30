"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Astrocartography calculation engine using Swiss Ephemeris.
    Provides core astronomical calculations for planetary line generation,
    zenith points, parans, local space lines, and aspect lines.

"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from immanuel.classes.astrocartography_entities import (
    AspectLine, LocalSpaceLine, ParanLine, PlanetaryLine, ZenithPoint
)
from immanuel.const import astrocartography, chart
from immanuel.tools import ephemeris


class AstrocartographyCalculator:
    """
    Core astrocartography calculation engine using Swiss Ephemeris.

    Provides low-level astronomical calculations for planetary line generation.
    """

    def __init__(
        self,
        julian_date: float,
        sampling_resolution: float = astrocartography.DEFAULT_SAMPLING_RESOLUTION,
        calculation_method: str = astrocartography.METHOD_ZODIACAL
    ):
        """
        Initialize calculator for specific birth moment.

        Args:
            julian_date: Birth moment in Julian Date format
            sampling_resolution: Degree interval for geographic sampling
            calculation_method: 'zodiacal' or 'mundo' calculation approach

        Raises:
            ValueError: If parameters are invalid
            EphemerisError: If Swiss Ephemeris initialization fails
        """
        # Validate julian date
        if not isinstance(julian_date, (int, float)) or julian_date <= 0:
            raise ValueError(f"Invalid julian_date: {julian_date}")

        # Validate sampling resolution
        if not (astrocartography.MIN_SAMPLING_RESOLUTION <= sampling_resolution <= astrocartography.MAX_SAMPLING_RESOLUTION):
            raise ValueError(f"Sampling resolution {sampling_resolution} out of valid range")

        # Validate calculation method
        if calculation_method not in astrocartography.CALCULATION_METHODS:
            raise ValueError(f"Invalid calculation_method: {calculation_method}")

        self.julian_date = julian_date
        self.sampling_resolution = sampling_resolution
        self.calculation_method = calculation_method

        # Cache for planetary positions
        self._position_cache = {}

        # Test Swiss Ephemeris accessibility
        try:
            # Try a simple calculation to verify ephemeris is working
            swe.calc_ut(julian_date, swe.SUN)
        except Exception as e:
            raise RuntimeError(f"Swiss Ephemeris initialization failed: {e}")

    def calculate_mc_ic_lines(
        self,
        planet_id: int,
        latitude_range: Tuple[float, float] = (astrocartography.MIN_LATITUDE, astrocartography.MAX_LATITUDE)
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Calculate Midheaven and Imum Coeli lines for a planet.

        MC/IC lines are simple vertical lines of constant longitude passing through the zenith.

        Args:
            planet_id: Planet identifier constant
            latitude_range: Latitude range to sample (min_lat, max_lat)

        Returns:
            Tuple of (mc_coordinates, ic_coordinates) as (longitude, latitude) pairs

        Raises:
            PlanetError: If planet_id is invalid
            CalculationError: If ephemeris calculation fails
        """
        # Validate inputs
        self._validate_planet_id(planet_id)
        self._validate_latitude_range(latitude_range)

        # Get zenith point using same calculation as zenith method
        zenith_longitude, zenith_latitude = self.calculate_zenith_point(planet_id)

        # MC line: vertical line through zenith longitude
        # IC line: vertical line 180° opposite to MC
        mc_longitude = zenith_longitude
        ic_longitude = self._normalize_longitude(mc_longitude + 180.0)

        mc_coordinates = []
        ic_coordinates = []

        # Generate coordinate points along latitude range - simple vertical lines
        min_lat, max_lat = latitude_range
        latitudes = self._generate_latitude_samples(min_lat, max_lat)

        for latitude in latitudes:
            mc_coordinates.append((mc_longitude, latitude))
            ic_coordinates.append((ic_longitude, latitude))

        return mc_coordinates, ic_coordinates

    def calculate_ascendant_descendant_lines(
        self,
        planet_id: int,
        longitude_range: Tuple[float, float] = (astrocartography.MIN_LONGITUDE, astrocartography.MAX_LONGITUDE),
        latitude_range: Tuple[float, float] = (astrocartography.MIN_LATITUDE, astrocartography.MAX_LATITUDE)
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Calculate Ascendant and Descendant lines for a planet.

        ASC/DESC lines are actually the SAME continuous curve that wraps around the globe.
        The curve switches between "ascending" and "descending" at its extreme points.

        Args:
            planet_id: Planet identifier constant
            longitude_range: Longitude range to sample (min_lon, max_lon)
            latitude_range: Latitude range to sample (min_lat, max_lat)

        Returns:
            Tuple of (asc_coordinates, desc_coordinates) as (longitude, latitude) pairs

        Raises:
            PlanetError: If planet_id is invalid
            CalculationError: If ephemeris calculation fails
        """
        # Validate inputs
        self._validate_planet_id(planet_id)
        self._validate_longitude_range(longitude_range)
        self._validate_latitude_range(latitude_range)

        # Get planetary position
        planet_position = self.get_planetary_position(planet_id)

        # Calculate the complete horizon curve using same approach as zenith
        complete_curve = self._trace_complete_horizon_curve(planet_position, longitude_range, latitude_range)

        # Split the continuous curve into ASC and DESC portions
        asc_coordinates, desc_coordinates = self._split_horizon_curve(complete_curve)

        return asc_coordinates, desc_coordinates

    def calculate_zenith_point(self, planet_id: int) -> Tuple[float, float]:
        """
        Calculate exact zenith point where planet was directly overhead.

        Args:
            planet_id: Planet identifier constant

        Returns:
            Tuple of (longitude, latitude) for zenith point

        Raises:
            PlanetError: If planet_id is invalid
            CalculationError: If zenith calculation fails
        """
        # Validate inputs
        self._validate_planet_id(planet_id)

        # Get planetary position
        planet_position = self.get_planetary_position(planet_id)

        # Calculate proper zenith point (where planet is directly overhead)
        import swisseph as swe

        # Get Greenwich Sidereal Time at birth moment
        gst_hours = swe.sidtime(self.julian_date)
        gst_degrees = gst_hours * 15.0  # Convert to degrees

        # Get planet's equatorial coordinates
        if self.calculation_method == astrocartography.METHOD_ZODIACAL:
            # Convert ecliptic to equatorial coordinates
            equatorial = self._ecliptic_to_equatorial(
                planet_position['longitude'],
                planet_position['latitude']
            )
            planet_ra = equatorial['right_ascension']
            planet_dec = equatorial['declination']
        else:
            # Already in equatorial coordinates
            planet_ra = planet_position['right_ascension']
            planet_dec = planet_position['declination']

        # Zenith longitude: where Local Sidereal Time equals planet's Right Ascension
        # Since LST = GST + longitude, then longitude = RA - GST
        zenith_longitude = self._normalize_longitude(planet_ra - gst_degrees)

        # Zenith latitude: planet's declination (where it appears directly overhead)
        zenith_latitude = planet_dec

        # Normalize coordinates
        zenith_latitude = max(astrocartography.MIN_LATITUDE,
                            min(astrocartography.MAX_LATITUDE, zenith_latitude))

        return zenith_longitude, zenith_latitude

    def calculate_paran_line(
        self,
        primary_planet_id: int,
        secondary_planet_id: int,
        primary_angle: str,
        secondary_angle: str,
        orb_tolerance: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Calculate paran line where two planets are simultaneously angular.

        Args:
            primary_planet_id: First planet identifier
            secondary_planet_id: Second planet identifier
            primary_angle: Angular position of first planet ('MC', 'IC', 'ASC', 'DESC')
            secondary_angle: Angular position of second planet
            orb_tolerance: Orb tolerance for simultaneity in degrees

        Returns:
            List of (longitude, latitude) pairs forming the paran line

        Raises:
            PlanetError: If either planet_id is invalid
            ValueError: If angle specifications are invalid
            CalculationError: If paran calculation fails
        """
        # Validate inputs
        self._validate_planet_id(primary_planet_id)
        self._validate_planet_id(secondary_planet_id)

        if primary_planet_id == secondary_planet_id:
            raise ValueError("Primary and secondary planets must be different")

        if primary_angle not in astrocartography.LINE_TYPES:
            raise ValueError(f"Invalid primary_angle: {primary_angle}")
        if secondary_angle not in astrocartography.LINE_TYPES:
            raise ValueError(f"Invalid secondary_angle: {secondary_angle}")

        if orb_tolerance <= 0:
            raise ValueError(f"Orb tolerance must be positive: {orb_tolerance}")

        # Get planetary positions
        primary_position = self.get_planetary_position(primary_planet_id)
        secondary_position = self.get_planetary_position(secondary_planet_id)

        paran_coordinates = []

        # Sample the globe to find where both planets are simultaneously angular
        for longitude in self._generate_longitude_samples():
            for latitude in self._generate_latitude_samples():
                try:
                    # Check if both planets are at their specified angles simultaneously
                    if self._planets_simultaneously_angular(
                        primary_position, secondary_position,
                        longitude, latitude,
                        primary_angle, secondary_angle,
                        orb_tolerance
                    ):
                        paran_coordinates.append((longitude, latitude))

                except Exception:
                    # Skip problematic coordinates (extreme latitudes, etc.)
                    continue

        return paran_coordinates

    def calculate_local_space_line(
        self,
        planet_id: int,
        birth_longitude: float,
        birth_latitude: float
    ) -> Tuple[float, Tuple[float, float], float]:
        """
        Calculate local space line from birth location toward planet.

        Args:
            planet_id: Planet identifier constant
            birth_longitude: Birth location longitude
            birth_latitude: Birth location latitude

        Returns:
            Tuple of (azimuth_degrees, endpoint_coordinates, distance_km)

        Raises:
            PlanetError: If planet_id is invalid
            ValueError: If birth coordinates are invalid
            CalculationError: If local space calculation fails
        """
        # Validate inputs
        self._validate_planet_id(planet_id)
        self._validate_coordinates(birth_longitude, birth_latitude)

        # Get planetary position
        planet_position = self.get_planetary_position(planet_id)

        # Calculate azimuth (compass direction) from birth location to planet
        azimuth = self._calculate_azimuth(
            birth_latitude, birth_longitude,
            planet_position['right_ascension'], planet_position['declination']
        )

        # Calculate endpoint where line intersects map boundary
        endpoint_lon, endpoint_lat = self._calculate_line_endpoint(
            birth_longitude, birth_latitude, azimuth
        )

        # Calculate distance
        distance_km = self._calculate_distance_km(
            birth_latitude, birth_longitude,
            endpoint_lat, endpoint_lon
        )

        return azimuth, (endpoint_lon, endpoint_lat), distance_km

    def calculate_aspect_line(
        self,
        natal_planet_id: int,
        relocated_planet_id: int,
        aspect_degrees: float,
        relocated_date: datetime,
        orb_tolerance: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Calculate line where aspect between natal and relocated planet is exact.

        Args:
            natal_planet_id: Natal planet identifier
            relocated_planet_id: Relocated planet identifier
            aspect_degrees: Aspect angle (0, 60, 90, 120, 180, etc.)
            relocated_date: Date for relocated planet position
            orb_tolerance: Orb tolerance for aspect in degrees

        Returns:
            List of (longitude, latitude) pairs where aspect is exact

        Raises:
            PlanetError: If either planet_id is invalid
            ValueError: If aspect_degrees or date is invalid
            CalculationError: If aspect line calculation fails
        """
        # Validate inputs
        self._validate_planet_id(natal_planet_id)
        self._validate_planet_id(relocated_planet_id)

        if not (0 <= aspect_degrees < 360):
            raise ValueError(f"Invalid aspect_degrees: {aspect_degrees}")
        if not isinstance(relocated_date, datetime):
            raise ValueError("relocated_date must be a datetime object")
        if orb_tolerance <= 0:
            raise ValueError(f"Orb tolerance must be positive: {orb_tolerance}")

        # Get natal planet position (at birth JD)
        natal_position = self.get_planetary_position(natal_planet_id)

        # Convert relocated date to Julian date
        relocated_jd = swe.julday(
            relocated_date.year, relocated_date.month, relocated_date.day,
            relocated_date.hour + relocated_date.minute/60.0 + relocated_date.second/3600.0
        )

        aspect_coordinates = []

        # Sample the globe to find where the aspect is exact
        for longitude in self._generate_longitude_samples():
            for latitude in self._generate_latitude_samples():
                try:
                    # Calculate relocated planet position at this location
                    relocated_position = self._get_planet_position_at_location(
                        relocated_planet_id, relocated_jd, latitude, longitude
                    )

                    # Check if aspect is within orb
                    current_aspect = self._calculate_aspect_angle(
                        natal_position, relocated_position
                    )

                    if self._aspect_within_orb(current_aspect, aspect_degrees, orb_tolerance):
                        aspect_coordinates.append((longitude, latitude))

                except Exception:
                    # Skip problematic coordinates
                    continue

        return aspect_coordinates

    def get_planetary_position(
        self,
        planet_id: int,
        calculation_method: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get planetary position for the calculator's Julian date.

        Args:
            planet_id: Planet identifier constant
            calculation_method: Override default calculation method

        Returns:
            Dictionary with keys: longitude, latitude, right_ascension, declination

        Raises:
            PlanetError: If planet_id is invalid
            CalculationError: If ephemeris calculation fails
        """
        # Use override method or default
        method = calculation_method or self.calculation_method

        # Check cache first
        cache_key = (planet_id, method)
        if cache_key in self._position_cache:
            return self._position_cache[cache_key]

        # Validate planet
        self._validate_planet_id(planet_id)

        try:
            # Get ecliptic coordinates
            if planet_id in ephemeris._SWE:
                swe_id = ephemeris._SWE[planet_id]
                ec_res = swe.calc_ut(self.julian_date, swe_id)[0]
            else:
                raise ValueError(f"Unsupported planet_id: {planet_id}")

            # Get equatorial coordinates
            obliquity = swe.calc_ut(self.julian_date, swe.ECL_NUT)[0][0]
            eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -obliquity)

            position = {
                'longitude': ec_res[0],
                'latitude': ec_res[1],
                'right_ascension': eq_res[0],
                'declination': eq_res[1]
            }

            # Cache result
            self._position_cache[cache_key] = position
            return position

        except Exception as e:
            raise RuntimeError(f"Failed to calculate position for planet {planet_id}: {e}")

    def interpolate_line_at_extremes(
        self,
        partial_coordinates: List[Tuple[float, float]],
        target_latitude_range: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Interpolate line coordinates for extreme latitudes where calculation failed.

        Args:
            partial_coordinates: Successfully calculated coordinates
            target_latitude_range: Desired latitude coverage

        Returns:
            Extended coordinate list with interpolated values

        Raises:
            ValueError: If insufficient data for interpolation
        """
        if len(partial_coordinates) < 2:
            raise ValueError("Need at least 2 coordinates for interpolation")

        # Sort by latitude for interpolation
        sorted_coords = sorted(partial_coordinates, key=lambda x: x[1])

        # Target range
        min_target_lat, max_target_lat = target_latitude_range

        # Current range
        current_min_lat = sorted_coords[0][1]
        current_max_lat = sorted_coords[-1][1]

        interpolated_coords = list(sorted_coords)

        # Extend to southern extreme if needed
        if current_min_lat > min_target_lat:
            # Linear extrapolation from first two points
            if len(sorted_coords) >= 2:
                first_point = sorted_coords[0]
                second_point = sorted_coords[1]

                # Calculate slope
                dx = second_point[0] - first_point[0]
                dy = second_point[1] - first_point[1]

                if dy != 0:
                    slope = dx / dy

                    # Extrapolate to target latitude
                    target_lon = first_point[0] + slope * (min_target_lat - first_point[1])
                    target_lon = self._normalize_longitude(target_lon)

                    interpolated_coords.insert(0, (target_lon, min_target_lat))

        # Extend to northern extreme if needed
        if current_max_lat < max_target_lat:
            # Linear extrapolation from last two points
            if len(sorted_coords) >= 2:
                second_last_point = sorted_coords[-2]
                last_point = sorted_coords[-1]

                # Calculate slope
                dx = last_point[0] - second_last_point[0]
                dy = last_point[1] - second_last_point[1]

                if dy != 0:
                    slope = dx / dy

                    # Extrapolate to target latitude
                    target_lon = last_point[0] + slope * (max_target_lat - last_point[1])
                    target_lon = self._normalize_longitude(target_lon)

                    interpolated_coords.append((target_lon, max_target_lat))

        return interpolated_coords

    def validate_performance(
        self,
        planet_count: int,
        line_types: List[str],
        target_seconds: float = 10.0
    ) -> Dict[str, float]:
        """
        Estimate calculation time for given configuration.

        Args:
            planet_count: Number of planets to calculate
            line_types: List of line types to calculate
            target_seconds: Target performance in seconds

        Returns:
            Dictionary with estimated times and performance metrics

        Raises:
            PerformanceError: If configuration exceeds performance targets
        """
        # Rough performance estimates based on sampling resolution
        base_time_per_planet = 0.5  # seconds
        time_per_line_type = 0.3    # seconds
        resolution_factor = self.sampling_resolution / astrocartography.DEFAULT_SAMPLING_RESOLUTION

        estimated_time = (
            planet_count * base_time_per_planet *
            len(line_types) * time_per_line_type *
            (1.0 / resolution_factor)  # finer resolution = slower
        )

        metrics = {
            'estimated_seconds': estimated_time,
            'target_seconds': target_seconds,
            'planet_count': planet_count,
            'line_type_count': len(line_types),
            'sampling_resolution': self.sampling_resolution,
            'performance_ratio': estimated_time / target_seconds
        }

        if estimated_time > target_seconds:
            raise RuntimeError(
                f"Configuration exceeds performance target: "
                f"{estimated_time:.1f}s > {target_seconds:.1f}s"
            )

        return metrics

    # Helper methods

    def _validate_planet_id(self, planet_id: int):
        """Validate planet ID is supported."""
        if planet_id not in ephemeris._SWE:
            raise ValueError(f"Unsupported planet_id: {planet_id}")

    def _validate_latitude_range(self, latitude_range: Tuple[float, float]):
        """Validate latitude range."""
        min_lat, max_lat = latitude_range
        if min_lat >= max_lat:
            raise ValueError(f"Invalid latitude range: min {min_lat} >= max {max_lat}")
        if not (astrocartography.MIN_LATITUDE <= min_lat <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid min latitude: {min_lat}")
        if not (astrocartography.MIN_LATITUDE <= max_lat <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid max latitude: {max_lat}")

    def _validate_longitude_range(self, longitude_range: Tuple[float, float]):
        """Validate longitude range."""
        min_lon, max_lon = longitude_range
        if min_lon >= max_lon:
            raise ValueError(f"Invalid longitude range: min {min_lon} >= max {max_lon}")

    def _validate_coordinates(self, longitude: float, latitude: float):
        """Validate individual coordinates."""
        if not (astrocartography.MIN_LONGITUDE <= longitude <= astrocartography.MAX_LONGITUDE):
            raise ValueError(f"Invalid longitude: {longitude}")
        if not (astrocartography.MIN_LATITUDE <= latitude <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid latitude: {latitude}")

    def _normalize_longitude(self, longitude: float) -> float:
        """Normalize longitude to -180 to 180 range."""
        while longitude > 180:
            longitude -= 360
        while longitude <= -180:
            longitude += 360
        return longitude

    def _generate_latitude_samples(
        self,
        min_lat: float = astrocartography.MIN_LATITUDE,
        max_lat: float = astrocartography.MAX_LATITUDE
    ) -> List[float]:
        """Generate latitude samples based on sampling resolution."""
        samples = []
        current_lat = min_lat
        while current_lat <= max_lat:
            samples.append(current_lat)
            current_lat += self.sampling_resolution

        # Ensure we include the max latitude
        if samples[-1] < max_lat:
            samples.append(max_lat)

        return samples

    def _generate_longitude_samples(
        self,
        min_lon: float = astrocartography.MIN_LONGITUDE,
        max_lon: float = astrocartography.MAX_LONGITUDE
    ) -> List[float]:
        """Generate longitude samples based on sampling resolution."""
        samples = []
        current_lon = min_lon
        while current_lon <= max_lon:
            samples.append(current_lon)
            current_lon += self.sampling_resolution

        # Ensure we include the max longitude
        if samples[-1] < max_lon:
            samples.append(max_lon)

        return samples


    def _trace_complete_horizon_curve(
        self,
        planet_position: Dict[str, float],
        longitude_range: Tuple[float, float],
        latitude_range: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Trace the complete horizon curve using the same approach as zenith calculation.

        Use proper sidereal time calculations like the zenith point method.
        """
        import swisseph as swe
        import math

        coordinates = []

        # Use SAME approach as zenith calculation
        # Get Greenwich Sidereal Time at birth moment (same as zenith)
        gst_hours = swe.sidtime(self.julian_date)
        gst_degrees = gst_hours * 15.0

        # Get planet's equatorial coordinates (same as zenith)
        if self.calculation_method == astrocartography.METHOD_ZODIACAL:
            equatorial = self._ecliptic_to_equatorial(
                planet_position['longitude'],
                planet_position['latitude']
            )
            planet_ra = equatorial['right_ascension']
            planet_dec = equatorial['declination']
        else:
            planet_ra = planet_position['right_ascension']
            planet_dec = planet_position['declination']

        # For each latitude, find longitudes where planet is on horizon
        # Using same sidereal time principles as zenith calculation

        min_lat, max_lat = latitude_range
        # Use finer step size for smooth curves extending to poles
        step_size = 0.5  # Half-degree steps for smooth S-curves

        latitude = min_lat
        while latitude <= max_lat:
            try:
                # Calculate hour angle when planet is on horizon at this latitude
                # cos(HA) = -tan(dec) * tan(lat)
                if abs(latitude) < 89.9 and abs(planet_dec) > 0.001:
                    cos_ha = (-math.tan(math.radians(planet_dec)) *
                             math.tan(math.radians(latitude)))

                    if -1.0 <= cos_ha <= 1.0:
                        # Two hour angles: rising and setting
                        ha1 = math.degrees(math.acos(cos_ha))
                        ha2 = -ha1

                        for hour_angle in [ha1, ha2]:
                            # Calculate longitude using EXACT same formula as zenith
                            # In zenith: longitude = RA - GST (when HA = 0)
                            # For horizon: longitude = RA + HA - GST (when HA ≠ 0)
                            longitude = self._normalize_longitude(planet_ra + hour_angle - gst_degrees)

                            min_lon, max_lon = longitude_range
                            if min_lon <= longitude <= max_lon:
                                coordinates.append((longitude, latitude))

            except (ValueError, ZeroDivisionError, OverflowError):
                pass

            latitude += step_size

        return coordinates

    def _split_horizon_curve(
        self,
        complete_curve: List[Tuple[float, float]]
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Split the complete horizon curve into ascending and descending portions.

        The curve naturally divides at its extreme latitude points where it
        switches from rising to setting behavior.
        """
        if not complete_curve:
            return [], []

        # Find the extreme points (highest and lowest latitudes)
        latitudes = [coord[1] for coord in complete_curve]
        max_lat = max(latitudes)
        min_lat = min(latitudes)

        # Find indices of extreme points
        max_idx = next(i for i, coord in enumerate(complete_curve) if coord[1] == max_lat)
        min_idx = next(i for i, coord in enumerate(complete_curve) if coord[1] == min_lat)

        # Ensure max_idx comes before min_idx for proper splitting
        if max_idx > min_idx:
            max_idx, min_idx = min_idx, max_idx
            max_lat, min_lat = min_lat, max_lat

        # Split the curve at the extreme points
        # ASC: from min extreme to max extreme (rising part)
        # DESC: from max extreme to min extreme (setting part)

        if max_idx < min_idx:
            # Normal case: ascending then descending
            asc_coordinates = complete_curve[max_idx:min_idx + 1]
            desc_coordinates = complete_curve[min_idx:] + complete_curve[:max_idx + 1]
        else:
            # Wrapped case: curve wraps around longitude boundaries
            asc_coordinates = complete_curve[:max_idx + 1]
            desc_coordinates = complete_curve[max_idx:]

        return asc_coordinates, desc_coordinates

    def _planets_simultaneously_angular(
        self,
        primary_pos: Dict, secondary_pos: Dict,
        longitude: float, latitude: float,
        primary_angle: str, secondary_angle: str,
        orb_tolerance: float
    ) -> bool:
        """Check if two planets are simultaneously angular at given location."""
        # Simplified implementation - would need full angular calculation
        return False  # Placeholder

    def _calculate_azimuth(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate azimuth from point 1 to point 2."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)

        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

        azimuth = math.atan2(y, x)
        azimuth_degrees = math.degrees(azimuth)

        # Normalize to 0-360
        return (azimuth_degrees + 360) % 360

    def _calculate_line_endpoint(
        self,
        start_lon: float, start_lat: float,
        azimuth: float
    ) -> Tuple[float, float]:
        """Calculate endpoint where line intersects map boundary."""
        # Simplified: project line to map edge
        # In practice, this would calculate intersection with world map bounds

        # Project 1000km in the azimuth direction
        distance_km = 1000.0
        earth_radius_km = 6371.0

        angular_distance = distance_km / earth_radius_km

        start_lat_rad = math.radians(start_lat)
        start_lon_rad = math.radians(start_lon)
        azimuth_rad = math.radians(azimuth)

        end_lat_rad = math.asin(
            math.sin(start_lat_rad) * math.cos(angular_distance) +
            math.cos(start_lat_rad) * math.sin(angular_distance) * math.cos(azimuth_rad)
        )

        end_lon_rad = start_lon_rad + math.atan2(
            math.sin(azimuth_rad) * math.sin(angular_distance) * math.cos(start_lat_rad),
            math.cos(angular_distance) - math.sin(start_lat_rad) * math.sin(end_lat_rad)
        )

        end_lat = math.degrees(end_lat_rad)
        end_lon = math.degrees(end_lon_rad)

        return self._normalize_longitude(end_lon), end_lat

    def _ecliptic_to_equatorial(self, longitude: float, latitude: float) -> Dict[str, float]:
        """
        Convert ecliptic coordinates to equatorial coordinates.

        Args:
            longitude: Ecliptic longitude in degrees
            latitude: Ecliptic latitude in degrees

        Returns:
            Dict with 'right_ascension' and 'declination' in degrees
        """
        import swisseph as swe
        import math

        # Get obliquity of ecliptic for current date
        obliquity_data = swe.calc_ut(self.julian_date, swe.ECL_NUT)[0]
        obliquity = obliquity_data[0]  # Mean obliquity in degrees

        # Convert to radians
        lon_rad = math.radians(longitude)
        lat_rad = math.radians(latitude)
        obl_rad = math.radians(obliquity)

        # Convert ecliptic to equatorial coordinates
        ra_rad = math.atan2(
            math.sin(lon_rad) * math.cos(obl_rad) - math.tan(lat_rad) * math.sin(obl_rad),
            math.cos(lon_rad)
        )

        dec_rad = math.asin(
            math.sin(lat_rad) * math.cos(obl_rad) +
            math.cos(lat_rad) * math.sin(obl_rad) * math.sin(lon_rad)
        )

        # Convert back to degrees
        ra_deg = math.degrees(ra_rad)
        dec_deg = math.degrees(dec_rad)

        # Normalize RA to 0-360
        if ra_deg < 0:
            ra_deg += 360

        return {
            'right_ascension': ra_deg,
            'declination': dec_deg
        }

    def _calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        earth_radius_km = 6371.0

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat_rad = math.radians(lat2 - lat1)
        dlon_rad = math.radians(lon2 - lon1)

        a = (math.sin(dlat_rad/2) * math.sin(dlat_rad/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(dlon_rad/2) * math.sin(dlon_rad/2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return earth_radius_km * c

    def _get_planet_position_at_location(
        self,
        planet_id: int,
        julian_date: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, float]:
        """Get planet position as seen from specific location."""
        # This would calculate topocentric position
        # For now, return geocentric position
        try:
            swe_id = ephemeris._SWE[planet_id]
            ec_res = swe.calc_ut(julian_date, swe_id)[0]
            obliquity = swe.calc_ut(julian_date, swe.ECL_NUT)[0][0]
            eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -obliquity)

            return {
                'longitude': ec_res[0],
                'latitude': ec_res[1],
                'right_ascension': eq_res[0],
                'declination': eq_res[1]
            }
        except Exception as e:
            raise RuntimeError(f"Failed to calculate position: {e}")

    def _calculate_aspect_angle(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate aspect angle between two planetary positions."""
        lon1 = pos1['longitude']
        lon2 = pos2['longitude']

        aspect = abs(lon1 - lon2)
        if aspect > 180:
            aspect = 360 - aspect

        return aspect

    def _aspect_within_orb(self, current_aspect: float, target_aspect: float, orb: float) -> bool:
        """Check if current aspect is within orb of target aspect."""
        diff = abs(current_aspect - target_aspect)
        if diff > 180:
            diff = 360 - diff
        return diff <= orb