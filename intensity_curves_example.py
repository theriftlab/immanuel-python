#!/usr/bin/env python3
"""
Intensity Curves Example

This example demonstrates the new intensity curves feature for transit aspects.
Intensity curves show how the orb (angular distance from exact) changes over time
as planets move through their orbits, including complex retrograde motions.

Usage:
    python intensity_curves_example.py
"""

import json
from datetime import datetime, timedelta

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Note: matplotlib not available. Install with 'pip install matplotlib' for plotting features.")

from immanuel import charts
from immanuel.const import calc, chart, transits
from immanuel.tools.transit_search import TransitSearch
from immanuel.classes.serialize import ToJSON


def plot_intensity_curve(curve, title="Transit Intensity Curve", save_as=None):
    """
    Plot an intensity curve showing orb distance over time.

    Args:
        curve: IntensityCurve object
        title: Plot title
        save_as: Filename to save plot (e.g., "curve.png" or "curve.svg")
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available - cannot plot curves")
        return

    if not curve or not curve.samples:
        print("No curve data to plot")
        return

    # Extract data for plotting
    dates = [sample['datetime'] for sample in curve.samples]
    orbs = [sample['orb_value'] for sample in curve.samples]
    applying = [sample['applying'] for sample in curve.samples]
    retrograde = [sample['retrograde'] for sample in curve.samples]
    retrograde_sessions = [sample['retrograde_session'] for sample in curve.samples]

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot the main intensity curve
    ax.plot(dates, orbs, 'b-', linewidth=2, label='Orb Distance', alpha=0.8)

    # Color-code points by motion type
    for i, (date, orb, appl, retro, session) in enumerate(zip(dates, orbs, applying, retrograde, retrograde_sessions)):
        if retro:
            # Retrograde motion - red
            color = 'red'
            marker = 's'  # square
            size = 25
        elif appl:
            # Applying (direct) - green
            color = 'green'
            marker = 'o'  # circle
            size = 20
        else:
            # Separating (direct) - orange
            color = 'orange'
            marker = '^'  # triangle
            size = 20

        ax.scatter(date, orb, c=color, marker=marker, s=size, alpha=0.7, edgecolors='black', linewidth=0.5)

    # Highlight retrograde periods with background shading
    retrograde_periods = curve.metadata.get('retrograde_sessions', [])
    for period in retrograde_periods:
        start_jd = period.get('start_jd')
        end_jd = period.get('end_jd')
        if start_jd and end_jd:
            from immanuel.tools import date as date_util
            start_dt = date_util.to_datetime(start_jd)
            end_dt = date_util.to_datetime(end_jd)
            ax.axvspan(start_dt, end_dt, alpha=0.1, color='red', label=f'Retrograde Session {period["session_number"]}' if period == retrograde_periods[0] else "")

    # Mark the exact moment (closest approach)
    peak_sample = curve.get_peak_intensity()
    if peak_sample:
        ax.axhline(y=peak_sample['orb_value'], color='purple', linestyle='--', alpha=0.7, label=f'Peak Intensity ({peak_sample["orb_value"]:.3f}°)')
        ax.scatter(peak_sample['datetime'], peak_sample['orb_value'], c='purple', s=100, marker='*', edgecolors='black', linewidth=1, label=f'Exact Moment')

    # Add orb threshold lines
    sampling_config = curve.sampling_config
    if 'curve_orb' in sampling_config:
        curve_orb = sampling_config['curve_orb']
        ax.axhline(y=curve_orb, color='gray', linestyle=':', alpha=0.5, label=f'Curve Orb Limit ({curve_orb}°)')

    # Format the plot
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Orb Distance (degrees)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Format date axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Determine date spacing based on time range
    date_range = max(dates) - min(dates)
    if date_range.days > 365:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    elif date_range.days > 90:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save or show
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Plot saved as {save_as}")
    else:
        plt.close(fig)  # Close to free memory

    return fig, ax


def plot_multiple_curves(curves_data, title="Multiple Transit Intensity Curves", save_as=None):
    """
    Plot multiple intensity curves on the same chart for comparison.

    Args:
        curves_data: List of tuples (curve, label, color)
        title: Plot title
        save_as: Filename to save plot
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available - cannot plot curves")
        return

    if not curves_data:
        print("No curve data to plot")
        return

    fig, ax = plt.subplots(figsize=(16, 10))

    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

    for i, (curve, label, color) in enumerate(curves_data):
        if not curve or not curve.samples:
            continue

        # Extract data
        dates = [sample['datetime'] for sample in curve.samples]
        orbs = [sample['orb_value'] for sample in curve.samples]

        # Use provided color or cycle through defaults
        plot_color = color if color else colors[i % len(colors)]

        # Plot curve
        ax.plot(dates, orbs, color=plot_color, linewidth=2, label=label, alpha=0.8)

        # Mark peak intensity
        peak_sample = curve.get_peak_intensity()
        if peak_sample:
            ax.scatter(peak_sample['datetime'], peak_sample['orb_value'],
                      c=plot_color, s=80, marker='*', edgecolors='black', linewidth=1)

    # Format the plot
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Orb Distance (degrees)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Format date axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save or show
    if save_as:
        plt.savefig(save_as, dpi=300, bbox_inches='tight')
        print(f"Plot saved as {save_as}")
    else:
        plt.close(fig)  # Close to free memory

    return fig, ax


