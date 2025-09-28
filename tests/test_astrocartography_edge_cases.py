"""
Edge case tests for astrocartography calculations.

This test module validates handling of extreme latitudes, edge coordinates,
and other boundary conditions.
These tests MUST FAIL initially to enforce TDD approach.
"""

import pytest
from datetime import datetime

# These imports will fail initially - that's expected for TDD
from immanuel import charts
from immanuel.charts import Subject, AstrocartographyChart
from immanuel.tools.astrocartography import AstrocartographyCalculator
from immanuel.const import chart, astrocartography


class TestAstrocartographyEdgeCases:
    """Edge case tests for astrocartography calculations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_julian_date = 2447892.0  # 1990-01-01 12:00:00

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_extreme_north_latitude(self):
        """Test calculations at extreme northern latitude."""
        # Arctic location - Svalbard
        arctic_subject = Subject(
            date_time='1990-06-21 12:00:00',  # Summer solstice for best conditions
            latitude='78.2232',  # Svalbard - very far north
            longitude='15.6267'
        )

        astro_chart = AstrocartographyChart(arctic_subject)

        # Should still generate planetary lines
        planetary_lines = astro_chart.planetary_lines
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) > 0

        # Sun lines should exist
        assert chart.SUN in planetary_lines
        sun_lines = planetary_lines[chart.SUN]
        assert isinstance(sun_lines, dict)

        # All line types should be present (may use interpolation)
        for line_type in ['MC', 'IC', 'ASC', 'DESC']:
            assert line_type in sun_lines
            line = sun_lines[line_type]
            assert line is not None

        # Zenith points should still be calculated
        zenith_points = astro_chart.zenith_points
        assert isinstance(zenith_points, dict)
        assert chart.SUN in zenith_points

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_extreme_south_latitude(self):
        """Test calculations at extreme southern latitude."""
        # Antarctic location
        antarctic_subject = Subject(
            date_time='1990-12-21 12:00:00',  # Summer solstice in southern hemisphere
            latitude='-77.8500',  # Antarctica - very far south
            longitude='166.6667'
        )

        astro_chart = AstrocartographyChart(antarctic_subject)

        # Should still generate planetary lines
        planetary_lines = astro_chart.planetary_lines
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) > 0

        # Sun lines should exist
        assert chart.SUN in planetary_lines
        sun_lines = planetary_lines[chart.SUN]

        # All line types should be present
        for line_type in ['MC', 'IC', 'ASC', 'DESC']:
            assert line_type in sun_lines
            assert sun_lines[line_type] is not None

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_polar_regions_interpolation(self):
        """Test interpolation handling for polar regions."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Test interpolation method with extreme latitude scenario
        partial_coords = [
            (-74.0, -80.0), (-74.0, -60.0), (-74.0, -40.0),
            (-74.0, -20.0), (-74.0, 0.0), (-74.0, 20.0),
            (-74.0, 40.0), (-74.0, 60.0), (-74.0, 80.0)
        ]

        # Request interpolation to full polar range
        interpolated_coords = calculator.interpolate_line_at_extremes(
            partial_coordinates=partial_coords,
            target_latitude_range=(-90.0, 90.0)
        )

        # Should extend coverage
        assert isinstance(interpolated_coords, list)
        assert len(interpolated_coords) >= len(partial_coords)

        # Should include extreme latitudes
        latitudes = [coord[1] for coord in interpolated_coords]
        min_lat = min(latitudes)
        max_lat = max(latitudes)

        # Should get closer to poles
        assert min_lat <= -85.0  # Close to south pole
        assert max_lat >= 85.0   # Close to north pole

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_date_line_crossing(self):
        """Test calculations that cross the international date line."""
        # Location near date line
        fiji_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='-18.1248',  # Fiji
            longitude='178.4501'  # Near date line
        )

        astro_chart = AstrocartographyChart(fiji_subject)
        planetary_lines = astro_chart.planetary_lines

        # Should handle longitude wrapping properly
        assert isinstance(planetary_lines, dict)
        assert len(planetary_lines) > 0

        # Verify coordinates are valid across date line
        for planet_id, planet_lines in planetary_lines.items():
            for line_type, line in planet_lines.items():
                if hasattr(line, 'coordinates') and line.coordinates:
                    for longitude, latitude in line.coordinates:
                        assert -180.0 <= longitude <= 180.0
                        assert -90.0 <= latitude <= 90.0

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_equatorial_crossing(self):
        """Test calculations that cross the equator."""
        # Location on equator
        equator_subject = Subject(
            date_time='1990-03-21 12:00:00',  # Equinox
            latitude='0.0',  # Equator
            longitude='0.0'  # Prime meridian
        )

        astro_chart = AstrocartographyChart(equator_subject)
        planetary_lines = astro_chart.planetary_lines

        # Should handle equatorial calculations
        assert isinstance(planetary_lines, dict)
        assert chart.SUN in planetary_lines

        # Ascendant/Descendant lines should cross equator smoothly
        sun_lines = planetary_lines[chart.SUN]
        for line_type in ['ASC', 'DESC']:
            line = sun_lines[line_type]
            if hasattr(line, 'coordinates') and line.coordinates:
                latitudes = [coord[1] for coord in line.coordinates]
                # Should span across equator
                has_north = any(lat > 0 for lat in latitudes)
                has_south = any(lat < 0 for lat in latitudes)
                assert has_north or has_south  # Should cross or approach equator

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_midnight_sun_conditions(self):
        """Test calculations during midnight sun conditions."""
        # Arctic summer - midnight sun scenario
        midnight_sun_subject = Subject(
            date_time='1990-06-21 00:00:00',  # Midnight on summer solstice
            latitude='78.2232',  # Svalbard
            longitude='15.6267'
        )

        astro_chart = AstrocartographyChart(midnight_sun_subject)

        # Should handle extreme solar conditions
        planetary_lines = astro_chart.planetary_lines
        assert isinstance(planetary_lines, dict)

        # Sun should still have calculable lines despite extreme conditions
        assert chart.SUN in planetary_lines
        sun_lines = planetary_lines[chart.SUN]

        # At least MC/IC should be calculable (vertical lines)
        assert 'MC' in sun_lines
        assert 'IC' in sun_lines

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_polar_night_conditions(self):
        """Test calculations during polar night conditions."""
        # Arctic winter - polar night scenario
        polar_night_subject = Subject(
            date_time='1990-12-21 12:00:00',  # Winter solstice
            latitude='78.2232',  # Svalbard
            longitude='15.6267'
        )

        astro_chart = AstrocartographyChart(polar_night_subject)

        # Should handle polar night conditions
        planetary_lines = astro_chart.planetary_lines
        assert isinstance(planetary_lines, dict)

        # Sun lines should still be calculable
        assert chart.SUN in planetary_lines
        sun_lines = planetary_lines[chart.SUN]

        # MC/IC lines should always be calculable
        assert 'MC' in sun_lines
        assert 'IC' in sun_lines

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_calculator_extreme_latitude_handling(self):
        """Test calculator handles extreme latitudes properly."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Test ASC/DESC calculation at extreme latitude
        try:
            asc_coords, desc_coords = calculator.calculate_ascendant_descendant_lines(
                planet_id=chart.SUN,
                latitude_range=(-85.0, 85.0)  # Near polar regions
            )

            # Should either succeed or raise appropriate error
            assert isinstance(asc_coords, list)
            assert isinstance(desc_coords, list)

        except Exception as e:
            # Should raise appropriate error type for extreme conditions
            error_name = type(e).__name__
            assert 'extreme' in error_name.lower() or 'latitude' in error_name.lower()

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_boundary_coordinate_validation(self):
        """Test validation of boundary coordinates."""
        # Test exactly at coordinate boundaries
        boundary_cases = [
            {'latitude': '90.0', 'longitude': '0.0'},      # North pole
            {'latitude': '-90.0', 'longitude': '0.0'},     # South pole
            {'latitude': '0.0', 'longitude': '180.0'},     # Date line east
            {'latitude': '0.0', 'longitude': '-180.0'},    # Date line west
            {'latitude': '0.0', 'longitude': '0.0'},       # Prime meridian
        ]

        for coords in boundary_cases:
            try:
                boundary_subject = Subject(
                    date_time='1990-01-01 12:00:00',
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )

                astro_chart = AstrocartographyChart(boundary_subject)
                planetary_lines = astro_chart.planetary_lines

                # Should handle boundary coordinates
                assert isinstance(planetary_lines, dict)

            except Exception as e:
                # Poles might be handled specially
                if coords['latitude'] in ['90.0', '-90.0']:
                    # Acceptable to raise error for exact poles
                    assert 'latitude' in str(e).lower() or 'pole' in str(e).lower()
                else:
                    # Other boundaries should work
                    raise

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_invalid_coordinate_handling(self):
        """Test proper error handling for invalid coordinates."""
        invalid_cases = [
            {'latitude': '95.0', 'longitude': '0.0'},      # Invalid latitude > 90
            {'latitude': '-95.0', 'longitude': '0.0'},     # Invalid latitude < -90
            {'latitude': '0.0', 'longitude': '200.0'},     # Invalid longitude > 180
            {'latitude': '0.0', 'longitude': '-200.0'},    # Invalid longitude < -180
        ]

        for coords in invalid_cases:
            with pytest.raises((ValueError, TypeError)):
                invalid_subject = Subject(
                    date_time='1990-01-01 12:00:00',
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )
                # Subject creation or chart creation should fail
                AstrocartographyChart(invalid_subject)

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_calculator_invalid_ranges(self):
        """Test calculator error handling for invalid ranges."""
        calculator = AstrocartographyCalculator(self.test_julian_date)

        # Invalid latitude range (min > max)
        with pytest.raises(ValueError):
            calculator.calculate_mc_ic_lines(
                planet_id=chart.SUN,
                latitude_range=(60.0, -60.0)  # Invalid: min > max
            )

        # Invalid longitude range (min > max, accounting for wrapping)
        with pytest.raises(ValueError):
            calculator.calculate_ascendant_descendant_lines(
                planet_id=chart.SUN,
                longitude_range=(180.0, -180.0)  # Might be invalid depending on implementation
            )

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_extreme_sampling_resolutions(self):
        """Test handling of extreme sampling resolutions."""
        # Very coarse sampling
        coarse_subject = Subject(
            date_time='1990-01-01 12:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        coarse_chart = AstrocartographyChart(
            subject=coarse_subject,
            sampling_resolution=5.0  # Very coarse
        )

        # Should still work with coarse sampling
        coarse_lines = coarse_chart.planetary_lines
        assert isinstance(coarse_lines, dict)

        # Very fine sampling (may be slow or cause performance error)
        try:
            fine_chart = AstrocartographyChart(
                subject=coarse_subject,
                sampling_resolution=0.01  # Very fine
            )
            fine_lines = fine_chart.planetary_lines
            assert isinstance(fine_lines, dict)

        except Exception as e:
            # May be prevented by performance validation
            if 'performance' in str(e).lower():
                # This is acceptable behavior
                pass
            else:
                raise

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_calculation_stability_near_poles(self):
        """Test calculation stability near polar regions."""
        # Test multiple high-latitude locations
        high_latitude_coords = [
            ('82.0', '0.0'),    # High north
            ('-82.0', '90.0'),  # High south
            ('85.0', '180.0'),  # Very high north
            ('-85.0', '-90.0'), # Very high south
        ]

        for lat, lon in high_latitude_coords:
            high_lat_subject = Subject(
                date_time='1990-01-01 12:00:00',
                latitude=lat,
                longitude=lon
            )

            try:
                high_lat_chart = AstrocartographyChart(high_lat_subject)
                planetary_lines = high_lat_chart.planetary_lines

                # Should produce some valid results
                assert isinstance(planetary_lines, dict)

                # At minimum, should have Sun data
                if chart.SUN in planetary_lines:
                    sun_lines = planetary_lines[chart.SUN]
                    # MC/IC should always be calculable
                    assert 'MC' in sun_lines
                    assert 'IC' in sun_lines

            except Exception as e:
                # Some extreme latitudes might require special handling
                error_type = type(e).__name__
                # Should be specific error types, not general failures
                assert any(keyword in error_type.lower() for keyword in
                          ['extreme', 'latitude', 'calculation', 'interpolation'])

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_temporal_edge_cases(self):
        """Test edge cases with extreme dates."""
        # Very old date
        ancient_subject = Subject(
            date_time='1600-01-01 12:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        # Future date
        future_subject = Subject(
            date_time='2100-01-01 12:00:00',
            latitude='40.7128',
            longitude='-74.0060'
        )

        for subject in [ancient_subject, future_subject]:
            try:
                temporal_chart = AstrocartographyChart(subject)
                planetary_lines = temporal_chart.planetary_lines

                # Should handle extreme dates
                assert isinstance(planetary_lines, dict)

            except Exception as e:
                # Swiss Ephemeris may have date range limitations
                if 'ephemeris' in str(e).lower() or 'date' in str(e).lower():
                    # This is acceptable - ephemeris has valid date ranges
                    pass
                else:
                    raise

    @pytest.mark.integration
    @pytest.mark.astrocartography
    def test_orb_influence_edge_cases(self):
        """Test edge cases with orb influence calculations."""
        # Test with very small orb
        small_orb_chart = AstrocartographyChart(
            subject=Subject(
                date_time='1990-01-01 12:00:00',
                latitude='40.7128',
                longitude='-74.0060'
            ),
            orb_influence_km=1.0  # Very small orb
        )

        influences = small_orb_chart.get_influences_at_location(
            longitude=-74.0,  # Very close to birth location
            latitude=40.7
        )

        assert isinstance(influences, dict)

        # Test with very large orb
        large_orb_chart = AstrocartographyChart(
            subject=Subject(
                date_time='1990-01-01 12:00:00',
                latitude='40.7128',
                longitude='-74.0060'
            ),
            orb_influence_km=1000.0  # Very large orb
        )

        influences_large = large_orb_chart.get_influences_at_location(
            longitude=-118.2437,  # Los Angeles - far away
            latitude=34.0522
        )

        assert isinstance(influences_large, dict)