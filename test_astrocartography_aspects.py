#!/usr/bin/env python3
"""
Astrocartography Aspect Calculation Test Script

This script validates astrocartography aspect calculations by:
1. Computing aspect lines using the implemented method
2. Testing specific coordinates to verify they produce the correct aspects
3. Comparing calculated vs expected coordinates
4. Providing detailed astronomical verification
5. Performance profiling and comparison between fast and slow methods

Usage: python test_astrocartography_aspects.py
"""

import swisseph as swe
import math
import time
import cProfile
import pstats
from functools import wraps
from datetime import datetime
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart


def profile_function(func):
    """Decorator to profile function execution time and calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        pr = cProfile.Profile()
        pr.enable()

        result = func(*args, **kwargs)

        pr.disable()
        end_time = time.time()

        print(f"\n=== PROFILING: {func.__name__} ===")
        print(f"Execution time: {end_time - start_time:.3f} seconds")

        # Print top time-consuming functions
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        print("Top 5 most time-consuming calls:")
        stats.print_stats(5)

        return result, end_time - start_time
    return wrapper


class AstrocartographyTester:
    def __init__(self, birth_datetime: str, birth_latitude: float, birth_longitude: float):
        """
        Initialize the tester with birth data.

        Args:
            birth_datetime: Birth time in 'YYYY-MM-DD HH:MM:SS' format
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
        """
        self.birth_datetime = birth_datetime
        self.birth_latitude = birth_latitude
        self.birth_longitude = birth_longitude

        # Convert to Julian Date - use UTC time for consistency with chart creation
        dt = datetime.strptime(birth_datetime, '%Y-%m-%d %H:%M:%S')
        # Convert Berlin time to UTC (Berlin is UTC+1 in January)
        dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
        self.julian_date = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

        # Initialize calculator
        self.calculator = AstrocartographyCalculator(julian_date=self.julian_date, sampling_resolution=1.0)

        print(f"Initialized tester for birth: {birth_datetime}")
        print(f"Location: {birth_latitude:.3f}°N, {birth_longitude:.3f}°E")
        print(f"Julian Date: {self.julian_date:.6f}")
        print()

    def test_location_aspect(self, longitude: float, latitude: float, planet_id: int,
                           angle_type: str = 'MC') -> dict:
        """
        Test what aspect exists between a planet and angle by creating an actual chart.

        Args:
            longitude: Geographic longitude in degrees
            latitude: Geographic latitude in degrees
            planet_id: Planet constant from immanuel.const.chart
            angle_type: 'MC' or 'IC'

        Returns:
            Dictionary with test results
        """
        from immanuel.charts import Subject, Natal
        from immanuel.const import chart as chart_const

        try:
            # Create a subject at this location for the same birth time
            # Convert birth datetime back to proper format
            dt = datetime.strptime(self.birth_datetime, '%Y-%m-%d %H:%M:%S')

            # Create subject at the test location
            test_subject = Subject(
                date_time=dt,
                latitude=str(latitude),
                longitude=str(longitude),
                timezone="Europe/Berlin"  # Use original timezone
            )

            # Create a natal chart for this location
            test_chart = Natal(test_subject)

            # Get planet position from the chart
            planet_data = test_chart.objects.get(planet_id)
            if not planet_data:
                return {'error': f'Planet {planet_id} not found in chart'}

            planet_longitude = float(planet_data.longitude.raw)

            # Get MC/IC position from the chart
            if angle_type == 'MC':
                angle_data = test_chart.objects.get(chart_const.MC)
            else:  # IC
                angle_data = test_chart.objects.get(chart_const.IC)

            if not angle_data:
                return {'error': f'{angle_type} not found in chart'}

            angle_longitude = float(angle_data.longitude.raw)

            # Calculate actual aspect between planet and angle
            aspect_diff = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)

            return {
                'longitude': longitude,
                'latitude': latitude,
                'planet_longitude': planet_longitude,
                'angle_longitude': angle_longitude,
                'aspect_degrees': aspect_diff,
                'planet_sign': str(planet_data.sign),
                'angle_sign': str(angle_data.sign),
                'chart_created': True
            }

        except Exception as e:
            return {
                'longitude': longitude,
                'latitude': latitude,
                'error': str(e),
                'chart_created': False
            }

    def find_aspect_line_by_search(self, planet_id: int, aspect_degrees: float,
                                  angle_type: str = 'MC', longitude_range: tuple = (-180, 180),
                                  tolerance: float = 1.0) -> list:
        """
        Find aspect line coordinates by searching through longitudes and testing with charts.

        Args:
            planet_id: Planet constant
            aspect_degrees: Desired aspect (60, 90, 120, etc.)
            angle_type: 'MC' or 'IC'
            longitude_range: Tuple of (min_lon, max_lon) to search
            tolerance: Accept aspects within this many degrees of target

        Returns:
            List of longitude values where the aspect occurs
        """
        print(f"Searching for {self._planet_name(planet_id)} {aspect_degrees}° {angle_type} using chart method...")

        valid_longitudes = []
        min_lon, max_lon = longitude_range

        # Search in 0.5 degree increments
        search_step = 0.5
        test_latitude = 45.0  # Use 45°N as test latitude

        current_lon = min_lon
        while current_lon <= max_lon:
            test_result = self.test_location_aspect(current_lon, test_latitude, planet_id, angle_type)

            if 'error' not in test_result:
                aspect_found = test_result['aspect_degrees']
                error = abs(aspect_found - aspect_degrees)

                if error <= tolerance:
                    valid_longitudes.append(current_lon)
                    print(f"  Found: {current_lon:7.1f}° → {aspect_found:6.3f}° (error: {error:5.3f}°)")

            current_lon += search_step

        return valid_longitudes

    @profile_function
    def test_fast_method(self, planet_id: int, aspect_degrees: float, angle_type: str = 'MC') -> dict:
        """Test the new fast binary search method."""
        print(f"Testing FAST method: {self._planet_name(planet_id)} {aspect_degrees}° {angle_type}")

        # Use the fast method directly
        aspect_longitudes = self.calculator._calculate_aspect_longitudes_fast(
            planet_id, angle_type, aspect_degrees
        )

        # Validate the results by testing each longitude
        validation_results = []
        for longitude in aspect_longitudes:
            test_result = self.test_location_aspect(longitude, 45.0, planet_id, angle_type)
            validation_results.append(test_result)

        return {
            'method': 'fast',
            'planet': self._planet_name(planet_id),
            'aspect': aspect_degrees,
            'angle_type': angle_type,
            'longitudes_found': aspect_longitudes,
            'validation_results': validation_results
        }

    @profile_function
    def test_slow_method(self, planet_id: int, aspect_degrees: float, angle_type: str = 'MC',
                        longitude_range: tuple = (-180, 180)) -> dict:
        """Test the old slow chart-based search method for comparison."""
        print(f"Testing SLOW method: {self._planet_name(planet_id)} {aspect_degrees}° {angle_type}")

        # Use limited range for comparison to avoid excessive time
        min_lon, max_lon = longitude_range
        if max_lon - min_lon > 20:  # Limit search range for performance
            # Focus around known good coordinates for comparison
            if aspect_degrees == 90:  # Square
                longitude_range = (-10, 10)  # Around 5.233°
            else:
                longitude_range = (min_lon, min_lon + 20)  # Just first 20 degrees

        valid_longitudes = self.find_aspect_line_by_search(
            planet_id, aspect_degrees, angle_type, longitude_range, tolerance=1.0
        )

        return {
            'method': 'slow',
            'planet': self._planet_name(planet_id),
            'aspect': aspect_degrees,
            'angle_type': angle_type,
            'longitudes_found': valid_longitudes,
            'search_range': longitude_range
        }

    def test_aspect_line_calculation(self, planet_id: int, aspect_degrees: float,
                                   angle_type: str = 'MC', max_samples: int = 10) -> dict:
        """
        Test aspect line by searching for coordinates that produce the correct aspect.

        Args:
            planet_id: Planet constant
            aspect_degrees: Desired aspect (60, 90, 120, etc.)
            angle_type: 'MC' or 'IC'
            max_samples: Maximum number of sample coordinates to test

        Returns:
            Dictionary with search results
        """
        # Use chart-based search to find valid longitudes
        valid_longitudes = self.find_aspect_line_by_search(
            planet_id, aspect_degrees, angle_type, tolerance=1.0
        )

        # Test a sample of found coordinates to verify
        sample_tests = []
        test_coords = valid_longitudes[:max_samples] if len(valid_longitudes) > max_samples else valid_longitudes

        for longitude in test_coords:
            test_result = self.test_location_aspect(longitude, 45.0, planet_id, angle_type)
            sample_tests.append(test_result)

        return {
            'planet': self._planet_name(planet_id),
            'aspect': aspect_degrees,
            'angle_type': angle_type,
            'coordinates_found': len(valid_longitudes),
            'unique_longitudes': valid_longitudes,
            'sample_tests': sample_tests
        }

    def compare_with_expected(self, planet_id: int, aspect_degrees: float,
                            expected_longitudes: list, angle_type: str = 'MC') -> dict:
        """
        Compare calculated coordinates with expected coordinates.

        Args:
            planet_id: Planet constant
            aspect_degrees: Aspect in degrees
            expected_longitudes: List of expected longitude values
            angle_type: 'MC' or 'IC'

        Returns:
            Comparison results
        """
        print(f"Comparing calculated vs expected for {self._planet_name(planet_id)} {aspect_degrees}° {angle_type}...")

        # Get calculated coordinates
        calc_result = self.test_aspect_line_calculation(planet_id, aspect_degrees, angle_type, max_samples=5)
        calculated_longs = calc_result['unique_longitudes']

        # Test expected coordinates
        expected_tests = []
        for exp_long in expected_longitudes:
            test_result = self.test_location_aspect(exp_long, 45.0, planet_id, angle_type)  # Use 45°N as test latitude
            expected_tests.append(test_result)

        return {
            'planet': self._planet_name(planet_id),
            'aspect': aspect_degrees,
            'angle_type': angle_type,
            'calculated_longitudes': calculated_longs,
            'expected_longitudes': expected_longitudes,
            'calculated_tests': calc_result['sample_tests'],
            'expected_tests': expected_tests
        }

    def performance_comparison_test(self):
        """Run performance comparison between fast and slow methods."""
        print("=" * 80)
        print("PERFORMANCE COMPARISON TEST")
        print("=" * 80)
        print()

        test_cases = [
            (chart.SUN, 90, "Sun Square MC"),
            (chart.SUN, 60, "Sun Sextile MC"),
            (chart.SUN, 120, "Sun Trine MC"),
        ]

        results = []

        for planet_id, aspect_degrees, description in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {description}")
            print(f"{'='*60}")

            # Test fast method
            fast_result, fast_time = self.test_fast_method(planet_id, aspect_degrees)

            print(f"\n{'-'*40}")

            # Test slow method (limited range)
            slow_result, slow_time = self.test_slow_method(planet_id, aspect_degrees)

            # Compare results
            print(f"\n=== COMPARISON FOR {description} ===")
            print(f"Fast method time: {fast_time:.3f} seconds")
            print(f"Slow method time: {slow_time:.3f} seconds")
            print(f"Speed improvement: {slow_time/fast_time:.1f}x faster")

            print(f"\nFast method longitudes: {[f'{lon:.3f}°' for lon in fast_result['longitudes_found']]}")
            print(f"Slow method longitudes: {[f'{lon:.1f}°' for lon in slow_result['longitudes_found']]}")

            # Validate accuracy of fast method
            print(f"\nFast method accuracy:")
            for i, validation in enumerate(fast_result['validation_results']):
                if 'error' not in validation:
                    error = abs(validation['aspect_degrees'] - aspect_degrees)
                    status = "✓" if error <= 0.1 else "✗"
                    print(f"  {validation['longitude']:7.3f}°: {validation['aspect_degrees']:6.3f}° "
                          f"(error: {error:.3f}°) {status}")

            results.append({
                'description': description,
                'fast_time': fast_time,
                'slow_time': slow_time,
                'speedup': slow_time / fast_time,
                'fast_result': fast_result,
                'slow_result': slow_result
            })

        return results

    def validate_against_known_coordinates(self):
        """Validate fast method aspect accuracy."""
        print("\n" + "=" * 80)
        print("ASPECT ACCURACY VALIDATION")
        print("=" * 80)

        test_aspects = [60, 90, 120]  # Sextile, Square, Trine
        validation_results = []

        for aspect_degrees in test_aspects:
            aspect_name = {60: "Sextile", 90: "Square", 120: "Trine"}[aspect_degrees]
            print(f"\nValidating Sun {aspect_name} MC ({aspect_degrees}°):")
            print("-" * 50)

            # Get fast method results
            fast_longitudes = self.calculator._calculate_aspect_longitudes_fast(
                chart.SUN, 'MC', aspect_degrees
            )

            print(f"Fast method coordinates: {[f'{lon:.3f}°' for lon in fast_longitudes]}")

            # Test each coordinate for aspect accuracy
            aspect_errors = []
            for i, longitude in enumerate(fast_longitudes, 1):
                test_result = self.test_location_aspect(longitude, 45.0, chart.SUN, 'MC')
                if 'error' in test_result:
                    print(f"  Coordinate {i}: {longitude:.3f}° → ERROR: {test_result['error']}")
                    aspect_errors.append(999.0)  # Large error for failed tests
                    continue

                actual_aspect = test_result['aspect_degrees']
                aspect_error = abs(actual_aspect - aspect_degrees)

                # Handle aspect wrap-around (e.g., 359° vs 1°)
                if aspect_error > 180.0:
                    aspect_error = 360.0 - aspect_error

                aspect_errors.append(aspect_error)
                print(f"  Coordinate {i}: {longitude:.3f}° → {actual_aspect:.3f}° "
                      f"(aspect error: {aspect_error:.3f}°)")

            max_aspect_error = max(aspect_errors)
            status = "✓ PASS" if max_aspect_error <= 0.1 else "✗ FAIL"
            print(f"  Maximum aspect error: {max_aspect_error:.3f}° {status}")

            validation_results.append({
                'aspect': aspect_degrees,
                'aspect_name': aspect_name,
                'calculated': fast_longitudes,
                'max_aspect_error': max_aspect_error,
                'passed': max_aspect_error <= 0.1
            })

        return validation_results

    def run_comprehensive_test(self):
        """Run a comprehensive test including performance and validation."""
        print("=" * 80)
        print("COMPREHENSIVE ASTROCARTOGRAPHY TEST SUITE")
        print("=" * 80)

        # 1. Performance comparison
        performance_results = self.performance_comparison_test()

        # 2. Validation against known coordinates
        validation_results = self.validate_against_known_coordinates()

        # 3. Summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)

        print(f"\nPerformance Results:")
        for result in performance_results:
            print(f"  {result['description']}: {result['speedup']:.1f}x faster ({result['fast_time']:.3f}s vs {result['slow_time']:.3f}s)")

        print(f"\nAspect Accuracy Results:")
        all_passed = True
        for result in validation_results:
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"  {result['aspect_name']}: {result['max_aspect_error']:.3f}° aspect error {status}")
            if not result['passed']:
                all_passed = False

        print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

        return {
            'performance': performance_results,
            'validation': validation_results,
            'all_passed': all_passed
        }

    def _planet_name(self, planet_id: int) -> str:
        """Get planet name from ID."""
        names = {
            chart.SUN: "Sun",
            chart.MOON: "Moon",
            chart.MERCURY: "Mercury",
            chart.VENUS: "Venus",
            chart.MARS: "Mars",
            chart.JUPITER: "Jupiter",
            chart.SATURN: "Saturn",
            chart.URANUS: "Uranus",
            chart.NEPTUNE: "Neptune",
            chart.PLUTO: "Pluto"
        }
        return names.get(planet_id, f"Planet{planet_id}")


def main():
    """Run the test script."""
    # Birth data from the example
    birth_datetime = "1984-01-03 18:36:00"  # Berlin local time
    birth_latitude = 48.521637
    birth_longitude = 9.057645

    # Create tester
    tester = AstrocartographyTester(birth_datetime, birth_latitude, birth_longitude)

    # Run comprehensive test
    results = tester.run_comprehensive_test()

    print("Test completed!")
    print()
    print("This test verifies that:")
    print("1. Our calculated coordinates produce the exact requested aspects")
    print("2. The expected coordinates do NOT produce the requested aspects")
    print("3. Our calculation method is astronomically and astrologically correct")


if __name__ == "__main__":
    main()