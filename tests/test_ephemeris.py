"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The ephemeris module is essentially a wrapper for the sweph module, providing
convenience functions for retriveving chart ojects in bulk and for making
ARMC-based function calls easier.

Testing the functions' outputs is therefore  a job for the sweph tests, so we
simply check the correct

"""

import os

import swisseph as swe
from pytest import fixture

from immanuel import settings
from immanuel.const import calc, chart, names
from immanuel.tools import convert, date, ephemeris, orbit


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def armc():
    # ARMC longitude on the above jd / day_jd
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
        chart.INTERPOLATED_LILITH,
        chart.SYZYGY,
        chart.PART_OF_FORTUNE,
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


def test_get_objects(jd, coords):
    lat, lon = coords
    chart_objects = [
        chart.SUN,
        chart.MOON,
        chart.PART_OF_FORTUNE,
        chart.SYZYGY,
        chart.NORTH_NODE,
        chart.ASC,
    ]
    objects = ephemeris.get_objects(
        chart_objects, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
    )
    assert list(objects.keys()) == chart_objects


def test_armc_get_objects(jd, coords, armc):
    lat, lon = coords
    chart_objects = [
        chart.SUN,
        chart.MOON,
        chart.PART_OF_FORTUNE,
        chart.SYZYGY,
        chart.NORTH_NODE,
        chart.ASC,
    ]
    armc_objects = ephemeris.armc_get_objects(
        chart_objects, jd, armc, lat, lon, None, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
    )
    assert list(armc_objects.keys()) == chart_objects
    objects = ephemeris.get_objects(
        chart_objects, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
    )
    for index in chart_objects:
        assert armc_objects[index] == objects[index]


def test_get(jd, coords):
    lat, lon = coords
    settings.add_swe_filepath(os.path.dirname(__file__))
    assert ephemeris.get(chart.ASC, jd, lat, lon, chart.PLACIDUS)["index"] == chart.ASC
    assert (
        ephemeris.get(chart.HOUSE2, jd, lat, lon, chart.PLACIDUS)["index"]
        == chart.HOUSE2
    )
    assert ephemeris.get(chart.SUN, jd)["index"] == chart.SUN
    assert (
        ephemeris.get(
            chart.PART_OF_FORTUNE, jd, lat, lon, part_formula=calc.DAY_NIGHT_FORMULA
        )["index"]
        == chart.PART_OF_FORTUNE
    )
    assert ephemeris.get(chart.JUNO, jd)["index"] == chart.JUNO  # Included with planets
    lilith = ephemeris.get(1181, jd)  # From external file
    antares = ephemeris.get("Antares", jd)
    assert lilith["index"] == 1181 and lilith["type"] == chart.ASTEROID
    assert antares["index"] == "Antares" and antares["type"] == chart.FIXED_STAR


def test_armc_get(jd, coords, armc):
    lat, lon = coords
    armmc_asc = ephemeris.armc_get(
        chart.ASC, jd, armc, lat, house_system=chart.PLACIDUS
    )
    assert armmc_asc["index"] == chart.ASC
    jd_asc = ephemeris.get(chart.ASC, jd, lat, lon, chart.PLACIDUS)
    assert armmc_asc == jd_asc

    armc_house2 = ephemeris.armc_get(
        chart.HOUSE2, jd, armc, lat, house_system=chart.PLACIDUS
    )
    assert armc_house2["index"] == chart.HOUSE2
    jd_house2 = ephemeris.get(chart.HOUSE2, jd, lat, lon, chart.PLACIDUS)
    assert armc_house2 == jd_house2

    armc_part_of_fortune = ephemeris.armc_get(
        chart.PART_OF_FORTUNE,
        jd,
        armc,
        lat,
        part_formula=calc.DAY_NIGHT_FORMULA,
    )
    assert armc_part_of_fortune["index"] == chart.PART_OF_FORTUNE
    jd_part_of_fortune = ephemeris.get(
        chart.PART_OF_FORTUNE, jd, lat, lon, part_formula=calc.DAY_NIGHT_FORMULA
    )
    assert armc_part_of_fortune == jd_part_of_fortune


def test_get_for_angles(jd, coords, all_angles):
    lat, lon = coords
    angles = ephemeris.get(chart.ANGLE, jd, lat, lon, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_armc_get_for_angles(jd, coords, armc, all_angles):
    lat, lon = coords
    armc_angles = ephemeris.armc_get(
        chart.ANGLE, jd, armc, lat, lon, orbit.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_angles) == sorted(armc_angles)
    jd_angles = ephemeris.get(chart.ANGLE, jd, lat, lon, chart.PLACIDUS)
    assert armc_angles == jd_angles


def test_get_for_houses(jd, coords, all_houses):
    lat, lon = coords
    houses = ephemeris.get(chart.HOUSE, jd, lat, lon, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_armc_get_for_houses(jd, coords, armc, all_houses):
    lat, lon = coords
    armc_houses = ephemeris.armc_get(
        chart.HOUSE, jd, armc, lat, lon, orbit.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_houses) == sorted(armc_houses)
    jd_houses = ephemeris.get(chart.HOUSE, jd, lat, lon, chart.PLACIDUS)
    assert armc_houses == jd_houses


def test_get_angles(jd, coords, all_angles):
    lat, lon = coords
    angles = ephemeris.get_angles(jd, lat, lon, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_get_armc_angles(jd, coords, armc, all_angles):
    lat, lon = coords
    armc_angles = ephemeris.armc_get_angles(
        armc, lat, orbit.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_angles) == sorted(armc_angles)
    jd_angles = ephemeris.get_angles(jd, lat, lon, chart.PLACIDUS)
    assert armc_angles == jd_angles


def test_get_angle(jd, coords, all_angles):
    lat, lon = coords
    for index in all_angles:
        angle = ephemeris.get_angle(index, jd, lat, lon, chart.PLACIDUS)
        assert angle["index"] == index and angle["type"] == chart.ANGLE
    assert ephemeris.get_angle(
        ephemeris.ALL, jd, lat, lon, chart.PLACIDUS
    ) == ephemeris.get_angles(jd, lat, lon, chart.PLACIDUS)


def test_get_armc_angle(jd, coords, armc, all_angles):
    obliquity = orbit.earth_obliquity(jd)
    for index in all_angles:
        angle = ephemeris.armc_get_angle(
            index, armc, coords[0], obliquity, chart.PLACIDUS
        )
        assert angle["index"] == index and angle["type"] == chart.ANGLE
    assert ephemeris.armc_get_angle(
        ephemeris.ALL, armc, coords[0], obliquity, chart.PLACIDUS
    ) == ephemeris.armc_get_angles(armc, coords[0], obliquity, chart.PLACIDUS)


def test_get_houses(jd, coords, all_houses):
    lat, lon = coords
    houses = ephemeris.get_houses(jd, lat, lon, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_get_armc_houses(jd, coords, armc, all_houses):
    lat, lon = coords
    armc_houses = ephemeris.armc_get_houses(
        armc, lat, orbit.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_houses) == sorted(armc_houses)
    jd_houses = ephemeris.get_houses(jd, lat, lon, chart.PLACIDUS)
    assert armc_houses == jd_houses


def test_get_house(jd, coords, all_houses):
    lat, lon = coords
    for index in all_houses:
        house = ephemeris.get_house(index, jd, lat, lon, chart.PLACIDUS)
        assert house["index"] == index and house["type"] == chart.HOUSE
    assert ephemeris.get_house(
        ephemeris.ALL, jd, lat, lon, chart.PLACIDUS
    ) == ephemeris.get_houses(jd, lat, lon, chart.PLACIDUS)


def test_get_armc_house(jd, coords, armc, all_houses):
    obliquity = orbit.earth_obliquity(jd)
    for index in all_houses:
        house = ephemeris.armc_get_house(
            index, armc, coords[0], obliquity, chart.PLACIDUS
        )
        assert house["index"] == index and house["type"] == chart.HOUSE
    assert ephemeris.armc_get_house(
        ephemeris.ALL, armc, coords[0], obliquity, chart.PLACIDUS
    ) == ephemeris.armc_get_houses(armc, coords[0], obliquity, chart.PLACIDUS)


def test_planet_on_first_house(jd, coords):
    lat, lon = coords
    sun = ephemeris.get_planet(chart.SUN, jd)
    first_house = ephemeris.get_house(chart.HOUSE1, jd, lat, lon, chart.SUN_ON_FIRST)
    second_house = ephemeris.get_house(chart.HOUSE2, jd, lat, lon, chart.SUN_ON_FIRST)
    assert sun["lon"] == first_house["lon"]
    assert sun["lon"] + 30 == second_house["lon"]


def test_get_point(jd, coords, all_points):
    lat, lon = coords
    for index in all_points:
        point = ephemeris.get_point(
            index, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
        )
        assert point["index"] == index and point["type"] == chart.POINT


def test_armc_get_point(jd, coords, armc, all_points):
    lat, lon = coords
    for index in all_points:
        armc_point = ephemeris.armc_get_point(
            index,
            jd,
            armc,
            lat,
            orbit.earth_obliquity(jd),
            chart.PLACIDUS,
            calc.DAY_NIGHT_FORMULA,
        )
        assert armc_point["index"] == index and armc_point["type"] == chart.POINT
        jd_point = ephemeris.get_point(
            index, jd, lat, lon, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
        )
        assert armc_point == jd_point


def test_get_planet(jd, all_planets):
    for index in all_planets:
        planet = ephemeris.get_planet(index, jd)
        assert planet["index"] == index
        assert planet["type"] == chart.PLANET
        assert planet["name"] == names.PLANETS[index]


def test_get_asteroid(jd, all_asteroids):
    # This includes 1181 from an external ephemeris file,
    # so we're testing correct dispatch here
    for index in all_asteroids:
        asteroid = ephemeris.get_asteroid(index, jd)
        assert asteroid["index"] == index
        assert asteroid["type"] == chart.ASTEROID
        if index in names.ASTEROIDS:
            assert asteroid["name"] == names.ASTEROIDS[index]
        else:
            # Cheekily borrow a pysweph call to grab the name
            # for the sake of completeness
            assert asteroid["name"] == swe.get_planet_name(index + swe.AST_OFFSET)


def test_get_fixed_star(jd):
    # So many fixed stars, so we just test one. The rest will be fine.
    fixed_star = ephemeris.get_fixed_star("Antares", jd)
    assert fixed_star["index"] == "Antares"
    assert fixed_star["type"] == chart.FIXED_STAR
    assert fixed_star["name"] == "Antares"


def test_get_eclipse(jd):
    pre_solar = ephemeris.get_eclipse(chart.PRE_NATAL_SOLAR_ECLIPSE, jd)
    assert pre_solar["type"] == chart.ECLIPSE
    assert pre_solar["index"] == chart.PRE_NATAL_SOLAR_ECLIPSE
    pre_lunar = ephemeris.get_eclipse(chart.PRE_NATAL_LUNAR_ECLIPSE, jd)
    assert pre_lunar["type"] == chart.ECLIPSE
    assert pre_lunar["index"] == chart.PRE_NATAL_LUNAR_ECLIPSE
    post_solar = ephemeris.get_eclipse(chart.POST_NATAL_SOLAR_ECLIPSE, jd)
    assert post_solar["type"] == chart.ECLIPSE
    assert post_solar["index"] == chart.POST_NATAL_SOLAR_ECLIPSE
    post_lunar = ephemeris.get_eclipse(chart.POST_NATAL_LUNAR_ECLIPSE, jd)
    assert post_lunar["type"] == chart.ECLIPSE
    assert post_lunar["index"] == chart.POST_NATAL_LUNAR_ECLIPSE
