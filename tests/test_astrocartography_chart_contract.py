"""
Contract tests for AstrocartographyChart class API.

This test module validates the public interface and behavior of the
AstrocartographyChart class according to its contract specification.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
from datetime import datetime
from typing import Dict, List, Optional

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject
from immanuel.charts import AstrocartographyChart
from immanuel.const import chart


class TestAstrocartographyChartContract:
    """Contract tests for AstrocartographyChart class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='40.7128',  # New York
            longitude='-74.0060'
        )

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_astrocartography_chart_initialization(self):
        """Test AstrocartographyChart can be initialized with Subject."""
        chart = AstrocartographyChart(self.test_subject)

        assert isinstance(chart, AstrocartographyChart)
        assert chart.subject == self.test_subject

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_astrocartography_chart_with_custom_config(self):
        """Test AstrocartographyChart initialization with custom configuration."""
        chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON],
            line_types=['MC', 'IC'],
            calculation_method='zodiacal',
            sampling_resolution=1.0,
            orb_influence_km=100.0,
            include_parans=True,
            include_local_space=True
        )

        assert isinstance(chart, AstrocartographyChart)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_planetary_lines_property(self):
        """Test planetary_lines property returns expected structure."""
        chart = AstrocartographyChart(self.test_subject)

        planetary_lines = chart.planetary_lines
        assert isinstance(planetary_lines, dict)

        # Should contain planet IDs as keys
        for planet_id, lines in planetary_lines.items():
            assert isinstance(planet_id, int)
            assert isinstance(lines, dict)

            # Should contain line types as keys
            for line_type, line in lines.items():
                assert line_type in ['MC', 'IC', 'ASC', 'DESC']

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_zenith_points_property(self):
        """Test zenith_points property returns expected structure."""
        chart = AstrocartographyChart(self.test_subject)

        zenith_points = chart.zenith_points
        assert isinstance(zenith_points, dict)

        # Should contain planet IDs as keys
        for planet_id, zenith_point in zenith_points.items():
            assert isinstance(planet_id, int)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_get_lines_for_planet(self):
        """Test get_lines_for_planet method."""
        chart = AstrocartographyChart(self.test_subject)

        sun_lines = chart.get_lines_for_planet(chart.SUN)
        assert isinstance(sun_lines, dict)

        # Should contain all line types
        expected_line_types = ['MC', 'IC', 'ASC', 'DESC']
        for line_type in expected_line_types:
            assert line_type in sun_lines

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_get_lines_by_type(self):
        """Test get_lines_by_type method."""
        chart = AstrocartographyChart(self.test_subject)

        mc_lines = chart.get_lines_by_type('MC')
        assert isinstance(mc_lines, dict)

        # Should contain planet IDs as keys
        for planet_id, line in mc_lines.items():
            assert isinstance(planet_id, int)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_get_influences_at_location(self):
        """Test get_influences_at_location method."""
        chart = AstrocartographyChart(self.test_subject)

        influences = chart.get_influences_at_location(
            longitude=-118.2437,  # Los Angeles
            latitude=34.0522
        )

        assert isinstance(influences, dict)
        assert 'active_lines' in influences
        assert 'nearby_lines' in influences
        assert 'zenith_distances' in influences

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_calculate_travel_recommendations(self):
        """Test calculate_travel_recommendations method."""
        chart = AstrocartographyChart(self.test_subject)

        recommendations = chart.calculate_travel_recommendations(
            target_influences=['Sun_MC', 'Venus_ASC'],
            max_distance_km=5000
        )

        assert isinstance(recommendations, list)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_export_coordinates(self):
        """Test export_coordinates method."""
        chart = AstrocartographyChart(self.test_subject)

        # Test GeoJSON export
        geojson_data = chart.export_coordinates(format='geojson', include_orbs=True)
        assert isinstance(geojson_data, dict)

        # Test KML export
        kml_data = chart.export_coordinates(format='kml')
        assert isinstance(kml_data, str)

        # Test CSV export
        csv_data = chart.export_coordinates(format='csv')
        assert isinstance(csv_data, str)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_json_serialization(self):
        """Test JSON serialization via __json__ method."""
        chart = AstrocartographyChart(self.test_subject)

        json_data = chart.__json__()
        assert isinstance(json_data, dict)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_string_representation(self):
        """Test string representation via __str__ method."""
        chart = AstrocartographyChart(self.test_subject)

        str_repr = str(chart)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_invalid_subject_raises_error(self):
        """Test that invalid subject raises appropriate error."""
        with pytest.raises((ValueError, TypeError)):
            AstrocartographyChart(None)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_invalid_coordinates_raises_error(self):
        """Test that invalid coordinates raise appropriate error."""
        chart = AstrocartographyChart(self.test_subject)

        with pytest.raises(ValueError):
            chart.get_influences_at_location(longitude=200, latitude=100)  # Invalid coordinates

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_invalid_export_format_raises_error(self):
        """Test that invalid export format raises appropriate error."""
        chart = AstrocartographyChart(self.test_subject)

        with pytest.raises(ValueError):
            chart.export_coordinates(format='invalid_format')

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_paran_lines_property(self):
        """Test paran_lines property when enabled."""
        chart = AstrocartographyChart(self.test_subject, include_parans=True)

        paran_lines = chart.paran_lines
        assert isinstance(paran_lines, list)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_local_space_lines_property(self):
        """Test local_space_lines property when enabled."""
        chart = AstrocartographyChart(self.test_subject, include_local_space=True)

        local_space_lines = chart.local_space_lines
        assert isinstance(local_space_lines, dict)

    @pytest.mark.contract
    @pytest.mark.astrocartography
    def test_aspect_lines_property(self):
        """Test aspect_lines property when configured."""
        aspect_config = {
            'aspects': [0, 60, 90, 120, 180],
            'relocated_date': datetime(2025, 6, 21),
            'orb_tolerance': 1.0
        }

        chart = AstrocartographyChart(
            self.test_subject,
            aspect_lines_config=aspect_config
        )

        aspect_lines = chart.aspect_lines
        assert isinstance(aspect_lines, list)