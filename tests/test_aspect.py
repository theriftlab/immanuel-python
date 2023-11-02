"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Aspect calculations are compared against those found by astro.com.
    Where possible, astro.com's aspects table is the preferred source
    of data, but the chart visual is also used to confirm data not in
    the table.

"""

import math

from datetime import datetime

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.reports import aspect
from immanuel.setup import settings
from immanuel.tools import convert, date, ephemeris


@fixture
def objects():
    lat, lon = [convert.string_to_dec(v) for v in ('32n43', '117w09')]
    jd = date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), lat, lon))
    return ephemeris.objects(settings.objects, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)

@fixture
def partner_objects():
    lat, lon = [convert.string_to_dec(v) for v in ('38n35', '121w30')]
    jd = date.to_jd(date.localize(datetime.fromisoformat('2001-02-16 06:00'), lat, lon))
    return ephemeris.objects(settings.objects, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)


def test_between(objects):
    a = aspect.between(objects[chart.SUN], objects[chart.MOON])
    assert a['active'] == chart.MOON
    assert a['passive'] == chart.SUN
    assert a['aspect'] == calc.SEXTILE
    assert a['difference'] <= a['orb']
    assert math.ceil(a['difference']) == -5                 # astro.com rounds up
    assert a['distance'] - a['difference'] == calc.SEXTILE
    assert a['movement'] == calc.SEPARATIVE
    assert a['condition'] == calc.ASSOCIATE                 # Not on astro.com report, can be ascertained visually


def test_for_object(objects):
    settings.aspect_rules[chart.ASC] = settings.default_aspect_rule     # astro.com chart visual does not include aspects to Asc but its aspects table does
    a = aspect.for_object(objects[chart.SUN], objects)
    assert sorted(tuple(a.keys())) == sorted((chart.ASC, chart.PARS_FORTUNA, chart.MOON, chart.MERCURY, chart.SATURN))
    assert a[chart.ASC]['aspect'] == calc.SEXTILE
    assert a[chart.PARS_FORTUNA]['aspect'] == calc.CONJUNCTION
    assert a[chart.MOON]['aspect'] == calc.SEXTILE
    assert a[chart.MERCURY]['aspect'] == calc.CONJUNCTION
    assert a[chart.SATURN]['aspect'] == calc.TRINE


def test_all(objects):
    settings.aspect_rules[chart.ASC] = settings.default_aspect_rule     # astro.com chart visual does not include aspects to Asc but its aspects table does
    settings.aspect_rules[chart.DESC] = {                               # Because we're looking at Asc aspects, don't allow Desc any
        'initiate': (),
        'receive': (),
    }
    all = aspect.all(objects)
    for index, aspect_list in all.items():
        for i, a in aspect_list.items():
            assert i in all
            assert index in all[i]
            assert a['aspect'] == all[i][index]['aspect']


def test_by_type(objects):
    settings.aspect_rules[chart.ASC] = settings.default_aspect_rule                                     # astro.com chart visual does not include aspects to Asc but its aspects table does
    settings.aspects = (calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE)       # Copy astro.com's "only major aspects"
    by_type = aspect.by_type(objects)
    assert sorted(tuple(by_type.keys())) == sorted((calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE))


def test_synastry(objects, partner_objects):
    synastry = aspect.synastry(objects, partner_objects)
    # Due to the sheer number of aspects between 2 charts, we spot-check the sun against astro.com
    sun = synastry[chart.SUN]
    assert chart.TRUE_NORTH_NODE in sun
    assert sun[chart.TRUE_NORTH_NODE]['aspect'] == calc.OPPOSITION
    assert chart.TRUE_SOUTH_NODE in sun
    assert sun[chart.TRUE_SOUTH_NODE]['aspect'] == calc.CONJUNCTION
    assert chart.VENUS in sun
    assert sun[chart.VENUS]['aspect'] == calc.SQUARE
