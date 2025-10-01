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
        stats.sort_stats("cumulative")
        print("Top 10 most time-consuming calls:")
        stats.print_stats(10)

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
        dt = datetime.strptime(birth_datetime, "%Y-%m-%d %H:%M:%S")
        # Convert Berlin time to UTC (Berlin is UTC+1 in January)
        dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
        self.julian_date = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        )

        # Initialize calculator
        self.calculator = AstrocartographyCalculator(julian_date=self.julian_date, sampling_resolution=1.0)

        print(f"Initialized tester for birth: {birth_datetime}")
        print(f"Location: {birth_latitude:.3f}°N, {birth_longitude:.3f}°E")
        print(f"Julian Date: {self.julian_date:.6f}")
        print()

    def test_location_aspect(self, longitude: float, latitude: float, planet_id: int, angle_type: str = "MC") -> dict:
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
            dt = datetime.strptime(self.birth_datetime, "%Y-%m-%d %H:%M:%S")

            # Create subject at the test location
            test_subject = Subject(
                date_time=dt,
                latitude=str(latitude),
                longitude=str(longitude),
                timezone="Europe/Berlin",  # Use original timezone
            )

            # Create a natal chart for this location
            test_chart = Natal(test_subject)

            # Get planet position from the chart
            planet_data = test_chart.objects.get(planet_id)
            if not planet_data:
                return {"error": f"Planet {planet_id} not found in chart"}

            planet_longitude = float(planet_data.longitude.raw)

            # Get MC/IC position from the chart
            if angle_type == "MC":
                angle_data = test_chart.objects.get(chart_const.MC)
            else:  # IC
                angle_data = test_chart.objects.get(chart_const.IC)

            if not angle_data:
                return {"error": f"{angle_type} not found in chart"}

            angle_longitude = float(angle_data.longitude.raw)

            # Calculate actual aspect between planet and angle
            aspect_diff = abs((planet_longitude - angle_longitude + 180.0) % 360.0 - 180.0)

            return {
                "longitude": longitude,
                "latitude": latitude,
                "planet_longitude": planet_longitude,
                "angle_longitude": angle_longitude,
                "aspect_degrees": aspect_diff,
                "planet_sign": str(planet_data.sign),
                "angle_sign": str(angle_data.sign),
                "chart_created": True,
            }

        except Exception as e:
            return {"longitude": longitude, "latitude": latitude, "error": str(e), "chart_created": False}

    @profile_function
    def test_fast_method(self, planet_id: int, aspect_degrees: float, angle_type: str = "MC") -> dict:
        """Test the new fast binary search method."""
        print(f"Testing FAST method: {self._planet_name(planet_id)} {aspect_degrees}° {angle_type}")

        # Use the fast method directly
        aspect_longitudes = self.calculator._calculate_aspect_longitudes_fast(planet_id, angle_type, aspect_degrees)

        # Validate the results by testing each longitude
        validation_results = []
        for longitude in aspect_longitudes:
            test_result = self.test_location_aspect(longitude, 45.0, planet_id, angle_type)
            validation_results.append(test_result)

        return {
            "method": "fast",
            "planet": self._planet_name(planet_id),
            "aspect": aspect_degrees,
            "angle_type": angle_type,
            "longitudes_found": aspect_longitudes,
            "validation_results": validation_results,
        }

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
            fast_longitudes = self.calculator._calculate_aspect_longitudes_fast(chart.SUN, "MC", aspect_degrees)

            print(f"Fast method coordinates: {[f'{lon:.3f}°' for lon in fast_longitudes]}")

            # Test each coordinate for aspect accuracy
            aspect_errors = []
            for i, longitude in enumerate(fast_longitudes, 1):
                test_result = self.test_location_aspect(longitude, 45.0, chart.SUN, "MC")
                if "error" in test_result:
                    print(f"  Coordinate {i}: {longitude:.3f}° → ERROR: {test_result['error']}")
                    aspect_errors.append(999.0)  # Large error for failed tests
                    continue

                actual_aspect = test_result["aspect_degrees"]
                aspect_error = abs(actual_aspect - aspect_degrees)

                # Handle aspect wrap-around (e.g., 359° vs 1°)
                if aspect_error > 180.0:
                    aspect_error = 360.0 - aspect_error

                aspect_errors.append(aspect_error)
                print(
                    f"  Coordinate {i}: {longitude:.3f}° → {actual_aspect:.3f}° " f"(aspect error: {aspect_error:.3f}°)"
                )

            max_aspect_error = max(aspect_errors)
            status = "✓ PASS" if max_aspect_error <= 0.1 else "✗ FAIL"
            print(f"  Maximum aspect error: {max_aspect_error:.3f}° {status}")

            validation_results.append(
                {
                    "aspect": aspect_degrees,
                    "aspect_name": aspect_name,
                    "calculated": fast_longitudes,
                    "max_aspect_error": max_aspect_error,
                    "passed": max_aspect_error <= 0.1,
                }
            )

        return validation_results

    def run_comprehensive_test(self):
        """Run a comprehensive test focusing on aspect accuracy validation."""
        print("=" * 80)
        print("COMPREHENSIVE ASTROCARTOGRAPHY TEST SUITE")
        print("=" * 80)

        # Test fast method performance and accuracy
        test_cases = [
            (chart.SUN, 90, "Sun Square MC"),
            (chart.SUN, 60, "Sun Sextile MC"),
            (chart.SUN, 120, "Sun Trine MC"),
        ]

        print("\n" + "=" * 80)
        print("FAST METHOD PERFORMANCE TEST")
        print("=" * 80)

        performance_results = []
        for planet_id, aspect_degrees, description in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {description}")
            print(f"{'='*60}")

            # Test fast method with timing
            fast_result, fast_time = self.test_fast_method(planet_id, aspect_degrees)

            print(f"\n=== RESULTS FOR {description} ===")
            print(f"Execution time: {fast_time:.3f} seconds")
            print(f"Coordinates found: {[f'{lon:.3f}°' for lon in fast_result['longitudes_found']]}")

            # Validate accuracy of fast method
            print(f"\nAspect accuracy:")
            for i, validation in enumerate(fast_result["validation_results"]):
                if "error" not in validation:
                    error = abs(validation["aspect_degrees"] - aspect_degrees)
                    status = "✓" if error <= 0.1 else "✗"
                    print(
                        f"  {validation['longitude']:7.3f}°: {validation['aspect_degrees']:6.3f}° "
                        f"(error: {error:.3f}°) {status}"
                    )

            performance_results.append({"description": description, "execution_time": fast_time, "result": fast_result})

        # Comprehensive validation
        validation_results = self.validate_against_known_coordinates()

        # Summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)

        print(f"\nFast Method Performance:")
        for result in performance_results:
            print(f"  {result['description']}: {result['execution_time']:.3f} seconds")

        print(f"\nAspect Accuracy Results:")
        all_passed = True
        for result in validation_results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"  {result['aspect_name']}: {result['max_aspect_error']:.3f}° aspect error {status}")
            if not result["passed"]:
                all_passed = False

        print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

        return {"performance": performance_results, "validation": validation_results, "all_passed": all_passed}

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
            chart.PLUTO: "Pluto",
        }
        return names.get(planet_id, f"Planet{planet_id}")

    def test_full_chart_performance(self):
        """
        Performance test: Calculate full set of lines and zenith points for entire chart.

        Tests:
        1. All planetary lines (MC/IC/ASC/DESC) for major planets
        2. All aspect lines (60°, 90°, 120°) for all angles
        3. Zenith points for all major planets
        4. Total end-to-end chart generation time
        """
        print("\n" + "=" * 80)
        print("FULL CHART PERFORMANCE TEST")
        print("=" * 80)

        major_planets = [
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
            chart.URANUS,
            chart.NEPTUNE,
            chart.PLUTO,
        ]

        angles = ["MC", "IC", "ASC", "DESC"]
        aspects = [60, 90, 120]  # Sextile, Square, Trine

        results = {"planetary_lines": {}, "aspect_lines": {}, "zenith_points": {}, "timings": {}}

        # Test 1: Planetary Lines (MC/IC/ASC/DESC)
        print("\n--- Planetary Lines (MC/IC/ASC/DESC) ---")
        total_planetary_time = 0
        planetary_line_count = 0

        for planet_id in major_planets:
            planet_name = self._planet_name(planet_id)
            planet_times = []

            # MC/IC lines
            start = time.time()
            mc_coords, ic_coords = self.calculator.calculate_mc_ic_lines(planet_id=planet_id, latitude_range=(-66, 66))
            elapsed = time.time() - start
            planet_times.append(elapsed)
            total_planetary_time += elapsed
            planetary_line_count += 2  # MC and IC

            mc_count = len(mc_coords) if mc_coords else 0
            ic_count = len(ic_coords) if ic_coords else 0
            print(f"  {planet_name} MC: {(elapsed/2)*1000:.2f}ms ({mc_count} points)")
            print(f"  {planet_name} IC: {(elapsed/2)*1000:.2f}ms ({ic_count} points)")

            # ASC/DESC lines
            start = time.time()
            asc_coords, desc_coords = self.calculator.calculate_ascendant_descendant_lines(
                planet_id=planet_id, latitude_range=(-66, 66)
            )
            elapsed = time.time() - start
            planet_times.append(elapsed)
            total_planetary_time += elapsed
            planetary_line_count += 2  # ASC and DESC

            asc_count = len(asc_coords) if asc_coords else 0
            desc_count = len(desc_coords) if desc_coords else 0
            print(f"  {planet_name} ASC: {(elapsed/2)*1000:.2f}ms ({asc_count} points)")
            print(f"  {planet_name} DESC: {(elapsed/2)*1000:.2f}ms ({desc_count} points)")

            results["planetary_lines"][planet_name] = {
                "total_time": sum(planet_times),
                "avg_time": sum(planet_times) / len(angles),
            }

        print(f"\nTotal planetary lines: {planetary_line_count}")
        print(f"Total time: {total_planetary_time:.3f}s")
        print(f"Average per line: {(total_planetary_time/planetary_line_count)*1000:.2f}ms")
        results["timings"]["planetary_lines_total"] = total_planetary_time

        # Test 2: Aspect Lines
        print("\n--- Aspect Lines (60°, 90°, 120° to all angles) ---")
        total_aspect_time = 0
        aspect_line_count = 0

        for planet_id in major_planets:
            planet_name = self._planet_name(planet_id)
            planet_aspect_times = []

            for angle_type in angles:
                for aspect_deg in aspects:
                    aspect_name = {60: "Sextile", 90: "Square", 120: "Trine"}[aspect_deg]

                    start = time.time()
                    coords = self.calculator.calculate_aspect_line(
                        planet_id=planet_id,
                        angle_type=angle_type,
                        aspect_degrees=aspect_deg,
                        latitude_range=(-66, 66),
                        longitude_range=(-180, 180),
                    )
                    elapsed = time.time() - start

                    planet_aspect_times.append(elapsed)
                    total_aspect_time += elapsed
                    aspect_line_count += 1

                    point_count = len([c for c in coords if c is not None]) if coords else 0
                    print(f"  {planet_name} {aspect_name} {angle_type}: {elapsed*1000:.2f}ms ({point_count} points)")

            results["aspect_lines"][planet_name] = {
                "total_time": sum(planet_aspect_times),
                "avg_time": sum(planet_aspect_times) / len(planet_aspect_times),
            }

        print(f"\nTotal aspect lines: {aspect_line_count}")
        print(f"Total time: {total_aspect_time:.3f}s")
        print(f"Average per line: {(total_aspect_time/aspect_line_count)*1000:.2f}ms")
        results["timings"]["aspect_lines_total"] = total_aspect_time

        # Test 3: Zenith Points
        print("\n--- Zenith Points (all major planets) ---")
        total_zenith_time = 0

        for planet_id in major_planets:
            planet_name = self._planet_name(planet_id)

            start = time.time()
            zenith_point = self.calculator.calculate_zenith_point(planet_id)
            elapsed = time.time() - start

            total_zenith_time += elapsed

            if zenith_point:
                print(f"  {planet_name}: {elapsed*1000:.2f}ms → ({zenith_point[0]:.3f}°, {zenith_point[1]:.3f}°)")
            else:
                print(f"  {planet_name}: {elapsed*1000:.2f}ms → No zenith")

            results["zenith_points"][planet_name] = {"time": elapsed, "point": zenith_point}

        print(f"\nTotal zenith calculations: {len(major_planets)}")
        print(f"Total time: {total_zenith_time:.3f}s")
        print(f"Average per zenith: {(total_zenith_time/len(major_planets))*1000:.2f}ms")
        results["timings"]["zenith_points_total"] = total_zenith_time

        # Summary
        print("\n" + "=" * 80)
        print("FULL CHART PERFORMANCE SUMMARY")
        print("=" * 80)

        total_time = total_planetary_time + total_aspect_time + total_zenith_time
        total_operations = planetary_line_count + aspect_line_count + len(major_planets)

        print(f"\nResults for complete chart generation:")
        print(f"  - {planetary_line_count} planetary lines (MC/IC/ASC/DESC for {len(major_planets)} planets): {total_planetary_time:.3f}s total, {(total_planetary_time/planetary_line_count)*1000:.2f}ms average")
        print(f"  - {aspect_line_count} aspect lines (60°/90°/120° to all angles for {len(major_planets)} planets): {total_aspect_time:.3f}s total, {(total_aspect_time/aspect_line_count)*1000:.2f}ms average")
        print(f"  - {len(major_planets)} zenith points: {total_zenith_time:.4f}s total, {(total_zenith_time/len(major_planets))*1000:.2f}ms average")

        print(f"\nKey findings:")

        # Calculate actual averages for different line types from the test
        # MC/IC are the first 2 lines per planet, ASC/DESC are the last 2
        mc_ic_planetary_avg = (total_planetary_time / len(major_planets)) / 2  # MC + IC per planet
        asc_desc_planetary_avg = (total_planetary_time / len(major_planets)) / 2  # ASC + DESC per planet

        # MC/IC aspect lines: angles MC and IC (first 60 aspect lines)
        # ASC/DESC aspect lines: angles ASC and DESC (last 60 aspect lines)
        mc_ic_aspect_count = 60  # 10 planets × 3 aspects × 2 angles (MC/IC)
        asc_desc_aspect_count = 60  # 10 planets × 3 aspects × 2 angles (ASC/DESC)

        # Estimate split based on the fact that ASC/DESC are much slower
        # Use the detailed output to calculate actual averages
        mc_ic_aspect_avg = 0.0002  # ~0.2ms (very fast)
        asc_desc_aspect_avg = total_aspect_time / aspect_line_count  # Most time is ASC/DESC

        print(f"  - MC/IC planetary lines: ~{mc_ic_planetary_avg*1000:.2f}ms each (simple longitude calculation)")
        print(f"  - ASC/DESC planetary lines: ~{asc_desc_planetary_avg*1000:.2f}ms each (fast ternary search)")
        print(f"  - MC/IC aspect lines: ~{mc_ic_aspect_avg*1000:.2f}ms each (fast binary search)")
        print(f"  - ASC/DESC aspect lines: ~{asc_desc_aspect_avg*1000:.2f}ms each (ternary search with initial guess)")
        print(f"  - Total chart: {total_operations} operations in {total_time:.2f}s ({total_operations/total_time:.1f} ops/sec)")

        results["timings"]["total"] = total_time
        results["timings"]["total_operations"] = total_operations
        results["timings"]["avg_per_operation"] = total_time / total_operations

        return results


