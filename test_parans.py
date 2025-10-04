#!/usr/bin/env python3
"""
Test paran line calculation with new intersection-based method.
Includes visualization of paran points on a world map.
"""

from datetime import datetime
import swisseph as swe
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import time
import cProfile
import pstats
from io import StringIO

from immanuel.const import chart
from immanuel.tools.astrocartography import AstrocartographyCalculator


def plot_all_parans_map(calculator, paran_data, planet_names, planet_colors, birth_datetime):
    """
    Plot a comprehensive world map showing all planetary lines and paran intersection points.

    Args:
        calculator: AstrocartographyCalculator instance
        paran_data: List of tuples (planet1_id, angle1, planet2_id, angle2, paran_coords)
        planet_names: Dict mapping planet IDs to names
        planet_colors: Dict mapping planet IDs to colors
        birth_datetime: Birth datetime string
    """
    # Create figure with cartopy projection
    fig = plt.figure(figsize=(24, 14))
    ax = plt.axes(projection=ccrs.PlateCarree())

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

    # Collect all unique lines from test cases (draw all lines, not just those with parans)
    lines_to_plot = {}  # key: (planet_id, angle), value: coords

    for planet1_id, angle1, planet2_id, angle2, paran_coords in paran_data:
        # Add both lines regardless of whether they have parans
        key1 = (planet1_id, angle1)
        key2 = (planet2_id, angle2)

        if key1 not in lines_to_plot:
            coords = calculator._get_line_coordinates(planet1_id, angle1, (-60, 60))
            if coords:
                lines_to_plot[key1] = coords

        if key2 not in lines_to_plot:
            coords = calculator._get_line_coordinates(planet2_id, angle2, (-60, 60))
            if coords:
                lines_to_plot[key2] = coords

    # Plot all planetary lines
    print(f"  📍 Plotting {len(lines_to_plot)} unique planetary lines...")
    for (planet_id, angle), coords in lines_to_plot.items():
        planet_name = planet_names.get(planet_id, f"Planet {planet_id}")
        color = planet_colors.get(planet_id, "#666666")

        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        # Different line styles for different angles
        if angle == "MC":
            linestyle = "-"
            linewidth = 2.5
        elif angle == "IC":
            linestyle = "-"
            linewidth = 2.0
        elif angle == "ASC":
            linestyle = ":"  # Dotted
            linewidth = 2.0
        elif angle == "DESC":
            linestyle = "--"  # Dashed
            linewidth = 2.0

        ax.plot(
            lons,
            lats,
            color=color,
            linewidth=linewidth,
            linestyle=linestyle,
            label=f"{planet_name} {angle}",
            transform=ccrs.PlateCarree(),
            alpha=0.7,
        )

        # Add labels for MC/IC lines at the top of the map
        if angle in ["MC", "IC"] and lons:
            # Place label at the top of the map (high latitude)
            label_lon = lons[0]  # Vertical lines have constant longitude
            label_lat = 55  # Near top of map but within bounds

            ax.text(
                label_lon,
                label_lat,
                f"{planet_name}\n{angle}",
                fontsize=9,
                color=color,
                weight="bold",
                ha="center",
                va="bottom",
                transform=ccrs.PlateCarree(),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor=color),
                zorder=20,
            )

    # Collect all paran points and create latitudinal lines
    all_paran_points = []
    paran_info = []

    for planet1_id, angle1, planet2_id, angle2, paran_coords in paran_data:
        if not paran_coords:
            continue

        planet1_name = planet_names.get(planet1_id, f"Planet {planet1_id}")
        planet2_name = planet_names.get(planet2_id, f"Planet {planet2_id}")

        for lon, lat in paran_coords:
            all_paran_points.append((lon, lat))
            paran_info.append(f"{planet1_name} {angle1} × {planet2_name} {angle2}")

    # Plot all paran points
    if all_paran_points:
        print(f"  ⭐ Plotting {len(all_paran_points)} paran points...")
        paran_lons = [coord[0] for coord in all_paran_points]
        paran_lats = [coord[1] for coord in all_paran_points]

        ax.plot(
            paran_lons,
            paran_lats,
            marker="*",
            markersize=18,
            color="gold",
            linestyle="",
            label=f"Paran Points ({len(all_paran_points)})",
            transform=ccrs.PlateCarree(),
            markeredgecolor="black",
            markeredgewidth=2,
            zorder=10,
        )

        # Add labels to paran points
        for i, ((lon, lat), label) in enumerate(zip(all_paran_points, paran_info)):
            ax.text(
                lon + 2,
                lat + 1,  # Offset text slightly from point
                label,
                fontsize=8,
                color="black",
                weight="bold",
                transform=ccrs.PlateCarree(),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
                zorder=15,
            )

        # Draw horizontal lines through unique paran latitudes
        unique_lats = sorted(set(lat for lon, lat in all_paran_points))
        print(f"  📏 Drawing {len(unique_lats)} latitudinal paran lines...")

        for lat in unique_lats:
            # Draw a line across the map at this latitude
            paran_line_lons = list(range(-180, 181, 5))
            paran_line_lats = [lat] * len(paran_line_lons)

            ax.plot(
                paran_line_lons,
                paran_line_lats,
                color="gold",
                linewidth=2.0,
                linestyle="--",
                transform=ccrs.PlateCarree(),
                alpha=0.6,
                zorder=5,
            )

    # Add legend
    ax.legend(loc="upper left", bbox_to_anchor=(0.01, 0.99), fontsize=9, ncol=2)

    # Add title
    title = f"Astrocartography Parans - All Planetary Line Intersections"
    plt.title(title, fontsize=18, weight="bold", pad=20)

    # Add info text
    total_parans = len([coords for _, _, _, _, coords in paran_data if coords])

    info_text = f"""
Birth: {birth_datetime}
Latitude Range: ±60°

Paran Combinations Found: {total_parans}
Total Paran Points: {len(all_paran_points)}

Paran Details:
"""

    # Add paran details
    for i, (planet1_id, angle1, planet2_id, angle2, paran_coords) in enumerate(paran_data):
        if paran_coords:
            planet1_name = planet_names.get(planet1_id, f"Planet {planet1_id}")
            planet2_name = planet_names.get(planet2_id, f"Planet {planet2_id}")
            info_text += f"\n{planet1_name} {angle1} × {planet2_name} {angle2}:"
            for lon, lat in paran_coords[:2]:
                info_text += f"\n  ({lon:.1f}°, {lat:.1f}°)"
            if len(paran_coords) > 2:
                info_text += f"\n  +{len(paran_coords)-2} more"

    plt.figtext(
        0.01,
        0.30,
        info_text,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.95),
    )

    plt.tight_layout()

    # Save the figure
    filename = f"parans_comprehensive_map.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"  💾 Saved comprehensive map: {filename}")

    plt.close()


