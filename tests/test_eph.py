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


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def armc():
    # ARMC longitude on the above Julian date
    return 253.55348499294269

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
    chart objects by picking one of each type. """
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


""" These tests simply check the correct chart objects are being
returned. Data is checked separately afterwards. """
def test_objects(jd, coords):
    chart_objects = (chart.SUN, chart.MOON, chart.PARS_FORTUNA, chart.SYZYGY, chart.NORTH_NODE, chart.ASC)
    objects = eph.objects(chart_objects, jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
    assert tuple(objects.keys()) == chart_objects


def test_armc_objects(jd, coords, armc):
    chart_objects = (chart.SUN, chart.MOON, chart.PARS_FORTUNA, chart.SYZYGY, chart.NORTH_NODE, chart.ASC)
    objects = eph.armc_objects(chart_objects, jd, armc, *coords, None, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
    assert tuple(objects.keys()) == chart_objects


def test_get(jd, coords):
    setup.add_filepath(os.path.dirname(__file__))
    assert eph.get(chart.ASC, jd, *coords, chart.PLACIDUS)['index'] == chart.ASC
    assert eph.get(chart.HOUSE2, jd, *coords, chart.PLACIDUS)['index'] == chart.HOUSE2
    assert eph.get(chart.SUN, jd)['index'] == chart.SUN
    assert eph.get(chart.PARS_FORTUNA, jd, *coords, pars_fortuna_formula=calc.DAY_NIGHT_FORMULA)['index'] == chart.PARS_FORTUNA
    assert eph.get(chart.JUNO, jd)['index'] == chart.JUNO   # Included with planets
    lilith = eph.get(1181, jd)                              # From external file
    antares = eph.get('Antares', jd)
    assert lilith['index'] == 1181 and lilith['type'] == chart.ASTEROID
    assert antares['index'] == 'Antares' and antares['type'] == chart.FIXED_STAR


def test_armc_get(jd, coords, armc):
    setup.add_filepath(os.path.dirname(__file__))
    assert eph.armc_get(chart.ASC, jd, armc, coords[0], house_system=chart.PLACIDUS)['index'] == chart.ASC
    assert eph.armc_get(chart.HOUSE2, jd, armc, coords[0], house_system=chart.PLACIDUS)['index'] == chart.HOUSE2
    assert eph.armc_get(chart.PARS_FORTUNA, jd, armc, coords[0], pars_fortuna_formula=calc.DAY_NIGHT_FORMULA)['index'] == chart.PARS_FORTUNA


def test_get_angles(jd, coords, all_angles):
    angles = eph.get(chart.ANGLE, jd, *coords, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_armc_get_angles(jd, coords, armc, all_angles):
    angles = eph.armc_get(chart.ANGLE, jd, armc, *coords, eph.obliquity(jd), chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_get_houses(jd, coords, all_houses):
    houses = eph.get(chart.HOUSE, jd, *coords, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_armc_get_houses(jd, coords, armc, all_houses):
    houses = eph.armc_get(chart.HOUSE, jd, armc, *coords, eph.obliquity(jd), chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_angles(jd, coords, all_angles):
    angles = eph.angles(jd, *coords, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_armc_angles(jd, coords, armc, all_angles):
    angles = eph.armc_angles(jd, armc, coords[0], eph.obliquity(jd), chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_angle(jd, coords, all_angles):
    for index in all_angles:
        angle = eph.angle(index, jd, *coords, chart.PLACIDUS)
        assert angle['index'] == index and angle['type'] == chart.ANGLE

    assert eph.angle(eph.ALL, jd, *coords, chart.PLACIDUS) == eph.angles(jd, *coords, chart.PLACIDUS)


def test_armc_angle(jd, coords, armc, all_angles):
    obliquity = eph.obliquity(jd)

    for index in all_angles:
        angle = eph.armc_angle(index, jd, armc, coords[0], obliquity, chart.PLACIDUS)
        assert angle['index'] == index and angle['type'] == chart.ANGLE

    assert eph.armc_angle(eph.ALL, jd, armc, coords[0], obliquity, chart.PLACIDUS) == eph.armc_angles(jd, armc, coords[0], obliquity, chart.PLACIDUS)


def test_houses(jd, coords, all_houses):
    houses = eph.houses(jd, *coords, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_armc_houses(jd, coords, armc, all_houses):
    houses = eph.armc_houses(armc, coords[0], eph.obliquity(jd), chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_house(jd, coords, all_houses):
    for index in all_houses:
        house = eph.house(index, jd, *coords, chart.PLACIDUS)
        assert house['index'] == index and house['type'] == chart.HOUSE

    assert eph.house(eph.ALL, jd, *coords, chart.PLACIDUS) == eph.houses(jd, *coords, chart.PLACIDUS)


def test_armc_house(jd, coords, armc, all_houses):
    obliquity = eph.obliquity(jd)

    for index in all_houses:
        house = eph.armc_house(index, armc, coords[0], obliquity, chart.PLACIDUS)
        assert house['index'] == index and house['type'] == chart.HOUSE

    assert eph.armc_house(eph.ALL, armc, coords[0], obliquity, chart.PLACIDUS) == eph.armc_houses(armc, coords[0], obliquity, chart.PLACIDUS)


def test_point(jd, coords, all_points):
    for index in all_points:
        point = eph.point(index, jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
        assert point['index'] == index and point['type'] == chart.POINT


def test_armc_point(jd, coords, armc, all_points):
    for index in all_points:
        point = eph.armc_point(index, jd, armc, coords[0], eph.obliquity(jd), chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
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


""" Now we are satisfied the correct chart objects are being returned,
we can test the accuracy of the module's data. """
def test_get_data(coords, jd, astro):
    setup.add_filepath(os.path.dirname(__file__))

    data = {
        'asc': eph.angle(chart.ASC, jd, *coords, chart.PLACIDUS),
        'house_2': eph.house(chart.HOUSE2, jd, *coords, chart.PLACIDUS),
        'sun': eph.planet(chart.SUN, jd),
        'pof': eph.point(chart.PARS_FORTUNA, jd, *coords, pars_fortuna_formula=calc.DAY_NIGHT_FORMULA),
        'juno': eph.asteroid(chart.JUNO, jd),    # Included with planets
        'lilith': eph.asteroid(1181, jd),        # From external file
        'antares': eph.fixed_star('Antares', jd),
    }

    for key, eph_object in data.items():
        # Convert ecliptical longitude to sign-based
        object = eph_object.copy()
        object['lon'] = position.signlon(object['lon'])[position.LON]

        # Format properties to string to match astro.com front-end output
        for property_key in ('lon', 'lat', 'speed', 'dec'):
            if property_key in object:
                object[property_key] = convert.dec_to_string(object[property_key])

        for property, value in astro[key].items():
            assert object[property] == value


