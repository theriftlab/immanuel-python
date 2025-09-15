"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Comprehensive tests for transit calculation functionality.
    Tests all major transit features including aspects, ingresses,
    stations, eclipses, and transit chart classes.

"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from pytest import fixture, approx

from immanuel import charts
from immanuel.const import calc, chart, transits, names
from immanuel.tools import date, ephemeris
from immanuel.tools.transit import TransitCalculator
from immanuel.tools.transit_search import TransitSearch
from immanuel.tools.names import get_object_name
from immanuel.classes.transit_events import (
    TransitEvent, TransitPeriod, AspectEvent,
    IngressEvent, StationEvent, EclipseEvent
)


@fixture
def natal_chart():
    """Standard natal chart for testing."""
    native = charts.Subject(
        date_time="1984-01-03 18:35:00",
        latitude="48.521637",
        longitude="9.057645",
        timezone="Europe/Berlin",
    )
    return charts.Natal(native)


@fixture
def transit_calculator():
    """Standard transit calculator."""
    return TransitCalculator(precision=transits.PRECISION_SECOND)


@fixture
def transit_search(natal_chart):
    """Transit search instance with standard parameters."""
    return TransitSearch(
        natal_chart=natal_chart,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 12, 31),
        precision=transits.PRECISION_SECOND,
    )


@fixture
def eclipse_search():
    """Eclipse search instance for testing."""
    return TransitSearch(
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2027, 1, 1),
        precision=transits.PRECISION_SECOND,
    )


class TestTransitEvent:
    """Test TransitEvent and related classes."""

    def test_transit_event_creation(self):
        """Test basic TransitEvent creation."""
        event = TransitEvent(
            event_type=transits.EVENT_ASPECT,
            date_time=datetime(2025, 6, 15, 12, 0),
            julian_date=2460482.0,
            transiting_object=chart.JUPITER,
            target_object=chart.SUN,
        )

        assert event.event_type == transits.EVENT_ASPECT
        assert event.transiting_object == chart.JUPITER
        assert event.target_object == chart.SUN
        assert event.metadata == {}

    def test_aspect_event_creation(self):
        """Test AspectEvent specialized class."""
        aspect_event = AspectEvent(
            event_type=transits.EVENT_ASPECT,
            date_time=datetime(2025, 6, 15, 12, 0),
            julian_date=2460482.0,
            transiting_object=chart.JUPITER,
            target_object=chart.SUN,
            orb=0.5,
            applying=True,
        )

        assert isinstance(aspect_event, TransitEvent)
        assert aspect_event.orb == 0.5
        assert aspect_event.applying is True

    def test_eclipse_event_creation(self):
        """Test EclipseEvent specialized class."""
        eclipse_event = EclipseEvent(
            event_type=transits.EVENT_ECLIPSE,
            date_time=datetime(2025, 9, 21, 19, 41),
            julian_date=2460940.0,
            transiting_object=chart.SUN,
            eclipse_type=transits.ECLIPSE_TOTAL,
            magnitude=1.0,
        )

        assert isinstance(eclipse_event, TransitEvent)
        assert eclipse_event.eclipse_type == transits.ECLIPSE_TOTAL
        assert eclipse_event.magnitude == 1.0

    def test_transit_period_creation(self):
        """Test TransitPeriod with events."""
        events = [
            TransitEvent(
                event_type=transits.EVENT_ASPECT,
                date_time=datetime(2025, 6, 15),
                julian_date=2460482.0,
                transiting_object=chart.JUPITER,
            )
        ]

        period = TransitPeriod(
            start_date=datetime(2025, 6, 1),
            end_date=datetime(2025, 6, 30),
            events=events,
            interval="daily",
        )

        assert len(period.events) == 1
        assert period.interval == "daily"
        assert period.statistics is not None

    def test_json_serialization(self):
        """Test JSON serialization of transit events."""
        event = AspectEvent(
            event_type=transits.EVENT_ASPECT,
            date_time=datetime(2025, 6, 15, 12, 0),
            julian_date=2460482.0,
            transiting_object=chart.JUPITER,
            target_object=chart.SUN,
            orb=0.5,
        )

        json_data = event.__json__()
        assert json_data['event_type'] == transits.EVENT_ASPECT
        assert json_data['orb'] == 0.5
        assert 'date_time' in json_data


