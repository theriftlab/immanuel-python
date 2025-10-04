#!/usr/bin/env python3
"""
Astrocartography Aspect Verification

This script tests coordinates by creating actual astrological charts
and checking what aspects exist between Sun and MC.
"""

from datetime import datetime
from immanuel.charts import Subject, Natal
from immanuel.const import chart


def create_chart_at_location(longitude, latitude=45.0):
    """Create a chart at the specified location for the birth time."""

    birth_time = "1984-01-03 18:36:00"

    subject = Subject(
        date_time=birth_time,
        latitude=str(latitude),
        longitude=str(longitude),
        timezone="Europe/Berlin"
    )

    chart_obj = Natal(subject)
    return chart_obj


def get_sun_mc_aspect(chart_obj):
    """Get the aspect between Sun and MC from a chart."""

    sun = chart_obj.objects.get(chart.SUN)
    mc = chart_obj.objects.get(chart.MC)

    if not sun or not mc:
        return None, None, None

    sun_longitude = float(sun.longitude.raw)
    mc_longitude = float(mc.longitude.raw)

    # Calculate aspect
    aspect = abs((sun_longitude - mc_longitude + 180.0) % 360.0 - 180.0)

    return sun_longitude, mc_longitude, aspect


def test_coordinates():
    """Test specific coordinates for Sun Square MC."""

    print("ASTROCARTOGRAPHY ASPECT VERIFICATION")
    print("=" * 60)
    print("Birth: 1984-01-03 18:36:00 Europe/Berlin")
    print("Testing for Sun Square MC (should be ~90°)")
    print()

    # Test coordinates
    coordinates_to_test = [
        # My calculated coordinates
        (-7.5, "My calculation 1"),
        (172.0, "My calculation 2"),

        # Expected coordinates provided by user
        (5.233, "User expected 1"),
        (-174.75, "User expected 2"),

        # Additional test points
        (0.0, "Greenwich"),
        (-82.915, "Sun zenith (conjunction)")
    ]

    print("RESULTS:")
    print("-" * 60)

    for longitude, description in coordinates_to_test:
        try:
            chart_obj = create_chart_at_location(longitude)
            sun_lon, mc_lon, aspect = get_sun_mc_aspect(chart_obj)

            if aspect is not None:
                error_from_90 = abs(aspect - 90.0)
                is_square = error_from_90 <= 1.0
                status = "✓ SQUARE" if is_square else "✗ Not square"

                print(f"{description:20} {longitude:8.3f}°:")
                print(f"  Sun: {sun_lon:7.3f}°  MC: {mc_lon:7.3f}°")
                print(f"  Aspect: {aspect:6.3f}° (error from 90°: {error_from_90:5.3f}°) {status}")
            else:
                print(f"{description:20} {longitude:8.3f}°: ERROR - Could not get Sun/MC")

        except Exception as e:
            print(f"{description:20} {longitude:8.3f}°: ERROR - {e}")

        print()

    print("\nTesting other aspects with my calculated coordinates:")
    print("-" * 60)

    # Test my calculated coordinates for different aspects
    aspect_tests = [
        (60, "Sextile", [-157.5, -37.5]),
        (90, "Square", [-7.5, 172.0]),
        (120, "Trine", [22.5, 142.5])
    ]

    for target_aspect, aspect_name, coordinates in aspect_tests:
        print(f"{aspect_name} ({target_aspect}°):")

        for coord in coordinates:
            try:
                chart_obj = create_chart_at_location(coord)
                sun_lon, mc_lon, aspect = get_sun_mc_aspect(chart_obj)

                if aspect is not None:
                    error = abs(aspect - target_aspect)
                    is_correct = error <= 1.0
                    status = "✓" if is_correct else "✗"

                    print(f"  {coord:7.1f}°: {aspect:6.3f}° (error: {error:5.3f}°) {status}")

            except Exception as e:
                print(f"  {coord:7.1f}°: ERROR - {e}")

        print()

    print("CONCLUSION:")
    print("=" * 60)
    print("Coordinates that produce aspects within 1° of the target are CORRECT.")
    print("Coordinates with larger errors are INCORRECT for that aspect.")


if __name__ == "__main__":
    test_coordinates()