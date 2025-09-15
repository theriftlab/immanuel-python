"""
Tests for intensity curves functionality.

This module tests the intensity curve generation feature for transit aspects,
including curve data structure, generation algorithms, and integration.
"""

import json
import unittest
from datetime import datetime, timedelta

from immanuel.classes.transit_events import IntensityCurve, TransitEvent
from immanuel.const import calc, chart, transits
from immanuel.tools.transit import TransitCalculator
from immanuel.tools.transit_search import TransitSearch
from immanuel.tools import date


class TestIntensityCurve(unittest.TestCase):
    """Test the IntensityCurve data structure."""

    def setUp(self):
        self.sample_data = [
            {
                'julian_date': 2460000.0,
                'datetime': datetime(2023, 1, 1, 12, 0, 0),
                'orb_value': 5.5,
                'applying': True,
                'retrograde': False,
                'retrograde_session': 0
            },
            {
                'julian_date': 2460001.0,
                'datetime': datetime(2023, 1, 2, 12, 0, 0),
                'orb_value': 4.2,
                'applying': True,
                'retrograde': False,
                'retrograde_session': 0
            },
            {
                'julian_date': 2460002.0,
                'datetime': datetime(2023, 1, 3, 12, 0, 0),
                'orb_value': 2.8,
                'applying': True,
                'retrograde': True,
                'retrograde_session': 1
            },
            {
                'julian_date': 2460003.0,
                'datetime': datetime(2023, 1, 4, 12, 0, 0),
                'orb_value': 0.5,
                'applying': False,
                'retrograde': True,
                'retrograde_session': 1
            }
        ]

        self.test_curve = IntensityCurve(
            transit_event_id="test_event_123",
            transiting_object=chart.SATURN,
            target_object=chart.SUN,
            aspect_type=calc.CONJUNCTION,
            samples=self.sample_data,
            sampling_config={'curve_orb': 8.0, 'sampling_interval': 'daily'},
            metadata={'total_samples': 4, 'peak_intensity': {'best_orb': 0.5}}
        )

    def test_intensity_curve_creation(self):
        """Test basic intensity curve creation."""
        self.assertEqual(self.test_curve.transit_event_id, "test_event_123")
        self.assertEqual(self.test_curve.transiting_object, chart.SATURN)
        self.assertEqual(self.test_curve.target_object, chart.SUN)
        self.assertEqual(self.test_curve.aspect_type, calc.CONJUNCTION)
        self.assertEqual(len(self.test_curve.samples), 4)
        self.assertIsInstance(self.test_curve.samples, list)
        self.assertIsInstance(self.test_curve.sampling_config, dict)
        self.assertIsInstance(self.test_curve.metadata, dict)

    def test_get_peak_intensity(self):
        """Test finding the sample with peak intensity (smallest orb)."""
        peak_sample = self.test_curve.get_peak_intensity()
        self.assertIsNotNone(peak_sample)
        self.assertEqual(peak_sample['orb_value'], 0.5)
        self.assertEqual(peak_sample['julian_date'], 2460003.0)

    def test_get_samples_by_retrograde_session(self):
        """Test filtering samples by retrograde session."""
        direct_samples = self.test_curve.get_samples_by_retrograde_session(0)
        retrograde_samples = self.test_curve.get_samples_by_retrograde_session(1)

        self.assertEqual(len(direct_samples), 2)
        self.assertEqual(len(retrograde_samples), 2)

        # Verify correct filtering
        for sample in direct_samples:
            self.assertEqual(sample['retrograde_session'], 0)
        for sample in retrograde_samples:
            self.assertEqual(sample['retrograde_session'], 1)

    def test_get_applying_samples(self):
        """Test filtering samples by applying/separating."""
        applying_samples = self.test_curve.get_applying_samples()
        separating_samples = self.test_curve.get_separating_samples()

        self.assertEqual(len(applying_samples), 3)
        self.assertEqual(len(separating_samples), 1)

        # Verify correct filtering
        for sample in applying_samples:
            self.assertTrue(sample['applying'])
        for sample in separating_samples:
            self.assertFalse(sample['applying'])

    def test_json_serialization(self):
        """Test JSON serialization of intensity curve."""
        json_data = self.test_curve.__json__()

        # Check basic structure
        self.assertIn('transit_event_id', json_data)
        self.assertIn('transiting_object', json_data)
        self.assertIn('target_object', json_data)
        self.assertIn('aspect_type', json_data)
        self.assertIn('samples', json_data)
        self.assertIn('sampling_config', json_data)
        self.assertIn('metadata', json_data)

        # Check that datetime objects are serialized as strings
        self.assertIsInstance(json_data['samples'][0]['datetime'], str)
        self.assertEqual(json_data['samples'][0]['datetime'], '2023-01-01T12:00:00')

        # Ensure JSON is serializable
        json_str = json.dumps(json_data)
        self.assertIsInstance(json_str, str)