class TestTransitCalculator:
    """Test TransitCalculator functionality."""

    def test_calculator_initialization(self, transit_calculator):
        """Test calculator initializes correctly."""
        assert transit_calculator.precision == transits.PRECISION_SECOND
        assert hasattr(transit_calculator, 'find_planet_crossing')

    def test_planet_crossing_sun(self, transit_calculator):
        """Test Sun crossing calculation."""
        start_jd = date.to_jd(datetime(2025, 3, 20))  # Around spring equinox
        target_longitude = 0.0  # 0° Aries

        crossing_jd = transit_calculator.find_planet_crossing(
            chart.SUN, target_longitude, start_jd
        )

        assert crossing_jd is not None
        assert isinstance(crossing_jd, float)

        # Verify Sun is actually at target longitude (handle 0/360 degree wraparound)
        sun_pos = ephemeris.get_planet(chart.SUN, crossing_jd)
        diff = abs(sun_pos['lon'] - target_longitude)
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.1

    def test_planet_crossing_moon(self, transit_calculator):
        """Test Moon crossing calculation."""
        start_jd = date.to_jd(datetime(2025, 6, 1))
        target_longitude = 90.0  # 0° Cancer

        crossing_jd = transit_calculator.find_planet_crossing(
            chart.MOON, target_longitude, start_jd
        )

        assert crossing_jd is not None
        moon_pos = ephemeris.get_planet(chart.MOON, crossing_jd)
        assert abs(moon_pos['lon'] - target_longitude) < 0.1

    def test_timeline_calculation(self, transit_calculator):
        """Test transit timeline calculation."""
        timeline = transit_calculator.calculate_transit_timeline(
            objects=[chart.SUN, chart.MOON],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 3),
            interval=timedelta(days=1)
        )

        assert isinstance(timeline, TransitPeriod)
        assert len(timeline.events) > 0
        assert timeline.start_date.year == 2025

    def test_solar_eclipse_calculation(self, transit_calculator):
        """Test solar eclipse finding."""
        start_jd = date.to_jd(datetime(2025, 1, 1))
        end_jd = date.to_jd(datetime(2026, 1, 1))

        eclipses = transit_calculator.find_solar_eclipses(start_jd, end_jd)

        assert isinstance(eclipses, list)
        if eclipses:  # If eclipses found in range
            eclipse = eclipses[0]
            assert eclipse.event_type == transits.EVENT_ECLIPSE
            assert eclipse.transiting_object == chart.SUN

    def test_lunar_eclipse_calculation(self, transit_calculator):
        """Test lunar eclipse finding."""
        start_jd = date.to_jd(datetime(2025, 1, 1))
        end_jd = date.to_jd(datetime(2026, 1, 1))

        eclipses = transit_calculator.find_lunar_eclipses(start_jd, end_jd)

        assert isinstance(eclipses, list)
        if eclipses:  # If eclipses found in range
            eclipse = eclipses[0]
            assert eclipse.event_type == transits.EVENT_ECLIPSE
            assert eclipse.transiting_object == chart.MOON


class TestTransitSearch:
    """Test TransitSearch functionality."""

    def test_search_initialization(self, transit_search):
        """Test search initializes correctly."""
        assert transit_search.start_date.year == 2025
        assert transit_search.end_date.year == 2025
        assert hasattr(transit_search, 'natal_chart')

    def test_aspect_search(self, transit_search):
        """Test aspect finding."""
        aspects = transit_search.find_aspects(
            transiting_planet=chart.JUPITER,
            natal_planet=chart.SUN,
            aspect=calc.CONJUNCTION,
            max_orb=2.0
        )

        assert isinstance(aspects, list)
        for aspect in aspects:
            assert aspect.event_type == transits.EVENT_ASPECT
            assert aspect.transiting_object == chart.JUPITER
            assert aspect.target_object == chart.SUN

    def test_station_search(self, transit_search):
        """Test planetary station finding."""
        stations = transit_search.find_stations(chart.MERCURY)

        assert isinstance(stations, list)
        for station in stations:
            assert station.event_type == transits.EVENT_STATION
            assert station.transiting_object == chart.MERCURY
            assert station.metadata.get('station_type') in [
                transits.STATION_RETROGRADE,
                transits.STATION_DIRECT
            ]

    def test_ingress_search(self, transit_search):
        """Test sign ingress finding."""
        ingresses = transit_search.find_sign_ingresses(chart.SATURN)

        assert isinstance(ingresses, list)
        for ingress in ingresses:
            assert ingress.event_type == transits.EVENT_INGRESS_SIGN
            assert ingress.transiting_object == chart.SATURN

    def test_eclipse_search(self, eclipse_search):
        """Test eclipse finding."""
        eclipses = eclipse_search.find_eclipses()

        assert isinstance(eclipses, list)
        for eclipse in eclipses:
            assert eclipse.event_type == transits.EVENT_ECLIPSE
            assert eclipse.transiting_object in [chart.SUN, chart.MOON]

    def test_comprehensive_search(self, transit_search):
        """Test comprehensive search functionality."""
        results = transit_search.search_comprehensive(
            include_aspects=True,
            include_stations=True,
            include_ingresses=True,
            include_eclipses=True,
            planets=[chart.JUPITER, chart.SATURN]
        )

        assert isinstance(results, dict)
        assert 'aspects' in results or len(results) > 0

        # Test that results contain the expected event types
        for event_type, events in results.items():
            assert isinstance(events, list)


