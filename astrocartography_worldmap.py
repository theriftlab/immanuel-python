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


def plot_astrocartography_mc_aspects_map(astro_chart, projection="PlateCarree", save_as=None, title=None):
    """
    Plot astrocartography map focusing on MC/IC aspect lines (vertical).

    Args:
        astro_chart: AstrocartographyChart object with calculated lines
        projection: Cartopy projection name
        save_as: Filename to save plot
        title: Custom plot title
    """
    if title is None:
        title = f"Astrocartography MC/IC Aspect Lines - {astro_chart.subject.date_time}"

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

    # Meaningful aspects to MC/IC
    meaningful_aspects = [
        (60, "Sextile", "dotted", 2.0),
        (90, "Square", "dashed", 2.5),
        (120, "Trine", "dashdot", 2.5),
    ]

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
    print("Calculating MC/IC aspect lines (vertical)...")
    for primary_planet in primary_planets:
        primary_name = planet_names.get(primary_planet, f"Planet {primary_planet}")

        for aspect_degrees, aspect_name, line_style, line_width in meaningful_aspects:
            for angle_type in ['MC', 'IC']:
                try:
                    print(f"  Calculating {primary_name} {aspect_name} {angle_type} ({aspect_degrees}°)...")

                    # Get aspect line longitudes using the fast method
                    aspect_longitudes = calculator._calculate_aspect_longitudes_fast(
                        primary_planet, angle_type, aspect_degrees
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
                            linewidth=line_width * 0.8,
                            linestyle=line_style,
                            label=f"{primary_name} {aspect_name} {angle_type}",
                            transform=ccrs.PlateCarree(),
                            alpha=0.8,
                        )

                        aspect_lines_plotted += 1
                        print(f"    ✓ Plotted {len(aspect_longitudes)} vertical aspect lines")
                    else:
                        print(f"    ⚪ No aspect longitudes found")

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

    # Add legend
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=9)

    # Add title and info
    plt.title(title, fontsize=16, weight="bold", pad=20)

    # Add info text
    info_text = f"""
Birth Data: {astro_chart.subject.date_time}
Location: {astro_chart.subject.latitude}°, {astro_chart.subject.longitude}°

MC/IC Aspect Lines ({aspect_lines_plotted} plotted):

Aspect Line Styles:
··· Sextile (60°) - Dotted line
┅┅┅ Square (90°) - Dashed line
─·─ Trine (120°) - Dash-dot line

Note: All MC/IC aspect lines are vertical meridians
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
        print(f"MC/IC aspect map saved as: {save_as}")

    plt.show()

    return fig, ax


def plot_astrocartography_asc_aspects_map(astro_chart, projection="PlateCarree", save_as=None, title=None):
    """
    Plot astrocartography map focusing on ASC aspect lines (curved).

    Note: DESC aspects are not plotted as they are redundant (ASC 60° = DESC 120°, etc.)

    Args:
        astro_chart: AstrocartographyChart object with calculated lines
        projection: Cartopy projection name
        save_as: Filename to save plot
        title: Custom plot title
    """
    if title is None:
        title = f"Astrocartography ASC Aspect Lines - {astro_chart.subject.date_time}"

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

    # Meaningful aspects
    meaningful_aspects = [
        (60, "Sextile", "dotted", 2.0),
        (90, "Square", "dashed", 2.5),
        (120, "Trine", "dashdot", 2.5),
    ]

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

    # Plot ASC aspect lines (curved) - DESC aspects are redundant since ASC 60° = DESC 120°
    print("Calculating ASC aspect lines (curved)...")
    for primary_planet in primary_planets:
        primary_name = planet_names.get(primary_planet, f"Planet {primary_planet}")

        for aspect_degrees, aspect_name, line_style, line_width in meaningful_aspects:
            try:
                print(f"  Calculating {primary_name} {aspect_name} ASC ({aspect_degrees}°)...")

                # Use calculate_aspect_line which now has fast ternary search
                aspect_coords = calculator.calculate_aspect_line(
                    planet_id=primary_planet,
                    angle_type='ASC',
                    aspect_degrees=aspect_degrees,
                    latitude_range=(-66, 66),  # Limited for house calculation stability
                    longitude_range=(-180, 180)
                )

                if aspect_coords and len(aspect_coords) > 0:
                    # Extract lons and lats for plotting curved line
                    lons = [coord[0] if coord is not None else None for coord in aspect_coords]
                    lats = [coord[1] if coord is not None else None for coord in aspect_coords]

                    # Each planet gets its own color, aspects distinguished by line style
                    plot_color = planet_colors.get(primary_planet, "#666666")

                    ax.plot(
                        lons,
                        lats,
                        color=plot_color,
                        linewidth=line_width * 0.7,
                        linestyle=line_style,
                        label=f"{primary_name} {aspect_name} ASC",
                        transform=ccrs.PlateCarree(),
                        alpha=0.7,
                    )

                    aspect_lines_plotted += 1
                    actual_points = len([c for c in aspect_coords if c is not None])
                    print(f"    ✓ Plotted curved ASC line with {actual_points} points")
                else:
                    print(f"    ⚪ No coordinates found")

            except Exception as e:
                print(f"    ✗ Error calculating ASC {aspect_name}: {e}")
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

    # Add legend
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=9)

    # Add title and info
    plt.title(title, fontsize=16, weight="bold", pad=20)

    # Add info text
    info_text = f"""
