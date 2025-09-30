#!/usr/bin/env python3
"""
 Astrocartography World Map Visualization

This example demonstrates correct astrocartography line plotting on a real world map:
- MC lines: Vertical meridian lines where planet is on the Midheaven
- IC lines: Vertical meridian lines where planet is on the Imum Coeli (opposite MC)
- ASC lines: Curved horizon lines where planet is rising
- DESC lines: Curved horizon lines where planet is setting

Uses cartopy for  geographic projection and real coastlines.
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
import math

# Import Immanuel astrocartography components
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.const import chart, astrocartography
import swisseph as swe


def plot_astrocartography_worldmap(astro_chart, projection="PlateCarree", save_as=None, show_zenith=True, title=None):
    """
    Plot  astrocartography world map with real geographic features.

    Args:
        astro_chart: AstrocartographyChart object with calculated lines
        projection: Cartopy projection name
        save_as: Filename to save plot
        show_zenith: Whether to show zenith points
        title: Custom plot title
    """
    if title is None:
        title = f"Astrocartography Map - {astro_chart.subject.date_time}"

    # Create figure with cartopy projection
    if projection == "PlateCarree":
        proj = ccrs.PlateCarree()
    elif projection == "Robinson":
        proj = ccrs.Robinson()
    elif projection == "Mollweide":
        proj = ccrs.Mollweide()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(20, 12))
    ax = plt.axes(projection=proj)

    # Add geographic features
    ax.add_feature(cfeature.LAND, color="lightgray", alpha=0.8)
    ax.add_feature(cfeature.OCEAN, color="lightblue", alpha=0.6)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color="black")
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color="gray", alpha=0.7)
    ax.add_feature(cfeature.RIVERS, linewidth=0.5, color="blue", alpha=0.6)
    ax.add_feature(cfeature.LAKES, color="lightblue", alpha=0.6)

    # Add gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, color="gray")
    gl.top_labels = False
    gl.right_labels = False

    # Set global extent to show the whole world
    ax.set_global()

    # Planet colors and names
    planet_colors = {
        chart.SUN: "#FFD700",  # Gold
        chart.MOON: "#C0C0C0",  # Silver
        chart.MERCURY: "#FFA500",  # Orange
        chart.VENUS: "#FF69B4",  # Hot Pink
        chart.MARS: "#FF4500",  # Red Orange
        chart.JUPITER: "#4169E1",  # Royal Blue
        chart.SATURN: "#8B4513",  # Saddle Brown
        chart.URANUS: "#00CED1",  # Dark Turquoise
        chart.NEPTUNE: "#0000FF",  # Blue
        chart.PLUTO: "#800080",  # Purple
    }

    planet_names = {
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

    # Plot astrocartography lines for each planet
    for planet_id, planetary_lines in astro_chart.planetary_lines.items():
        if planet_id not in planet_colors:
            continue

        color = planet_colors[planet_id]
        name = planet_names[planet_id]

        print(f"Plotting {name} lines...")

        try:
            # Plot each line type with  styling
            for line_type, line_data in planetary_lines.items():
                if "coordinates" not in line_data or not line_data["coordinates"]:
                    continue

                coordinates = line_data["coordinates"]
                lons = [coord[0] for coord in coordinates]
                lats = [coord[1] for coord in coordinates]

                # Different line styles for different types
                if line_type == "MC":
                    linestyle = "-"
                    linewidth = 2.5
                elif line_type == "IC":
                    linestyle = "--"
                    linewidth = 2.5
                elif line_type == "ASC":
                    linestyle = ":"
                    linewidth = 2
                elif line_type == "DESC":
                    linestyle = "-."
                    linewidth = 2
                else:
                    linestyle = "-"
                    linewidth = 1.5

                ax.plot(
                    lons,
                    lats,
                    color=color,
                    linewidth=linewidth,
                    linestyle=linestyle,
                    label=f"{name} {line_type}",
                    transform=ccrs.PlateCarree(),
                )

        except Exception as e:
            print(f"Error plotting {name} lines: {e}")
            continue

    # Add birth location
    birth_lon = float(astro_chart.subject.longitude)
    birth_lat = float(astro_chart.subject.latitude)
    ax.plot(
        birth_lon,
        birth_lat,
        marker="*",
        markersize=15,
        color="red",
        transform=ccrs.PlateCarree(),
        label="Birth Location",
        markeredgecolor="black",
    )

    # Add zenith points if requested
    if show_zenith:
        print("Plotting zenith points...")
        try:
            zenith_points = astro_chart.zenith_points

            for planet_id, zenith in zenith_points.items():
                if planet_id in planet_colors and isinstance(zenith, dict):
                    color = planet_colors[planet_id]
                    name = planet_names[planet_id]
                    zenith_lon = zenith["longitude"]
                    zenith_lat = zenith["latitude"]

                    ax.plot(
                        zenith_lon,
                        zenith_lat,
                        marker="o",
                        markersize=8,
                        color=color,
                        transform=ccrs.PlateCarree(),
                        markeredgecolor="black",
                        markeredgewidth=1,
                    )

                    # Add label
                    ax.text(
                        zenith_lon + 2,
                        zenith_lat + 2,
                        f"{name} Zenith",
                        fontsize=8,
                        color=color,
                        weight="bold",
                        transform=ccrs.PlateCarree(),
                    )

        except Exception as e:
            print(f"Error plotting zenith points: {e}")

    # Add legend
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=10)

    # Add title and info
    plt.title(title, fontsize=16, weight="bold", pad=20)

    # Add info text
    info_text = f"""