def test_armc_get_data(coords, jd, astro, armc):
    setup.add_filepath(os.path.dirname(__file__))

    obliquity = eph.obliquity(jd)

    data = {
        'asc': eph.armc_angle(chart.ASC, jd, armc, coords[0], obliquity, chart.PLACIDUS),
        'house_2': eph.armc_house(chart.HOUSE2, armc, coords[0], obliquity, chart.PLACIDUS),
        'pof': eph.armc_point(chart.PARS_FORTUNA, jd, armc, coords[0], obliquity, pars_fortuna_formula=calc.DAY_NIGHT_FORMULA),
    }

    for key, eph_object in data.items():
        # Convert ecliptical longitude to sign-based
        object = eph_object.copy()
        object['lon'] = position.signlon(object['lon'])[position.LON]

        # Format properties to string to match astro.com front-end output
        for property_key in ('lon', 'lat', 'speed', 'dec'):
            if property_key in object:
                object[property_key] = convert.dec_to_string(object[property_key])

        for property, value in astro[key].items():
            assert object[property] == value


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


def test_armc_is_daytime(jd, coords, armc):
    # Sun above ascendant in astro.com chart visual
    assert eph.armc_is_daytime(jd, armc, coords[0], eph.obliquity(jd))


def test_deltat():
    pass


def test_sidereal_time():
    pass