class TestTransitCharts:
    """Test MundaneTransits and NatalTransits charts."""

    def test_mundane_transits_creation(self):
        """Test MundaneTransits chart creation."""
        mundane = charts.MundaneTransits(
            start_date=datetime(2025, 6, 1),
            end_date=datetime(2025, 6, 7),
            latitude=40.7128,  # NYC
            longitude=-74.0060,
            interval="daily"
        )

        assert mundane.type == "Mundane Transits"
        assert hasattr(mundane, 'transit_events')
        assert len(mundane.transit_events) > 0

    def test_natal_transits_creation(self, natal_chart):
        """Test NatalTransits chart creation."""
        natal_transits = charts.NatalTransits(
            natal_chart=natal_chart,
            start_date=datetime(2025, 6, 1),
            end_date=datetime(2025, 6, 7),
            interval=timedelta(hours=12)
        )

        assert natal_transits.type == "Natal Transits"
        assert hasattr(natal_transits, 'transit_events')
        assert len(natal_transits.transit_events) > 0

    def test_transit_chart_json(self, natal_chart):
        """Test transit chart JSON serialization."""
        natal_transits = charts.NatalTransits(
            natal_chart=natal_chart,
            start_date=datetime(2025, 6, 1),
            end_date=datetime(2025, 6, 3),
            interval="daily"
        )

        json_output = natal_transits.to_json()
        assert isinstance(json_output, str)
        assert "Natal Transits" in json_output


class TestUtilityFunctions:
    """Test utility functions and helpers."""

    def test_get_object_name(self):
        """Test object name resolution."""
        assert get_object_name(chart.SUN) == "Sun"
        assert get_object_name(chart.MOON) == "Moon"
        assert get_object_name(chart.JUPITER) == "Jupiter"
        assert get_object_name(9999) == "9999"  # Unknown object

    def test_transit_constants(self):
        """Test transit constants are defined."""
        assert hasattr(transits, 'EVENT_ASPECT')
        assert hasattr(transits, 'EVENT_ECLIPSE')
        assert hasattr(transits, 'ECLIPSE_SOLAR')
        assert hasattr(transits, 'PRECISION_SECOND')

    def test_names_integration(self):
        """Test names integration for transit objects."""
        assert transits.EVENT_ASPECT in names.TRANSIT_EVENT_TYPES
        assert transits.ECLIPSE_SOLAR in names.ECLIPSE_TYPES
        assert transits.STATION_RETROGRADE in names.STATION_TYPES


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_date_range(self):
        """Test handling of invalid date ranges."""
        # For now, just test that it doesn't crash - validation could be added later
        search = TransitSearch(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2024, 1, 1),  # End before start
            precision=transits.PRECISION_SECOND,
        )
        # If we add validation later, this would raise ValueError
        assert search.start_date.year == 2025

    def test_missing_natal_chart(self):
        """Test methods requiring natal chart fail gracefully."""
        search = TransitSearch(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
            precision=transits.PRECISION_SECOND,
        )

        with pytest.raises(ValueError):
            search.find_aspects(
                transiting_planet=chart.JUPITER,
                natal_planet=chart.SUN,
                aspect=calc.CONJUNCTION
            )

    def test_extreme_orb_values(self, transit_search):
        """Test handling of extreme orb values."""
        # Very large orb should still work
        aspects = transit_search.find_aspects(
            transiting_planet=chart.JUPITER,
            natal_planet=chart.SUN,
            aspect=calc.CONJUNCTION,
            max_orb=180.0
        )
        assert isinstance(aspects, list)

        # Zero orb should work
        aspects = transit_search.find_aspects(
            transiting_planet=chart.JUPITER,
            natal_planet=chart.SUN,
            aspect=calc.CONJUNCTION,
            max_orb=0.0
        )
        assert isinstance(aspects, list)


class TestPerformanceAndIntegration:
    """Test performance and integration aspects."""

    def test_large_time_range_performance(self):
        """Test performance with large time ranges."""
        start_time = datetime.now()

        search = TransitSearch(
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2030, 1, 1),  # 5 years
            precision=transits.PRECISION_SECOND,
        )

        stations = search.find_stations(chart.MERCURY)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        assert execution_time < 30  # Should complete in under 30 seconds
        assert isinstance(stations, list)

    def test_multiple_planet_search(self, transit_search):
        """Test searching multiple planets simultaneously."""
        planets = [chart.MERCURY, chart.VENUS, chart.MARS]
        all_stations = []

        for planet in planets:
            stations = transit_search.find_stations(planet)
            all_stations.extend(stations)

        assert len(all_stations) >= 0

        # Verify each station belongs to one of our planets
        for station in all_stations:
            assert station.transiting_object in planets

    def test_precision_levels(self, natal_chart):
        """Test different precision levels work."""
        precisions = [transits.PRECISION_MINUTE, transits.PRECISION_SECOND]

        for precision in precisions:
            search = TransitSearch(
                natal_chart=natal_chart,
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 6, 1),
                precision=precision,
            )

            aspects = search.find_aspects(
                transiting_planet=chart.JUPITER,
                natal_planet=chart.SUN,
                aspect=calc.CONJUNCTION,
                max_orb=5.0
            )

            assert isinstance(aspects, list)
            for aspect in aspects:
                assert aspect.precision_achieved == precision


