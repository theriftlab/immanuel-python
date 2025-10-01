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

        # Calculate ASC and DESC curves separately to avoid mirroring issues
        asc_coordinates, desc_coordinates = self._calculate_asc_desc_curves_separately(
            planet_position, longitude_range, latitude_range
        )

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
        planet_id: int,
        angle_type: str,
        aspect_degrees: float,
        latitude_range: Tuple[float, float] = (-85, 85),
        longitude_range: Tuple[float, float] = (-180, 180)
    ) -> List[Tuple[float, float]]:
        """
        Calculate line where natal planet forms specific aspect to local angles.

        This shows where you would relocate for your natal planet to form
        the specified aspect to the local ASC/DESC/MC/IC at that location.

        Args:
            planet_id: Natal planet identifier
            angle_type: Local angle ('ASC', 'DESC', 'MC', 'IC')
            aspect_degrees: Aspect angle (0, 60, 90, 120, 180, etc.)
            latitude_range: Latitude range to sample
            longitude_range: Longitude range to sample

        Returns:
            List of (longitude, latitude) pairs where aspect is exact

        Raises:
            PlanetError: If planet_id is invalid
            ValueError: If angle_type or aspect_degrees is invalid
        """
        # Validate inputs
        self._validate_planet_id(planet_id)

        valid_angles = ['ASC', 'DESC', 'MC', 'IC']
        if angle_type not in valid_angles:
            raise ValueError(f"Invalid angle_type: {angle_type}. Must be one of {valid_angles}")

        if not (0 <= aspect_degrees < 360):
            raise ValueError(f"Invalid aspect_degrees: {aspect_degrees}")

        # Get natal planet position
        planet_position = self.get_planetary_position(planet_id)
        planet_longitude = planet_position['longitude']

        coordinates = []

        # For MC/IC angles, we need to find where the planet is at the specified aspect from MC/IC
        if angle_type in ['MC', 'IC']:
            # Get planet's celestial coordinates
            planet_position = self.get_planetary_position(planet_id)

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

            # Get apparent sidereal time at birth moment for higher accuracy
            import swisseph as swe
            import math

            # Calculate apparent sidereal time (more accurate than mean sidereal time)
            mean_st_hours = swe.sidtime(self.julian_date)

            # Get nutation for equation of equinoxes
            nut_data = swe.calc_ut(self.julian_date, swe.ECL_NUT)
            obliquity = nut_data[0][0]
            nutation_longitude = nut_data[0][2]

            # Equation of equinoxes = nutation_longitude * cos(obliquity)
            eqeq_hours = (nutation_longitude * math.cos(math.radians(obliquity))) / 15.0
            apparent_st_hours = mean_st_hours + eqeq_hours

            gst_degrees = apparent_st_hours * 15.0

            # For each latitude, calculate where the aspect occurs
            min_lat, max_lat = latitude_range
            latitudes = self._generate_latitude_samples(min_lat, max_lat)

            # FAST METHOD: Use binary search with smart initial guesses
            aspect_longitudes = self._calculate_aspect_longitudes_fast(
                planet_id, angle_type, aspect_degrees
            )

            # Create vertical lines at the found longitudes
            min_lat, max_lat = latitude_range
            latitudes = self._generate_latitude_samples(min_lat, max_lat)

            for aspect_longitude in aspect_longitudes:
                for latitude in latitudes:
                    coordinates.append((aspect_longitude, latitude))

        # For ASC/DESC angles, use fast ternary search method
        elif angle_type in ['ASC', 'DESC']:
            # Optimization: ASC aspect_deg = DESC (180° - aspect_deg)
            # So ASC 60° = DESC 120°, ASC 120° = DESC 60°, ASC 90° = DESC 90°
            # We can calculate one and derive the other
            complementary_aspect = 180.0 - aspect_degrees

            # Always calculate for ASC, then map to DESC if needed
            calc_angle = 'ASC'
            calc_aspect = aspect_degrees if angle_type == 'ASC' else complementary_aspect

            # Get planet position once
            planet_position = self.get_planetary_position(planet_id)
            planet_longitude = planet_position['longitude']

            # Generate latitude samples (limit to ±66° to avoid polar issues with house calculations)
            min_lat, max_lat = latitude_range
            # Clamp latitude range to avoid polar regions where swe.houses() can fail
            safe_min_lat = max(min_lat, -66.0)
            safe_max_lat = min(max_lat, 66.0)
            latitudes = self._generate_latitude_samples(safe_min_lat, safe_max_lat)

            # Collect coordinates for each hemisphere separately
            western_coords = []  # Longitudes < 0
            eastern_coords = []  # Longitudes >= 0

            # Use ternary search to find accurate longitudes at each latitude
            # Returns list (typically 2 solutions - one per hemisphere)
            for latitude in latitudes:
                longitudes = self._find_asc_desc_aspect_longitudes(
                    planet_longitude, latitude, calc_aspect, calc_angle
                )

                for longitude in longitudes:
                    if longitude_range[0] <= longitude <= longitude_range[1]:
                        if longitude < 0:
                            western_coords.append((longitude, latitude))
                        else:
                            eastern_coords.append((longitude, latitude))

            # Sort each hemisphere by latitude for smooth line plotting
            western_coords.sort(key=lambda c: c[1])
            eastern_coords.sort(key=lambda c: c[1])

            # Combine: western line, then None separator, then eastern line
            # matplotlib uses None to break lines
            coordinates = western_coords
            if western_coords and eastern_coords:
                coordinates.append(None)  # Line break
            coordinates.extend(eastern_coords)

        return coordinates

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

    def _generate_samples(self, min_val: float, max_val: float, step: float) -> List[float]:
        """Generate samples within the given range with specified step."""
        samples = []
        current_val = min_val
        while current_val <= max_val:
            samples.append(current_val)
            current_val += step

        # Ensure we include the max value
        if samples[-1] < max_val:
            samples.append(max_val)

        return samples

    def _calculate_mc_ecliptic_longitude_at_location(self, longitude: float, latitude: float) -> float:
        """Calculate MC ecliptic longitude at a specific geographic location."""
        import swisseph as swe
        import math

        # Get apparent sidereal time at birth moment
        mean_st_hours = swe.sidtime(self.julian_date)
        nut_data = swe.calc_ut(self.julian_date, swe.ECL_NUT)
        obliquity = nut_data[0][0]
        nutation_longitude = nut_data[0][2]
        eqeq_hours = (nutation_longitude * math.cos(math.radians(obliquity))) / 15.0
        apparent_st_hours = mean_st_hours + eqeq_hours
        gst_degrees = apparent_st_hours * 15.0

        # Calculate Local Sidereal Time at this location
        lst_degrees = (gst_degrees + longitude) % 360.0

        # MC in equatorial coordinates: RA = LST, Dec = 0° (on celestial equator)
        mc_ra = lst_degrees
        mc_dec = 0.0

        # Convert MC from equatorial to ecliptic coordinates
        # Using inverse of the earlier transformation
        mc_ecliptic = swe.cotrans([mc_ra, mc_dec, 1.0], obliquity)
        mc_ecliptic_longitude = mc_ecliptic[0]

        return mc_ecliptic_longitude % 360.0

    def _calculate_aspect_longitudes_fast(self, planet_id: int, angle_type: str, aspect_degrees: float) -> List[float]:
        """
        Fast calculation of aspect line longitudes using binary search with smart initial guesses.

        Args:
            planet_id: Planet constant
            angle_type: 'MC' or 'IC'
            aspect_degrees: Desired aspect in degrees

        Returns:
            List of longitude values where the aspect occurs
        """
        import swisseph as swe
        import math

        # Get planet position and sidereal time for smart initial guess
        planet_position = self.get_planetary_position(planet_id)

        if self.calculation_method == astrocartography.METHOD_ZODIACAL:
            equatorial = self._ecliptic_to_equatorial(
                planet_position['longitude'],
                planet_position['latitude']
            )
            planet_ra = equatorial['right_ascension']
        else:
            planet_ra = planet_position['right_ascension']

        # Get apparent sidereal time
        mean_st_hours = swe.sidtime(self.julian_date)
        nut_data = swe.calc_ut(self.julian_date, swe.ECL_NUT)
        obliquity = nut_data[0][0]
        nutation_longitude = nut_data[0][2]
        eqeq_hours = (nutation_longitude * math.cos(math.radians(obliquity))) / 15.0
        apparent_st_hours = mean_st_hours + eqeq_hours
        gst_degrees = apparent_st_hours * 15.0

        # Smart initial guesses: where hour angle = ±aspect_degrees
        # longitude = (planet_RA ± aspect_degrees) - GST
        initial_guess_1 = self._normalize_longitude((planet_ra + aspect_degrees) - gst_degrees)
        initial_guess_2 = self._normalize_longitude((planet_ra - aspect_degrees) - gst_degrees)

        # For IC, add 180° to both guesses
        if angle_type == 'IC':
            initial_guess_1 = self._normalize_longitude(initial_guess_1 + 180.0)
            initial_guess_2 = self._normalize_longitude(initial_guess_2 + 180.0)

        # Binary search around each guess with very tight error tolerance
        longitude_1 = self._binary_search_aspect_longitude(
            planet_id, angle_type, aspect_degrees, initial_guess_1, max_error=0.05
        )
        longitude_2 = self._binary_search_aspect_longitude(
            planet_id, angle_type, aspect_degrees, initial_guess_2, max_error=0.05
        )

        # Verify accuracy and ensure we have distinct coordinates
        aspect_1 = self._calculate_aspect_at_longitude(longitude_1, planet_id, angle_type)
        aspect_2 = self._calculate_aspect_at_longitude(longitude_2, planet_id, angle_type)

        error_1 = abs(aspect_1 - aspect_degrees)
        error_2 = abs(aspect_2 - aspect_degrees)

        # If coordinates are too close or second has high error, find alternative
        longitude_diff = abs(longitude_1 - longitude_2)
        if longitude_diff < 5.0 or error_2 > 1.0:
            # Try systematic search across longitude range
            best_longitude_2 = longitude_2
            best_error_2 = error_2

            # Try multiple alternative starting points around the globe
            test_points = [
                initial_guess_2 + 180.0,  # Opposite side
                initial_guess_2 + 90.0,   # Perpendicular
                initial_guess_2 - 90.0,   # Other perpendicular
                initial_guess_1 + 180.0,  # Opposite of first
                0.0,                      # Greenwich
                180.0,                    # Antimeridian
                -90.0,                    # West
                90.0                      # East
            ]

            for test_point in test_points:
                test_point = self._normalize_longitude(test_point)
                # Skip if too close to first coordinate
                if abs(test_point - longitude_1) < 5.0:
                    continue

                test_longitude = self._binary_search_aspect_longitude(
                    planet_id, angle_type, aspect_degrees, test_point, max_error=0.05
                )
                test_aspect = self._calculate_aspect_at_longitude(test_longitude, planet_id, angle_type)
                test_error = abs(test_aspect - aspect_degrees)

                # Use if significantly better and distinct from first coordinate
                if test_error < best_error_2 and abs(test_longitude - longitude_1) > 5.0:
                    best_longitude_2 = test_longitude
                    best_error_2 = test_error

            longitude_2 = best_longitude_2

        return [longitude_1, longitude_2]

    def _binary_search_aspect_longitude(self, planet_id: int, angle_type: str,
                                      target_aspect: float, initial_guess: float,
                                      tolerance: float = 0.01, max_error: float = 0.1) -> float:
        """
        Find longitude where aspect occurs using ternary search to minimize error.

        Args:
            planet_id: Planet constant
            angle_type: 'MC' or 'IC'
            target_aspect: Target aspect in degrees
            initial_guess: Starting longitude guess
            tolerance: Precision tolerance for longitude convergence in degrees
            max_error: Maximum allowed error in aspect degrees

        Returns:
            Precise longitude where aspect occurs
        """
        def aspect_error(longitude):
            """Calculate error between actual and target aspect."""
            actual_aspect = self._calculate_aspect_at_longitude(longitude, planet_id, angle_type)
            error = abs(actual_aspect - target_aspect)
            # Handle aspect wrap-around (e.g., 359° vs 1°)
            if error > 180.0:
                error = 360.0 - error
            return error

        # Start with initial search range
        search_range = 10.0
        best_longitude = initial_guess
        best_error = aspect_error(initial_guess)

        # Try expanding search ranges if needed
        for range_multiplier in [1.0, 2.0, 3.0]:
            current_range = search_range * range_multiplier
            left = initial_guess - current_range
            right = initial_guess + current_range

            # Ternary search to minimize error (proper optimization)
            iteration_count = 0
            max_iterations = 60

            while (right - left) > tolerance and iteration_count < max_iterations:
                # Ternary search points
                mid1 = left + (right - left) / 3.0
                mid2 = right - (right - left) / 3.0

                error1 = aspect_error(mid1)
                error2 = aspect_error(mid2)

                # Track best result
                if error1 < best_error:
                    best_error = error1
                    best_longitude = mid1
                if error2 < best_error:
                    best_error = error2
                    best_longitude = mid2

                # If we've achieved the desired accuracy, we can stop
                if best_error <= max_error:
                    return best_longitude

                # Ternary search logic: eliminate the worse third
                if error1 < error2:
                    right = mid2  # Minimum is in left 2/3
                else:
                    left = mid1   # Minimum is in right 2/3

                iteration_count += 1

            # If we found a good result in this range, use it
            if best_error <= max_error:
                break

        return best_longitude

    def _calculate_aspect_at_longitude(self, longitude: float, planet_id: int, angle_type: str) -> float:
        """
        Calculate the actual aspect between planet and MC/IC at a specific longitude.

        Args:
            longitude: Geographic longitude
            planet_id: Planet constant
            angle_type: 'MC' or 'IC'

        Returns:
            Aspect in degrees between planet and angle
        """
        import swisseph as swe

        # Use swe.houses for accurate MC calculation
        # Format: houses(julian_day, latitude, longitude, house_system, flags=0)
        # IMPORTANT: Must use UTC Julian date for consistency with chart creation
        test_latitude = 45.0  # Use 45°N as standard test latitude
        houses = swe.houses(self.julian_date, test_latitude, longitude, b'P')  # Placidus system

        # houses[1] contains additional points, MC is at index 1
        mc_longitude = houses[1][1]

        # For IC, add 180° to MC
        if angle_type == 'IC':
            angle_longitude = (mc_longitude + 180.0) % 360.0
        else:
            angle_longitude = mc_longitude

        # Get planet ecliptic longitude
        planet_position = self.get_planetary_position(planet_id)
        planet_longitude = planet_position.get('longitude', planet_position.get('ecliptic_longitude', 0))

        # Calculate aspect
        aspect = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)

        return aspect

    def _find_asc_desc_aspect_longitudes(self, planet_longitude: float, latitude: float,
                                          aspect_degrees: float, angle_type: str,
                                          tolerance: float = 0.25) -> List[float]:
        """
        Find ALL longitudes where planet forms exact aspect to ASC/DESC at given latitude.

        For most aspects, there are TWO locations around the globe (180° apart conceptually).
        Uses fast ternary search with swe.houses() for optimal performance.

        Args:
            planet_longitude: Planet's ecliptic longitude
            latitude: Geographic latitude
            aspect_degrees: Target aspect (60, 90, 120, etc.)
            angle_type: 'ASC' or 'DESC'
            tolerance: Search tolerance in degrees (default 0.25° for speed/accuracy balance)

        Returns:
            List of longitudes where aspect is exact (typically 0, 1, or 2 results)
        """
        def calculate_aspect_error(test_longitude: float) -> float:
            """Calculate aspect error at given longitude."""
            try:
                # Get ASC/DESC at this location using swe.houses
                houses_result = swe.houses(self.julian_date, latitude, test_longitude, b'P')
                ascmc = houses_result[1]

                if angle_type == 'ASC':
                    angle_longitude = ascmc[0]  # ASC at index 0
                elif angle_type == 'DESC':
                    asc_longitude = ascmc[0]
                    angle_longitude = (asc_longitude + 180.0) % 360.0
                else:
                    return 999.0

                # Calculate aspect
                actual_aspect = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)

                # Calculate error from target aspect
                error = abs(actual_aspect - aspect_degrees)
                if error > 180.0:
                    error = 360.0 - error

                return error
            except:
                return 999.0  # Return large error on failure

        def ternary_search(left: float, right: float) -> Optional[float]:
            """Perform ternary search in given range."""
            last_err1 = None
            last_err2 = None

            while (right - left) > tolerance:
                mid1 = left + (right - left) / 3.0
                mid2 = right - (right - left) / 3.0

                err1 = calculate_aspect_error(mid1)
                err2 = calculate_aspect_error(mid2)

                if err1 < err2:
                    right = mid2
                    last_err1 = err1
                else:
                    left = mid1
                    last_err2 = err2

            best_longitude = (left + right) / 2.0
            # Use the last calculated error instead of recalculating
            best_error = min(last_err1, last_err2) if last_err1 is not None and last_err2 is not None else calculate_aspect_error(best_longitude)

            # Return only if error is acceptable (< 1°)
            return best_longitude if best_error < 1.0 else None

        # Search two hemispheres separately to find both solutions
        results = []

        # Search western hemisphere
        result1 = ternary_search(-180.0, 0.0)
        if result1 is not None:
            results.append(result1)

        # Search eastern hemisphere
        result2 = ternary_search(0.0, 180.0)
        if result2 is not None:
            results.append(result2)

        return results

    def _test_location_for_aspect(self, longitude: float, latitude: float, planet_id: int,
                                 angle_type: str, aspect_degrees: float, tolerance: float) -> bool:
        """Test if a location has the desired planetary aspect by creating a chart."""
        import swisseph as swe
        import math

        # Get apparent sidereal time and calculate local chart
        mean_st_hours = swe.sidtime(self.julian_date)
        nut_data = swe.calc_ut(self.julian_date, swe.ECL_NUT)
        obliquity = nut_data[0][0]
        nutation_longitude = nut_data[0][2]
        eqeq_hours = (nutation_longitude * math.cos(math.radians(obliquity))) / 15.0
        apparent_st_hours = mean_st_hours + eqeq_hours
        gst_degrees = apparent_st_hours * 15.0

        # Calculate Local Sidereal Time at this location
        lst_degrees = (gst_degrees + longitude) % 360.0

        # Get planet's ecliptic longitude at birth time (use existing method)
        planet_position = self.get_planetary_position(planet_id)
        planet_longitude = planet_position.get('longitude', planet_position.get('ecliptic_longitude', 0))

        # Calculate MC ecliptic longitude at this location
        # MC in equatorial: RA = LST, Dec = 0
        mc_ra = lst_degrees
        mc_dec = 0.0

        # Convert MC to ecliptic coordinates
        mc_ecliptic = swe.cotrans([mc_ra, mc_dec, 1.0], obliquity)
        mc_ecliptic_longitude = mc_ecliptic[0] % 360.0

        # For IC, add 180° to MC
        if angle_type == 'IC':
            target_angle_longitude = (mc_ecliptic_longitude + 180.0) % 360.0
        else:  # MC
            target_angle_longitude = mc_ecliptic_longitude

        # Calculate the actual aspect between planet and angle
        aspect_diff = abs((planet_longitude - target_angle_longitude + 180.0) % 360.0 - 180.0)

        # Check if the aspect matches our target (within tolerance)
        is_match = abs(aspect_diff - aspect_degrees) <= tolerance

        return is_match

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


    def _calculate_asc_desc_curves_separately(
        self,
        planet_position: Dict[str, float],
        longitude_range: Tuple[float, float],
        latitude_range: Tuple[float, float]
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Calculate ASC and DESC curves separately as proper S-curves.

        ASC = planet rising (negative hour angle)
        DESC = planet setting (positive hour angle)
        """
        import swisseph as swe
        import math
        import numpy as np

        # Use SAME approach as zenith calculation
        gst_hours = swe.sidtime(self.julian_date)
        gst_degrees = gst_hours * 15.0

        # Get planet's equatorial coordinates
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

        asc_coordinates = []
        desc_coordinates = []
        min_lat, max_lat = latitude_range

        # Step through latitudes to create smooth curves
        latitudes = np.arange(min_lat, max_lat + 0.5, 0.5)

        for latitude in latitudes:
            try:
                if abs(latitude) < 89.5 and abs(planet_dec) > 0.001:
                    # Calculate cos(HA) = -tan(dec) * tan(lat)
                    cos_ha = (-math.tan(math.radians(planet_dec)) *
                             math.tan(math.radians(latitude)))

                    if -1.0 <= cos_ha <= 1.0:
                        # Calculate both hour angles (positive and negative)
                        ha_abs = math.degrees(math.acos(cos_ha))

                        # ASC: negative hour angle (rising, eastern horizon)
                        ha_asc = -ha_abs
                        lon_asc = self._normalize_longitude(planet_ra + ha_asc - gst_degrees)

                        # DESC: positive hour angle (setting, western horizon)
                        ha_desc = ha_abs
                        lon_desc = self._normalize_longitude(planet_ra + ha_desc - gst_degrees)

                        min_lon, max_lon = longitude_range

                        # Add ASC point if in range
                        if min_lon <= lon_asc <= max_lon:
                            asc_coordinates.append((lon_asc, latitude))

                        # Add DESC point if in range
                        if min_lon <= lon_desc <= max_lon:
                            desc_coordinates.append((lon_desc, latitude))

            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                continue

        # Sort both curves by latitude for smooth plotting
        asc_coordinates.sort(key=lambda x: x[1])
        desc_coordinates.sort(key=lambda x: x[1])

        return asc_coordinates, desc_coordinates

    def _split_horizon_curve(
        self,
        complete_curve: List[Tuple[float, float]]
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Create both ASC and DESC curves from the complete horizon curve.

        In astrocartography, ASC and DESC are often shown as the same curve
        with different visual styling to indicate rising vs setting.
        """
        if not complete_curve:
            return [], []

        # For now, use the same curve for both ASC and DESC
        # The visual distinction comes from line styling, not separate curves
        asc_coordinates = complete_curve.copy()
        desc_coordinates = complete_curve.copy()

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