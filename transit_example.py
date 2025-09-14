#!/usr/bin/env python3
"""
Basic usage example of the new transit calculation features in Immanuel.
This demonstrates the key functionality of MundaneTransits, NatalTransits, and TransitSearch.
"""

from datetime import datetime, timedelta
import json

# Import Immanuel classes
from immanuel import charts
from immanuel.const import chart, calc, names
from immanuel.tools.transit_search import TransitSearch
from immanuel.classes.serialize import ToJSON
from immanuel.tools.names import get_object_name


def main():
    print("🌟 Immanuel Transit Calculation Example")
    print("=" * 50)

    # Create a sample natal chart
    native = charts.Subject(
        date_time="1984-01-03 18:35:00",
        latitude="48.521637",
        longitude="9.057645",
        timezone="Europe/Berlin",
    )
    natal_chart = charts.Natal(native)

    print(f"✨ Created natal chart for {native.date_time}")
    longitude_dir = "E" if native.longitude >= 0 else "W"
    print(f"   Location: {native.latitude:.4f}°N, {abs(native.longitude):.4f}°{longitude_dir}")

    # Example 1: Mundane Transits - planetary positions for NYC over a week
    print("\n📍 Example 1: Mundane Transits (NYC, next 7 days)")
    print("-" * 45)

    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)

    mundane_transits = charts.MundaneTransits(
        start_date=start_date,
        end_date=end_date,
        latitude=40.7128,
        longitude=-74.0060,
        interval="daily",  # Calculate positions daily
        timezone="America/New_York",
    )

    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Interval: Daily")
    print(f"Location: New York City")
    print(f"House System: {mundane_transits.house_system}")

    # Example 2: Natal Transits - transits to the natal chart
    print("\n🎯 Example 2: Natal Transits (to birth chart, next 3 months)")
    print("-" * 55)

    natal_transits = charts.NatalTransits(
        natal_chart=natal_chart,
        start_date=start_date,
        end_date=start_date + timedelta(days=30),  # One month for demo
        aspects_to_calculate=[calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE],
        interval=timedelta(hours=12),  # Every 12 hours using timedelta
    )

    print(f"Natal chart: {natal_chart.native.date_time}")
    print(
        f"Transit period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=30)).strftime('%Y-%m-%d')}"
    )
    print(f"Interval: Every 12 hours")
    print(f"Total transit events: {len(natal_transits.transit_events)}")

    # Show what NatalTransits actually provides
    print("NatalTransits provides:")
    print(f"  - {len(natal_transits.transit_events)} planetary position events")
    print(f"  - Transit period data with statistics")

    # Show aspects if available
    if hasattr(natal_transits, "aspects") and natal_transits.aspects:
        print(f"  - {len(natal_transits.aspects)} aspect categories to natal planets")
        print("\nSample natal aspects found:")
        for aspect_obj, aspects_list in list(natal_transits.aspects.items()):
            obj_name = get_object_name(aspect_obj)
            print(f"  • {obj_name}: {len(aspects_list)} aspects")
            # Show first few aspects for this object
            for aspect in aspects_list:
                print(f"    - {get_object_name( aspect)}")

    print(f"\nNote: NatalTransits tracks planetary movements over time.")
    print(f"For specific transit aspects (conjunctions, squares, etc.),")
    print(f"use TransitSearch as shown in Example 3.")

    # Example 3: Transit Search - find specific events
    print("\n🔍 Example 3: Transit Search (find Jupiter aspects)")
    print("-" * 45)

    search = TransitSearch(
        natal_chart=natal_chart,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=12 * 365),  # Next 12 years
        precision="second",
    )

    # Find all Jupiter se to natal Sun
    jupiter_sun_aspects = search.find_aspects(
        transiting_planet=chart.JUPITER,
        natal_planet=chart.JUPITER,
        aspect=calc.SEXTILE,
        max_orb=5.0,  # Within 2 degrees
    )

    print(f"Searching for Jupiter sextiles to natal Sun...")
    print(f"Search period: 12 years from now")
    print(f"Maximum orb: 5.0 degrees")
    print(f"Found {len(jupiter_sun_aspects)} events")

    for event in jupiter_sun_aspects:
        print(f"  • {event.date_time.strftime('%Y-%m-%d %H:%M:%S')} - Orb: {event.orb:.3f}°")

    # Find Mercury stations (retrograde/direct)
    print("\n⭐ Mercury Stations (next year)")
    mercury_stations = search.find_stations(chart.MERCURY)
    print(f"Found {len(mercury_stations)} Mercury stations:")

    for station in mercury_stations:
        station_type = station.metadata.get("station_type", "station")
        print(f"  • {station.date_time.strftime('%Y-%m-%d %H:%M:%S')} - Mercury {station_type}")

    # Find Mars stations (retrograde/direct)
    print("\n⭐ Mars Stations (next year)")
    mars_stations = search.find_stations(chart.MARS)
    print(f"Found {len(mars_stations)} Mars stations:")

    for station in mars_stations:
        station_type = station.metadata.get("station_type", "station")
        print(f"  • {station.date_time.strftime('%Y-%m-%d %H:%M:%S')} - Mars {station_type}")

    # Find sign ingresses for Saturn
    print("\n Saturn Sign Ingresses")
    saturn_ingresses = search.find_sign_ingresses(chart.SATURN)
    print(f"Found {len(saturn_ingresses)} Saturn sign changes:")

    for ingress in saturn_ingresses:
        to_sign = ingress.metadata.get("to_position", "Unknown")
        sign_name = names.SIGNS[to_sign]
        print(f"  • {ingress.date_time.strftime('%Y-%m-%d %H:%M')} - Saturn enters sign {sign_name}")

    # Example 4: JSON serialization of transit objects
    print("\n📋 Example 4: Transit JSON Serialization")
    print("-" * 40)

    print("✅ Creating a small transit example for JSON demo...")

    # Create a short mundane transit example
    mundane_example = charts.MundaneTransits(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=2),
        latitude=40.7128,  # NYC
        longitude=-74.0060,
        interval="daily",
        timezone="America/New_York",
    )

    print("\n🌍 Mundane Transits JSON (first 300 chars):")
    mundane_json = mundane_example.to_json(indent=2)
    print(mundane_json[:300] + "...")

    # Show transit event JSON if we found any
    if jupiter_sun_aspects:
        print(f"\n🪐 Sample Transit Event JSON:")
        event_json = json.dumps(jupiter_sun_aspects[0], cls=ToJSON, indent=2)
        print(event_json[:400] + "..." if len(event_json) > 400 else event_json)

    print("\n🎉 Transit calculation examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
