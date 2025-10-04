#!/usr/bin/env python3
"""
Fuzzing test for astrocartography calculations.

Generates 500 random charts with random dates, times, and locations,
then calculates planetary lines, aspect lines, and parans while collecting
performance statistics. Tests system reliability and performance under
varied conditions.

Usage:
    python profiling/fuzz_test_astrocartography.py
    python profiling/fuzz_test_astrocartography.py --charts 1000  # Custom chart count
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

from immanuel.const import chart
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.tools import date


def generate_random_datetime() -> datetime:
    """Generate a random datetime between 1900 and 2100."""
    start_date = datetime(1900, 1, 1)
    end_date = datetime(2100, 12, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)

    random_date = start_date + timedelta(days=random_number_of_days)

    # Add random time
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)


def generate_random_location() -> Tuple[float, float]:
    """Generate random latitude and longitude."""
    # Latitude: -60 to +60 (avoid extreme polar regions)
    latitude = random.uniform(-60.0, 60.0)
    # Longitude: -180 to +180
    longitude = random.uniform(-180.0, 180.0)
    return latitude, longitude


def run_fuzz_test(num_charts: int = 500):
    """
    Run fuzzing test with random charts.

    Args:
        num_charts: Number of random charts to generate and test
    """
    print(f"{'=' * 80}")
    print(f"Astrocartography Fuzzing Test - {num_charts} Random Charts")
    print(f"{'=' * 80}\n")

    # Statistics tracking
    stats = {
        'total_time': 0.0,
        'line_calc_times': [],
        'aspect_calc_times': [],
        'paran_calc_times': [],
        'line_counts': [],
        'aspect_line_counts': [],
        'paran_counts': [],
        'charts_processed': 0,
        'charts_failed': 0,
    }

    # All planets
    all_planets = [
        chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
        chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO
    ]

    start_total = time.time()

    for i in range(num_charts):
        try:
            # Generate random chart
            birth_dt = generate_random_datetime()
            birth_lat, birth_lon = generate_random_location()

            # Convert to Julian date
            jd = date.to_jd(birth_dt)

            if (i + 1) % 50 == 0:
                print(f"Processing chart {i + 1}/{num_charts}...")

            # Create calculator
            calculator = AstrocartographyCalculator(
                julian_date=jd,
                sampling_resolution=2.0  # Coarser for speed
            )

            # Test 1: Calculate planetary lines
            start = time.time()
            planetary_lines = calculator.generate_all_planetary_lines(
                latitude_range=(-60, 60)
            )
            line_time = time.time() - start
            stats['line_calc_times'].append(line_time)

            # Count lines (number of actual lines, not coordinate points)
            total_lines = len(planetary_lines)  # Should be 52 (13 planets × 4 angles)
            stats['line_counts'].append(total_lines)

            # Test 2: Calculate aspect lines (for a few planets/aspects for speed)
            start = time.time()
            aspect_line_count = 0
            for planet_id in [chart.SUN, chart.MOON]:
                for angle_type in ['MC', 'ASC']:
                    for aspect in [60, 90, 120]:
                        line = calculator.calculate_aspect_line(
                            planet_id=planet_id,
                            angle_type=angle_type,
                            aspect_degrees=aspect
                        )
                        if line:  # Count non-empty lines
                            aspect_line_count += 1
            aspect_time = time.time() - start
            stats['aspect_calc_times'].append(aspect_time)
            stats['aspect_line_counts'].append(aspect_line_count)

            # Test 3: Calculate parans
            start = time.time()
            parans = calculator.calculate_all_parans_from_lines(
                planetary_lines=planetary_lines,
                exclude_node_pairs=True
            )
            paran_time = time.time() - start
            stats['paran_calc_times'].append(paran_time)

            # Count parans (parans is a list of tuples)
            stats['paran_counts'].append(len(parans))

            stats['charts_processed'] += 1

        except Exception as e:
            print(f"  ⚠️  Chart {i + 1} failed: {e}")
            stats['charts_failed'] += 1
            continue

    stats['total_time'] = time.time() - start_total

    # Print results
    print(f"\n{'=' * 80}")
    print("Fuzzing Test Results")
    print(f"{'=' * 80}\n")

    print(f"Charts processed: {stats['charts_processed']}/{num_charts}")
    print(f"Charts failed: {stats['charts_failed']}")
    print(f"Success rate: {stats['charts_processed']/num_charts*100:.1f}%\n")

    # Performance statistics
    print("=" * 80)
    print("PERFORMANCE STATISTICS")
    print("=" * 80)
    print(f"\nTotal execution time: {stats['total_time']:.2f}s")
    print(f"Average time per chart: {stats['total_time']/num_charts:.3f}s")

    if stats['line_calc_times']:
        print(f"\nPlanetary Line Calculation:")
        print(f"  Mean:   {statistics.mean(stats['line_calc_times'])*1000:.1f}ms")
        print(f"  Median: {statistics.median(stats['line_calc_times'])*1000:.1f}ms")
        print(f"  Min:    {min(stats['line_calc_times'])*1000:.1f}ms")
        print(f"  Max:    {max(stats['line_calc_times'])*1000:.1f}ms")
        print(f"  Stddev: {statistics.stdev(stats['line_calc_times'])*1000:.1f}ms")

    if stats['aspect_calc_times']:
        print(f"\nAspect Line Calculation (2 planets × 2 angles × 3 aspects = 12 lines):")
        print(f"  Mean:   {statistics.mean(stats['aspect_calc_times'])*1000:.1f}ms")
        print(f"  Median: {statistics.median(stats['aspect_calc_times'])*1000:.1f}ms")
        print(f"  Min:    {min(stats['aspect_calc_times'])*1000:.1f}ms")
        print(f"  Max:    {max(stats['aspect_calc_times'])*1000:.1f}ms")
        print(f"  Stddev: {statistics.stdev(stats['aspect_calc_times'])*1000:.1f}ms")

    if stats['paran_calc_times']:
        print(f"\nParan Calculation:")
        print(f"  Mean:   {statistics.mean(stats['paran_calc_times'])*1000:.1f}ms")
        print(f"  Median: {statistics.median(stats['paran_calc_times'])*1000:.1f}ms")
        print(f"  Min:    {min(stats['paran_calc_times'])*1000:.1f}ms")
        print(f"  Max:    {max(stats['paran_calc_times'])*1000:.1f}ms")
        print(f"  Stddev: {statistics.stdev(stats['paran_calc_times'])*1000:.1f}ms")

    # Line count statistics
    print("\n" + "=" * 80)
    print("LINE COUNT STATISTICS")
    print("=" * 80)

    if stats['line_counts']:
        print(f"\nPlanetary Lines per Chart (13 planets × 4 angles):")
        print(f"  Mean:   {statistics.mean(stats['line_counts']):.1f}")
        print(f"  Median: {statistics.median(stats['line_counts']):.1f}")
        print(f"  Min:    {min(stats['line_counts'])}")
        print(f"  Max:    {max(stats['line_counts'])}")

    if stats['aspect_line_counts']:
        print(f"\nAspect Lines Calculated per Chart (2 planets × 2 angles × 3 aspects):")
        print(f"  Mean:   {statistics.mean(stats['aspect_line_counts']):.1f}")
        print(f"  Median: {statistics.median(stats['aspect_line_counts']):.1f}")
        print(f"  Min:    {min(stats['aspect_line_counts'])}")
        print(f"  Max:    {max(stats['aspect_line_counts'])}")

    if stats['paran_counts']:
        print(f"\nParan Combinations Found per Chart:")
        print(f"  Mean:   {statistics.mean(stats['paran_counts']):.1f}")
        print(f"  Median: {statistics.median(stats['paran_counts']):.1f}")
        print(f"  Min:    {min(stats['paran_counts'])}")
        print(f"  Max:    {max(stats['paran_counts'])}")

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

    # Summary recommendations
    print("\n📊 Summary:")
    if stats['charts_processed'] == num_charts:
        print("  ✅ All charts processed successfully")
    else:
        print(f"  ⚠️  {stats['charts_failed']} charts failed")

    if stats['line_calc_times']:
        avg_time = statistics.mean(stats['line_calc_times']) * 1000
        if avg_time < 100:
            print(f"  ✅ Line generation performance excellent (avg {avg_time:.0f}ms)")
        elif avg_time < 500:
            print(f"  ⚠️  Line generation performance acceptable (avg {avg_time:.0f}ms)")
        else:
            print(f"  ❌ Line generation needs optimization (avg {avg_time:.0f}ms)")

    if stats['paran_calc_times']:
        avg_paran_time = statistics.mean(stats['paran_calc_times']) * 1000
        if avg_paran_time < 50:
            print(f"  ✅ Paran calculation performance excellent (avg {avg_paran_time:.0f}ms)")
        elif avg_paran_time < 200:
            print(f"  ⚠️  Paran calculation performance acceptable (avg {avg_paran_time:.0f}ms)")
        else:
            print(f"  ❌ Paran calculation needs optimization (avg {avg_paran_time:.0f}ms)")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fuzz test astrocartography calculations')
    parser.add_argument('--charts', type=int, default=500,
                       help='Number of random charts to generate (default: 500)')
    args = parser.parse_args()

    run_fuzz_test(num_charts=args.charts)