def verify_paran_accuracy(paran_data, jd, planet_names, target_accuracy=0.01):
    """
    Verify paran accuracy by casting charts at paran points and checking planet positions.

    Args:
        paran_data: List of (planet1_id, angle1, planet2_id, angle2, paran_coords) tuples
        jd: Julian date
        planet_names: Dict of planet ID to name
        target_accuracy: Target accuracy in degrees (default 0.01°)

    Returns:
        Dict with accuracy statistics
    """
    from immanuel.charts import Subject, Natal

    print("\n" + "=" * 70)
    print("🔍 PARAN ACCURACY VERIFICATION")
    print("=" * 70)
    print(f"Target accuracy: ±{target_accuracy}° (astrological precision)")
    print()

    total_checks = 0
    passed_checks = 0
    failed_checks = 0
    max_error = 0.0
    errors = []

    for planet1_id, angle1, planet2_id, angle2, paran_coords in paran_data:
        if not paran_coords:
            continue

        planet1_name = planet_names.get(planet1_id, f"Planet {planet1_id}")
        planet2_name = planet_names.get(planet2_id, f"Planet {planet2_id}")

        # Check first paran point for this combination
        lon, lat = paran_coords[0]

        # Cast chart at paran location
        # Convert JD back to datetime for Subject
        import swisseph as swe

        year, month, day, hour = swe.revjul(jd)
        time_decimal = hour
        hour_int = int(time_decimal)
        minute = int((time_decimal - hour_int) * 60)
        second = int(((time_decimal - hour_int) * 60 - minute) * 60)

        dt_str = f"{year:04d}-{month:02d}-{day:02d} {hour_int:02d}:{minute:02d}:{second:02d}"

        subject = Subject(date_time=dt_str, latitude=str(lat), longitude=str(lon), timezone="UTC")

        natal_chart = Natal(subject)

        # Get planet positions
        planet1_obj = natal_chart.objects.get(planet1_id)
        planet2_obj = natal_chart.objects.get(planet2_id)

        if not planet1_obj or not planet2_obj:
            continue

        # Check planet1 at angle1
        total_checks += 1
        error1 = check_planet_at_angle(planet1_obj, angle1, natal_chart)
        errors.append(error1)
        max_error = max(max_error, error1)

        if error1 <= target_accuracy:
            passed_checks += 1
            status1 = "✅"
        else:
            failed_checks += 1
            status1 = "❌"

        # Check planet2 at angle2
        total_checks += 1
        error2 = check_planet_at_angle(planet2_obj, angle2, natal_chart)
        errors.append(error2)
        max_error = max(max_error, error2)

        if error2 <= target_accuracy:
            passed_checks += 1
            status2 = "✅"
        else:
            failed_checks += 1
            status2 = "❌"

        # Only print if there are errors or first few
        if error1 > target_accuracy or error2 > target_accuracy or total_checks <= 10:
            print(f"{planet1_name} {angle1} × {planet2_name} {angle2} at ({lon:.2f}°, {lat:.2f}°):")
            print(f"  {status1} {planet1_name} {angle1}: {error1:.4f}° error")
            print(f"  {status2} {planet2_name} {angle2}: {error2:.4f}° error")

    # Print summary
    print("\n" + "-" * 70)
    print("📊 ACCURACY SUMMARY:")
    print("-" * 70)
    print(f"Total checks: {total_checks}")
    print(f"Passed (≤{target_accuracy}°): {passed_checks} ({100*passed_checks/total_checks:.1f}%)")
    print(f"Failed (>{target_accuracy}°): {failed_checks} ({100*failed_checks/total_checks:.1f}%)")
    print(f"Max error: {max_error:.4f}°")
    print(f"Avg error: {sum(errors)/len(errors):.4f}°")
    print(f"Median error: {sorted(errors)[len(errors)//2]:.4f}°")

    return {
        "total_checks": total_checks,
        "passed": passed_checks,
        "failed": failed_checks,
        "max_error": max_error,
        "avg_error": sum(errors) / len(errors),
        "median_error": sorted(errors)[len(errors) // 2],
        "errors": errors,
    }


def check_planet_at_angle(planet_obj, angle, natal_chart):
    """
    Check how close a planet is to being exactly at a specified angle.

    Returns error in degrees.
    """
    planet_lon = planet_obj.longitude.raw

    # Get the angle from chart objects (angles are separate from houses)
    from immanuel.const import chart as chart_const

    if angle == "MC":
        angle_obj = natal_chart.objects.get(chart_const.MC)
    elif angle == "IC":
        angle_obj = natal_chart.objects.get(chart_const.IC)
    elif angle == "ASC":
        angle_obj = natal_chart.objects.get(chart_const.ASC)
    elif angle == "DESC":
        angle_obj = natal_chart.objects.get(chart_const.DESC)
    else:
        return float("inf")

    if not angle_obj:
        return float("inf")

    target_lon = angle_obj.longitude.raw

    # Calculate shortest angular distance
    diff = abs(planet_lon - target_lon)
    if diff > 180:
        diff = 360 - diff

    return diff


def benchmark_douglas_peucker_precision(birth_datetime, jd, verify_accuracy=False):
    """
    Benchmark different Douglas-Peucker epsilon values to find optimal precision/performance balance.

    Args:
        birth_datetime: Birth datetime string
        jd: Julian date
        verify_accuracy: Whether to verify chart accuracy (slower)
    """
    print("\n" + "=" * 70)
    print("🔬 DOUGLAS-PEUCKER PRECISION COMPARISON")
    print("=" * 70)

    # Test different epsilon values (in degrees)
    epsilon_values = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
    results = []

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
        chart.NORTH_NODE: "North Node",
        chart.SOUTH_NODE: "South Node",
        chart.CHIRON: "Chiron",
    }

    for epsilon in epsilon_values:
        print(f"\nTesting epsilon = {epsilon}°...")

        # Create calculator
        calculator = AstrocartographyCalculator(julian_date=jd, sampling_resolution=2.0)

        # Set the Douglas-Peucker epsilon by monkey-patching the method
        original_create = calculator._create_planetary_line

        def create_with_epsilon(planet_id, line_type, coordinates, simplify_tolerance=epsilon):
            return original_create(planet_id, line_type, coordinates, simplify_tolerance)

        calculator._create_planetary_line = create_with_epsilon

        start = time.time()

        # Generate lines with this epsilon
        planetary_lines = calculator.generate_all_planetary_lines(latitude_range=(-60, 60))

        # Calculate parans
        all_paran_data = calculator.calculate_all_parans_from_lines(
            planetary_lines=planetary_lines, exclude_node_pairs=True
        )

        elapsed = time.time() - start

        # Collect stats
        stats = calculator.profile_stats
        simp_stats = calculator.simplification_stats if hasattr(calculator, "simplification_stats") else {}

        parans_found = len([p for p in all_paran_data if p[4]])
        total_points = sum(len(p[4]) for p in all_paran_data if p[4])

        # Verify chart accuracy if requested
        accuracy_stats = None
        if verify_accuracy:
            accuracy_stats = verify_paran_accuracy(all_paran_data, jd, planet_names, target_accuracy=0.01)

        result = {
            "epsilon": epsilon,
            "time": elapsed,
            "parans_found": parans_found,
            "total_points": total_points,
            "intersections": stats.get("intersections_found", 0),
            "calculations": stats.get("intersection_calculations", 0),
            "points_removed": simp_stats.get("points_removed", 0),
            "lines_simplified": simp_stats.get("lines_simplified", 0),
            "accuracy": accuracy_stats,
        }
        results.append(result)

        print(f"  Time: {elapsed:.3f}s")
        print(f"  Parans found: {parans_found}")
        print(f"  Total paran points: {total_points}")
        print(f"  Calculations: {stats.get('intersection_calculations', 0):,}")
        if simp_stats.get("lines_simplified", 0) > 0:
            avg_removed = simp_stats["points_removed"] / simp_stats["lines_simplified"]
            print(f"  Points removed: {simp_stats['points_removed']:,} (avg {avg_removed:.1f} per line)")
        if accuracy_stats:
            print(
                f"  Accuracy: {accuracy_stats['passed']}/{accuracy_stats['total_checks']} pass ({100*accuracy_stats['passed']/accuracy_stats['total_checks']:.1f}%), max error: {accuracy_stats['max_error']:.4f}°"
            )

    # Find optimal epsilon
    print("\n" + "-" * 100)
    print("📊 COMPARISON SUMMARY:")
    print("-" * 100)

    if verify_accuracy:
        print(
            f"{'Epsilon':<10} {'Time':<10} {'Parans':<10} {'Points':<10} {'Calcs':<12} {'Accuracy':<15} {'Avg Err':<10} {'Max Err':<10}"
        )
        print("-" * 100)
        for r in results:
            if r["accuracy"]:
                acc_pct = 100 * r["accuracy"]["passed"] / r["accuracy"]["total_checks"]
                max_err = r["accuracy"]["max_error"]
                print(
                    f"{r['epsilon']:<10.4f} {r['time']:<10.3f} {r['parans_found']:<10} {r['total_points']:<10} {r['calculations']:<12,} {acc_pct:>6.1f}% ({r['accuracy']['passed']}/{r['accuracy']['total_checks']})   {r['accuracy']['avg_error']:<10.4f} {max_err:<10.4f}"
                )
            else:
                print(
                    f"{r['epsilon']:<10.1f} {r['time']:<10.3f} {r['parans_found']:<10} {r['total_points']:<10} {r['calculations']:<12,}"
                )
    else:
        print(f"{'Epsilon':<10} {'Time':<10} {'Parans':<10} {'Points':<10} {'Calcs':<12} {'Removed':<10}")
        print("-" * 70)
        for r in results:
            print(
                f"{r['epsilon']:<10.1f} {r['time']:<10.3f} {r['parans_found']:<10} {r['total_points']:<10} {r['calculations']:<12,} {r['points_removed']:<10,}"
            )

    # Find fastest with same results as most precise
    baseline = results[0]  # epsilon=0.1 as baseline

    print("\n📈 RECOMMENDATIONS:")
    for r in results:
        speedup = baseline["time"] / r["time"]
        if r["parans_found"] == baseline["parans_found"] and r["total_points"] == baseline["total_points"]:
            if speedup > 1.1:  # At least 10% faster
                print(f"  ✅ Epsilon {r['epsilon']}° gives {speedup:.2f}x speedup with identical results")
        elif r["parans_found"] != baseline["parans_found"]:
            print(
                f"  ⚠️  Epsilon {r['epsilon']}° finds different parans ({r['parans_found']} vs {baseline['parans_found']}) - too imprecise"
            )

    return results


