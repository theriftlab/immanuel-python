"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The position module's calculations are tested against
    figures from astro.com. The signlon() function will already
    have been partially tested in the eph module's tests since
    there is no other way to convert the eph module's longitudes
    into sign-specific longitudes.
"""

import os
from datetime import datetime

from pytest import fixture

from immanuel import setup
from immanuel.const import calc, chart
from immanuel.tools import convert, date, eph, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def data(jd, coords):
    setup.add_filepath(os.path.dirname(__file__))

    return {
        'asc': eph.angle(chart.ASC, jd, *coords, chart.PLACIDUS),
        'house_2': eph.house(chart.HOUSE2, jd, *coords, chart.PLACIDUS),
        'sun': eph.planet(chart.SUN, jd),
        'pof': eph.point(chart.PARS_FORTUNA, jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA),
        'juno': eph.asteroid(chart.JUNO, jd),       # Included with planets
        'lilith': eph.asteroid(1181, jd),           # From its own file
        'antares': eph.fixed_star('Antares', jd),
    }

@fixture
def astro():
    """ Results copied from astro.com chart table. """
    return {
        # angle
        'asc': {
            'sign' : chart.PISCES,
            'opposite_sign': chart.VIRGO,
            'lon': '05°36\'38"',
            'decan': chart.DECAN1,
            'element': chart.WATER,
            'modality': chart.MUTABLE,
        },
        # house
        'house_2': {
            'sign': chart.ARIES,
            'opposite_sign': chart.LIBRA,
            'lon': '17°59\'40"',
            'decan': chart.DECAN2,
            'element': chart.FIRE,
            'modality': chart.CARDINAL,
        },
        # planet
        'sun': {
            'sign': chart.CAPRICORN,
            'opposite_sign': chart.CANCER,
            'house': 11,
            'opposite_house': 5,
            'lon': '10°37\'26"',
            'decan': chart.DECAN2,
            'element': chart.EARTH,
            'modality': chart.CARDINAL,
        },
        # point
        'pof': {
            'sign': chart.CAPRICORN,
            'opposite_sign': chart.CANCER,
            'house': 11,
            'opposite_house': 5,
            'lon': '11°18\'41"',
            'decan': chart.DECAN2,
            'element': chart.EARTH,
            'modality': chart.CARDINAL,
        },
        # default asteroid
        'juno': {
            'sign': chart.CAPRICORN,
            'opposite_sign': chart.CANCER,
            'house': 11,
            'opposite_house': 5,
            'lon': '08°05\'21"',
            'decan': chart.DECAN1,
            'element': chart.EARTH,
            'modality': chart.CARDINAL,
        },
        # external asteroid
        'lilith': {
            'sign': chart.PISCES,
            'opposite_sign': chart.VIRGO,
            'house': 1,
            'opposite_house': 7,
            'lon': '18°16\'47"',
            'decan': chart.DECAN2,
            'element': chart.WATER,
            'modality': chart.MUTABLE,
        },
        # fixed star
        'antares': {
            'sign': chart.SAGITTARIUS,
            'opposite_sign': chart.GEMINI,
            'house': 9,
            'opposite_house': 3,
            'lon': '09°45\'12"',
            'decan': chart.DECAN1,
            'element': chart.FIRE,
            'modality': chart.MUTABLE,
        },
    }


def test_sign(data, astro):
    for key, object in data.items():
        assert position.sign(object['lon']) == astro[key]['sign']


def test_signlon(data, astro):
    for key, object in data.items():
        sign, lon = position.signlon(object['lon'])
        assert sign == astro[key]['sign']
        assert convert.dec_to_string(lon) == astro[key]['lon']


def test_opposite_sign(data, astro):
    for key, object in data.items():
        assert position.opposite_sign(object['lon']) == astro[key]['opposite_sign']


def test_decan(data, astro):
    for key, object in data.items():
        assert position.decan(object['lon']) == astro[key]['decan']


def test_house(jd, coords, data, astro):
    houses = eph.houses(jd, *coords, chart.PLACIDUS)

    for key, object in {k: v for k, v in data.items() if 'house' in v}:
        assert position.house(object['lon'], houses) == astro[key]['house']


def test_opposite_house(jd, coords, data, astro):
    houses = eph.houses(jd, *coords, chart.PLACIDUS)

    for key, object in {k: v for k, v in data.items() if 'house' in v}:
        assert position.opposite_house(object['lon'], houses) == astro[key]['opposite_house']


def test_element(data, astro):
    for key, object in data.items():
        assert position.element(object['lon']) == astro[key]['element']


def test_modality(data, astro):
    for key, object in data.items():
        assert position.modality(object['lon']) == astro[key]['modality']