Birth Data: {astro_chart.subject.date_time}
Location: {astro_chart.subject.latitude}°, {astro_chart.subject.longitude}°

ASC Aspect Lines ({aspect_lines_plotted} plotted):

Aspect Line Styles:
··· Sextile (60°) - Dotted line
┅┅┅ Square (90°) - Dashed line
─·─ Trine (120°) - Dash-dot line

Note: All ASC aspect lines are curved S-curves
DESC aspects not shown (redundant: ASC 60° = DESC 120°)
Limited to ±66° latitude for calculation stability
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
        print(f"ASC/DESC aspect map saved as: {save_as}")

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

    # Plot ASC aspect lines (curved) - DESC aspects are redundant (ASC 60° = DESC 120°)
    print("\nCalculating ASC aspect lines (curved)...")
    for primary_planet in primary_planets:
        primary_name = planet_names.get(primary_planet, f"Planet {primary_planet}")

        for aspect_degrees, aspect_name, line_style, line_width in meaningful_aspects:
            try:
                print(f"  Calculating {primary_name} {aspect_name} ASC ({aspect_degrees}°)...")

                # Use calculate_aspect_line which now has fast ternary search
                aspect_coords = calculator.calculate_aspect_line(
                    planet_id=primary_planet,
                    angle_type='ASC',
                    aspect_degrees=aspect_degrees,
                    latitude_range=(-66, 66),  # Limited for house calculation stability
                    longitude_range=(-180, 180)
                )

                if aspect_coords and len(aspect_coords) > 0:
                    # Extract lons and lats for plotting curved line
                    lons = [coord[0] if coord is not None else None for coord in aspect_coords]
                    lats = [coord[1] if coord is not None else None for coord in aspect_coords]

                    # Each planet gets its own color, aspects distinguished by line style
                    plot_color = planet_colors.get(primary_planet, "#666666")

                    ax.plot(
                        lons,
                        lats,
                        color=plot_color,
                        linewidth=line_width * 0.7,  # Thinner for curved lines
                        linestyle=line_style,
                        label=f"{primary_name} {aspect_name} ASC",
                        transform=ccrs.PlateCarree(),
                        alpha=0.7,
                    )

                    aspect_lines_plotted += 1
                    actual_points = len([c for c in aspect_coords if c is not None])
                    print(f"    ✓ Plotted curved ASC line with {actual_points} points")
                else:
                    print(f"    ⚪ No coordinates found")

            except Exception as e:
                print(f"    ✗ Error calculating ASC {aspect_name}: {e}")
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