Birth Data: {astro_chart.subject.date_time}
Location: {astro_chart.subject.latitude}°, {astro_chart.subject.longitude}°

Line Types:
━━━ MC (Midheaven) - Planet at highest point
┅┅┅ IC (Imum Coeli) - Planet at lowest point
··· ASC (Ascendant) - Planet rising
─·─ DESC (Descendant) - Planet setting
"""

    plt.figtext(
        0.02,
        0.15,
        info_text,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"Map saved as: {save_as}")

    plt.show()

    return fig, ax


def main():
    """Demo the  astrocartography world map."""
    print("===  Astrocartography World Map Demo ===\n")

    # Example birth data
    subject = Subject(
        date_time="1984-01-03 18:36:00",
        latitude="48.521637",
        longitude="9.057645",
        timezone="Europe/Berlin",
    )

    # SUN Zenith should be at 82w40', 22s50 for this chart
    # MOON Zenith should be at 76w00', 25s00' for this chart

    print(f"Birth Data:")
    print(f"Date/Time: {subject.date_time}")
    print(f"Location: {subject.latitude}°N, {abs(float(subject.longitude))}°W")
    print()

    # Create  astrocartography map
    print("Creating astrocartography world map with astronomical calculations...")
    print("This may take a moment to calculate all planetary lines...\n")

    # Create astrocartography chart using the corrected calculator
    print("Creating astrocartography chart with corrected calculations...")
    from immanuel.charts import AstrocartographyChart

    astro_chart = AstrocartographyChart(
        subject=subject,
        planets=[chart.SUN, chart.MOON, chart.VENUS, chart.MARS, chart.JUPITER],
        sampling_resolution=1.0,
    )

    print(f"Chart created successfully!")
    print(
        f"Sun zenith: {astro_chart.zenith_points[chart.SUN]['longitude']:.3f}°, {astro_chart.zenith_points[chart.SUN]['latitude']:.3f}°"
    )
    print(
        f"Moon zenith: {astro_chart.zenith_points[chart.MOON]['longitude']:.3f}°, {astro_chart.zenith_points[chart.MOON]['latitude']:.3f}°"
    )
    print()

    try:
        fig, ax = plot_astrocartography_worldmap(
            astro_chart=astro_chart,
            projection="PlateCarree",  # Try 'Robinson' or 'Mollweide' for other projections
            save_as="astrocartography_worldmap.png",
            show_zenith=True,
            title="Astrocartography World Map - Real Geographic Projection",
        )

        print("\n=== World Map Created Successfully! ===")
        print("Features:")
        print("✓ Real world coastlines and geographic features")
        print("✓  MC/IC vertical meridian lines")
        print("✓ Curved ASC/DESC horizon lines")
        print("✓ Zenith points (where planets are directly overhead)")
        print("✓ Birth location marked")
        print("✓ Professional cartographic projection")

    except Exception as e:
        print(f"Error creating map: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
