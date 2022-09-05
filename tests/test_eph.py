"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The eph module's figures are tested against output
    from astro.com with default Placidus house system.
    Additional data courtesy of websites cited in test
    function comments.
"""

import os
from datetime import datetime

from pytest import approx, fixture

from immanuel import setup
from immanuel.const import calc, chart
from immanuel.tools import convert, date, eph, position
from immanuel.setup import options


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def all_angles():
    return (
        chart.ASC,
        chart.DESC,
        chart.MC,
        chart.IC,
        chart.ARMC,
    )

@fixture
def all_houses():
    return (
        chart.HOUSE1,
        chart.HOUSE2,
        chart.HOUSE3,
        chart.HOUSE4,
        chart.HOUSE5,
        chart.HOUSE6,
        chart.HOUSE7,
        chart.HOUSE8,
        chart.HOUSE9,
        chart.HOUSE10,
        chart.HOUSE11,
        chart.HOUSE12,
    )

@fixture
def all_points():
    return (
        chart.NORTH_NODE,
        chart.SOUTH_NODE,
        chart.TRUE_NORTH_NODE,
        chart.TRUE_SOUTH_NODE,
        chart.VERTEX,
        chart.LILITH,
        chart.TRUE_LILITH,
        chart.SYZYGY,
        chart.PARS_FORTUNA,
    )

@fixture
def all_planets():
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
def all_asteroids():
    return (
        chart.CHIRON,
        chart.PHOLUS,
        chart.CERES,
        chart.PALLAS,
        chart.JUNO,
        chart.VESTA,
        1181,
    )

@fixture
def astro():
    """ Results copied from astro.com chart table. We spot-check
    chart items by picking one of each type. """
    return {
        # angle
        'asc': {
            'lon': '05°36\'38"',
        },
        # house
        'house_2': {
            'lon': '17°59\'40"',
        },
        # planet
        'sun': {
            'lon': '10°37\'26"',
            'lat': '00°00\'01"',
            'speed': '01°01\'10"',
            'dec': '-23°00\'45"',
        },
        # point
        'pof': {
            'lon': '11°18\'41"',
        },
        # default asteroid
        'juno': {
            'lon': '08°05\'21"',
            'lat': '09°26\'57"',
            'speed': '00°22\'21"',
            'dec': '-13°45\'30"',
        },
        # external asteroid
        'lilith': {
            'lon': '18°16\'47"',
            'lat': '04°49\'07"',
            'speed': '00°24\'37"',
            'dec': '-00°11\'50"',
        },
        # fixed star
        'antares': {
            'lon': '09°45\'12"',
            'lat': '-04°34\'11"',
        },
    }


""" These tests simply check the correct chart items are being
returned. Data is checked separately afterwards. """
def test_all(jd, coords):
    all = eph.all(jd, *coords)
    assert tuple(all.keys()) == options.items


def test_items(jd, coords):
    chart_items = (chart.SUN, chart.MOON, chart.PARS_FORTUNA, chart.SYZYGY, chart.NORTH_NODE, chart.ASC)
    items = eph.items(chart_items, jd, *coords)
    assert tuple(items.keys()) == chart_items


def test_get(jd, coords):
    setup.add_filepath(os.path.dirname(__file__))
    assert eph.get(chart.ASC, jd, *coords)['index'] == chart.ASC
    assert eph.get(chart.HOUSE2, jd, *coords)['index'] == chart.HOUSE2
    assert eph.get(chart.SUN, jd)['index'] == chart.SUN
    assert eph.get(chart.PARS_FORTUNA, jd, *coords)['index'] == chart.PARS_FORTUNA
    assert eph.get(chart.JUNO, jd)['index'] == chart.JUNO
    # These are from external ephemeris files.
    lilith = eph.get(1181, jd)
    antares = eph.get('Antares', jd)
    assert lilith['index'] == 1181 and lilith['type'] == chart.ASTEROID
    assert antares['index'] == 'Antares' and antares['type'] == chart.FIXED_STAR


def test_angles(jd, coords, all_angles):
    angles = eph.angles(jd, *coords)
    assert len(set(all_angles).difference(set(angles.keys()))) == 0


def test_angle(jd, coords, all_angles):
    for index in all_angles:
        angle = eph.angle(index, jd, *coords)
        assert angle['index'] == index and angle['type'] == chart.ANGLE

    assert eph.angle(eph.ALL, jd, *coords) == eph.angles(jd, *coords)


def test_houses(jd, coords, all_houses):
    houses = eph.houses(jd, *coords)
    assert len(set(all_houses).difference(set(houses.keys()))) == 0


def test_house(jd, coords, all_houses):
    for index in all_houses:
        house = eph.house(index, jd, *coords)
        assert house['index'] == index and house['type'] == chart.HOUSE

    assert eph.house(eph.ALL, jd, *coords) == eph.houses(jd, *coords)


def test_point(jd, coords, all_points):
    for index in all_points:
        point = eph.point(index, jd, *coords)
        assert point['index'] == index and point['type'] == chart.POINT


def test_planet(jd, all_planets):
    for index in all_planets:
        planet = eph.planet(index, jd)
        assert planet['index'] == index and planet['type'] == chart.PLANET


def test_asteroid(jd, all_asteroids):
    setup.add_filepath(os.path.dirname(__file__))

    for index in all_asteroids:
        asteroid = eph.asteroid(index, jd)
        assert asteroid['index'] == index and asteroid['type'] == chart.ASTEROID


def test_fixed_star(jd):
    # So many fixed stars we just test one
    fixed_star = eph.fixed_star('Antares', jd)
    assert fixed_star['index'] == 'Antares' and fixed_star['type'] == chart.FIXED_STAR


""" Now we are satisfied the correct chart items are being returned,
we can test the accuracy of the module's data. """
def test_get_data(coords, jd, astro):
    setup.add_filepath(os.path.dirname(__file__))
    pars_fortuna_option = options.pars_fortuna
    options.pars_fortuna = calc.DAY_NIGHT_FORMULA

    data = {
        'asc': eph.get(chart.ASC, jd, *coords),
        'house_2': eph.get(chart.HOUSE2, jd, *coords),
        'sun': eph.get(chart.SUN, jd),
        'pof': eph.get(chart.PARS_FORTUNA, jd, *coords),
        'juno': eph.get(chart.JUNO, jd),    # Included with planets
        'lilith': eph.get(1181, jd),        # From its own file
        'antares': eph.get('Antares', jd),  # From its own file
    }

    options.pars_fortuna = pars_fortuna_option

    for key, eph_item in data.items():
        # Convert ecliptical longitude to sign-based
        item = eph_item.copy()
        item['lon'] = position.signlon(item['lon'])[position.LON]

        # Format properties to string to match astro.com front-end output
        for property_key in ('lon', 'lat', 'speed', 'dec'):
            if property_key in item:
                item[property_key] = convert.dec_to_string(item[property_key])

        for property, value in astro[key].items():
            assert item[property] == value


def test_moon_phase(jd):
    # Courtesy of https://stardate.org/nightsky/moon
    assert eph.moon_phase(jd) == calc.THIRD_QUARTER             # third quarter = waning crescent


def test_obliquity(jd):
    # Courtesy of http://neoprogrammics.com/obliquity_of_the_ecliptic/Obliquity_Of_The_Ecliptic_Calculator.php
    assert eph.obliquity(jd) == approx(23.4376888901)
    assert eph.obliquity(jd, True) == approx(23.4392911408)


def test_is_daytime(jd, coords):
    # Sun above ascendant in astro.com chart visual
    assert eph.is_daytime(jd, *coords)


def test_house_system_not_cached(jd, coords):
    options.house_system = chart.PLACIDUS
    house2_placidus = eph.get(chart.HOUSE2, jd, *coords)
    options.house_system = chart.EQUAL
    house2_equal = eph.get(chart.HOUSE2, jd, *coords)
    assert house2_placidus['lon'] != house2_equal['lon']