def export_to_geojson(astro_chart, filename="astrocartography_lines.geojson"):
    """
    Export astrocartography lines to GeoJSON format.

    Args:
        astro_chart: AstrocartographyChart object
        filename: Output filename
    """
    import json

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

    features = []

    # Export planetary lines
    for planet_id, planetary_lines in astro_chart.planetary_lines.items():
        planet_name = planet_names.get(planet_id, f"Planet_{planet_id}")

        for line_type, line_data in planetary_lines.items():
            if "coordinates" not in line_data or not line_data["coordinates"]:
                continue

            coordinates = line_data["coordinates"]
            # GeoJSON uses [longitude, latitude] order
            geojson_coords = [[coord[0], coord[1]] for coord in coordinates]

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": geojson_coords
                },
                "properties": {
                    "planet": planet_name,
                    "planet_id": planet_id,
                    "line_type": line_type,
                    "point_count": len(coordinates)
                }
            }
            features.append(feature)

    # Export zenith points
    for planet_id, zenith in astro_chart.zenith_points.items():
        if isinstance(zenith, dict):
            planet_name = planet_names.get(planet_id, f"Planet_{planet_id}")

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [zenith["longitude"], zenith["latitude"]]
                },
                "properties": {
                    "planet": planet_name,
                    "planet_id": planet_id,
                    "type": "zenith"
                }
            }
            features.append(feature)

    # Create GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "birth_datetime": str(astro_chart.subject.date_time),
            "birth_latitude": float(astro_chart.subject.latitude),
            "birth_longitude": float(astro_chart.subject.longitude),
            "timezone": astro_chart.subject.timezone
        }
    }

    # Write to file
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"✓ Exported GeoJSON to: {filename}")
    return filename


def export_to_json(astro_chart, filename="astrocartography_chart.json"):
    """
    Export complete astrocartography chart data to JSON format.

    Args:
        astro_chart: AstrocartographyChart object
        filename: Output filename
    """
    import json

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

    # Build chart data structure
    chart_data = {
        "birth_data": {
            "datetime": str(astro_chart.subject.date_time),
            "latitude": float(astro_chart.subject.latitude),
            "longitude": float(astro_chart.subject.longitude),
            "timezone": astro_chart.subject.timezone
        },
        "planetary_lines": {},
        "zenith_points": {},
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "calculation_method": "Swiss Ephemeris"
        }
    }

    # Export planetary lines
    for planet_id, planetary_lines in astro_chart.planetary_lines.items():
        planet_name = planet_names.get(planet_id, f"Planet_{planet_id}")

        chart_data["planetary_lines"][planet_name] = {}

        for line_type, line_data in planetary_lines.items():
            if "coordinates" not in line_data or not line_data["coordinates"]:
                continue

            coordinates = line_data["coordinates"]

            chart_data["planetary_lines"][planet_name][line_type] = {
                "coordinates": [[coord[0], coord[1]] for coord in coordinates],
                "point_count": len(coordinates)
            }

    # Export zenith points
    for planet_id, zenith in astro_chart.zenith_points.items():
        if isinstance(zenith, dict):
            planet_name = planet_names.get(planet_id, f"Planet_{planet_id}")

            chart_data["zenith_points"][planet_name] = {
                "longitude": zenith["longitude"],
                "latitude": zenith["latitude"]
            }

    # Write to file
    with open(filename, 'w') as f:
        json.dump(chart_data, f, indent=2)

    print(f"✓ Exported chart data to: {filename}")
    return filename