def main():
    print("\n=== Paran Line Calculation & Visualization Test ===\n")

    # Birth data
    birth_datetime = "1984-01-03 18:36:00"
    print(f"Birth: {birth_datetime}\n")

    # Create calculator
    dt = datetime.strptime(birth_datetime, "%Y-%m-%d %H:%M:%S")
    dt_utc = datetime(dt.year, dt.month, dt.day, dt.hour - 1, dt.minute, dt.second)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

    # Run Douglas-Peucker precision comparison
    dp_results = benchmark_douglas_peucker_precision(birth_datetime, jd, verify_accuracy=True)

    return

    # Use optimal epsilon from benchmark (or default)
    optimal_epsilon = 1.0  # Default, will be updated based on benchmark
    for r in dp_results:
        baseline = dp_results[0]
        if (
            r["parans_found"] == baseline["parans_found"]
            and r["total_points"] == baseline["total_points"]
            and r["time"] < baseline["time"] * 0.8
        ):  # At least 20% faster
            optimal_epsilon = r["epsilon"]
            break

    print(f"\n🎯 Using optimal epsilon: {optimal_epsilon}°")

    # Start profiling for main run
    pr = cProfile.Profile()
    pr.enable()
    start_time = time.time()

    calculator = AstrocartographyCalculator(julian_date=jd, sampling_resolution=2.0)

    # Apply optimal epsilon
    original_create = calculator._create_planetary_line

    def create_with_optimal_epsilon(planet_id, line_type, coordinates, simplify_tolerance=optimal_epsilon):
        return original_create(planet_id, line_type, coordinates, simplify_tolerance)

    calculator._create_planetary_line = create_with_optimal_epsilon

    # PHASE 1: Generate all planetary lines once (improved architecture)
    planetary_lines = calculator.generate_all_planetary_lines(latitude_range=(-60, 60))

    # PHASE 2: Calculate all parans from cached lines
    all_paran_data = calculator.calculate_all_parans_from_lines(
        planetary_lines=planetary_lines, exclude_node_pairs=True
    )

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
        chart.NORTH_NODE: "North Node",
        chart.SOUTH_NODE: "South Node",
        chart.CHIRON: "Chiron",
    }

    planet_colors = {
        chart.SUN: "#FFD700",  # Gold
        chart.MOON: "#C0C0C0",  # Silver
        chart.MERCURY: "#FFA500",  # Orange
        chart.VENUS: "#FF69B4",  # Hot Pink
        chart.MARS: "#FF4500",  # Red Orange
        chart.JUPITER: "#4169E1",  # Royal Blue
        chart.SATURN: "#8B4513",  # Saddle Brown
        chart.URANUS: "#00CED1",  # Dark Turquoise
        chart.NEPTUNE: "#4682B4",  # Steel Blue
        chart.PLUTO: "#8B008B",  # Dark Magenta
        chart.NORTH_NODE: "#32CD32",  # Lime Green
        chart.SOUTH_NODE: "#228B22",  # Forest Green
        chart.CHIRON: "#CD853F",  # Peru
    }

    print("=" * 70)

    # Process results and display
    total_paran_points = 0

    for planet1_id, angle1, planet2_id, angle2, paran_coords in all_paran_data:
        if paran_coords:
            planet1_name = planet_names.get(planet1_id, f"Planet {planet1_id}")
            planet2_name = planet_names.get(planet2_id, f"Planet {planet2_id}")

            print(f"  ✓ Found {len(paran_coords)} paran point(s) {planet1_name} {angle1} × {planet2_name} {angle2}")
            total_paran_points += len(paran_coords)

            # Show coordinates
            for i, (lon, lat) in enumerate(paran_coords[:3], 1):  # Show first 3
                print(f"    {i}. ({lon:.2f}°, {lat:.2f}°)")
            if len(paran_coords) > 3:
                print(f"    ... and {len(paran_coords) - 3} more")
    # Stop profiling and show results
    pr.disable()
    end_time = time.time()

    print("\n" + "=" * 70)
    print(f"\n📊 Generating comprehensive paran map...")
    print("=" * 70)

    # Generate one comprehensive map with all lines and parans
    plot_all_parans_map(
        calculator=calculator,
        paran_data=all_paran_data,
        planet_names=planet_names,
        planet_colors=planet_colors,
        birth_datetime=birth_datetime,
    )

    print("\n" + "=" * 70)
    print(f"\n✓ Test complete!")
    print(f"  Paran combinations tested: {len(all_paran_data)}")
    print(f"  Parans with intersections: {len([p for p in all_paran_data if p[4]])}")
    print(f"  Total paran points: {total_paran_points}")
    print(f"  Comprehensive map: parans_comprehensive_map.png")
    print(f"\nNote: Paran lines are latitudinal (horizontal) gold dashed lines.")

    # Performance profiling results
    total_time = end_time - start_time
    stats = calculator.profile_stats

    print(f"\n" + "=" * 70)
    print(f"📊 PERFORMANCE PROFILING RESULTS")
    print(f"=" * 70)
    print(f"Total execution time: {total_time:.3f} seconds")
    print(stats)

    # Calculate efficiency metrics
    if stats["intersection_calculations"] > 0:
        line_bounds_efficiency = (stats["line_bounds_skipped"] / len(all_paran_data)) * 100
        intersection_success_rate = (stats["intersections_found"] / stats["intersection_calculations"]) * 100

        print(f"\n📈 EFFICIENCY METRICS:")
        print(
            f"Line bounds skip rate: {line_bounds_efficiency:.1f}% ({stats['line_bounds_skipped']} of {len(all_paran_data)} line pairs)"
        )
        if "segment_bounds_skipped" in stats:
            print(f"Segment bounds skipped: {stats['segment_bounds_skipped']:,}")
        print(f"Intersection success rate: {intersection_success_rate:.3f}%")
        print(f"Calculations per second: {stats['intersection_calculations']/total_time:.0f}")
        print(f"Intersections per second: {stats['intersections_found']/total_time:.1f}")

        # Show Douglas-Peucker simplification stats
        if hasattr(calculator, "simplification_stats"):
            simp_stats = calculator.simplification_stats
            print(f"Douglas-Peucker simplification:")
            print(f"  Lines simplified: {simp_stats['lines_simplified']}")
            print(f"  Points removed: {simp_stats['points_removed']:,}")
            if simp_stats["lines_simplified"] > 0:
                avg_reduction = simp_stats["points_removed"] / simp_stats["lines_simplified"]
                print(f"  Average points removed per line: {avg_reduction:.1f}")

    # Show top time-consuming functions
    print(f"\n🔍 TOP TIME-CONSUMING FUNCTIONS:")
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(10)  # Top 10 functions
    profile_output = s.getvalue()

    # Extract and show relevant lines
    lines = profile_output.split("\n")
    for line in lines[5:15]:  # Skip header, show top 10
        if line.strip() and not line.startswith("ncalls"):
            print(f"  {line}")

    print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
    if line_bounds_efficiency < 50:
        print(f"  • Line bounds checking is only skipping {line_bounds_efficiency:.1f}% - consider tighter bounds")
    if intersection_success_rate < 1:
        print(f"  • Very low intersection success rate ({intersection_success_rate:.3f}%) - consider spatial indexing")
    if stats["intersection_calculations"] > 10000000:
        print(
            f"  • High calculation count ({stats['intersection_calculations']:,}) - consider spatial indexing or coarser sampling"
        )

    print(f"\n🎯 CURRENT OPTIMIZATIONS WORKING:")
    print(f"  ✅ PlanetaryLine objects with precomputed bounds")
    print(f"  ✅ Line-level bounds checking (skipping {stats['line_bounds_skipped']} line pairs)")
    print(f"  ✅ Duplicate elimination (testing {len(all_paran_data)} vs {len(all_paran_data)*2} combinations)")
    print(f"  ✅ Wrap-around segment filtering")


if __name__ == "__main__":
    main()