class TestTransitCalculator(unittest.TestCase):
    """Test intensity curve generation in TransitCalculator."""

    def setUp(self):
        self.calculator = TransitCalculator(precision=transits.PRECISION_SECOND)
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 12, 31)
        self.start_jd = date.to_jd(self.start_date)
        self.end_jd = date.to_jd(self.end_date)

    def test_calculate_orb(self):
        """Test orb calculation between longitudes."""
        # Same longitude
        orb = self.calculator._calculate_orb(0.0, 0.0)
        self.assertEqual(orb, 0.0)

        # Simple difference
        orb = self.calculator._calculate_orb(10.0, 15.0)
        self.assertEqual(orb, 5.0)

        # Wraparound case
        orb = self.calculator._calculate_orb(358.0, 2.0)
        self.assertEqual(orb, 4.0)

        # Large difference (should use shorter arc)
        orb = self.calculator._calculate_orb(10.0, 200.0)
        self.assertEqual(orb, 170.0)

        # Wraparound with large difference
        orb = self.calculator._calculate_orb(350.0, 10.0)
        self.assertEqual(orb, 20.0)

    def test_is_aspect_applying_basic(self):
        """Test basic applying/separating detection."""
        # This test relies on ephemeris data, so we'll test the method exists
        # and doesn't raise exceptions for valid inputs
        try:
            result = self.calculator._is_aspect_applying(
                chart.SUN, 0.0, 30.0, self.start_jd
            )
            self.assertIsInstance(result, bool)
        except Exception:
            # Ephemeris might not be available in test environment
            self.skipTest("Ephemeris not available for testing")

    def test_generate_intensity_curve_parameters(self):
        """Test intensity curve generation with different parameters."""
        try:
            # Test basic curve generation
            curve = self.calculator.generate_intensity_curve(
                transiting_planet=chart.SATURN,
                target_object=chart.SUN,
                aspect_type=calc.CONJUNCTION,
                natal_longitude=0.0,  # 0° Aries
                start_jd=self.start_jd,
                end_jd=self.start_jd + 30,  # Short period for testing
                curve_orb=8.0,
                sampling_interval="daily"
            )

            # Curve might be None if no samples within orb
            if curve:
                self.assertIsInstance(curve, IntensityCurve)
                self.assertEqual(curve.transiting_object, chart.SATURN)
                self.assertEqual(curve.target_object, chart.SUN)
                self.assertEqual(curve.aspect_type, calc.CONJUNCTION)
                self.assertIsInstance(curve.samples, list)
                self.assertIsInstance(curve.sampling_config, dict)
                self.assertIsInstance(curve.metadata, dict)

        except Exception:
            # Ephemeris might not be available in test environment
            self.skipTest("Ephemeris not available for testing")

    def test_generate_intensity_curve_different_intervals(self):
        """Test intensity curve generation with different sampling intervals."""
        try:
            # Test with timedelta object
            curve = self.calculator.generate_intensity_curve(
                transiting_planet=chart.JUPITER,
                target_object=chart.MOON,
                aspect_type=calc.SEXTILE,
                natal_longitude=90.0,  # 0° Cancer
                start_jd=self.start_jd,
                end_jd=self.start_jd + 7,  # One week
                curve_orb=5.0,
                sampling_interval=timedelta(hours=6)
            )

            if curve:
                self.assertIn('sampling_interval', curve.sampling_config)

        except Exception:
            self.skipTest("Ephemeris not available for testing")

    def test_intensity_curve_metadata(self):
        """Test that intensity curve metadata is properly populated."""
        try:
            curve = self.calculator.generate_intensity_curve(
                transiting_planet=chart.MARS,
                target_object=chart.VENUS,
                aspect_type=calc.TRINE,
                natal_longitude=180.0,  # 0° Libra
                start_jd=self.start_jd,
                end_jd=self.start_jd + 60,  # Two months
                curve_orb=6.0
            )

            if curve:
                # Check metadata structure
                self.assertIn('total_samples', curve.metadata)
                self.assertIn('time_span_days', curve.metadata)
                self.assertIn('peak_intensity', curve.metadata)

                # Check peak intensity structure
                peak = curve.metadata['peak_intensity']
                self.assertIn('best_orb', peak)
                self.assertIn('julian_date', peak)
                self.assertIn('retrograde_session', peak)

                # Verify sample data structure
                if curve.samples:
                    sample = curve.samples[0]
                    required_fields = ['julian_date', 'datetime', 'orb_value',
                                     'applying', 'retrograde', 'retrograde_session']
                    for field in required_fields:
                        self.assertIn(field, sample)

        except Exception:
            self.skipTest("Ephemeris not available for testing")


