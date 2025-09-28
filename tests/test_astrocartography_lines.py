"""
Integration tests for planetary line calculations.

This test module validates planetary line calculation accuracy,
coordinate generation, and line type behavior.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
from math import isclose

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart, astrocartography


class TestAstrocartographyLines:
    """Integration tests for planetary line calculations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='40.7128',  # New York
            longitude='-74.0060'
        )
        self.test_julian_date = 2447892.0  # Corresponding Julian date

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_mc_ic_line_calculations(self):
        """Test MC and IC line calculations for accuracy and structure."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Get Sun MC and IC lines
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        mc_line = sun_lines['MC']
        ic_line = sun_lines['IC']

        # MC and IC lines should exist
        assert mc_line is not None
        assert ic_line is not None

        # MC and IC should be vertical lines (constant longitude)
        # Test this by checking if all coordinates have same longitude
        if hasattr(mc_line, 'coordinates') and mc_line.coordinates:
            mc_coords = mc_line.coordinates
            if len(mc_coords) > 1:
                first_lon = mc_coords[0][0]
                for lon, lat in mc_coords:
                    assert isclose(lon, first_lon, abs_tol=0.1), "MC line should be vertical"

        # IC line should be 180 degrees opposite to MC
        if hasattr(ic_line, 'coordinates') and ic_line.coordinates:
            ic_coords = ic_line.coordinates
            if len(ic_coords) > 1:
                first_lon = ic_coords[0][0]
                for lon, lat in ic_coords:
                    assert isclose(lon, first_lon, abs_tol=0.1), "IC line should be vertical"

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_ascendant_descendant_line_calculations(self):
        """Test Ascendant and Descendant line calculations."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Get Sun Ascendant and Descendant lines
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        asc_line = sun_lines['ASC']
        desc_line = sun_lines['DESC']

        # ASC and DESC lines should exist
        assert asc_line is not None
        assert desc_line is not None

        # ASC and DESC should be curved lines (varying longitude with latitude)
        if hasattr(asc_line, 'coordinates') and asc_line.coordinates:
            asc_coords = asc_line.coordinates
            if len(asc_coords) > 2:
                # Check that longitude varies across different latitudes
                longitudes = [coord[0] for coord in asc_coords]
                assert max(longitudes) - min(longitudes) > 1.0, "ASC line should be curved"

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_multiple_planet_line_calculations(self):
        """Test line calculations for multiple planets."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS, chart.MARS]
        )

        planetary_lines = astro_chart.planetary_lines

        # Each planet should have all four line types
        for planet_id in [chart.SUN, chart.MOON, chart.VENUS, chart.MARS]:
            assert planet_id in planetary_lines
            planet_lines = planetary_lines[planet_id]

            for line_type in ['MC', 'IC', 'ASC', 'DESC']:
                assert line_type in planet_lines
                assert planet_lines[line_type] is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_calculation_with_different_methods(self):
        """Test line calculations with zodiacal vs mundo methods."""
        # Zodiacal method chart
        zodiacal_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='zodiacal'
        )

        # Mundo method chart
        mundo_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='mundo'
        )

        # Get Sun lines from both methods
        zodiacal_sun = zodiacal_chart.get_lines_for_planet(chart.SUN)
        mundo_sun = mundo_chart.get_lines_for_planet(chart.SUN)

        # Both should have all line types
        for line_type in ['MC', 'IC', 'ASC', 'DESC']:
            assert line_type in zodiacal_sun
            assert line_type in mundo_sun
            assert zodiacal_sun[line_type] is not None
            assert mundo_sun[line_type] is not None

        # Results should be different (different calculation approaches)
        assert zodiacal_sun != mundo_sun

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_sampling_resolution_effects(self):
        """Test how sampling resolution affects line detail."""
        # Coarse sampling
        coarse_chart = AstrocartographyChart(
            subject=self.test_subject,
            sampling_resolution=2.0
        )

        # Fine sampling
        fine_chart = AstrocartographyChart(
            subject=self.test_subject,
            sampling_resolution=0.5
        )

        # Get Sun ASC lines (curved, most affected by sampling)
        coarse_asc = coarse_chart.get_lines_for_planet(chart.SUN)['ASC']
        fine_asc = fine_chart.get_lines_for_planet(chart.SUN)['ASC']

        # Both should exist
        assert coarse_asc is not None
        assert fine_asc is not None

        # Fine sampling should generally have more coordinates
        if hasattr(coarse_asc, 'coordinates') and hasattr(fine_asc, 'coordinates'):
            if coarse_asc.coordinates and fine_asc.coordinates:
                assert len(fine_asc.coordinates) >= len(coarse_asc.coordinates)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_coordinate_accuracy(self):
        """Test coordinate accuracy and precision."""
        astro_chart = AstrocartographyChart(self.test_subject)
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)

        for line_type, line in sun_lines.items():
            if hasattr(line, 'coordinates') and line.coordinates:
                for longitude, latitude in line.coordinates:
                    # Coordinates should be within valid ranges
                    assert -180.0 <= longitude <= 180.0, f"Invalid longitude in {line_type} line"
                    assert -90.0 <= latitude <= 90.0, f"Invalid latitude in {line_type} line"

                    # Coordinates should have reasonable precision
                    assert isinstance(longitude, (int, float))
                    assert isinstance(latitude, (int, float))

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_geographic_coverage(self):
        """Test that lines provide adequate geographic coverage."""
        astro_chart = AstrocartographyChart(self.test_subject)
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)

        # MC and IC lines should span full latitude range
        for line_type in ['MC', 'IC']:
            line = sun_lines[line_type]
            if hasattr(line, 'coordinates') and line.coordinates:
                latitudes = [coord[1] for coord in line.coordinates]
                lat_range = max(latitudes) - min(latitudes)
                assert lat_range >= 120.0, f"{line_type} should span significant latitude range"

        # ASC and DESC lines should span significant longitude range
        for line_type in ['ASC', 'DESC']:
            line = sun_lines[line_type]
            if hasattr(line, 'coordinates') and line.coordinates:
                longitudes = [coord[0] for coord in line.coordinates]
                if len(longitudes) > 1:
                    lon_range = max(longitudes) - min(longitudes)
                    # Account for potential longitude wrapping
                    if lon_range > 180:
                        lon_range = 360 - lon_range
                    assert lon_range >= 30.0, f"{line_type} should span significant longitude range"

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_calculator_integration_with_chart(self):
        """Test integration between calculator and chart classes."""
        astro_chart = AstrocartographyChart(self.test_subject)
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Chart should produce same basic planetary position as calculator
        chart_sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        calc_sun_position = calculator.get_planetary_position(chart.SUN)

        # Both should exist and provide consistent data
        assert chart_sun_lines is not None
        assert calc_sun_position is not None
        assert isinstance(calc_sun_position, dict)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_type_access_methods(self):
        """Test different methods of accessing line data."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS]
        )

        # Test get_lines_for_planet
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        assert isinstance(sun_lines, dict)
        assert 'MC' in sun_lines

        # Test get_lines_by_type
        mc_lines = astro_chart.get_lines_by_type('MC')
        assert isinstance(mc_lines, dict)
        assert chart.SUN in mc_lines

        # Verify consistency between access methods
        sun_mc_from_planet = sun_lines['MC']
        sun_mc_from_type = mc_lines[chart.SUN]
        assert sun_mc_from_planet == sun_mc_from_type

        # Test all line types are accessible
        for line_type in ['MC', 'IC', 'ASC', 'DESC']:
            type_lines = astro_chart.get_lines_by_type(line_type)
            assert isinstance(type_lines, dict)
            assert len(type_lines) >= 3  # Should have at least Sun, Moon, Venus

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_calculation_edge_cases(self):
        """Test line calculations handle edge cases properly."""
        # Test subject at extreme latitude
        arctic_subject = Subject(
            date_time='1990-06-21 12:00:00',  # Summer solstice
            latitude='78.2232',  # Svalbard
            longitude='15.6267'
        )

        arctic_chart = AstrocartographyChart(arctic_subject)
        arctic_lines = arctic_chart.planetary_lines

        # Should still generate lines even at extreme latitude
        assert len(arctic_lines) > 0
        assert chart.SUN in arctic_lines

        # Test subject at equator
        equator_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='0.0',  # Equator
            longitude='0.0'  # Prime meridian
        )

        equator_chart = AstrocartographyChart(equator_subject)
        equator_lines = equator_chart.planetary_lines

        # Should generate lines at equator
        assert len(equator_lines) > 0
        assert chart.SUN in equator_lines

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_calculations_with_custom_line_types(self):
        """Test line calculations with custom line type selection."""
        # Test with only MC and IC
        chart_mc_ic = AstrocartographyChart(
            subject=self.test_subject,
            line_types=['MC', 'IC']
        )

        sun_lines = chart_mc_ic.get_lines_for_planet(chart.SUN)
        assert 'MC' in sun_lines
        assert 'IC' in sun_lines
        assert 'ASC' not in sun_lines
        assert 'DESC' not in sun_lines

        # Test with only ASC and DESC
        chart_asc_desc = AstrocartographyChart(
            subject=self.test_subject,
            line_types=['ASC', 'DESC']
        )

        sun_lines_2 = chart_asc_desc.get_lines_for_planet(chart.SUN)
        assert 'ASC' in sun_lines_2
        assert 'DESC' in sun_lines_2
        assert 'MC' not in sun_lines_2
        assert 'IC' not in sun_lines_2

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_data_consistency(self):
        """Test data consistency across multiple calculations."""
        # Create multiple charts with same parameters
        chart1 = AstrocartographyChart(self.test_subject)
        chart2 = AstrocartographyChart(self.test_subject)

        # Should produce identical results
        sun_lines1 = chart1.get_lines_for_planet(chart.SUN)
        sun_lines2 = chart2.get_lines_for_planet(chart.SUN)

        assert sun_lines1 == sun_lines2

        # Zenith points should also be consistent
        zenith1 = chart1.zenith_points
        zenith2 = chart2.zenith_points

        assert zenith1 == zenith2

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_calculations_with_orb_influence(self):
        """Test how orb influence affects line calculations."""
        # Chart with default orb
        default_chart = AstrocartographyChart(self.test_subject)

        # Chart with custom orb
        custom_chart = AstrocartographyChart(
            subject=self.test_subject,
            orb_influence_km=100.0
        )

        # Both should generate lines
        default_lines = default_chart.planetary_lines
        custom_lines = custom_chart.planetary_lines

        assert len(default_lines) > 0
        assert len(custom_lines) > 0

        # Should have same basic structure
        assert chart.SUN in default_lines
        assert chart.SUN in custom_lines