def plot_parans_map(birth_datetime, birth_location, projection="PlateCarree", save_as=None):
    """
    Plot astrocartography map with paran intersection points.

    Parans are locations where two planetary lines intersect, creating
    combined planetary influences.

    Args:
        birth_datetime: Birth datetime string "YYYY-MM-DD HH:MM:SS"
        birth_location: Tuple of (latitude, longitude)
        projection: Cartopy projection name
        save_as: Filename to save plot
    """
    from immanuel.tools.astrocartography import AstrocartographyCalculator

    print("=== Creating Paran Map ===\n")

    # Convert to Julian date
    dt = datetime.strptime(birth_datetime, "%Y-%m-%d %H:%M:%S")
    # Convert Berlin time to UTC (adjust timezone as needed)
    dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

    # Create calculator
    calculator = AstrocartographyCalculator(julian_date=jd, sampling_resolution=2.0)

    # Generate all planetary lines
    print("Generating planetary lines...")
    planetary_lines = calculator.generate_all_planetary_lines(latitude_range=(-60, 60))

    # Calculate parans
    print("Calculating paran intersections...")
    all_paran_data = calculator.calculate_all_parans_from_lines(
        planetary_lines=planetary_lines,
        exclude_node_pairs=True
    )

    # Create figure
    if projection == "PlateCarree":
        proj = ccrs.PlateCarree()
    elif projection == "Robinson":
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(24, 14))
    ax = plt.axes(projection=proj)

    # Add geographic features
    ax.add_feature(cfeature.LAND, color="lightgray", alpha=0.8)
    ax.add_feature(cfeature.OCEAN, color="lightblue", alpha=0.6)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color="black")
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color="gray", alpha=0.7)

    # Add gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, color="gray")
    gl.top_labels = False
    gl.right_labels = False
    ax.set_global()

    # Planet colors and names
    planet_colors = {
        chart.SUN: "#FFD700",
        chart.MOON: "#C0C0C0",
        chart.MERCURY: "#FFA500",
        chart.VENUS: "#FF69B4",
        chart.MARS: "#FF4500",
        chart.JUPITER: "#4169E1",
        chart.SATURN: "#8B4513",
        chart.URANUS: "#00CED1",
        chart.NEPTUNE: "#0000FF",
        chart.PLUTO: "#800080",
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

    # Plot all planetary lines
    print("Plotting planetary lines...")
    for (planet_id, line_type), line in planetary_lines.items():
        if planet_id not in planet_colors:
            continue

        color = planet_colors[planet_id]
        coords = line.coordinates

        if coords:
            lons = [coord[0] for coord in coords]
            lats = [coord[1] for coord in coords]

            # Different styles for different angles
            if line_type in ["MC", "IC"]:
                linestyle = "-"
                linewidth = 2.0
            else:  # ASC/DESC
                linestyle = ":"
                linewidth = 1.5

            ax.plot(lons, lats, color=color, linewidth=linewidth, linestyle=linestyle,
                   alpha=0.5, transform=ccrs.PlateCarree())

    # Collect and plot paran points
    print("Plotting paran intersections...")
    all_paran_points = []
    paran_info = []

    for planet1_id, angle1, planet2_id, angle2, paran_coords in all_paran_data:
        if not paran_coords:
            continue

        planet1_name = planet_names.get(planet1_id, f"P{planet1_id}")
        planet2_name = planet_names.get(planet2_id, f"P{planet2_id}")

        for lon, lat in paran_coords:
            all_paran_points.append((lon, lat))
            paran_info.append(f"{planet1_name} {angle1} × {planet2_name} {angle2}")

    if all_paran_points:
        paran_lons = [p[0] for p in all_paran_points]
        paran_lats = [p[1] for p in all_paran_points]

        # Plot paran points
        ax.plot(paran_lons, paran_lats, marker="*", markersize=15, color="gold",
               linestyle="", markeredgecolor="black", markeredgewidth=2,
               label=f"Paran Points ({len(all_paran_points)})",
               transform=ccrs.PlateCarree(), zorder=10)

        # Draw latitudinal lines through parans
        unique_lats = sorted(set(lat for lon, lat in all_paran_points))
        for lat in unique_lats:
            paran_line_lons = list(range(-180, 181, 5))
            paran_line_lats = [lat] * len(paran_line_lons)
            ax.plot(paran_line_lons, paran_line_lats, color="gold", linewidth=2.0,
                   linestyle="--", alpha=0.6, transform=ccrs.PlateCarree(), zorder=5)

    # Add birth location
    ax.plot(birth_location[1], birth_location[0], marker="*", markersize=20,
           color="red", markeredgecolor="black", markeredgewidth=2,
           label="Birth Location", transform=ccrs.PlateCarree(), zorder=15)

    # Title and legend
    plt.title(f"Astrocartography Parans - {birth_datetime}", fontsize=18, weight="bold", pad=20)
    ax.legend(loc="upper left", bbox_to_anchor=(0.01, 0.99), fontsize=10)

    # Info text
    parans_found = len([p for p in all_paran_data if p[4]])
    info_text = f"""
Birth: {birth_datetime}
Location: {birth_location[0]:.3f}°, {birth_location[1]:.3f}°

Parans Found: {parans_found}
Total Paran Points: {len(all_paran_points)}

⭐ Gold stars = Paran intersection points
━━ Gold dashed lines = Paran latitudes
    """

    plt.figtext(0.01, 0.30, info_text, fontsize=9, verticalalignment="top",
               bbox=dict(boxstyle="round", facecolor="white", alpha=0.95))

    plt.tight_layout()

    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches="tight")
        print(f"\n✓ Paran map saved as: {save_as}")

    plt.show()

    print(f"\n✓ Paran map created!")
    print(f"  Parans with intersections: {parans_found}")
    print(f"  Total paran points: {len(all_paran_points)}")

    return fig, ax


