#!/usr/bin/env python3
"""
Test ASC/DESC aspect lines visualization - Sun only
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime

from immanuel.charts import Subject, AstrocartographyChart
from immanuel.const import chart
from immanuel.tools.astrocartography import AstrocartographyCalculator
import swisseph as swe


def main():
    print("\n=== ASC/DESC Aspect Lines Test ===\n")

    # Birth data
    birth_datetime = "1984-01-03 18:36:00"
    birth_latitude = "48.521637"
    birth_longitude = "9.057645"

    print(f"Birth: {birth_datetime}")
    print(f"Location: {birth_latitude}°N, {birth_longitude}°E\n")

    # Create chart
    subject = Subject(
        date_time=birth_datetime,
        latitude=birth_latitude,
        longitude=birth_longitude,
        timezone="Europe/Berlin"
    )
    astro_chart = AstrocartographyChart(subject)

    # Create calculator
    dt = datetime.strptime(birth_datetime, "%Y-%m-%d %H:%M:%S")
    dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                   dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
    calculator = AstrocartographyCalculator(julian_date=jd, sampling_resolution=2.0)

    # Setup plot
    fig = plt.figure(figsize=(20, 12))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, color="lightgray", alpha=0.8)
    ax.add_feature(cfeature.OCEAN, color="lightblue", alpha=0.6)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color="black")
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color="gray", alpha=0.7)

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, color="gray")
    gl.top_labels = False
    gl.right_labels = False
    ax.set_global()

    # Aspect configurations
    aspects = [
        (60, "Sextile", "--", "#00FF00"),
        (90, "Square", "-", "#FF0000"),
        (120, "Trine", ":", "#0000FF"),
    ]

    print("Calculating Sun ASC/DESC aspect lines...\n")

    # Calculate and plot
    for aspect_deg, aspect_name, line_style, color in aspects:
        for angle_type in ['ASC', 'DESC']:
            print(f"  {aspect_name} {angle_type} ({aspect_deg}°)...", end=" ")

            coords = calculator.calculate_aspect_line(
                planet_id=chart.SUN,
                angle_type=angle_type,
                aspect_degrees=aspect_deg,
                latitude_range=(-66, 66),
                longitude_range=(-180, 180)
            )

            if coords:
                # Extract lons/lats (None values break the line automatically)
                lons = []
                lats = []
                for coord in coords:
                    if coord is None:
                        lons.append(None)
                        lats.append(None)
                    else:
                        lons.append(coord[0])
                        lats.append(coord[1])

                ax.plot(
                    lons, lats,
                    color=color,
                    linewidth=2.5,
                    linestyle=line_style,
                    label=f"Sun {aspect_name} {angle_type}",
                    transform=ccrs.PlateCarree(),
                    alpha=0.8
                )

                # Count actual points (excluding None separators)
                actual_points = sum(1 for c in coords if c is not None)
                print(f"✓ {actual_points} points")
            else:
                print("✗ No coordinates")

    # Birth location
    ax.plot(
        float(birth_longitude), float(birth_latitude),
        marker="*", markersize=20, color="gold",
        markeredgecolor="black", markeredgewidth=2,
        transform=ccrs.PlateCarree(),
        label="Birth Location", zorder=10
    )

    ax.legend(loc="upper left", fontsize=11, framealpha=0.9)
    plt.title("Sun ASC/DESC Aspect Lines - Curved (Fast Method)", fontsize=16, weight="bold", pad=20)

    plt.savefig("asc_desc_test.png", dpi=150, bbox_inches="tight")
    print(f"\n✓ Saved: asc_desc_test.png")

    plt.close()


if __name__ == "__main__":
    main()
