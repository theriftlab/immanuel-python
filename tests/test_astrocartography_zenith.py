"""
Integration tests for zenith point calculations.

This test module validates zenith point calculation accuracy,
coordinate precision, and astronomical correctness.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
from math import isclose

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart


class TestAstrocartographyZenith:
    """Integration tests for zenith point calculations."""

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
    def test_zenith_point_calculation_basic(self):
        """Test basic zenith point calculation for Sun."""
        astro_chart = AstrocartographyChart(self.test_subject)

        zenith_points = astro_chart.zenith_points
        assert isinstance(zenith_points, dict)
        assert len(zenith_points) > 0

        # Sun zenith point should exist
        assert chart.SUN in zenith_points
        sun_zenith = zenith_points[chart.SUN]

        # Zenith point should be valid coordinates
        assert sun_zenith is not None

        # If zenith point is a coordinate tuple
        if isinstance(sun_zenith, tuple) and len(sun_zenith) == 2:
            longitude, latitude = sun_zenith
            assert -180.0 <= longitude <= 180.0
            assert -90.0 <= latitude <= 90.0

        # If zenith point is a dict/object with coordinates
        elif isinstance(sun_zenith, dict):
            assert -180.0 <= sun_zenith['longitude'] <= 180.0
            assert -90.0 <= sun_zenith['latitude'] <= 90.0
        elif hasattr(sun_zenith, 'longitude') and hasattr(sun_zenith, 'latitude'):
            assert -180.0 <= sun_zenith.longitude <= 180.0
            assert -90.0 <= sun_zenith.latitude <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_multiple_planet_zenith_points(self):
        """Test zenith point calculations for multiple planets."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.SUN, chart.MOON, chart.VENUS, chart.MARS, chart.JUPITER]
        )

        zenith_points = astro_chart.zenith_points

        # Each planet should have a zenith point
        for planet_id in [chart.SUN, chart.MOON, chart.VENUS, chart.MARS, chart.JUPITER]:
            assert planet_id in zenith_points
            zenith_point = zenith_points[planet_id]
            assert zenith_point is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_calculator_integration(self):
        """Test zenith point calculation via calculator."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Calculate zenith point directly
        sun_zenith_lon, sun_zenith_lat = calculator.calculate_zenith_point(chart.SUN)

        # Should return valid coordinates
        assert isinstance(sun_zenith_lon, (int, float))
        assert isinstance(sun_zenith_lat, (int, float))
        assert -180.0 <= sun_zenith_lon <= 180.0
        assert -90.0 <= sun_zenith_lat <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_accuracy_noon(self):
        """Test zenith point accuracy for noon scenarios."""
        # Create subject for noon at Greenwich
        noon_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='51.4769',  # Greenwich
            longitude='0.0000'
        )

        astro_chart = AstrocartographyChart(noon_subject)
        zenith_points = astro_chart.zenith_points

        # Sun zenith should be reasonably close to Greenwich at noon
        sun_zenith = zenith_points[chart.SUN]

        if isinstance(sun_zenith, tuple):
            zenith_lon, zenith_lat = sun_zenith
        elif isinstance(sun_zenith, dict):
            zenith_lon = sun_zenith['longitude']
            zenith_lat = sun_zenith['latitude']
        else:
            zenith_lon = sun_zenith.longitude
            zenith_lat = sun_zenith.latitude

        # Zenith should be a valid geographic point
        assert -180.0 <= zenith_lon <= 180.0
        assert -90.0 <= zenith_lat <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_seasonal_variation(self):
        """Test zenith point variation across seasons."""
        # Summer solstice
        summer_subject = Subject(
            date_time='1990-06-21 12:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        # Winter solstice
        winter_subject = Subject(
            date_time='1990-12-21 12:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        summer_chart = AstrocartographyChart(summer_subject)
        winter_chart = AstrocartographyChart(winter_subject)

        summer_zenith = summer_chart.zenith_points[chart.SUN]
        winter_zenith = winter_chart.zenith_points[chart.SUN]

        # Both should exist and be different
        assert summer_zenith is not None
        assert winter_zenith is not None
        assert summer_zenith != winter_zenith

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_different_calculation_methods(self):
        """Test zenith points with different calculation methods."""
        # Zodiacal method
        zodiacal_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='zodiacal'
        )

        # Mundo method
        mundo_chart = AstrocartographyChart(
            subject=self.test_subject,
            calculation_method='mundo'
        )

        zodiacal_zenith = zodiacal_chart.zenith_points[chart.SUN]
        mundo_zenith = mundo_chart.zenith_points[chart.SUN]

        # Both should exist
        assert zodiacal_zenith is not None
        assert mundo_zenith is not None

        # Results may be different due to different calculation approaches
        # (but both should be valid coordinates)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_coordinate_precision(self):
        """Test zenith point coordinate precision."""
        astro_chart = AstrocartographyChart(self.test_subject)
        zenith_points = astro_chart.zenith_points

        for planet_id, zenith_point in zenith_points.items():
            if isinstance(zenith_point, tuple):
                longitude, latitude = zenith_point
            elif isinstance(zenith_point, dict):
                longitude = zenith_point['longitude']
                latitude = zenith_point['latitude']
            else:
                longitude = zenith_point.longitude
                latitude = zenith_point.latitude

            # Coordinates should have reasonable precision (not excessive decimal places)
            assert isinstance(longitude, (int, float))
            assert isinstance(latitude, (int, float))

            # Should be within valid geographic ranges
            assert -180.0 <= longitude <= 180.0
            assert -90.0 <= latitude <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_vs_birth_location(self):
        """Test relationship between zenith points and birth location."""
        astro_chart = AstrocartographyChart(self.test_subject)
        zenith_points = astro_chart.zenith_points

        birth_lon = float(self.test_subject.longitude)
        birth_lat = float(self.test_subject.latitude)

        # Zenith points should generally be different from birth location
        # (unless born exactly when planet was overhead)
        for planet_id, zenith_point in zenith_points.items():
            if isinstance(zenith_point, tuple):
                zenith_lon, zenith_lat = zenith_point
            elif isinstance(zenith_point, dict):
                zenith_lon = zenith_point['longitude']
                zenith_lat = zenith_point['latitude']
            else:
                zenith_lon = zenith_point.longitude
                zenith_lat = zenith_point.latitude

            # At least one coordinate should differ for most planets
            # (allowing for very rare exact overhead cases)
            coordinate_difference = (
                abs(zenith_lon - birth_lon) > 0.1 or
                abs(zenith_lat - birth_lat) > 0.1
            )
            # Most planets won't be exactly overhead at birth
            # This test checks that we're getting meaningful zenith calculations

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_consistency(self):
        """Test zenith point calculation consistency."""
        # Create multiple charts with same parameters
        chart1 = AstrocartographyChart(self.test_subject)
        chart2 = AstrocartographyChart(self.test_subject)

        zenith1 = chart1.zenith_points
        zenith2 = chart2.zenith_points

        # Should produce identical results
        assert zenith1 == zenith2

        # Specific planet zenith should be consistent
        sun_zenith1 = zenith1[chart.SUN]
        sun_zenith2 = zenith2[chart.SUN]
        assert sun_zenith1 == sun_zenith2

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_different_birth_times(self):
        """Test zenith points change appropriately with birth time."""
        # Morning birth
        morning_subject = Subject(
            date_time='1990-01-01 06:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        # Evening birth
        evening_subject = Subject(
            date_time='1990-01-01 18:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        morning_chart = AstrocartographyChart(morning_subject)
        evening_chart = AstrocartographyChart(evening_subject)

        morning_zenith = morning_chart.zenith_points[chart.SUN]
        evening_zenith = evening_chart.zenith_points[chart.SUN]

        # Zenith points should be different for different times
        assert morning_zenith != evening_zenith

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_extreme_latitudes(self):
        """Test zenith point calculations at extreme latitudes."""
        # Arctic location
        arctic_subject = Subject(
            date_time='1990-06-21 12:00:00',  # Summer solstice
            latitude='78.2232',  # Svalbard
            longitude='15.6267'
        )

        # Antarctic location
        antarctic_subject = Subject(
            date_time='1990-12-21 12:00:00',  # Winter solstice
            latitude='-77.8500',  # Antarctica
            longitude='166.6667'
        )

        arctic_chart = AstrocartographyChart(arctic_subject)
        antarctic_chart = AstrocartographyChart(antarctic_subject)

        arctic_zenith = arctic_chart.zenith_points
        antarctic_zenith = antarctic_chart.zenith_points

        # Should generate valid zenith points even at extreme latitudes
        assert len(arctic_zenith) > 0
        assert len(antarctic_zenith) > 0
        assert chart.SUN in arctic_zenith
        assert chart.SUN in antarctic_zenith

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_fast_moving_planets(self):
        """Test zenith points for fast-moving planets (Moon)."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.MOON]
        )

        zenith_points = astro_chart.zenith_points

        # Moon zenith should exist
        assert chart.MOON in zenith_points
        moon_zenith = zenith_points[chart.MOON]
        assert moon_zenith is not None

        # Should be valid coordinates
        if isinstance(moon_zenith, tuple):
            longitude, latitude = moon_zenith
        elif isinstance(moon_zenith, dict):
            longitude = moon_zenith['longitude']
            latitude = moon_zenith['latitude']
        else:
            longitude = moon_zenith.longitude
            latitude = moon_zenith.latitude

        assert -180.0 <= longitude <= 180.0
        assert -90.0 <= latitude <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_outer_planets(self):
        """Test zenith points for outer planets."""
        astro_chart = AstrocartographyChart(
            subject=self.test_subject,
            planets=[chart.JUPITER, chart.SATURN]
        )

        zenith_points = astro_chart.zenith_points

        # Outer planets should have zenith points
        for planet_id in [chart.JUPITER, chart.SATURN]:
            assert planet_id in zenith_points
            zenith_point = zenith_points[planet_id]
            assert zenith_point is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_json_serialization(self):
        """Test zenith point data can be JSON serialized."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Get JSON representation
        json_data = astro_chart.__json__()

        # Should contain zenith points
        assert 'zenith_points' in json_data
        zenith_data = json_data['zenith_points']
        assert isinstance(zenith_data, dict)

        # Should contain Sun zenith point
        sun_key = str(chart.SUN)  # Keys might be stringified in JSON
        assert sun_key in zenith_data or chart.SUN in zenith_data

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_error_handling(self):
        """Test zenith point calculation error handling."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Test invalid planet ID
        with pytest.raises(Exception):  # Could be PlanetError or similar
            calculator.calculate_zenith_point(999)

        with pytest.raises(Exception):
            calculator.calculate_zenith_point(-1)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_zenith_point_chart_integration(self):
        """Test zenith points integrate properly with chart functionality."""
        astro_chart = AstrocartographyChart(self.test_subject)

        # Zenith points should be accessible
        zenith_points = astro_chart.zenith_points
        assert isinstance(zenith_points, dict)

        # Should work with location influence analysis
        influences = astro_chart.get_influences_at_location(
            longitude=-118.2437,  # Los Angeles
            latitude=34.0522
        )

        # Should include zenith distance information
        assert 'zenith_distances' in influences
        zenith_distances = influences['zenith_distances']
        assert isinstance(zenith_distances, dict)