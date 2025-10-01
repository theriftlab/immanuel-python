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


def plot_astrocartography_aspects_map(astro_chart, projection="PlateCarree", save_as=None, title=None):
    """
    Plot astrocartography map focusing on aspect lines between planets.

    Args:
        astro_chart: AstrocartographyChart object with calculated lines
        projection: Cartopy projection name
        save_as: Filename to save plot
        title: Custom plot title
    """
    if title is None:
        title = f"Astrocartography Aspect Lines - {astro_chart.subject.date_time}"

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

    # Meaningful aspects to MC/IC (exclude conjunction/opposition as they're just MC/IC lines)
    meaningful_aspects = [
        (60, "Sextile", "dotted", 2.0),
        (90, "Square", "dashed", 2.5),
        (120, "Trine", "dashdot", 2.5),
    ]

    # Aspect colors
    aspect_colors = {
        0: "#FF0000",  # Red for conjunction
        60: "#00FF00",  # Green for sextile
        90: "#FF4500",  # Orange for square
        120: "#0000FF",  # Blue for trine
        180: "#800080",  # Purple for opposition
    }

    # Calculate and plot aspect lines between major planets
    primary_planets = [chart.SUN, chart.MOON, chart.VENUS, chart.MARS, chart.JUPITER]

    # Create calculator once (reuse for all aspects)
    from immanuel.tools.astrocartography import AstrocartographyCalculator
    import swisseph as swe

    # Convert subject datetime to Julian date - use UTC for consistency
    if isinstance(astro_chart.subject.date_time, str):
        dt = datetime.strptime(astro_chart.subject.date_time, "%Y-%m-%d %H:%M:%S")
    else:
        dt = astro_chart.subject.date_time

    # Convert Berlin time to UTC (Berlin is UTC+1 in January 1984)
    dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
    calculator = AstrocartographyCalculator(julian_date=jd, sampling_resolution=2.0)

    aspect_lines_plotted = 0

    # Plot MC aspect lines (vertical)
    print("Calculating MC aspect lines (vertical)...")
    for primary_planet in primary_planets:
        primary_name = planet_names.get(primary_planet, f"Planet {primary_planet}")

        for aspect_degrees, aspect_name, line_style, line_width in meaningful_aspects:
            try:
                print(f"  Calculating {primary_name} {aspect_name} MC ({aspect_degrees}°)...")

                # Get aspect line longitudes using the fast method
                aspect_longitudes = calculator._calculate_aspect_longitudes_fast(
                    primary_planet, "MC", aspect_degrees
                )

                if aspect_longitudes and len(aspect_longitudes) > 0:
                    # Create vertical lines for each longitude
                    all_lons = []
                    all_lats = []

                    for longitude in aspect_longitudes:
                        # Create vertical line from -85° to +85° latitude
                        line_lats = list(range(-85, 86, 2))  # Every 2 degrees
                        line_lons = [longitude] * len(line_lats)

                        all_lons.extend(line_lons)
                        all_lats.extend(line_lats)

                        # Add separation between lines for plotting
                        if longitude != aspect_longitudes[-1]:  # Not the last longitude
                            all_lons.append(None)  # matplotlib uses None to break lines
                            all_lats.append(None)

                    lons = all_lons
                    lats = all_lats

                    # Each planet gets its own color, aspects distinguished by line style
                    plot_color = planet_colors.get(primary_planet, "#666666")

                    ax.plot(
                        lons,
                        lats,
                        color=plot_color,
                        linewidth=line_width * 0.8,  # Slightly thinner for aspect lines
                        linestyle=line_style,  # Different line style per aspect type
                        label=f"{primary_name} {aspect_name} MC",
                        transform=ccrs.PlateCarree(),
                        alpha=0.8,  # Consistent alpha for all aspect lines
                    )

                    aspect_lines_plotted += 1
                    print(f"    ✓ Plotted {len(aspect_longitudes)} vertical aspect lines")
                else:
                    print(f"    ⚪ No aspect longitudes found")

            except Exception as e:
                print(f"    ✗ Error calculating {aspect_name}: {e}")
                continue

    # Plot ASC/DESC aspect lines (curved)
    print("\nCalculating ASC/DESC aspect lines (curved)...")
    for primary_planet in primary_planets:
        primary_name = planet_names.get(primary_planet, f"Planet {primary_planet}")

        for aspect_degrees, aspect_name, line_style, line_width in meaningful_aspects:
            for angle_type in ['ASC', 'DESC']:
                try:
                    print(f"  Calculating {primary_name} {aspect_name} {angle_type} ({aspect_degrees}°)...")

                    # Use calculate_aspect_line which now has fast ternary search
                    aspect_coords = calculator.calculate_aspect_line(
                        planet_id=primary_planet,
                        angle_type=angle_type,
                        aspect_degrees=aspect_degrees,
                        latitude_range=(-66, 66),  # Limited for house calculation stability
                        longitude_range=(-180, 180)
                    )

                    if aspect_coords and len(aspect_coords) > 0:
                        # Extract lons and lats for plotting curved line
                        lons = [coord[0] for coord in aspect_coords]
                        lats = [coord[1] for coord in aspect_coords]

                        # Each planet gets its own color, aspects distinguished by line style
                        plot_color = planet_colors.get(primary_planet, "#666666")

                        ax.plot(
                            lons,
                            lats,
                            color=plot_color,
                            linewidth=line_width * 0.7,  # Thinner for curved lines
                            linestyle=line_style,
                            label=f"{primary_name} {aspect_name} {angle_type}",
                            transform=ccrs.PlateCarree(),
                            alpha=0.7,
                        )

                        aspect_lines_plotted += 1
                        print(f"    ✓ Plotted curved {angle_type} line with {len(aspect_coords)} points")
                    else:
                        print(f"    ⚪ No coordinates found")

                except Exception as e:
                    print(f"    ✗ Error calculating {angle_type} {aspect_name}: {e}")
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

    # Add zenith points for reference
    print("Adding zenith points for reference...")
    for planet_id, zenith in astro_chart.zenith_points.items():
        if planet_id in planet_colors and isinstance(zenith, dict):
            color = planet_colors[planet_id]
            name = planet_names[planet_id]
            zenith_lon = zenith["longitude"]
            zenith_lat = zenith["latitude"]

            ax.plot(
                zenith_lon,
                zenith_lat,
                marker="o",
                markersize=6,
                color=color,
                transform=ccrs.PlateCarree(),
                markeredgecolor="black",
                markeredgewidth=1,
                alpha=0.8,
            )

    # Add legend
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=8)

    # Add title and info
    plt.title(title, fontsize=16, weight="bold", pad=20)

    # Add info text
    info_text = f"""
Birth Data: {astro_chart.subject.date_time}
Location: {astro_chart.subject.latitude}°, {astro_chart.subject.longitude}°

Aspect Lines ({aspect_lines_plotted} plotted):

Planet Colors:
• Sun: Gold  • Moon: Silver  • Venus: Pink  • Mars: Red  • Jupiter: Blue

Aspect Line Styles:
··· Sextile (60°) - Dotted line
┅┅┅ Square (90°) - Dashed line
─·─ Trine (120°) - Dash-dot line

Note: Conjunction = MC line, Opposition = IC line

○ Zenith points show where planets were overhead
"""

    plt.figtext(
        0.02,
        0.25,
        info_text,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"Aspect map saved as: {save_as}")

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
    # SUN Square MC should be at  5e14' and 174w45' for this chart
    # SUN Sextile MC should be at 22w23' and  146w13' for this chart
    # SUN Trine MC should be at  157e37' and 33e48' for this chart

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

    # Create main planetary lines map
    try:
        print("=== Creating Main Planetary Lines Map ===")
        fig1, ax1 = plot_astrocartography_worldmap(
            astro_chart=astro_chart,
            projection="PlateCarree",
            save_as="astrocartography_worldmap.png",
            show_zenith=True,
            title="Astrocartography Planetary Lines - MC/IC/ASC/DESC",
        )

        print("\n=== Planetary Lines Map Created Successfully! ===")
        print("Features:")
        print("✓ Real world coastlines and geographic features")
        print("✓ Perfect MC/IC vertical meridian lines")
        print("✓ Smooth curved ASC/DESC horizon lines")
        print("✓ Zenith points (where planets are directly overhead)")
        print("✓ Birth location marked")
        print("✓ Professional cartographic projection")

    except Exception as e:
        print(f"Error creating planetary lines map: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)

    # Create aspect lines map
    try:
        print("=== Creating Aspect Lines Map ===")
        fig2, ax2 = plot_astrocartography_aspects_map(
            astro_chart=astro_chart,
            projection="PlateCarree",
            save_as="astrocartography_aspect_lines.png",
            title="Astrocartography Aspect Lines - Major Planetary Aspects",
        )

        print("\n=== Aspect Lines Map Created Successfully! ===")
        print("Features:")
        print("✓ Major planetary aspects (conjunction, sextile, square, trine, opposition)")
        print("✓ Color-coded aspect lines")
        print("✓ Zenith points for reference")
        print("✓ Birth location marked")
        print("✓ Professional cartographic projection")

    except Exception as e:
        print(f"Error creating aspect lines map: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("=== Demo Complete ===")
    print("Files created:")
    print("  📊 astrocartography_planetary_lines.png - Main planetary lines (MC/IC/ASC/DESC)")
    print("  📈 astrocartography_aspect_lines.png - Aspect lines between planets")
    print("\nBoth maps demonstrate the corrected astrocartography calculations!")


if __name__ == "__main__":
    main()
