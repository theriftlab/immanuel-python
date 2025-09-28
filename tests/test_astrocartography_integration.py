"""
Integration tests for basic astrocartography chart generation.

This test module validates end-to-end chart generation workflow
and integration between components.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
from datetime import datetime

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.const import chart


class TestAstrocartographyIntegration:
    """Integration tests for astrocartography chart generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='40.7128',  # New York
            longitude='-74.0060'
        )

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_basic_chart_generation_workflow(self):
        """Test complete chart generation from Subject to planetary lines."""
        # Create chart
        astro_chart = AstrocartographyChart(self.test_subject)

        # Verify chart was created
        assert isinstance(astro_chart, AstrocartographyChart)
        assert astro_chart.subject == self.test_subject

        # Verify planetary lines are generated
        planetary_lines = astro_chart.planetary_lines
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) > 0

        # Verify Sun lines exist (fundamental requirement)
        assert chart.SUN in planetary_lines
        sun_lines = planetary_lines[chart.SUN]
        assert isinstance(sun_lines, dict)

        # Verify all line types for Sun
        expected_line_types = ['MC', 'IC', 'ASC', 'DESC']
        for line_type in expected_line_types:
            assert line_type in sun_lines
            line_data = sun_lines[line_type]
            assert line_data is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_chart_with_default_planets(self):
        """Test chart generation includes all default planets."""
        astro_chart = AstrocartographyChart(self.test_subject)

        planetary_lines = astro_chart.planetary_lines

        # Should include luminaries and major planets by default
        expected_planets = [chart.SUN, chart.MOON]
        for planet_id in expected_planets:
            assert planet_id in planetary_lines

            planet_lines = planetary_lines[planet_id]
            assert isinstance(planet_lines, dict)
            assert len(planet_lines) == 4  # MC, IC, ASC, DESC

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_chart_with_custom_planets(self):
        """Test chart generation with custom planet selection."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.VENUS, chart.MARS]
        )

        planetary_lines = astro_chart.planetary_lines

        # Should only include specified planets
        assert chart.SUN in planetary_lines
        assert chart.VENUS in planetary_lines
        assert chart.MARS in planetary_lines

        # Should not include unspecified planets
        assert chart.MOON not in planetary_lines

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_points_generation(self):
        """Test zenith points are correctly generated."""
        astro_chart = AstrocartographyChart(self.test_subject)

        zenith_points = astro_chart.zenith_points
        assert isinstance(zenith_points, dict)
        assert len(zenith_points) > 0

        # Verify Sun zenith point exists
        assert chart.SUN in zenith_points
        sun_zenith = zenith_points[chart.SUN]

        # Zenith point should be a coordinate tuple or dict
        assert sun_zenith is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_chart_calculation_methods(self):
        """Test chart generation with different calculation methods."""
        # Test zodiacal method
        zodiacal_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='zodiacal'
        )
        assert zodiacal_chart.planetary_lines is not None

        # Test mundo method
        mundo_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='mundo'
        )
        assert mundo_chart.planetary_lines is not None

        # Results should be different between methods
        zodiacal_sun = zodiacal_chart.get_lines_for_planet(chart.SUN)
        mundo_sun = mundo_chart.get_lines_for_planet(chart.SUN)

        # At least one coordinate should differ (different calculation approach)
        assert zodiacal_sun != mundo_sun

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_chart_with_custom_sampling(self):
        """Test chart generation with custom sampling resolution."""
        # Test coarse sampling
        coarse_chart = AstrocartographyChart(
            subject=self.test_subject,
            sampling_resolution=2.0
        )
        assert coarse_chart.planetary_lines is not None

        # Test fine sampling
        fine_chart = AstrocartographyChart(
            subject=self.test_subject,
            sampling_resolution=0.1
        )
        assert fine_chart.planetary_lines is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_location_influence_analysis(self):
        """Test location influence analysis integration."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Test influences at Los Angeles
        influences = astro_chart.get_influences_at_location(
            longitude=-118.2437,
            latitude=34.0522
        )

        assert isinstance(influences, dict)
        assert 'active_lines' in influences
        assert 'nearby_lines' in influences
        assert 'zenith_distances' in influences

        # Should return meaningful data
        assert influences['active_lines'] is not None
        assert influences['nearby_lines'] is not None
        assert influences['zenith_distances'] is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_line_access_methods_integration(self):
        """Test planetary line access methods work together."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Test get_lines_for_planet
        sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
        assert isinstance(sun_lines, dict)
        assert 'MC' in sun_lines

        # Test get_lines_by_type
        mc_lines = astro_chart.get_lines_by_type('MC')
        assert isinstance(mc_lines, dict)
        assert chart.SUN in mc_lines

        # Cross-verify data consistency
        sun_mc_from_planet = sun_lines['MC']
        sun_mc_from_type = mc_lines[chart.SUN]
        assert sun_mc_from_planet == sun_mc_from_type

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_coordinate_export_integration(self):
        """Test coordinate export functionality integration."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Test GeoJSON export
        geojson_data = astro_chart.export_coordinates(format='geojson')
        assert isinstance(geojson_data, dict)
        assert 'type' in geojson_data
        assert 'features' in geojson_data

        # Test KML export
        kml_data = astro_chart.export_coordinates(format='kml')
        assert isinstance(kml_data, str)
        assert 'kml' in kml_data.lower()

        # Test CSV export
        csv_data = astro_chart.export_coordinates(format='csv')
        assert isinstance(csv_data, str)
        assert ',' in csv_data  # Should contain comma separators

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_json_serialization_integration(self):
        """Test complete JSON serialization workflow."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Test JSON serialization
        json_data = astro_chart.__json__()
        assert isinstance(json_data, dict)

        # Should contain key chart data
        assert 'planetary_lines' in json_data
        assert 'zenith_points' in json_data
        assert 'subject' in json_data

        # Planetary lines should be serializable
        planetary_lines = json_data['planetary_lines']
        assert isinstance(planetary_lines, dict)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_advanced_features_integration(self):
        """Test advanced features integration when enabled."""
        # Test with parans enabled
        paran_chart = AstrocartographyChart(
            subject=self.test_subject,
            include_parans=True
        )

        paran_lines = paran_chart.paran_lines
        assert isinstance(paran_lines, list)

        # Test with local space enabled
        local_chart = AstrocartographyChart(
            subject=self.test_subject,
            include_local_space=True
        )

        local_lines = local_chart.local_space_lines
        assert isinstance(local_lines, dict)

        # Test with aspect lines enabled
        aspect_config = {
            'aspects': [0, 90, 120, 180],
            'relocated_date': datetime(2025, 6, 21),
            'orb_tolerance': 1.0
        }

        aspect_chart = AstrocartographyChart(
            subject=self.test_subject,
            aspect_lines_config=aspect_config
        )

        aspect_lines = aspect_chart.aspect_lines
        assert isinstance(aspect_lines, list)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_travel_recommendations_integration(self):
        """Test travel recommendations integration."""
        astro_chart = AstrocartographyChart(self.test_subject)

        recommendations = astro_chart.calculate_travel_recommendations(
            target_influences=['Sun_MC', 'Venus_ASC'],
            max_distance_km=5000
        )

        assert isinstance(recommendations, list)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_different_birth_locations(self):
        """Test chart generation works for different birth locations."""
        # Test Southern Hemisphere location
        sydney_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='-33.8688',  # Sydney
            longitude='151.2093'
        )

        sydney_chart = AstrocartographyChart(sydney_subject)
        sydney_lines = sydney_chart.planetary_lines
        assert len(sydney_lines) > 0

        # Test different Northern location
        london_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='51.5074',  # London
            longitude='-0.1278'
        )

        london_chart = AstrocartographyChart(london_subject)
        london_lines = london_chart.planetary_lines
        assert len(london_lines) > 0

        # Charts should have different line positions
        assert sydney_lines != london_lines

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_string_representation_integration(self):
        """Test string representation provides meaningful information."""
        astro_chart = AstrocartographyChart(self.test_subject)

        str_repr = str(astro_chart)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

        # Should contain relevant information
        assert 'astrocartography' in str_repr.lower() or 'chart' in str_repr.lower()

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_error_handling_integration(self):
        """Test error handling across integrated components."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Test invalid planet ID handling
        with pytest.raises(Exception):
            astro_chart.get_lines_for_planet(999)

        # Test invalid line type handling
        with pytest.raises(Exception):
            astro_chart.get_lines_by_type('INVALID')

        # Test invalid coordinates handling
        with pytest.raises(ValueError):
            astro_chart.get_influences_at_location(
                longitude=200,  # Invalid
                latitude=100    # Invalid
            )

        # Test invalid export format handling
        with pytest.raises(ValueError):
            astro_chart.export_coordinates(format='invalid')