def main():
    """Demonstrate intensity curves functionality."""

    print("=" * 80)
    print("INTENSITY CURVES EXAMPLE")
    print("=" * 80)
    print()

    # Create a sample natal chart
    print("Creating sample natal chart...")
    natal = charts.Subject(
        date_time=datetime(1990, 1, 1, 12, 0, 0),
        latitude=40.7128,   # New York
        longitude=-74.0060, # New York
    )

    natal_chart = charts.Natal(natal)
    print(f"Natal chart created for {natal.date_time}")
    print(f"Location: {natal.latitude}°N, {abs(natal.longitude)}°W")
    print()

    # Search period
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 12, 31)

    print(f"Searching for transits from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()

    # Example 1: Saturn conjunctions with intensity curves
    print("EXAMPLE 1: Saturn Conjunctions with Intensity Curves")
    print("-" * 60)

    search = TransitSearch(
        natal_chart=natal_chart,
        start_date=start_date,
        end_date=end_date
    )

    # Find Saturn conjunctions to natal Sun with curves enabled
    saturn_conjunctions = search.find_aspects(
        transiting_planet=chart.SATURN,
        natal_planet=chart.SUN,
        aspect=calc.CONJUNCTION,
        max_orb=3.0,                    # 3° orb for event detection
        generate_curves=True,           # Enable intensity curves
        curve_orb=8.0,                  # 8° orb for curve visualization
        curve_sampling="daily"          # Daily sampling
    )

    print(f"Found {len(saturn_conjunctions)} Saturn-Sun conjunctions:")
    print()

    for i, aspect in enumerate(saturn_conjunctions, 1):
        print(f"Conjunction {i}:")
        print(f"  Date: {aspect.date_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Orb: {aspect.orb:.2f}°")
        print(f"  Exact: {aspect.exact}")

        if aspect.intensity_curve:
            curve = aspect.intensity_curve
            print(f"  Intensity Curve: {len(curve.samples)} samples")

            # Show peak intensity
            peak = curve.get_peak_intensity()
            if peak:
                print(f"  Peak Intensity: {peak['orb_value']:.3f}° on {peak['datetime'].strftime('%Y-%m-%d')}")

            # Show retrograde sessions
            retrograde_sessions = curve.metadata.get('retrograde_sessions', [])
            if retrograde_sessions:
                print(f"  Retrograde Sessions: {len(retrograde_sessions)}")
                for session in retrograde_sessions:
                    print(f"    Session {session['session_number']}: {session.get('multiple_exactness', False) and 'Multiple exactness' or 'Single pass'}")

            # Sample some curve data points
            print("  Sample curve points:")
            for j, sample in enumerate(curve.samples[:5]):  # Show first 5 samples
                direction = "applying" if sample['applying'] else "separating"
                motion = "retrograde" if sample['retrograde'] else "direct"
                print(f"    {sample['datetime'].strftime('%Y-%m-%d')}: {sample['orb_value']:.2f}° ({direction}, {motion})")

            if len(curve.samples) > 5:
                print(f"    ... and {len(curve.samples) - 5} more samples")
        else:
            print("  No intensity curve generated")

        print()

    # Example 2: Mars aspects with different sampling
    print("EXAMPLE 2: Mars Square Aspects with Hourly Sampling")
    print("-" * 60)

    mars_squares = search.find_aspects(
        transiting_planet=chart.MARS,
        natal_planet=chart.MOON,
        aspect=calc.SQUARE,
        max_orb=2.0,
        generate_curves=True,
        curve_orb=6.0,
        curve_sampling=timedelta(hours=6)  # 6-hour sampling
    )

    print(f"Found {len(mars_squares)} Mars-Moon squares:")
    print()

    for i, aspect in enumerate(mars_squares, 1):
        print(f"Square {i}: {aspect.date_time.strftime('%Y-%m-%d')} (orb: {aspect.orb:.2f}°)")

        if aspect.intensity_curve:
            curve = aspect.intensity_curve
            applying_count = len(curve.get_applying_samples())
            separating_count = len(curve.get_separating_samples())
            print(f"  Curve: {applying_count} applying, {separating_count} separating samples")

    print()

    # Example 2.5: Saturn Retrograde Motion Demonstration
    print("EXAMPLE 2.5: Saturn Retrograde Motion (Extended Period)")
    print("-" * 60)

    # Use an even longer period and Saturn for better retrograde visibility
    retrograde_start_date = datetime(2024, 1, 1)
    retrograde_end_date = datetime(2028, 12, 31)  # 5 years to catch Saturn retrograde patterns

    retrograde_search = TransitSearch(
        natal_chart=natal_chart,
        start_date=retrograde_start_date,
        end_date=retrograde_end_date
    )

    print(f"Searching for Saturn aspects over extended period: {retrograde_start_date.strftime('%Y-%m-%d')} to {retrograde_end_date.strftime('%Y-%m-%d')}")
    print("(Saturn has ~5 month retrograde periods annually, creating dramatic intensity curves)")
    print()

    # Find Saturn aspects to natal Sun (good for showing retrograde effects)
    saturn_aspects = []

    # Try different aspects to find one that shows retrograde motion
    aspects_to_try = [
        (calc.CONJUNCTION, "Conjunction"),
        (calc.OPPOSITION, "Opposition"),
        (calc.SQUARE, "Square"),
        (calc.TRINE, "Trine"),
        (calc.SEXTILE, "Sextile")
    ]

    for aspect_type, aspect_name in aspects_to_try:
        if saturn_aspects:
            break  # Found aspects, no need to continue

        print(f"Searching for Saturn-Sun {aspect_name}s...")
        found_aspects = retrograde_search.find_aspects(
            transiting_planet=chart.SATURN,
            natal_planet=chart.SUN,
            aspect=aspect_type,
            max_orb=3.0,
            generate_curves=True,
            curve_orb=12.0,  # Wide orb for comprehensive retrograde visualization
            curve_sampling="daily"
        )

        if found_aspects:
            saturn_aspects.extend(found_aspects)
            print(f"Found {len(found_aspects)} Saturn-Sun {aspect_name}(s)")
            break
        else:
            print(f"No Saturn-Sun {aspect_name}s found")

    print(f"\nTotal Saturn aspects found: {len(saturn_aspects)}")
    print()
    best_retrograde_example = None
    most_retrograde_sessions = 0

    for i, aspect in enumerate(saturn_aspects, 1):
        aspect_name = {
            calc.CONJUNCTION: "Conjunction",
            calc.OPPOSITION: "Opposition",
            calc.TRINE: "Trine",
            calc.SEXTILE: "Sextile",
            calc.SQUARE: "Square"
        }.get(aspect.aspect_type, f"Aspect {aspect.aspect_type}°")

        print(f"Saturn-Sun {aspect_name} {i}:")
        print(f"  Date: {aspect.date_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Orb: {aspect.orb:.3f}°")

        if aspect.intensity_curve:
            curve = aspect.intensity_curve
            retrograde_sessions = curve.metadata.get('retrograde_sessions', [])
            retrograde_samples = [s for s in curve.samples if s['retrograde']]

            print(f"  Intensity Curve: {len(curve.samples)} total samples")
            print(f"  Retrograde Sessions: {len(retrograde_sessions)}")
            print(f"  Retrograde Samples: {len(retrograde_samples)}/{len(curve.samples)} ({len(retrograde_samples)/len(curve.samples)*100:.1f}%)")

            # Analyze retrograde sessions in detail
            for session in retrograde_sessions:
                multiple_exact = session.get('multiple_exactness', False)
                print(f"    Session {session['session_number']}: {'Multiple passes through exact' if multiple_exact else 'Single retrograde period'}")

            # Check if this is our best retrograde example
            if len(retrograde_sessions) > most_retrograde_sessions:
                most_retrograde_sessions = len(retrograde_sessions)
                best_retrograde_example = aspect

            # Show timeline of retrograde motion
            if retrograde_sessions:
                print("  Retrograde Timeline:")
                for session in retrograde_sessions[:2]:  # Show first 2 sessions
                    start_jd = session.get('start_jd')
                    end_jd = session.get('end_jd')
                    if start_jd and end_jd:
                        from immanuel.tools import date as date_util
                        start_dt = date_util.to_datetime(start_jd)
                        end_dt = date_util.to_datetime(end_jd)
                        duration = end_dt - start_dt
                        print(f"    {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')} ({duration.days} days)")

            print()
        else:
            print("  No intensity curve generated")
            print()

    # If we found a good retrograde example, create a special plot for it
    if best_retrograde_example and best_retrograde_example.intensity_curve:
        print("🌟 RETROGRADE SHOWCASE: Creating detailed retrograde motion plot...")
        curve = best_retrograde_example.intensity_curve

        aspect_name = {
            calc.CONJUNCTION: "Conjunction",
            calc.OPPOSITION: "Opposition",
            calc.TRINE: "Trine",
            calc.SEXTILE: "Sextile",
            calc.SQUARE: "Square"
        }.get(best_retrograde_example.aspect_type, f"Aspect {best_retrograde_example.aspect_type}°")

        if MATPLOTLIB_AVAILABLE:
            # Create a specialized retrograde plot
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)

            dates = [sample['datetime'] for sample in curve.samples]
            orbs = [sample['orb_value'] for sample in curve.samples]
            applying = [sample['applying'] for sample in curve.samples]
            retrograde = [sample['retrograde'] for sample in curve.samples]
            retrograde_sessions = [sample['retrograde_session'] for sample in curve.samples]

            # Top plot: Full intensity curve with retrograde highlighting
            ax1.plot(dates, orbs, 'b-', linewidth=2, alpha=0.8, label='Orb Distance')

            # Highlight retrograde periods
            retrograde_periods = curve.metadata.get('retrograde_sessions', [])
            colors = ['red', 'orange', 'purple', 'brown']
            for i, period in enumerate(retrograde_periods[:4]):  # Max 4 colors
                start_jd = period.get('start_jd')
                end_jd = period.get('end_jd')
                if start_jd and end_jd:
                    from immanuel.tools import date as date_util
                    start_dt = date_util.to_datetime(start_jd)
                    end_dt = date_util.to_datetime(end_jd)
                    color = colors[i % len(colors)]
                    ax1.axvspan(start_dt, end_dt, alpha=0.2, color=color,
                               label=f'Retrograde Session {period["session_number"]}')

            # Mark exact moment
            peak_sample = curve.get_peak_intensity()
            if peak_sample:
                ax1.scatter(peak_sample['datetime'], peak_sample['orb_value'],
                           c='gold', s=150, marker='*', edgecolors='black', linewidth=2,
                           label=f'Exact Moment ({peak_sample["orb_value"]:.3f}°)')

            ax1.set_ylabel('Orb Distance (degrees)', fontsize=12)
            ax1.set_title(f'Saturn-Sun {aspect_name} - Retrograde Motion Analysis', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            # Middle plot: Applying vs Separating
            applying_values = [1 if app else -1 for app in applying]
            ax2.plot(dates, applying_values, 'g-', linewidth=2, alpha=0.8)
            ax2.fill_between(dates, applying_values, alpha=0.3, color='green')
            ax2.set_ylabel('Applying/Separating', fontsize=12)
            ax2.set_yticks([-1, 1])
            ax2.set_yticklabels(['Separating', 'Applying'])
            ax2.grid(True, alpha=0.3)

            # Bottom plot: Retrograde sessions over time
            retrograde_values = [-1 if retro else 1 for retro in retrograde]
            ax3.plot(dates, retrograde_values, 'r-', linewidth=2, alpha=0.8)
            ax3.fill_between(dates, retrograde_values, alpha=0.3,
                           color=['red' if r < 0 else 'blue' for r in retrograde_values])
            ax3.set_ylabel('Motion Direction', fontsize=12)
            ax3.set_xlabel('Date', fontsize=12)
            ax3.set_yticks([-1, 1])
            ax3.set_yticklabels(['Retrograde', 'Direct'])
            ax3.grid(True, alpha=0.3)

            # Enhanced date axis formatting for detailed analysis
            if dates:
                date_range = max(dates) - min(dates)

                if date_range.days > 730:  # > 2 years
                    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
                    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                    ax3.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
                elif date_range.days > 365:  # > 1 year
                    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                    ax3.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
                else:
                    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                    ax3.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=2))

                # Add station markers on time axis
                for station in curve.metadata.get('all_stations_found', []):
                    station_dt = station['datetime']
                    station_type = station['type']
                    color = 'red' if station_type == transits.STATION_RETROGRADE else 'blue'
                    symbol = 'R' if station_type == transits.STATION_RETROGRADE else 'D'

                    # Add vertical lines on all subplots
                    for ax in [ax1, ax2, ax3]:
                        ax.axvline(x=station_dt, color=color, linestyle=':', alpha=0.7, linewidth=1)

                    # Add text annotation on bottom plot
                    ax3.annotate(symbol, xy=(station_dt, -0.5), xytext=(0, -10),
                                textcoords='offset points', ha='center', va='top',
                                fontsize=8, color=color, fontweight='bold')

            ax3.tick_params(which='minor', length=3)
            ax3.tick_params(which='major', length=6)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('saturn_retrograde_showcase.png', dpi=300, bbox_inches='tight')
            print("Retrograde showcase plot saved as saturn_retrograde_showcase.png")
            plt.close(fig)

        print()
        print("📊 Retrograde Analysis Summary:")
        retrograde_periods = curve.metadata.get('retrograde_sessions', [])
        print(f"  Total retrograde sessions: {len(retrograde_periods)}")

        total_retro_days = 0
        for period in retrograde_periods:
            if period.get('start_jd') and period.get('end_jd'):
                days = period['end_jd'] - period['start_jd']
                total_retro_days += days
                multiple = "Yes" if period.get('multiple_exactness', False) else "No"
                print(f"  Session {period['session_number']}: {days:.0f} days, Multiple exactness: {multiple}")

        total_curve_days = curve.metadata.get('time_span_days', 0)
        if total_curve_days > 0:
            retro_percentage = (total_retro_days / total_curve_days) * 100
            print(f"  Total retrograde time: {total_retro_days:.0f} days ({retro_percentage:.1f}% of transit period)")

        exact_moments = curve.metadata.get('exact_moments', 0)
        print(f"  Exact moments (< 0.1°): {exact_moments}")

    else:
        print("No suitable retrograde examples found in the current time period.")
        print("Try extending the search period or using slower planets like Saturn.")

    print()

    # Example 3: JSON serialization of curves
    print("EXAMPLE 3: JSON Serialization")
    print("-" * 60)

    if saturn_conjunctions and saturn_conjunctions[0].intensity_curve:
        # Serialize the first aspect with its curve to JSON
        aspect_with_curve = saturn_conjunctions[0]

        print("Serializing aspect with intensity curve to JSON...")
        json_data = ToJSON.export(aspect_with_curve)

        # Pretty print a sample of the JSON (truncated for readability)
        print("JSON structure (sample):")
        print(json.dumps(json_data, indent=2)[:1000] + "..." if len(str(json_data)) > 1000 else json.dumps(json_data, indent=2))
        print()

    # Example 4: Analyzing curve features
    print("EXAMPLE 4: Curve Analysis")
    print("-" * 60)

    if saturn_conjunctions and saturn_conjunctions[0].intensity_curve:
        curve = saturn_conjunctions[0].intensity_curve

        print("Analyzing intensity curve features:")
        print(f"  Total samples: {len(curve.samples)}")
        print(f"  Sampling config: {curve.sampling_config}")

        # Find closest approach
        peak_sample = curve.get_peak_intensity()
        if peak_sample:
            print(f"  Closest approach: {peak_sample['orb_value']:.3f}° on {peak_sample['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  During retrograde: {peak_sample['retrograde']}")
            print(f"  Retrograde session: {peak_sample['retrograde_session']}")

        # Analyze applying vs separating phases
        applying_samples = curve.get_applying_samples()
        separating_samples = curve.get_separating_samples()
        print(f"  Applying phase: {len(applying_samples)} samples")
        print(f"  Separating phase: {len(separating_samples)} samples")

        # Find exact moments (orb < 0.1°)
        exact_samples = [s for s in curve.samples if s['orb_value'] < 0.1]
        print(f"  Exact moments (< 0.1°): {len(exact_samples)}")

        for exact in exact_samples[:3]:  # Show up to 3 exact moments
            motion = "retrograde" if exact['retrograde'] else "direct"
            print(f"    {exact['datetime'].strftime('%Y-%m-%d %H:%M')}: {exact['orb_value']:.4f}° ({motion})")

        print()

    # Example 5: Actual Plotting with Matplotlib
    print("EXAMPLE 5: Matplotlib Visualization")
    print("-" * 60)

    if MATPLOTLIB_AVAILABLE:
        print("Creating visual plots of intensity curves...")
        print()

        # Plot Saturn conjunction if available
        if saturn_conjunctions and saturn_conjunctions[0].intensity_curve:
            print("Plotting Saturn-Sun conjunction intensity curve...")
            curve = saturn_conjunctions[0].intensity_curve
            plot_intensity_curve(
                curve,
                title="Saturn-Sun Conjunction Intensity Curve",
                save_as="saturn_conjunction_curve.png"
            )
            print()

        # Plot Mars squares if available
        mars_curves_data = []
        for i, aspect in enumerate(mars_squares):
            if aspect.intensity_curve:
                label = f"Mars-Moon Square {i+1} ({aspect.date_time.strftime('%Y-%m-%d')})"
                color = ['red', 'blue', 'green', 'orange'][i % 4]
                mars_curves_data.append((aspect.intensity_curve, label, color))

        if mars_curves_data:
            print("Plotting multiple Mars-Moon square curves for comparison...")
            plot_multiple_curves(
                mars_curves_data,
                title="Mars-Moon Square Intensity Curves Comparison",
                save_as="mars_squares_comparison.png"
            )
            print()

        # Create a detailed analysis plot of the first available curve
        first_curve = None
        first_aspect_info = ""

        if saturn_conjunctions and saturn_conjunctions[0].intensity_curve:
            first_curve = saturn_conjunctions[0].intensity_curve
            first_aspect_info = "Saturn-Sun Conjunction"
        elif mars_squares and mars_squares[0].intensity_curve:
            first_curve = mars_squares[0].intensity_curve
            first_aspect_info = "Mars-Moon Square"

        if first_curve:
            print(f"Creating detailed analysis plot for {first_aspect_info}...")

            # Create a more detailed plot with annotations
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

            # Top plot: Orb distance over time
            dates = [sample['datetime'] for sample in first_curve.samples]
            orbs = [sample['orb_value'] for sample in first_curve.samples]
            applying = [sample['applying'] for sample in first_curve.samples]
            retrograde = [sample['retrograde'] for sample in first_curve.samples]

            # Main curve
            ax1.plot(dates, orbs, 'b-', linewidth=2, alpha=0.8)

            # Color-coded scatter points
            for i, (date, orb, appl, retro) in enumerate(zip(dates, orbs, applying, retrograde)):
                if retro:
                    ax1.scatter(date, orb, c='red', s=15, alpha=0.7)
                elif appl:
                    ax1.scatter(date, orb, c='green', s=10, alpha=0.7)
                else:
                    ax1.scatter(date, orb, c='orange', s=10, alpha=0.7)

            # Mark exact moment
            peak_sample = first_curve.get_peak_intensity()
            if peak_sample:
                ax1.scatter(peak_sample['datetime'], peak_sample['orb_value'],
                           c='purple', s=100, marker='*', edgecolors='black', linewidth=1)
                ax1.annotate(f'Exact: {peak_sample["orb_value"]:.3f}°',
                            xy=(peak_sample['datetime'], peak_sample['orb_value']),
                            xytext=(10, 10), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

            ax1.set_ylabel('Orb Distance (degrees)')
            ax1.set_title(f'{first_aspect_info} - Detailed Analysis')
            ax1.grid(True, alpha=0.3)
            ax1.legend(['Orb Distance', 'Retrograde', 'Applying', 'Separating', 'Exact Moment'])

            # Bottom plot: Motion analysis
            motion_values = []
            for sample in first_curve.samples:
                if sample['retrograde']:
                    motion_values.append(-1)  # Retrograde
                elif sample['applying']:
                    motion_values.append(1)   # Applying
                else:
                    motion_values.append(0.5) # Separating

            ax2.plot(dates, motion_values, 'g-', linewidth=2, alpha=0.8)
            ax2.fill_between(dates, motion_values, alpha=0.3)
            ax2.set_ylabel('Motion Type')
            ax2.set_xlabel('Date')
            ax2.set_yticks([-1, 0.5, 1])
            ax2.set_yticklabels(['Retrograde', 'Separating', 'Applying'])
            ax2.grid(True, alpha=0.3)

            # Format date axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            if len(dates) > 0:
                date_range = max(dates) - min(dates)
                if date_range.days > 365:
                    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                elif date_range.days > 90:
                    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                else:
                    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{first_aspect_info.lower().replace('-', '_').replace(' ', '_')}_detailed_analysis.png",
                       dpi=300, bbox_inches='tight')
            print(f"Detailed analysis plot saved as {first_aspect_info.lower().replace('-', '_').replace(' ', '_')}_detailed_analysis.png")
            plt.close(fig)

        print("Visual plots complete! Check the saved PNG files.")
        print()
        print("Plot Legend:")
        print("  • Blue line: Orb distance over time")
        print("  • Green points: Applying (getting closer)")
        print("  • Orange points: Separating (moving away)")
        print("  • Red points: Retrograde motion")
        print("  • Purple star: Moment of exact aspect")
        print("  • Red shaded areas: Retrograde periods")
        print()

    else:
        print("Matplotlib not available. Install with:")
        print("  pip install matplotlib")
        print("to enable visual plotting features.")
        print()

        print("Sample data points for manual plotting:")
        if saturn_conjunctions and saturn_conjunctions[0].intensity_curve:
            curve = saturn_conjunctions[0].intensity_curve
            for sample in curve.samples[::max(1, len(curve.samples)//10)]:
                retro_marker = " (R)" if sample['retrograde'] else ""
                print(f"  {sample['datetime'].strftime('%Y-%m-%d')}: {sample['orb_value']:.2f}°{retro_marker}")

    print()
    print("=" * 80)
    print("Example complete! The intensity curves feature provides detailed")
    print("time-series data for visualizing how transit aspects evolve,")
    print("including complex patterns during retrograde motion.")
    if MATPLOTLIB_AVAILABLE:
        print("Visual plots have been saved as PNG files for further analysis.")
    print("=" * 80)


if __name__ == "__main__":
    main()