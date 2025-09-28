"""
Performance tests for astrocartography calculations.

This test module validates the 10-second world map calculation requirement
and other performance constraints.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
import time
from datetime import datetime

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart, astrocartography


class TestAstrocartographyPerformance:
    """Performance tests for astrocartography calculations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='40.7128',  # New York
            longitude='-74.0060'
        )
        self.test_julian_date = 2447892.0  # Corresponding Julian date

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_world_map_10_second_requirement(self):
        """Test world map calculation completes within 10 seconds."""
        # Configuration for world map: all major planets, all line types
        major_planets = [
            chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
            chart.JUPITER, chart.SATURN
        ]

        start_time = time.time()

        # Create comprehensive astrocartography chart
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=major_planets,
            line_types=['MC', 'IC', 'ASC', 'DESC'],
            sampling_resolution=0.5,  # Default resolution
            calculation_method='zodiacal'
        )

        # Force calculation by accessing planetary lines
        planetary_lines = astro_chart.planetary_lines
        zenith_points = astro_chart.zenith_points

        end_time = time.time()
        calculation_time = end_time - start_time

        # Verify calculation completed
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) > 0
        assert isinstance(zenith_points, dict)

        # Critical requirement: must complete within 10 seconds
        assert calculation_time <= 10.0, f"World map calculation took {calculation_time:.2f}s, exceeds 10s limit"

        # Log performance for monitoring
        print(f"World map calculation time: {calculation_time:.2f} seconds")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_calculator_performance_validation(self):
        """Test calculator performance validation method."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Test performance estimation
        performance_metrics = calculator.validate_performance(
            planet_count=7,  # Major planets
            line_types=['MC', 'IC', 'ASC', 'DESC'],
            target_seconds=10.0
        )

        assert isinstance(performance_metrics, dict)

        # Should not raise PerformanceError for reasonable configuration
        # (this test verifies the performance validation system works)

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_single_planet_performance(self):
        """Test single planet calculation performance."""
        start_time = time.time()

        # Calculate just Sun lines
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN],
            sampling_resolution=0.5
        )

        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        sun_zenith = astro_chart.zenith_points[chart.SUN]

        end_time = time.time()
        calculation_time = end_time - start_time

        # Single planet should be very fast (under 2 seconds)
        assert calculation_time <= 2.0, f"Single planet calculation took {calculation_time:.2f}s"

        # Verify calculation completed
        assert isinstance(sun_lines, dict)
        assert len(sun_lines) == 4  # All line types
        assert sun_zenith is not None

        print(f"Single planet calculation time: {calculation_time:.2f} seconds")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_sampling_resolution_performance_impact(self):
        """Test how sampling resolution affects performance."""
        # Coarse sampling (faster)
        start_time = time.time()
        coarse_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON],
            sampling_resolution=2.0  # Coarse
        )
        coarse_lines = coarse_chart.planetary_lines
        coarse_time = time.time() - start_time

        # Fine sampling (slower)
        start_time = time.time()
        fine_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON],
            sampling_resolution=0.1  # Fine
        )
        fine_lines = fine_chart.planetary_lines
        fine_time = time.time() - start_time

        # Both should complete
        assert isinstance(coarse_lines, dict)
        assert isinstance(fine_lines, dict)

        # Coarse sampling should be faster than fine sampling
        assert coarse_time <= fine_time

        # Both should be reasonable (under 5 seconds for 2 planets)
        assert coarse_time <= 5.0
        assert fine_time <= 10.0

        print(f"Coarse sampling time: {coarse_time:.2f}s, Fine sampling time: {fine_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_calculation_method_performance(self):
        """Test performance difference between calculation methods."""
        planets = [chart.SUN, chart.MOON, chart.VENUS]

        # Zodiacal method
        start_time = time.time()
        zodiacal_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=planets,
            calculation_method='zodiacal'
        )
        zodiacal_lines = zodiacal_chart.planetary_lines
        zodiacal_time = time.time() - start_time

        # Mundo method
        start_time = time.time()
        mundo_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=planets,
            calculation_method='mundo'
        )
        mundo_lines = mundo_chart.planetary_lines
        mundo_time = time.time() - start_time

        # Both should complete successfully
        assert isinstance(zodiacal_lines, dict)
        assert isinstance(mundo_lines, dict)

        # Both should be reasonably fast (under 5 seconds for 3 planets)
        assert zodiacal_time <= 5.0
        assert mundo_time <= 5.0

        print(f"Zodiacal method time: {zodiacal_time:.2f}s, Mundo method time: {mundo_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_line_type_subset_performance(self):
        """Test performance with subset of line types."""
        # Full line types
        start_time = time.time()
        full_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS],
            line_types=['MC', 'IC', 'ASC', 'DESC']
        )
        full_lines = full_chart.planetary_lines
        full_time = time.time() - start_time

        # Subset line types (should be faster)
        start_time = time.time()
        subset_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS],
            line_types=['MC', 'IC']  # Only vertical lines
        )
        subset_lines = subset_chart.planetary_lines
        subset_time = time.time() - start_time

        # Both should complete
        assert isinstance(full_lines, dict)
        assert isinstance(subset_lines, dict)

        # Subset should be faster or equal
        assert subset_time <= full_time

        # Verify subset has fewer line types
        for planet_id in subset_lines:
            planet_lines = subset_lines[planet_id]
            assert 'MC' in planet_lines
            assert 'IC' in planet_lines
            assert 'ASC' not in planet_lines
            assert 'DESC' not in planet_lines

        print(f"Full lines time: {full_time:.2f}s, Subset lines time: {subset_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_memory_usage_efficiency(self):
        """Test memory usage doesn't grow excessively."""
        import gc
        import sys

        # Force garbage collection before test
        gc.collect()

        # Get baseline memory (approximate)
        initial_objects = len(gc.get_objects())

        # Create multiple charts
        charts = []
        for i in range(5):
            astro_chart = AstrocartographyChart(
                subject=self.test_subject,
                planets=[chart.SUN, chart.MOON],
                sampling_resolution=1.0
            )
            # Access data to ensure calculation
            _ = astro_chart.planetary_lines
            charts.append(astro_chart)

        # Memory shouldn't grow excessively
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects

        # Allow reasonable growth but not excessive
        assert object_growth < 10000, f"Object count grew by {object_growth}, potential memory leak"

        # Clean up
        del charts
        gc.collect()

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_concurrent_chart_creation_performance(self):
        """Test performance when creating multiple charts."""
        start_time = time.time()

        # Create multiple charts sequentially
        charts = []
        for i in range(3):
            subject = Subject(
                date_time=f'199{i}-01-01 12:00:00',
                latitude='40.7128',
                longitude='-74.0060'
            )
            astro_chart = AstrocartographyChart(
                subject=subject,
                planets=[chart.SUN, chart.MOON]
            )
            # Force calculation
            _ = astro_chart.planetary_lines
            charts.append(astro_chart)

        total_time = time.time() - start_time

        # Should complete in reasonable time (under 8 seconds for 3 charts)
        assert total_time <= 8.0, f"3 charts took {total_time:.2f}s, too slow"

        # Verify all charts were created
        assert len(charts) == 3
        for astro_chart in charts:
            assert isinstance(astro_chart.planetary_lines, dict)

        print(f"3 charts creation time: {total_time:.2f} seconds")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_calculator_direct_performance(self):
        """Test calculator direct method performance."""
        calculator = AstrocartographyCalculator(
            julian_date=self.test_julian_date,
            sampling_resolution=0.5
        )

        start_time = time.time()

        # Direct calculator operations
        mc_coords, ic_coords = calculator.calculate_mc_ic_lines(chart.SUN)
        asc_coords, desc_coords = calculator.calculate_ascendant_descendant_lines(chart.SUN)
        zenith_point = calculator.calculate_zenith_point(chart.SUN)

        calculation_time = time.time() - start_time

        # Direct calculation should be fast (under 3 seconds)
        assert calculation_time <= 3.0, f"Direct calculation took {calculation_time:.2f}s"

        # Verify results
        assert isinstance(mc_coords, list)
        assert isinstance(ic_coords, list)
        assert isinstance(asc_coords, list)
        assert isinstance(desc_coords, list)
        assert zenith_point is not None

        print(f"Direct calculator time: {calculation_time:.2f} seconds")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_extreme_configuration_performance(self):
        """Test performance with extreme but valid configuration."""
        # Test with maximum reasonable planet count and finest resolution
        many_planets = [
            chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
            chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO
        ]

        start_time = time.time()

        try:
            extreme_chart = AstrocartographyChart(
                subject=self.test_subject,
                planets=many_planets,
                line_types=['MC', 'IC', 'ASC', 'DESC'],
                sampling_resolution=0.2,  # Fine resolution
                calculation_method='zodiacal'
            )

            # Force calculation
            planetary_lines = extreme_chart.planetary_lines

            calculation_time = time.time() - start_time

            # Should still complete, but may take longer (allow up to 15 seconds)
            assert calculation_time <= 15.0, f"Extreme config took {calculation_time:.2f}s"

            # Verify calculation completed
            assert isinstance(planetary_lines, dict)
            assert len(planetary_lines) == len(many_planets)

            print(f"Extreme configuration time: {calculation_time:.2f} seconds")

        except Exception as e:
            # If performance validation prevents this, that's acceptable
            if "performance" in str(e).lower():
                pytest.skip(f"Configuration prevented by performance validation: {e}")
            else:
                raise

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_coordinate_export_performance(self):
        """Test coordinate export performance."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS]
        )

        # Force calculation first
        _ = astro_chart.planetary_lines

        # Test GeoJSON export performance
        start_time = time.time()
        geojson_data = astro_chart.export_coordinates(format='geojson')
        geojson_time = time.time() - start_time

        # Test KML export performance
        start_time = time.time()
        kml_data = astro_chart.export_coordinates(format='kml')
        kml_time = time.time() - start_time

        # Test CSV export performance
        start_time = time.time()
        csv_data = astro_chart.export_coordinates(format='csv')
        csv_time = time.time() - start_time

        # All exports should be fast (under 2 seconds each)
        assert geojson_time <= 2.0, f"GeoJSON export took {geojson_time:.2f}s"
        assert kml_time <= 2.0, f"KML export took {kml_time:.2f}s"
        assert csv_time <= 2.0, f"CSV export took {csv_time:.2f}s"

        # Verify exports completed
        assert isinstance(geojson_data, dict)
        assert isinstance(kml_data, str)
        assert isinstance(csv_data, str)

        total_export_time = geojson_time + kml_time + csv_time
        print(f"Export times - GeoJSON: {geojson_time:.2f}s, KML: {kml_time:.2f}s, CSV: {csv_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.astrocartography
    def test_performance_regression_baseline(self):
        """Test performance baseline for regression detection."""
        # Standard configuration for baseline measurement
        baseline_config = {
            'planets': [chart.SUN, chart.MOON, chart.VENUS, chart.MARS],
            'line_types': ['MC', 'IC', 'ASC', 'DESC'],
            'sampling_resolution': 0.5,
            'calculation_method': 'zodiacal'
        }

        start_time = time.time()

        baseline_chart = AstrocartographyChart(
            subject=self.test_subject,
            **baseline_config
        )

        # Force full calculation
        planetary_lines = baseline_chart.planetary_lines
        zenith_points = baseline_chart.zenith_points

        baseline_time = time.time() - start_time

        # Baseline should complete within 5 seconds
        assert baseline_time <= 5.0, f"Baseline took {baseline_time:.2f}s, performance regression detected"

        # Verify calculation completed
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) == 4  # 4 planets
        assert isinstance(zenith_points, dict)

        print(f"Performance baseline: {baseline_time:.2f} seconds for 4 planets")

        # Store baseline for future regression testing
        # (In practice, this could write to a performance log file)