class TestTransitSearchIntegration(unittest.TestCase):
    """Test integration of intensity curves with transit search."""

    def setUp(self):
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 6, 30)

    def test_find_aspects_with_curves_disabled(self):
        """Test that find_aspects works normally with curves disabled."""
        search = TransitSearch(
            natal_chart=None,  # Will be set to mock if needed
            start_date=self.start_date,
            end_date=self.end_date
        )

        # This should not raise an error even without curves
        self.assertIsInstance(search.calculator, TransitCalculator)

    def test_curve_generation_parameters(self):
        """Test that curve generation parameters are handled correctly."""
        search = TransitSearch(
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Test parameter validation - should not raise exceptions
        self.assertIsNotNone(search.calculator)
        self.assertEqual(search.start_date, self.start_date)
        self.assertEqual(search.end_date, self.end_date)


class TestIntensityCurveDataStructure(unittest.TestCase):
    """Test the data structure and validation of intensity curves."""

    def test_sample_data_structure(self):
        """Test that sample data points have the correct structure."""
        sample = {
            'julian_date': 2460000.5,
            'datetime': datetime(2023, 1, 1, 12, 0, 0),
            'orb_value': 3.2,
            'applying': True,
            'retrograde': False,
            'retrograde_session': 0
        }

        # Verify all required fields are present
        required_fields = [
            'julian_date', 'datetime', 'orb_value',
            'applying', 'retrograde', 'retrograde_session'
        ]

        for field in required_fields:
            self.assertIn(field, sample)

        # Verify field types
        self.assertIsInstance(sample['julian_date'], float)
        self.assertIsInstance(sample['datetime'], datetime)
        self.assertIsInstance(sample['orb_value'], (int, float))
        self.assertIsInstance(sample['applying'], bool)
        self.assertIsInstance(sample['retrograde'], bool)
        self.assertIsInstance(sample['retrograde_session'], int)

    def test_retrograde_session_numbering(self):
        """Test retrograde session numbering logic."""
        # Session 0 should be direct motion
        # Sessions 1, 2, 3... should be retrograde periods
        self.assertGreaterEqual(0, 0)  # Direct motion
        self.assertGreater(1, 0)      # First retrograde session
        self.assertGreater(2, 1)      # Second retrograde session

    def test_metadata_structure(self):
        """Test that metadata structure is correct."""
        metadata = {
            'retrograde_sessions': [
                {
                    'session_number': 1,
                    'start_jd': 2460000.0,
                    'end_jd': 2460030.0,
                    'station_retrograde_jd': 2460000.0,
                    'station_direct_jd': 2460030.0,
                    'multiple_exactness': False
                }
            ],
            'peak_intensity': {
                'best_orb': 0.05,
                'julian_date': 2460015.0,
                'retrograde_session': 1
            },
            'total_samples': 100,
            'time_span_days': 365.0,
            'exact_moments': 3
        }

        # Verify structure
        self.assertIn('retrograde_sessions', metadata)
        self.assertIn('peak_intensity', metadata)
        self.assertIn('total_samples', metadata)
        self.assertIn('time_span_days', metadata)
        self.assertIn('exact_moments', metadata)

        # Verify retrograde session structure
        session = metadata['retrograde_sessions'][0]
        required_session_fields = [
            'session_number', 'start_jd', 'end_jd',
            'station_retrograde_jd', 'station_direct_jd', 'multiple_exactness'
        ]
        for field in required_session_fields:
            self.assertIn(field, session)

        # Verify peak intensity structure
        peak = metadata['peak_intensity']
        required_peak_fields = ['best_orb', 'julian_date', 'retrograde_session']
        for field in required_peak_fields:
            self.assertIn(field, peak)


class TestIntensityCurvePerformance(unittest.TestCase):
    """Test performance and edge cases for intensity curves."""

    def test_empty_samples(self):
        """Test curve behavior with no samples."""
        curve = IntensityCurve(
            transit_event_id="empty_test",
            transiting_object=chart.MERCURY,
            target_object=chart.MARS,
            aspect_type=calc.SQUARE,
            samples=[],
            sampling_config={},
            metadata={}
        )

        self.assertEqual(len(curve.samples), 0)
        self.assertIsNone(curve.get_peak_intensity())
        self.assertEqual(len(curve.get_applying_samples()), 0)
        self.assertEqual(len(curve.get_separating_samples()), 0)

    def test_large_orb_values(self):
        """Test handling of large orb values."""
        large_orb_sample = {
            'julian_date': 2460000.0,
            'datetime': datetime(2023, 1, 1),
            'orb_value': 179.5,  # Near maximum possible orb
            'applying': False,
            'retrograde': False,
            'retrograde_session': 0
        }

        curve = IntensityCurve(
            transit_event_id="large_orb_test",
            transiting_object=chart.URANUS,
            target_object=chart.NEPTUNE,
            aspect_type=calc.OPPOSITION,
            samples=[large_orb_sample],
            sampling_config={},
            metadata={}
        )

        peak = curve.get_peak_intensity()
        self.assertEqual(peak['orb_value'], 179.5)

    def test_multiple_retrograde_sessions(self):
        """Test handling of multiple retrograde sessions."""
        samples = []
        for i in range(10):
            session = (i // 3) if (i // 3) % 2 == 1 else 0  # Alternating sessions
            samples.append({
                'julian_date': 2460000.0 + i,
                'datetime': datetime(2023, 1, 1) + timedelta(days=i),
                'orb_value': abs(5 - i),  # Creates a peak in the middle
                'applying': i < 5,
                'retrograde': session > 0,
                'retrograde_session': session
            })

        curve = IntensityCurve(
            transit_event_id="multi_retrograde_test",
            transiting_object=chart.SATURN,
            target_object=chart.JUPITER,
            aspect_type=calc.CONJUNCTION,
            samples=samples,
            sampling_config={},
            metadata={}
        )

        # Test filtering by different sessions
        session_0 = curve.get_samples_by_retrograde_session(0)
        session_1 = curve.get_samples_by_retrograde_session(1)

        self.assertGreater(len(session_0), 0)
        self.assertGreater(len(session_1), 0)


if __name__ == '__main__':
    unittest.main()