"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Test a natal chart's object distribution against astro.com's reports.

"""

from datetime import datetime

from pytest import fixture

from immanuel.const import chart
from immanuel.reports import weighting
from immanuel.tools import convert, date, ephemeris


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def objects(coords, jd):
    object_indices = (
        chart.ASC,
        chart.MC,
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
        chart.TRUE_NORTH_NODE,
        chart.CHIRON,
    )
    return ephemeris.objects(object_indices, jd, *coords, chart.PLACIDUS)

@fixture
def houses(coords, jd):
    return ephemeris.houses(jd, *coords, chart.PLACIDUS)


def test_elements(objects):
    elements = weighting.elements(objects)
    assert elements[chart.FIRE] == [chart.MC, chart.VENUS, chart.JUPITER, chart.PLUTO, chart.TRUE_NORTH_NODE, chart.CHIRON]
    assert elements[chart.EARTH] == [chart.SUN, chart.MERCURY, chart.SATURN]
    assert elements[chart.AIR] == [chart.MARS, chart.URANUS, chart.NEPTUNE]
    assert elements[chart.WATER] == [chart.ASC, chart.MOON]


def test_modalities(objects):
    modalities = weighting.modalities(objects)
    assert modalities[chart.CARDINAL] == [chart.SUN, chart.MERCURY, chart.JUPITER]
    assert modalities[chart.FIXED] == [chart.MOON, chart.MARS, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.TRUE_NORTH_NODE]
    assert modalities[chart.MUTABLE] == [chart.ASC, chart.MC, chart.VENUS, chart.PLUTO, chart.CHIRON]


def test_quadrants(objects, houses):
    quadrants = weighting.quadrants(objects, houses)
    assert quadrants[1] == [chart.ASC, chart.JUPITER, chart.SATURN]
    assert quadrants[2] == [chart.TRUE_NORTH_NODE]
    assert quadrants[3] == [chart.MOON, chart.VENUS, chart.PLUTO, chart.CHIRON]
    assert quadrants[4] == [chart.MC, chart.SUN, chart.MERCURY, chart.MARS, chart.URANUS, chart.NEPTUNE]
