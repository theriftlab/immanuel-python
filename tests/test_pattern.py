"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Test aspect pattern detection and various birth charts with known
chart shapes. Celebrity natal chart data & chart shapes are courtesy of
https://horoscopes.astro-seek.com

"""

from datetime import datetime

from pytest import fixture

from immanuel import charts
from immanuel.const import calc, chart
from immanuel.reports import aspect, pattern
from immanuel.tools import convert, date, ephemeris


@fixture
def aspect_objects():
    return {
        chart.SUN: {
            "index": chart.SUN,
            "speed": 0.0,
            "lon": None,
        },
        chart.MOON: {
            "index": chart.MOON,
            "speed": 0.0,
            "lon": None,
        },
        chart.MERCURY: {
            "index": chart.MERCURY,
            "speed": 0.0,
            "lon": None,
        },
        chart.VENUS: {
            "index": chart.VENUS,
            "speed": 0.0,
            "lon": None,
        },
        chart.MARS: {
            "index": chart.MARS,
            "speed": 0.0,
            "lon": None,
        },
        chart.JUPITER: {
            "index": chart.JUPITER,
            "speed": 0.0,
            "lon": None,
        },
        chart.SATURN: {
            "index": chart.SATURN,
            "speed": 0.0,
            "lon": None,
        },
        chart.URANUS: {
            "index": chart.URANUS,
            "speed": 0.0,
            "lon": None,
        },
        chart.NEPTUNE: {
            "index": chart.NEPTUNE,
            "speed": 0.0,
            "lon": None,
        },
        chart.PLUTO: {
            "index": chart.PLUTO,
            "speed": 0.0,
            "lon": None,
        },
    }


@fixture
def object_indices():
    return (
        chart.SUN,
        chart.MOON,
        chart.MERCURY,
        chart.VENUS,
        chart.MARS,
        chart.JUPITER,
        chart.SATURN,
        chart.URANUS,
        chart.NEPTUNE,
        chart.PLUTO,
    )


@fixture
def birth_data():
    return {
        # Harrison Ford
        calc.BUNDLE: {
            "latitude": "41n51",
            "longitude": "87w39",
            "dob": "1942-07-13 11:41:00",
        },
        # Clint Eastwood
        calc.BUCKET: {
            "latitude": "37n47",
            "longitude": "122w25",
            "dob": "1930-05-31 17:35:00",
        },
        # Alfred Hitchcock
        calc.BOWL: {
            "latitude": "51n30",
            "longitude": "0w10",
            "dob": "1899-08-13 20:00:00",
        },
        # Isaac Newton
        calc.LOCOMOTIVE: {
            "latitude": "52n49",
            "longitude": "0w38",
            "dob": "1643-01-04 01:38:00",
        },
        # William Blake
        calc.SEESAW: {
            "latitude": "51n30",
            "longitude": "0w08",
            "dob": "1757-11-28 19:45:00",
        },
        # Carl Jung
        calc.SPLASH: {
            "latitude": "46n36",
            "longitude": "9e19",
            "dob": "1875-07-26 19:29:00",
        },
        # Random DOB to get a non-shape
        calc.SPLAY: {
            "latitude": "32n43",
            "longitude": "117w09",
            "dob": "1902-01-01 10:00:00",
        },
    }


def test_aspect_pattern(aspect_objects):
    vertices = {
        calc.T_SQUARE: (0, 90, 180),
        calc.GRAND_TRINE: (0, 120, 240),
        calc.YOD: (0, 60, 210),
        calc.GRAND_CROSS: (0, 90, 180, 270),
        calc.KITE: (0, 120, 180, 240),
        calc.MYSTIC_RECTANGLE: (0, 60, 180, 240),
        calc.CRADLE: (0, 60, 120, 180),
        calc.GRAND_SEXTILE: (0, 60, 120, 180, 240, 300),
        calc.GRAND_QUINTILE: (0, 72, 144, 216, 288),
    }

    config = charts.Config()
    config.aspects += (calc.QUINTILE, calc.BIQUINTILE)
    for pattern_type, angles in vertices.items():
        test_objects = {
            aspect_objects[index]["index"]: aspect_objects[index] | {"lon": lon}
            for index, lon in zip(aspect_objects, angles)
        }
        # test straightforward patterns
        aspects = aspect.all(test_objects, config=config)
        aspect_patterns = pattern.aspect_patterns(aspects)
        assert pattern_type in aspect_patterns
        assert len(aspect_patterns[pattern_type]) == 1
        assert len(aspect_patterns[pattern_type][0]) == len(angles)
        vertex_sizes = [len(vertex) for vertex in aspect_patterns[pattern_type][0]]
        assert all(size == 1 for size in vertex_sizes)
        # test conjunct vertices by adding Pluto conjunct Sun for every pattern
        test_objects[chart.PLUTO] = aspect_objects[chart.PLUTO] | {"lon": 0.0}
        aspects = aspect.all(test_objects, config=config)
        aspect_patterns = pattern.aspect_patterns(aspects)
        assert pattern_type in aspect_patterns
        assert len(aspect_patterns[pattern_type]) == 1
        assert len(aspect_patterns[pattern_type][0]) == len(angles)
        vertex_sizes = [len(vertex) for vertex in aspect_patterns[pattern_type][0]]
        assert (
            vertex_sizes.count(2) == 1
            and vertex_sizes.count(1) == len(vertex_sizes) - 1
        )

        # ensure nested patterns don't show
        if pattern_type == calc.GRAND_CROSS:
            assert calc.T_SQUARE not in aspect_patterns
        elif pattern_type == calc.KITE:
            assert calc.GRAND_TRINE not in aspect_patterns


def test_chart_shape(object_indices, birth_data):
    for chart_shape, data in birth_data.items():
        lat, lon = (
            convert.string_to_dec(v) for v in (data["latitude"], data["longitude"])
        )
        dob_dt = date.localize(datetime.fromisoformat(data["dob"]), lat, lon)
        jd = date.to_jd(dob_dt)
        objects = ephemeris.get_objects(object_indices, jd, lat, lon, chart.PLACIDUS)
        assert pattern.chart_shape(objects) == chart_shape