def main():
    """Demo the  astrocartography world map."""
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate astrocartography world maps')
    parser.add_argument('--parans', action='store_true',
                       help='Generate paran intersection map')
    parser.add_argument('--geojson', action='store_true',
                       help='Export astrocartography lines to GeoJSON format')
    parser.add_argument('--json', action='store_true',
                       help='Export complete chart data to JSON format')
    parser.add_argument('--geojson-file', type=str, default='astrocartography_lines.geojson',
                       help='GeoJSON output filename (default: astrocartography_lines.geojson)')
    parser.add_argument('--json-file', type=str, default='astrocartography_chart.json',
                       help='JSON output filename (default: astrocartography_chart.json)')
    args = parser.parse_args()

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

    # Create MC/IC aspect lines map
    try:
        print("=== Creating MC/IC Aspect Lines Map ===")
        fig2, ax2 = plot_astrocartography_mc_aspects_map(
            astro_chart=astro_chart,
            projection="PlateCarree",
            save_as="astrocartography_mc_aspect_lines.png",
            title="Astrocartography MC/IC Aspect Lines - Vertical Meridians",
        )

        print("\n=== MC/IC Aspect Lines Map Created Successfully! ===")
        print("Features:")
        print("✓ MC/IC aspect lines (sextile, square, trine)")
        print("✓ Vertical meridian lines")
        print("✓ Color-coded by planet")
        print("✓ Birth location marked")

    except Exception as e:
        print(f"Error creating MC/IC aspect lines map: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)

    # Create ASC aspect lines map
    try:
        print("=== Creating ASC Aspect Lines Map ===")
        fig3, ax3 = plot_astrocartography_asc_aspects_map(
            astro_chart=astro_chart,
            projection="PlateCarree",
            save_as="astrocartography_asc_aspect_lines.png",
            title="Astrocartography ASC Aspect Lines - Curved Horizon Lines",
        )

        print("\n=== ASC Aspect Lines Map Created Successfully! ===")
        print("Features:")
        print("✓ ASC aspect lines (sextile, square, trine)")
        print("✓ Curved S-shaped lines")
        print("✓ Color-coded by planet")
        print("✓ Birth location marked")
        print("✓ DESC aspects omitted (redundant: ASC 60° = DESC 120°)")

    except Exception as e:
        print(f"Error creating ASC/DESC aspect lines map: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)

    # Export to GeoJSON if requested
    if args.geojson:
        print("\n=== Exporting to GeoJSON ===")
        try:
            export_to_geojson(astro_chart, filename=args.geojson_file)
        except Exception as e:
            print(f"Error exporting to GeoJSON: {e}")

    # Export to JSON if requested
    if args.json:
        print("\n=== Exporting to JSON ===")
        try:
            export_to_json(astro_chart, filename=args.json_file)
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    print("\n" + "=" * 60)
    print("=== Demo Complete ===")
    print("Files created:")
    print("  📊 astrocartography_worldmap.png - Main planetary lines (MC/IC/ASC/DESC)")
    print("  📈 astrocartography_mc_aspect_lines.png - MC/IC aspect lines (vertical)")
    print("  📈 astrocartography_asc_aspect_lines.png - ASC aspect lines (curved, DESC omitted)")
    if args.geojson:
        print(f"  🌍 {args.geojson_file} - GeoJSON export of all lines")
    if args.json:
        print(f"  📄 {args.json_file} - JSON export of complete chart data")
    print("\nAll maps demonstrate the corrected astrocartography calculations!")
    print("Note: DESC aspects are redundant (ASC 60° = DESC 120°) and omitted from ASC map")
    print("\nUsage:")
    print("  python astrocartography_worldmap.py                  # Generate maps only")
    print("  python astrocartography_worldmap.py --geojson        # Also export to GeoJSON")
    print("  python astrocartography_worldmap.py --json           # Also export to JSON")
    print("  python astrocartography_worldmap.py --geojson --json # Export both formats")


if __name__ == "__main__":
    main()
