#!/usr/bin/env python3
"""
ASC/DESC Aspect Lines Implementation Testbed

This testbed validates any ASC/DESC aspect line implementation by:
1. Testing the current (incorrect) implementation as baseline
2. Providing framework to test new spherical astronomy implementations
3. Measuring accuracy, consistency, and geographic coverage
4. Guiding development of the correct mathematical approach

Key Goals:
- Establish accuracy metrics for any implementation
- Compare different calculation methods
- Validate against chart-based verification
- Guide spherical astronomy concept development
"""

from datetime import datetime
from immanuel.charts import Subject, Natal
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart
import swisseph as swe
import math
import numpy as np
import time
from functools import wraps
from typing import List, Tuple, Dict, Optional


def profile_method(func):
    """Decorator to profile method execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"  ⏱ {func.__name__}: {elapsed_time:.3f}s")
        return result
    return wrapper


class ASCDESCAspectTestbed:
    """Comprehensive testbed for ASC/DESC aspect line implementations."""

    def __init__(self, birth_datetime: str, birth_latitude: str, birth_longitude: str):
        """Initialize testbed with birth data."""
        self.birth_datetime = birth_datetime
        self.birth_latitude = birth_latitude
        self.birth_longitude = birth_longitude

        # Convert to Julian Date using UTC (consistent with working methods)
        dt = datetime.strptime(birth_datetime, '%Y-%m-%d %H:%M:%S')
        dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
        self.julian_date = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                                     dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

        # Create calculator
        self.calculator = AstrocartographyCalculator(julian_date=self.julian_date, sampling_resolution=2.0)

        # Profiling stats
        self.iteration_count = 0
        self.chart_creation_count = 0
        self.fast_calculation_count = 0

        print(f"ASC/DESC Aspect Lines Testbed Initialized")
        print(f"Birth: {birth_datetime} → UTC: {dt_utc}")
        print(f"Julian Date: {self.julian_date:.6f}")
        print()

    def test_current_implementation(self, planet_id: int, aspect_degrees: float, angle_type: str = 'ASC') -> Dict:
        """Test the current (incorrect) implementation in astrocartography.py."""
        print(f"TESTING CURRENT IMPLEMENTATION")
        print(f"Planet: {self._planet_name(planet_id)}, Aspect: {aspect_degrees}°, Angle: {angle_type}")
        print("-" * 60)

        # Use the existing calculate_aspect_line method
        try:
            aspect_coords = self.calculator.calculate_aspect_line(
                planet_id=planet_id,
                angle_type=angle_type,
                aspect_degrees=aspect_degrees,
                latitude_range=(-85, 85),
                longitude_range=(-180, 180)
            )

            print(f"Generated coordinates: {len(aspect_coords)} points")

            if aspect_coords:
                # Sample and validate points
                validation_results = self._validate_aspect_coordinates(
                    aspect_coords, planet_id, aspect_degrees, angle_type, sample_count=15
                )

                return {
                    'method': 'current_implementation',
                    'coordinates': aspect_coords,
                    'validation': validation_results,
                    'success': True
                }
            else:
                print("No coordinates generated!")
                return {'method': 'current_implementation', 'success': False}

        except Exception as e:
            print(f"Error in current implementation: {e}")
            return {'method': 'current_implementation', 'error': str(e), 'success': False}

    def test_spherical_method_concept(self, planet_id: int, aspect_degrees: float, angle_type: str = 'ASC') -> Dict:
        """Test a spherical astronomy method concept (to be implemented)."""
        print(f"TESTING SPHERICAL METHOD CONCEPT")
        print(f"Planet: {self._planet_name(planet_id)}, Aspect: {aspect_degrees}°, Angle: {angle_type}")
        print("-" * 60)

        # For now, this is a placeholder for the spherical method
        # We'll implement the actual spherical calculations step by step

        print("SPHERICAL METHOD CONCEPT:")
        print("1. Calculate planet's equatorial coordinates (RA, Dec)")
        print("2. For each latitude:")
        print("   a. Calculate local sidereal time at longitude where aspect occurs")
        print("   b. Use modified hour angle formula: HA = LST - RA ± aspect_offset")
        print("   c. Convert back to geographic longitude")
        print("3. Create smooth curve through calculated points")
        print()

        # Prototype implementation (simplified)
        try:
            spherical_coords = self._prototype_spherical_method(planet_id, aspect_degrees, angle_type)

            if spherical_coords:
                validation_results = self._validate_aspect_coordinates(
                    spherical_coords, planet_id, aspect_degrees, angle_type, sample_count=15
                )

                return {
                    'method': 'spherical_prototype',
                    'coordinates': spherical_coords,
                    'validation': validation_results,
                    'success': True
                }
            else:
                return {'method': 'spherical_prototype', 'success': False}

        except Exception as e:
            print(f"Error in spherical prototype: {e}")
            return {'method': 'spherical_prototype', 'error': str(e), 'success': False}

    def _calculate_aspect_fast(self, longitude: float, latitude: float,
                                planet_id: int, angle_type: str) -> float:
        """Fast aspect calculation using swe.houses() directly (no chart creation)."""
        self.fast_calculation_count += 1

        try:
            # Limit latitude to avoid polar issues with house calculations
            # swe.houses() can fail near poles (above ~66° latitude)
            safe_latitude = max(-80.0, min(80.0, latitude))

            # Get ASC/DESC at this location using swe.houses
            # Format: houses(julian_day, latitude, longitude, house_system)
            # Returns: (houses_cusps, ascmc) tuple
            houses_result = swe.houses(self.julian_date, safe_latitude, longitude, b'P')

            # houses_result is a tuple: (houses_cusps, ascmc)
            # ascmc contains: ASC, MC, ARMC, Vertex, Equatorial Ascendant, etc.
            ascmc = houses_result[1]

            if angle_type == 'ASC':
                angle_longitude = ascmc[0]  # ASC at index 0
            elif angle_type == 'DESC':
                asc_longitude = ascmc[0]
                angle_longitude = (asc_longitude + 180.0) % 360.0
            else:
                raise ValueError(f"Unsupported angle_type: {angle_type}")

            # Get planet position
            planet_longitude = self.calculator.get_planetary_position(planet_id)['longitude']

            # Calculate aspect
            aspect = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)
            return aspect

        except Exception as e:
            raise RuntimeError(f"Error in _calculate_aspect_fast at lon={longitude}, lat={latitude}: {e}")

    def _find_base_point_with_ternary_search(self, planet_id: int, aspect_degrees: float,
                                             angle_type: str, latitude: float,
                                             use_fast_method: bool = False) -> Optional[float]:
        """Find accurate longitude for aspect at given latitude using ternary search.

        Args:
            use_fast_method: If True, use fast swe.houses() method. If False, use chart creation.
        """

        def aspect_error(longitude):
            """Calculate aspect error at this longitude."""
            self.iteration_count += 1

            if use_fast_method:
                # Fast method using swe.houses directly
                actual_aspect = self._calculate_aspect_fast(longitude, latitude, planet_id, angle_type)
            else:
                # Slow method using full chart creation
                self.chart_creation_count += 1
                result = self._create_chart_and_measure_aspect(longitude, latitude, planet_id, angle_type)
                if 'error' in result:
                    return 999.0  # Large error for invalid points
                actual_aspect = result['aspect_degrees']

            error = abs(actual_aspect - aspect_degrees)
            if error > 180.0:
                error = 360.0 - error
            return error

        # Ternary search over full longitude range
        left, right = -180.0, 180.0
        tolerance = 0.01  # 0.01 degree tolerance

        while (right - left) > tolerance:
            mid1 = left + (right - left) / 3.0
            mid2 = right - (right - left) / 3.0

            err1 = aspect_error(mid1)
            err2 = aspect_error(mid2)

            if err1 < err2:
                right = mid2
            else:
                left = mid1

        best_longitude = (left + right) / 2.0
        best_error = aspect_error(best_longitude)

        return best_longitude if best_error < 1.0 else None

    def _test_translation_hypothesis(self, planet_id: int, aspect_degrees: float, angle_type: str) -> Dict:
        """Test if aspect lines are simple translations from base points."""
        print("Testing translation hypothesis with ternary search base points...")
        print("-" * 60)

        # Find accurate base points at key latitudes using ternary search
        key_latitudes = [0.0, 45.0, -45.0]
        base_points = {}

        print("Finding base points with ternary search:")
        for lat in key_latitudes:
            print(f"  Searching at {lat:+6.1f}° latitude...", end=" ")
            lon = self._find_base_point_with_ternary_search(planet_id, aspect_degrees, angle_type, lat)
            if lon is not None:
                base_points[lat] = lon
                print(f"Found: {lon:7.2f}°")
            else:
                print("Failed to converge")

        if len(base_points) < 2:
            return {'success': False, 'error': 'Could not find enough base points'}

        print(f"\nBase points found: {len(base_points)}")

        # Calculate translation offset from base point at equator
        if 0.0 in base_points:
            base_longitude = base_points[0.0]
            print(f"Using equator base: {base_longitude:.2f}°")
        else:
            # Use average of available base points
            base_longitude = np.mean(list(base_points.values()))
            print(f"Using average base: {base_longitude:.2f}°")

        # Test if translation is constant across latitudes
        print("\nTesting translation consistency:")
        test_latitudes = np.linspace(-85, 85, 20)
        coordinates = []
        errors = []

        for lat in test_latitudes:
            # Use base point as translation
            lon = base_longitude

            # Validate this point
            result = self._create_chart_and_measure_aspect(lon, lat, planet_id, angle_type)
            if 'error' not in result:
                actual_aspect = result['aspect_degrees']
                error = abs(actual_aspect - aspect_degrees)
                if error > 180.0:
                    error = 360.0 - error

                errors.append(error)
                coordinates.append((lon, lat))

                status = "✓" if error < 1.0 else "⚠" if error < 5.0 else "✗"
                print(f"  {lat:+6.1f}° → {actual_aspect:6.2f}° (±{error:5.2f}°) {status}")

        # Calculate statistics
        if errors:
            stats = {
                'mean_error': np.mean(errors),
                'std_error': np.std(errors),
                'min_error': min(errors),
                'max_error': max(errors),
                'error_range': max(errors) - min(errors),
            }

            print(f"\nTranslation Test Statistics:")
            print(f"  Mean error: {stats['mean_error']:.2f}°")
            print(f"  Std dev: {stats['std_error']:.2f}°")
            print(f"  Range: {stats['min_error']:.2f}° - {stats['max_error']:.2f}°")

            # Determine if translation works
            is_translation = stats['std_error'] < 2.0 and stats['mean_error'] < 5.0

            if is_translation:
                print(f"\n✓ TRANSLATION HYPOTHESIS CONFIRMED")
                print(f"  Aspect line is simple vertical line at {base_longitude:.2f}°")
            else:
                print(f"\n✗ TRANSLATION HYPOTHESIS REJECTED")
                print(f"  High variability (std={stats['std_error']:.2f}°) indicates complex curve")

            return {
                'success': True,
                'base_points': base_points,
                'base_longitude': base_longitude,
                'coordinates': coordinates,
                'statistics': stats,
                'is_translation': is_translation
            }

        return {'success': False}

    def _latitude_dependent_ternary_search_method(self, planet_id: int, aspect_degrees: float,
                                                   angle_type: str, use_fast_method: bool = False) -> List[Tuple[float, float]]:
        """Generate ASC/DESC aspect line using ternary search at each latitude.

        Args:
            use_fast_method: If True, use fast swe.houses() method. If False, use chart creation.
        """
        method_name = "fast swe.houses()" if use_fast_method else "chart creation"
        print(f"Implementing latitude-dependent ternary search method ({method_name})...")
        print("This uses ternary search at each latitude to find accurate curved lines")

        # Reset profiling counters
        self.iteration_count = 0
        self.chart_creation_count = 0
        self.fast_calculation_count = 0

        coordinates = []
        # Limit to -66 to 66 (Arctic Circle) for fast method to avoid polar issues with swe.houses()
        if use_fast_method:
            latitudes = np.arange(-66, 67, 5.0)  # Every 5 degrees, avoiding polar regions
        else:
            latitudes = np.arange(-85, 86, 5.0)  # Every 5 degrees for faster calculation

        print(f"Calculating {len(latitudes)} points...")
        successful = 0
        start_time = time.time()

        for i, latitude in enumerate(latitudes):
            # Find accurate longitude at this latitude using ternary search
            longitude = self._find_base_point_with_ternary_search(
                planet_id, aspect_degrees, angle_type, latitude, use_fast_method=use_fast_method
            )

            if longitude is not None:
                coordinates.append((longitude, latitude))
                successful += 1

                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i+1}/{len(latitudes)} ({successful} successful)")

        elapsed_time = time.time() - start_time
        print(f"Generated {len(coordinates)} accurate coordinates using ternary search")
        print(f"Performance: {elapsed_time:.3f}s total ({elapsed_time/len(latitudes)*1000:.1f}ms per latitude)")
        print(f"Iterations: {self.iteration_count} total ({self.iteration_count/len(latitudes):.1f} per latitude)")
        if use_fast_method:
            print(f"Fast calculations: {self.fast_calculation_count}")
        else:
            print(f"Chart creations: {self.chart_creation_count}")
        return coordinates

    def _prototype_spherical_method(self, planet_id: int, aspect_degrees: float, angle_type: str) -> List[Tuple[float, float]]:
        """Prototype spherical method for ASC/DESC aspect lines."""
        print("Implementing prototype spherical method...")

        # Get planet position
        planet_position = self.calculator.get_planetary_position(planet_id)

        # Convert to equatorial coordinates if needed
        if self.calculator.calculation_method == 'zodiacal':
            equatorial = self.calculator._ecliptic_to_equatorial(
                planet_position['longitude'],
                planet_position['latitude']
            )
            planet_ra = equatorial['right_ascension']
            planet_dec = equatorial['declination']
        else:
            planet_ra = planet_position['right_ascension']
            planet_dec = planet_position['declination']

        print(f"Planet RA: {planet_ra:.3f}°, Dec: {planet_dec:.3f}°")

        # Calculate Greenwich Sidereal Time
        gst_hours = swe.sidtime(self.julian_date)
        gst_degrees = gst_hours * 15.0

        coordinates = []
        latitudes = np.arange(-85, 86, 1.0)  # Every 1 degree

        print("Calculating spherical aspect positions...")

        for latitude in latitudes:
            try:
                if abs(latitude) < 89.5 and abs(planet_dec) > 0.001:
                    # Base hour angle calculation (for conjunction)
                    cos_ha = (-math.tan(math.radians(planet_dec)) *
                             math.tan(math.radians(latitude)))

                    if -1.0 <= cos_ha <= 1.0:
                        ha_base = math.degrees(math.acos(cos_ha))

                        # CONCEPT: Apply aspect offset to hour angle
                        # This is the key insight - aspects modify the hour angle
                        # For ASC: negative hour angle (rising)
                        # For DESC: positive hour angle (setting)

                        if angle_type == 'ASC':
                            # ASC aspect: modify the rising hour angle
                            ha_aspect = -ha_base + (aspect_degrees / 15.0)  # Convert degrees to hours
                            longitude = self._normalize_longitude(planet_ra + ha_aspect * 15.0 - gst_degrees)
                        else:  # DESC
                            # DESC aspect: modify the setting hour angle
                            ha_aspect = ha_base + (aspect_degrees / 15.0)
                            longitude = self._normalize_longitude(planet_ra + ha_aspect * 15.0 - gst_degrees)

                        # Only add if within reasonable bounds
                        if -180 <= longitude <= 180:
                            coordinates.append((longitude, latitude))

            except (ValueError, ZeroDivisionError, OverflowError):
                continue

        print(f"Generated {len(coordinates)} prototype coordinates")
        return coordinates

    def _validate_aspect_coordinates(self, coords: List[Tuple[float, float]],
                                   planet_id: int, expected_aspect: float,
                                   angle_type: str, sample_count: int = 15) -> Dict:
        """Validate aspect accuracy at coordinates."""
        print(f"Validating {expected_aspect}° aspect to {angle_type}...")

        if len(coords) < sample_count:
            sample_indices = range(len(coords))
        else:
            sample_indices = np.linspace(0, len(coords) - 1, sample_count, dtype=int)

        validation_results = []
        errors = []
        valid_points = 0

        for i, idx in enumerate(sample_indices):
            lon, lat = coords[idx]

            try:
                # Create chart and measure aspect
                test_result = self._create_chart_and_measure_aspect(lon, lat, planet_id, angle_type)

                if 'error' not in test_result:
                    actual_aspect = test_result['aspect_degrees']
                    error = abs(actual_aspect - expected_aspect)

                    # Handle aspect wrap-around
                    if error > 180.0:
                        error = 360.0 - error

                    errors.append(error)
                    valid_points += 1

                    validation_results.append({
                        'point': i + 1,
                        'longitude': lon,
                        'latitude': lat,
                        'actual_aspect': actual_aspect,
                        'error': error,
                        'valid': error < 10.0  # Consider <10° as reasonable
                    })

                    status = "✓" if error < 5.0 else "⚠" if error < 10.0 else "✗"
                    print(f"  {i+1:2d}: {lon:7.2f}°,{lat:5.1f}° → {actual_aspect:6.2f}° (±{error:5.2f}°) {status}")

            except Exception as e:
                validation_results.append({
                    'point': i + 1,
                    'longitude': lon,
                    'latitude': lat,
                    'error': str(e),
                    'valid': False
                })

        # Calculate statistics
        if errors:
            stats = {
                'total_points': len(validation_results),
                'valid_points': valid_points,
                'mean_error': np.mean(errors),
                'std_error': np.std(errors),
                'min_error': min(errors),
                'max_error': max(errors),
                'error_range': max(errors) - min(errors),
                'accuracy_5deg': sum(1 for e in errors if e < 5.0) / len(errors) * 100,
                'accuracy_10deg': sum(1 for e in errors if e < 10.0) / len(errors) * 100
            }

            print(f"\nValidation Statistics:")
            print(f"  Valid points: {valid_points}/{len(validation_results)}")
            print(f"  Mean error: {stats['mean_error']:.2f}°")
            print(f"  Error range: {stats['min_error']:.2f}° - {stats['max_error']:.2f}°")
            print(f"  Accuracy <5°: {stats['accuracy_5deg']:.1f}%")
            print(f"  Accuracy <10°: {stats['accuracy_10deg']:.1f}%")
        else:
            stats = {'total_points': 0, 'valid_points': 0}

        return {
            'validation_results': validation_results,
            'errors': errors,
            'statistics': stats
        }

    def _create_chart_and_measure_aspect(self, longitude: float, latitude: float,
                                       planet_id: int, angle_type: str) -> Dict:
        """Create chart at location and measure planet-angle aspect."""
        try:
            subject = Subject(
                date_time=self.birth_datetime,
                latitude=str(latitude),
                longitude=str(longitude),
                timezone="Europe/Berlin"
            )

            natal_chart = Natal(subject)

            # Get planet and angle positions
            planet_data = natal_chart.objects.get(planet_id)
            if angle_type == 'ASC':
                angle_data = natal_chart.objects.get(chart.ASC)
            elif angle_type == 'DESC':
                angle_data = natal_chart.objects.get(chart.DESC)
            else:
                return {'error': f'Unsupported angle: {angle_type}'}

            if not planet_data or not angle_data:
                return {'error': 'Missing planet or angle data'}

            # Calculate aspect
            planet_longitude = float(planet_data.longitude.raw)
            angle_longitude = float(angle_data.longitude.raw)
            aspect_diff = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)

            return {
                'longitude': longitude,
                'latitude': latitude,
                'planet_longitude': planet_longitude,
                'angle_longitude': angle_longitude,
                'aspect_degrees': aspect_diff
            }

        except Exception as e:
            return {'error': str(e)}

    def compare_implementations(self, planet_id: int, aspect_degrees: float, angle_type: str = 'ASC'):
        """Compare current vs spherical implementations."""
        print("=" * 80)
        print(f"IMPLEMENTATION COMPARISON: {self._planet_name(planet_id)} {aspect_degrees}° {angle_type}")
        print("=" * 80)

        # Test current implementation
        print("\n1. CURRENT IMPLEMENTATION TEST:")
        current_results = self.test_current_implementation(planet_id, aspect_degrees, angle_type)

        print("\n" + "=" * 60)

        # Test spherical method concept
        print("\n2. SPHERICAL METHOD CONCEPT TEST:")
        spherical_results = self.test_spherical_method_concept(planet_id, aspect_degrees, angle_type)

        # Compare results
        print("\n" + "=" * 60)
        print("COMPARISON SUMMARY:")
        print("=" * 60)

        if current_results.get('success') and spherical_results.get('success'):
            current_stats = current_results['validation']['statistics']
            spherical_stats = spherical_results['validation']['statistics']

            print(f"\nCurrent Implementation:")
            print(f"  Coordinates: {len(current_results['coordinates'])}")
            print(f"  Mean error: {current_stats['mean_error']:.2f}°")
            print(f"  Accuracy <5°: {current_stats['accuracy_5deg']:.1f}%")

            print(f"\nSpherical Method:")
            print(f"  Coordinates: {len(spherical_results['coordinates'])}")
            print(f"  Mean error: {spherical_stats['mean_error']:.2f}°")
            print(f"  Accuracy <5°: {spherical_stats['accuracy_5deg']:.1f}%")

            # Determine which is better
            if spherical_stats['mean_error'] < current_stats['mean_error']:
                print(f"\n✓ Spherical method is MORE ACCURATE by {current_stats['mean_error'] - spherical_stats['mean_error']:.2f}°")
            else:
                print(f"\n✗ Current method is still better by {spherical_stats['mean_error'] - current_stats['mean_error']:.2f}°")

        print("\nNEXT STEPS FOR SPHERICAL METHOD:")
        print("1. Refine hour angle offset calculation")
        print("2. Add latitude-dependent aspect corrections")
        print("3. Implement proper celestial coordinate transformations")
        print("4. Test with different planets and aspects")

    def run_comprehensive_test(self):
        """Run comprehensive test across multiple aspects."""
        print("COMPREHENSIVE ASC/DESC ASPECT TESTBED")
        print("=" * 80)

        test_cases = [
            (chart.SUN, 60, 'ASC', "Sun Sextile ASC"),
            (chart.SUN, 90, 'ASC', "Sun Square ASC"),
            (chart.SUN, 120, 'ASC', "Sun Trine ASC"),
        ]

        for planet_id, aspect_degrees, angle_type, description in test_cases:
            print(f"\n{'=' * 80}")
            print(f"TESTING: {description}")
            print(f"{'=' * 80}")

            self.compare_implementations(planet_id, aspect_degrees, angle_type)

    def test_ternary_search_method(self, planet_id: int, aspect_degrees: float, angle_type: str = 'ASC',
                                   use_fast_method: bool = False) -> Dict:
        """Test latitude-dependent ternary search method."""
        method_name = "FAST" if use_fast_method else "CHART-BASED"
        print(f"TESTING {method_name} LATITUDE-DEPENDENT TERNARY SEARCH METHOD")
        print(f"Planet: {self._planet_name(planet_id)}, Aspect: {aspect_degrees}°, Angle: {angle_type}")
        print("-" * 60)

        try:
            ternary_coords = self._latitude_dependent_ternary_search_method(
                planet_id, aspect_degrees, angle_type, use_fast_method=use_fast_method
            )

            if ternary_coords:
                validation_results = self._validate_aspect_coordinates(
                    ternary_coords, planet_id, aspect_degrees, angle_type, sample_count=len(ternary_coords)
                )

                return {
                    'method': 'ternary_search_fast' if use_fast_method else 'ternary_search_chart',
                    'coordinates': ternary_coords,
                    'validation': validation_results,
                    'success': True,
                    'use_fast_method': use_fast_method
                }
            else:
                return {'method': 'ternary_search', 'success': False}

        except Exception as e:
            print(f"Error in ternary search method: {e}")
            return {'method': 'ternary_search', 'error': str(e), 'success': False}

    def run_translation_hypothesis_test(self):
        """Test if ASC/DESC aspect lines are simple translations."""
        print("TRANSLATION HYPOTHESIS TEST")
        print("=" * 80)
        print("Testing if aspect lines are vertical lines (simple translations)")
        print()

        test_cases = [
            (chart.SUN, 60, 'ASC', "Sun Sextile ASC"),
            (chart.SUN, 90, 'ASC', "Sun Square ASC"),
            (chart.SUN, 120, 'ASC', "Sun Trine ASC"),
        ]

        results = []
        for planet_id, aspect_degrees, angle_type, description in test_cases:
            print(f"\n{'=' * 80}")
            print(f"TESTING: {description}")
            print(f"{'=' * 80}\n")

            result = self._test_translation_hypothesis(planet_id, aspect_degrees, angle_type)
            results.append((description, result))

        # Summary
        print(f"\n{'=' * 80}")
        print("TRANSLATION HYPOTHESIS SUMMARY")
        print(f"{'=' * 80}")

        for description, result in results:
            if result.get('success'):
                is_trans = result.get('is_translation', False)
                mean_err = result['statistics']['mean_error']
                std_err = result['statistics']['std_error']

                status = "✓ VERTICAL" if is_trans else "✗ CURVED"
                print(f"{description:20s}: {status} (mean={mean_err:.2f}°, std={std_err:.2f}°)")
            else:
                print(f"{description:20s}: ✗ FAILED")

    def run_ternary_search_test(self, use_fast_method: bool = False):
        """Test the latitude-dependent ternary search method."""
        method_name = "FAST (swe.houses)" if use_fast_method else "CHART-BASED"
        print(f"LATITUDE-DEPENDENT TERNARY SEARCH METHOD TEST - {method_name}")
        print("=" * 80)
        print("Testing accurate curved line generation using ternary search at each latitude")
        print()

        test_cases = [
            (chart.SUN, 60, 'ASC', "Sun Sextile ASC"),
            (chart.SUN, 90, 'ASC', "Sun Square ASC"),
            (chart.SUN, 120, 'ASC', "Sun Trine ASC"),
        ]

        results = []
        for planet_id, aspect_degrees, angle_type, description in test_cases:
            print(f"\n{'=' * 80}")
            print(f"TESTING: {description}")
            print(f"{'=' * 80}\n")

            result = self.test_ternary_search_method(planet_id, aspect_degrees, angle_type, use_fast_method=use_fast_method)
            results.append((description, result))

        # Summary
        print(f"\n{'=' * 80}")
        print(f"TERNARY SEARCH METHOD SUMMARY - {method_name}")
        print(f"{'=' * 80}")

        for description, result in results:
            if result.get('success'):
                stats = result['validation']['statistics']
                mean_err = stats['mean_error']
                accuracy_1deg = stats.get('accuracy_1deg', sum(1 for e in result['validation']['errors'] if e < 1.0) / len(result['validation']['errors']) * 100 if result['validation']['errors'] else 0)

                status = "✓ EXCELLENT" if mean_err < 1.0 else "⚠ GOOD" if mean_err < 5.0 else "✗ POOR"
                print(f"{description:20s}: {status} (mean={mean_err:.2f}°, <1°: {accuracy_1deg:.1f}%)")
            else:
                print(f"{description:20s}: ✗ FAILED")

    def run_performance_comparison(self):
        """Compare performance between chart-based and fast methods."""
        print("PERFORMANCE COMPARISON: CHART-BASED vs FAST METHOD")
        print("=" * 80)
        print("Testing Sun Square ASC with both methods")
        print()

        # Test chart-based method
        print("=" * 80)
        print("1. CHART-BASED METHOD (Full Natal chart creation)")
        print("=" * 80)
        result_slow = self.test_ternary_search_method(chart.SUN, 90, 'ASC', use_fast_method=False)

        print("\n" + "=" * 80)
        print("2. FAST METHOD (swe.houses() direct)")
        print("=" * 80)
        result_fast = self.test_ternary_search_method(chart.SUN, 90, 'ASC', use_fast_method=True)

        # Comparison summary
        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON SUMMARY")
        print("=" * 80)

        if result_slow.get('success') and result_fast.get('success'):
            slow_stats = result_slow['validation']['statistics']
            fast_stats = result_fast['validation']['statistics']

            print(f"\nAccuracy (both should be identical):")
            print(f"  Chart-based: {slow_stats['mean_error']:.4f}° mean error")
            print(f"  Fast method: {fast_stats['mean_error']:.4f}° mean error")
            print(f"  Match: {'✓ YES' if abs(slow_stats['mean_error'] - fast_stats['mean_error']) < 0.01 else '✗ NO'}")

            print(f"\nNote: Run with timing enabled to see performance difference")
            print(f"      Fast method should be 100-1000x faster than chart-based")

    def _normalize_longitude(self, longitude: float) -> float:
        """Normalize longitude to [-180, 180] range."""
        while longitude > 180:
            longitude -= 360
        while longitude < -180:
            longitude += 360
        return longitude

    def _planet_name(self, planet_id: int) -> str:
        """Get planet name from ID."""
        names = {
            chart.SUN: "Sun",
            chart.MOON: "Moon",
            chart.MERCURY: "Mercury",
            chart.VENUS: "Venus",
            chart.MARS: "Mars",
            chart.JUPITER: "Jupiter",
            chart.SATURN: "Saturn"
        }
        return names.get(planet_id, f"Planet {planet_id}")


    def benchmark_smart_search(self):
        """Benchmark smart search vs brute force hemisphere search."""
        print("SMART SEARCH BENCHMARK")
        print("=" * 80)
        print("Comparing hemisphere search vs smart region detection")
        print()

        planet_id = chart.SUN
        aspect_degrees = 60
        planet_longitude = self.calculator.get_planetary_position(planet_id)['longitude']
        test_latitudes = np.arange(-66, 67, 1.0)
        tolerance = 0.25

        # Method 1: Current hemisphere search
        print("Method 1: Hemisphere Search (current)")
        start = time.time()
        total_iterations_hemi = 0

        for latitude in test_latitudes:
            # Search western hemisphere
            left, right = -180.0, 0.0
            iterations = 0
            while (right - left) > tolerance:
                mid1 = left + (right - left) / 3.0
                mid2 = right - (right - left) / 3.0
                houses1 = swe.houses(self.julian_date, latitude, mid1, b'P')
                houses2 = swe.houses(self.julian_date, latitude, mid2, b'P')
                asc1 = houses1[1][0]
                asc2 = houses2[1][0]
                aspect1 = abs((planet_longitude - asc1 + 180.0) % 360.0 - 180.0)
                aspect2 = abs((planet_longitude - asc2 + 180.0) % 360.0 - 180.0)
                err1 = abs(aspect1 - aspect_degrees)
                err2 = abs(aspect2 - aspect_degrees)
                if err1 > 180.0:
                    err1 = 360.0 - err1
                if err2 > 180.0:
                    err2 = 360.0 - err2
                if err1 < err2:
                    right = mid2
                else:
                    left = mid1
                iterations += 1

            # Search eastern hemisphere
            left, right = 0.0, 180.0
            while (right - left) > tolerance:
                mid1 = left + (right - left) / 3.0
                mid2 = right - (right - left) / 3.0
                houses1 = swe.houses(self.julian_date, latitude, mid1, b'P')
                houses2 = swe.houses(self.julian_date, latitude, mid2, b'P')
                asc1 = houses1[1][0]
                asc2 = houses2[1][0]
                aspect1 = abs((planet_longitude - asc1 + 180.0) % 360.0 - 180.0)
                aspect2 = abs((planet_longitude - asc2 + 180.0) % 360.0 - 180.0)
                err1 = abs(aspect1 - aspect_degrees)
                err2 = abs(aspect2 - aspect_degrees)
                if err1 > 180.0:
                    err1 = 360.0 - err1
                if err2 > 180.0:
                    err2 = 360.0 - err2
                if err1 < err2:
                    right = mid2
                else:
                    left = mid1
                iterations += 1

            total_iterations_hemi += iterations

        time_hemi = time.time() - start
        avg_iter_hemi = total_iterations_hemi / len(test_latitudes)

        print(f"  Time: {time_hemi*1000:.2f}ms ({time_hemi/len(test_latitudes)*1000:.3f}ms per lat)")
        print(f"  Iterations: {avg_iter_hemi:.1f} per latitude")
        print(f"  swe.houses() calls: {total_iterations_hemi*2}")
        print()

        # Method 2: Smart coarse scan then fine search
        print("Method 2: Smart Coarse Scan + Fine Search")
        start = time.time()
        total_iterations_smart = 0

        for latitude in test_latitudes:
            # Coarse scan to find promising regions
            scan_points = 12  # Every 30 degrees
            scan_lons = np.linspace(-180, 180, scan_points)
            errors = []

            for lon in scan_lons:
                houses = swe.houses(self.julian_date, latitude, lon, b'P')
                asc = houses[1][0]
                aspect = abs((planet_longitude - asc + 180.0) % 360.0 - 180.0)
                err = abs(aspect - aspect_degrees)
                if err > 180.0:
                    err = 360.0 - err
                errors.append((lon, err))

            # Find local minima (where error is less than neighbors)
            minima = []
            for i in range(1, len(errors)-1):
                if errors[i][1] < errors[i-1][1] and errors[i][1] < errors[i+1][1]:
                    minima.append(errors[i][0])

            # Refine each minimum with ternary search
            for min_lon in minima[:2]:  # Limit to 2 best minima
                left = min_lon - 10.0
                right = min_lon + 10.0
                iterations = 0

                while (right - left) > tolerance:
                    mid1 = left + (right - left) / 3.0
                    mid2 = right - (right - left) / 3.0
                    houses1 = swe.houses(self.julian_date, latitude, mid1, b'P')
                    houses2 = swe.houses(self.julian_date, latitude, mid2, b'P')
                    asc1 = houses1[1][0]
                    asc2 = houses2[1][0]
                    aspect1 = abs((planet_longitude - asc1 + 180.0) % 360.0 - 180.0)
                    aspect2 = abs((planet_longitude - asc2 + 180.0) % 360.0 - 180.0)
                    err1 = abs(aspect1 - aspect_degrees)
                    err2 = abs(aspect2 - aspect_degrees)
                    if err1 > 180.0:
                        err1 = 360.0 - err1
                    if err2 > 180.0:
                        err2 = 360.0 - err2
                    if err1 < err2:
                        right = mid2
                    else:
                        left = mid1
                    iterations += 1

                total_iterations_smart += iterations

            total_iterations_smart += scan_points  # Add coarse scan

        time_smart = time.time() - start
        avg_iter_smart = total_iterations_smart / len(test_latitudes)

        print(f"  Time: {time_smart*1000:.2f}ms ({time_smart/len(test_latitudes)*1000:.3f}ms per lat)")
        print(f"  Iterations: {avg_iter_smart:.1f} per latitude")
        print(f"  swe.houses() calls: {total_iterations_smart}")
        print()

        # Comparison
        print("=" * 80)
        print("COMPARISON")
        print("=" * 80)
        speedup = time_hemi / time_smart
        print(f"Hemisphere search:   {time_hemi*1000:.2f}ms ({avg_iter_hemi:.1f} iter/lat)")
        print(f"Smart search:        {time_smart*1000:.2f}ms ({avg_iter_smart:.1f} iter/lat)")
        print(f"Speedup:             {speedup:.2f}x {'WORSE' if speedup < 1 else 'BETTER'}")

    def benchmark_tolerance(self, tolerance_values=[0.01, 0.1, 0.25, 0.5, 1.0]):
        """Benchmark different tolerance values for speed and accuracy."""
        print("TOLERANCE BENCHMARK")
        print("=" * 80)
        print("Testing speed vs accuracy tradeoff")
        print()

        planet_id = chart.SUN
        aspect_degrees = 90
        planet_longitude = self.calculator.get_planetary_position(planet_id)['longitude']
        test_latitudes = np.arange(-66, 67, 5.0)

        results = []

        for tolerance in tolerance_values:
            print(f"Testing tolerance = {tolerance}°:")

            # Pure search timing
            total_iterations = 0
            start_search = time.time()
            longitudes = []

            for latitude in test_latitudes:
                # Ternary search
                left, right = -180.0, 180.0
                iterations = 0

                while (right - left) > tolerance:
                    mid1 = left + (right - left) / 3.0
                    mid2 = right - (right - left) / 3.0

                    houses1 = swe.houses(self.julian_date, latitude, mid1, b'P')
                    asc1 = houses1[1][0]
                    aspect1 = abs((planet_longitude - asc1 + 180.0) % 360.0 - 180.0)
                    err1 = abs(aspect1 - aspect_degrees)
                    if err1 > 180.0:
                        err1 = 360.0 - err1

                    houses2 = swe.houses(self.julian_date, latitude, mid2, b'P')
                    asc2 = houses2[1][0]
                    aspect2 = abs((planet_longitude - asc2 + 180.0) % 360.0 - 180.0)
                    err2 = abs(aspect2 - aspect_degrees)
                    if err2 > 180.0:
                        err2 = 360.0 - err2

                    if err1 < err2:
                        right = mid2
                    else:
                        left = mid1
                    iterations += 1

                longitude = (left + right) / 2.0
                longitudes.append(longitude)
                total_iterations += iterations

            search_time = time.time() - start_search

            # Validate accuracy with charts
            errors = []
            for i, latitude in enumerate(test_latitudes):
                result = self._create_chart_and_measure_aspect(
                    longitudes[i], latitude, planet_id, 'ASC'
                )
                if 'error' not in result:
                    error = abs(result['aspect_degrees'] - aspect_degrees)
                    if error > 180.0:
                        error = 360.0 - error
                    errors.append(error)

            mean_error = np.mean(errors) if errors else 0
            max_error = max(errors) if errors else 0
            avg_iterations = total_iterations / len(test_latitudes)

            results.append({
                'tolerance': tolerance,
                'iterations': avg_iterations,
                'time': search_time,
                'mean_error': mean_error,
                'max_error': max_error
            })

            print(f"  Iterations: {avg_iterations:.1f} avg")
            print(f"  Time: {search_time*1000:.2f}ms ({search_time/len(test_latitudes)*1000:.3f}ms per lat)")
            print(f"  Accuracy: mean={mean_error:.4f}° max={max_error:.4f}°")
            print()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        baseline = results[0]
        print(f"{'Tolerance':>10} {'Iterations':>12} {'Time':>10} {'Max Error':>12} {'Speedup':>10}")
        print("-" * 80)
        for r in results:
            speedup = baseline['time'] / r['time']
            print(f"{r['tolerance']:>10.2f}° {r['iterations']:>12.1f} {r['time']*1000:>9.2f}ms "
                  f"{r['max_error']:>11.4f}° {speedup:>9.2f}x")

    def benchmark_raw_speed(self, iterations=10000):
        """Benchmark raw calculation speed."""
        print("RAW SPEED BENCHMARK")
        print("=" * 80)
        print(f"Running {iterations:,} iterations")
        print()

        planet_id = chart.SUN
        planet_longitude = self.calculator.get_planetary_position(planet_id)['longitude']

        test_longitudes = np.random.uniform(-180, 180, iterations)
        test_latitudes = np.random.uniform(-66, 66, iterations)

        # Raw swe.houses() benchmark
        start = time.time()
        for i in range(iterations):
            houses = swe.houses(self.julian_date, test_latitudes[i], test_longitudes[i], b'P')
            asc = houses[1][0]
        elapsed = time.time() - start

        print(f"Raw swe.houses() calls:")
        print(f"  Total: {elapsed:.3f}s")
        print(f"  Per call: {elapsed/iterations*1000:.4f}ms ({elapsed/iterations*1000000:.1f}µs)")
        print(f"  Calls/sec: {iterations/elapsed:,.0f}")
        print()

        # Full aspect calculation
        start = time.time()
        for i in range(iterations):
            houses = swe.houses(self.julian_date, test_latitudes[i], test_longitudes[i], b'P')
            asc = houses[1][0]
            aspect = abs((planet_longitude - asc + 180.0) % 360.0 - 180.0)
        elapsed = time.time() - start

        print(f"Full aspect calculations:")
        print(f"  Total: {elapsed:.3f}s")
        print(f"  Per calc: {elapsed/iterations*1000:.4f}ms ({elapsed/iterations*1000000:.1f}µs)")
        print(f"  Calcs/sec: {iterations/elapsed:,.0f}")


def main():
    """Run the ASC/DESC aspect testbed."""
    import sys

    print("ASC/DESC ASPECT LINES IMPLEMENTATION TESTBED")
    print("=" * 80)
    print()

    # Initialize testbed
    testbed = ASCDESCAspectTestbed(
        birth_datetime="1984-01-03 18:36:00",
        birth_latitude="48.521637",
        birth_longitude="9.057645"
    )

    # Check command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "tolerance":
            testbed.benchmark_tolerance()
        elif sys.argv[1] == "speed":
            testbed.benchmark_raw_speed()
        elif sys.argv[1] == "full":
            testbed.run_ternary_search_test(use_fast_method=True)
        elif sys.argv[1] == "smart":
            testbed.benchmark_smart_search()
        else:
            print("Usage: python asc_desc_aspect_testbed.py [tolerance|speed|full|smart]")
    else:
        # Default: run tolerance benchmark
        testbed.benchmark_tolerance()


if __name__ == "__main__":
    main()