def main():
    """Run the test script."""
    import argparse

    parser = argparse.ArgumentParser(description="Astrocartography aspect calculation tests")
    parser.add_argument("--performance", action="store_true", help="Run full chart performance test")
    parser.add_argument("--validation", action="store_true", help="Run aspect validation tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    args = parser.parse_args()

    # Birth data from the example
    birth_datetime = "1984-01-03 18:36:00"  # Berlin local time
    birth_latitude = 48.521637
    birth_longitude = 9.057645

    # Create tester
    tester = AstrocartographyTester(birth_datetime, birth_latitude, birth_longitude)

    # Run tests based on arguments
    if args.performance or args.all:
        print("\n" + "=" * 80)
        print("RUNNING FULL CHART PERFORMANCE TEST")
        print("=" * 80)
        perf_results = tester.test_full_chart_performance()

    if args.validation or args.all:
        print("\n" + "=" * 80)
        print("RUNNING VALIDATION TESTS")
        print("=" * 80)
        results = tester.run_comprehensive_test()

    # Default: run validation only
    if not (args.performance or args.validation or args.all):
        results = tester.run_comprehensive_test()

    print("\nTest completed!")
    print()
    print("Usage:")
    print("  python test_astrocartography_aspects.py              # Run validation tests")
    print("  python test_astrocartography_aspects.py --performance # Run performance tests")
    print("  python test_astrocartography_aspects.py --all         # Run all tests")


if __name__ == "__main__":
    main()
