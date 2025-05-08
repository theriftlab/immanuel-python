"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The ephemeris module's figures are tested against output
    from astro.com with default Placidus house system.
    Additional data courtesy of websites cited in test
    function comments.

"""

import os

from pytest import approx, fixture

from immanuel.setup import settings
from immanuel.const import calc, chart
from immanuel.tools import convert, date, ephemeris, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def day_jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def night_jd(coords):
    return date.to_jd("2000-01-01 00:00", *coords)


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


@fixture
def astro():
    """Results copied from astro.com chart table. We spot-check
    chart objects by picking one of each type."""
    return {
        # angle
        "asc": {
            "lon": "05°36'38\"",
            # This is the only figure disagreeing with astro.com (~1 arcsec) and nobody knows why
            # 'dec': '-09°27\'13"',
        },
        # house
        "house_2": {
            "lon": "17°59'40\"",
            "dec": "07°03'29\"",
        },
        # planet
        "sun": {
            "lon": "10°37'26\"",
            "lat": "00°00'01\"",
            "speed": "01°01'10\"",
            "dec": "-23°00'45\"",
        },
        # point
        "pof": {
            "lon": "11°18'41\"",
            "dec": "-22°57'22\"",
        },
        # default asteroid
        "juno": {
            "lon": "08°05'21\"",
            "lat": "09°26'57\"",
            "speed": "00°22'21\"",
            "dec": "-13°45'30\"",
        },
        # external asteroid
        "lilith": {
            "lon": "18°16'47\"",
            "lat": "04°49'07\"",
            "speed": "00°24'37\"",
            "dec": "-00°11'50\"",
        },
        # fixed star
        "antares": {
            "lon": "09°45'12\"",
            "lat": "-04°34'11\"",
        },
        # eclipses
        "pre_natal_solar_eclipse": {
            "lon": "18°20'59\"",
            "lat": "00°00'00\"",
            "speed": "00°00'00\"",
            "dec": "15°19'40\"",
            "eclipse_type": chart.TOTAL,
            "date": "11 August",
        },
        "pre_natal_lunar_eclipse": {
            "lon": "05°02'21\"",
            "lat": "00°43'35\"",
            "speed": "00°00'00\"",
            "dec": "-18°18'03\"",
            "eclipse_type": chart.PARTIAL,
            "date": "28 July",
        },
        "post_natal_solar_eclipse": {
            "lon": "16°01'14\"",
            "lat": "00°00'00\"",
            "speed": "00°00'00\"",
            "dec": "-16°02'00\"",
            "eclipse_type": chart.PARTIAL,
            "date": "05 February",
        },
        "post_natal_lunar_eclipse": {
            "lon": "00°28'04\"",
            "lat": "-00°17'53\"",
            "speed": "00°00'00\"",
            "dec": "19°45'29\"",
            "eclipse_type": chart.TOTAL,
            "date": "20 January",
        },
    }


def teardown_function():
    settings.reset()


"""
CHART OBJECTS
--------------------------------------------------------------------------------
"""

""" These tests simply check the correct chart objects are being
returned. Data is checked separately afterwards. """


def test_get_objects(jd, coords):
    chart_objects = (
        chart.SUN,
        chart.MOON,
        chart.PART_OF_FORTUNE,
        chart.SYZYGY,
        chart.NORTH_NODE,
        chart.ASC,
    )
    objects = ephemeris.get_objects(
        chart_objects, jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
    )
    assert tuple(objects.keys()) == chart_objects


def test_get_armc_objects(jd, coords, armc):
    chart_objects = (
        chart.SUN,
        chart.MOON,
        chart.PART_OF_FORTUNE,
        chart.SYZYGY,
        chart.NORTH_NODE,
        chart.ASC,
    )
    objects = ephemeris.get_armc_objects(
        chart_objects, jd, armc, *coords, None, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
    )
    assert tuple(objects.keys()) == chart_objects


def test_get(jd, coords):
    settings.add_filepath(os.path.dirname(__file__))
    assert ephemeris.get(chart.ASC, jd, *coords, chart.PLACIDUS)["index"] == chart.ASC
    assert (
        ephemeris.get(chart.HOUSE2, jd, *coords, chart.PLACIDUS)["index"]
        == chart.HOUSE2
    )
    assert ephemeris.get(chart.SUN, jd)["index"] == chart.SUN
    assert (
        ephemeris.get(
            chart.PART_OF_FORTUNE, jd, *coords, part_formula=calc.DAY_NIGHT_FORMULA
        )["index"]
        == chart.PART_OF_FORTUNE
    )
    assert ephemeris.get(chart.JUNO, jd)["index"] == chart.JUNO  # Included with planets
    lilith = ephemeris.get(1181, jd)  # From external file
    antares = ephemeris.get("Antares", jd)
    assert lilith["index"] == 1181 and lilith["type"] == chart.ASTEROID
    assert antares["index"] == "Antares" and antares["type"] == chart.FIXED_STAR


def test_armc_get(jd, coords, armc):
    settings.add_filepath(os.path.dirname(__file__))
    assert (
        ephemeris.armc_get(chart.ASC, jd, armc, coords[0], house_system=chart.PLACIDUS)[
            "index"
        ]
        == chart.ASC
    )
    assert (
        ephemeris.armc_get(
            chart.HOUSE2, jd, armc, coords[0], house_system=chart.PLACIDUS
        )["index"]
        == chart.HOUSE2
    )
    assert (
        ephemeris.armc_get(
            chart.PART_OF_FORTUNE,
            jd,
            armc,
            coords[0],
            part_formula=calc.DAY_NIGHT_FORMULA,
        )["index"]
        == chart.PART_OF_FORTUNE
    )


def test_get_for_angles(jd, coords, all_angles):
    angles = ephemeris.get(chart.ANGLE, jd, *coords, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_armc_get_for_angles(jd, coords, armc, all_angles):
    angles = ephemeris.armc_get(
        chart.ANGLE, jd, armc, *coords, ephemeris.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_angles) == sorted(angles)


def test_get_for_houses(jd, coords, all_houses):
    houses = ephemeris.get(chart.HOUSE, jd, *coords, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_armc_get_for_houses(jd, coords, armc, all_houses):
    houses = ephemeris.armc_get(
        chart.HOUSE, jd, armc, *coords, ephemeris.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_houses) == sorted(houses)


def test_get_angles(jd, coords, all_angles):
    angles = ephemeris.get_angles(jd, *coords, chart.PLACIDUS)
    assert sorted(all_angles) == sorted(angles)


def test_get_armc_angles(jd, coords, armc, all_angles):
    angles = ephemeris.get_armc_angles(
        armc, coords[0], ephemeris.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_angles) == sorted(angles)


def test_get_angle(jd, coords, all_angles):
    for index in all_angles:
        angle = ephemeris.get_angle(index, jd, *coords, chart.PLACIDUS)
        assert angle["index"] == index and angle["type"] == chart.ANGLE

    assert ephemeris.get_angle(
        ephemeris.ALL, jd, *coords, chart.PLACIDUS
    ) == ephemeris.get_angles(jd, *coords, chart.PLACIDUS)


def test_get_armc_angle(jd, coords, armc, all_angles):
    obliquity = ephemeris.earth_obliquity(jd)

    for index in all_angles:
        angle = ephemeris.get_armc_angle(index, armc, coords[0], obliquity, chart.PLACIDUS)
        assert angle["index"] == index and angle["type"] == chart.ANGLE

    assert ephemeris.get_armc_angle(
        ephemeris.ALL, armc, coords[0], obliquity, chart.PLACIDUS
    ) == ephemeris.get_armc_angles(armc, coords[0], obliquity, chart.PLACIDUS)


def test_get_houses(jd, coords, all_houses):
    houses = ephemeris.get_houses(jd, *coords, chart.PLACIDUS)
    assert sorted(all_houses) == sorted(houses)


def test_get_armc_houses(jd, coords, armc, all_houses):
    houses = ephemeris.get_armc_houses(
        armc, coords[0], ephemeris.earth_obliquity(jd), chart.PLACIDUS
    )
    assert sorted(all_houses) == sorted(houses)


def test_get_house(jd, coords, all_houses):
    for index in all_houses:
        house = ephemeris.get_house(index, jd, *coords, chart.PLACIDUS)
        assert house["index"] == index and house["type"] == chart.HOUSE

    assert ephemeris.get_house(
        ephemeris.ALL, jd, *coords, chart.PLACIDUS
    ) == ephemeris.get_houses(jd, *coords, chart.PLACIDUS)


def test_get_armc_house(jd, coords, armc, all_houses):
    obliquity = ephemeris.earth_obliquity(jd)

    for index in all_houses:
        house = ephemeris.get_armc_house(index, armc, coords[0], obliquity, chart.PLACIDUS)
        assert house["index"] == index and house["type"] == chart.HOUSE

    assert ephemeris.get_armc_house(
        ephemeris.ALL, armc, coords[0], obliquity, chart.PLACIDUS
    ) == ephemeris.get_armc_houses(armc, coords[0], obliquity, chart.PLACIDUS)


def test_planet_on_first_house(jd, coords):
    sun = ephemeris.get_planet(chart.SUN, jd)
    first_house = ephemeris.get_house(chart.HOUSE1, jd, *coords, chart.SUN_ON_FIRST)
    second_house = ephemeris.get_house(chart.HOUSE2, jd, *coords, chart.SUN_ON_FIRST)

    assert sun["lon"] == first_house["lon"]
    assert sun["lon"] + 30 == second_house["lon"]


def test_get_point(jd, coords, all_points):
    for index in all_points:
        point = ephemeris.get_point(
            index, jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA
        )
        assert point["index"] == index and point["type"] == chart.POINT


def test_get_armc_point(jd, coords, armc, all_points):
    for index in all_points:
        point = ephemeris.get_armc_point(
            index,
            jd,
            armc,
            coords[0],
            ephemeris.earth_obliquity(jd),
            chart.PLACIDUS,
            calc.DAY_NIGHT_FORMULA,
        )
        assert point["index"] == index and point["type"] == chart.POINT


def test_get_planet(jd, all_planets):
    for index in all_planets:
        planet = ephemeris.get_planet(index, jd)
        assert planet["index"] == index and planet["type"] == chart.PLANET


def test_get_asteroid(jd, all_asteroids):
    settings.add_filepath(os.path.dirname(__file__))

    for index in all_asteroids:
        asteroid = ephemeris.get_asteroid(index, jd)
        assert asteroid["index"] == index and asteroid["type"] == chart.ASTEROID


def test_get_fixed_star(jd):
    # So many fixed stars we just test one
    fixed_star = ephemeris.get_fixed_star("Antares", jd)
    assert fixed_star["index"] == "Antares" and fixed_star["type"] == chart.FIXED_STAR


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


""" Now we are satisfied the correct chart objects are being returned,
we can test the accuracy of the module's data. """


def test_get_data(coords, jd, astro):
    settings.add_filepath(os.path.dirname(__file__))

    data = {
        "asc": ephemeris.get_angle(chart.ASC, jd, *coords, chart.PLACIDUS),
        "house_2": ephemeris.get_house(chart.HOUSE2, jd, *coords, chart.PLACIDUS),
        "sun": ephemeris.get_planet(chart.SUN, jd),
        "pof": ephemeris.get_point(
            chart.PART_OF_FORTUNE, jd, *coords, part_formula=calc.DAY_NIGHT_FORMULA
        ),
        "juno": ephemeris.get_asteroid(chart.JUNO, jd),  # Included with planets
        "lilith": ephemeris.get_asteroid(1181, jd),  # From external file
        "antares": ephemeris.get_fixed_star("Antares", jd),
        "pre_natal_solar_eclipse": ephemeris.get_eclipse(chart.PRE_NATAL_SOLAR_ECLIPSE, jd),
        "pre_natal_lunar_eclipse": ephemeris.get_eclipse(chart.PRE_NATAL_LUNAR_ECLIPSE, jd),
        "post_natal_solar_eclipse": ephemeris.get_eclipse(
            chart.POST_NATAL_SOLAR_ECLIPSE, jd
        ),
        "post_natal_lunar_eclipse": ephemeris.get_eclipse(
            chart.POST_NATAL_LUNAR_ECLIPSE, jd
        ),
    }

    for key, eph_object in data.items():
        # Convert ecliptical longitude to sign-based
        object = eph_object.copy()
        object["lon"] = position.sign_longitude(object)

        # Format properties to string to match astro.com front-end output
        for property_key in ("lon", "lat", "speed", "dec"):
            if property_key in object:
                object[property_key] = convert.dec_to_string(object[property_key])

        # For eclipse dates
        if "date" in astro[key]:
            object["date"] = date.to_datetime(object["jd"], *coords).strftime("%d %B")

        for property, value in astro[key].items():
            assert object[property] == value


def test_armc_get_data(coords, jd, astro, armc):
    settings.add_filepath(os.path.dirname(__file__))

    obliquity = ephemeris.earth_obliquity(jd)

    data = {
        "asc": ephemeris.get_armc_angle(
            chart.ASC, armc, coords[0], obliquity, chart.PLACIDUS
        ),
        "house_2": ephemeris.get_armc_house(
            chart.HOUSE2, armc, coords[0], obliquity, chart.PLACIDUS
        ),
        "pof": ephemeris.get_armc_point(
            chart.PART_OF_FORTUNE,
            jd,
            armc,
            coords[0],
            obliquity,
            part_formula=calc.DAY_NIGHT_FORMULA,
        ),
    }

    for key, eph_object in data.items():
        # Convert ecliptic longitude to sign-based
        object = eph_object.copy()
        object["lon"] = position.sign_longitude(object)

        # Format properties to string to match astro.com front-end output
        for property_key in ("lon", "lat", "speed", "dec"):
            if property_key in object:
                object[property_key] = convert.dec_to_string(object[property_key])

        for property, value in astro[key].items():
            assert object[property] == value


"""
CALCULATIONS
--------------------------------------------------------------------------------
"""

def test_part_of_fortune_day_formula(day_jd, coords):
    sun, moon, asc = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS
    ).values()
    pof = ephemeris.part_longitude(
        chart.PART_OF_FORTUNE, sun, moon, asc, formula=calc.DAY_FORMULA
    )
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.CAPRICORN
    assert convert.dec_to_string(lon) == "11°18'41\""


def test_part_of_fortune_night_formula(night_jd, coords):
    sun, moon, asc = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS
    ).values()
    pof = ephemeris.part_longitude(
        chart.PART_OF_FORTUNE, sun, moon, asc, formula=calc.NIGHT_FORMULA
    )
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.SAGITTARIUS
    assert convert.dec_to_string(lon) == "10°04'30\""


def test_part_of_spirit_day_formula(day_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS
    ).values()
    pos = ephemeris.part_longitude(
        chart.PART_OF_SPIRIT, sun, moon, asc, formula=calc.DAY_FORMULA
    )
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.ARIES
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("29°54'"), 1)


def test_part_of_spirit_night_formula(night_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS
    ).values()
    pos = ephemeris.part_longitude(
        chart.PART_OF_SPIRIT, sun, moon, asc, formula=calc.NIGHT_FORMULA
    )
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.LEO
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("12°18'"), 1)


def test_part_of_eros_day_formula(day_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc, venus = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC, chart.VENUS), day_jd, *coords, chart.PLACIDUS
    ).values()
    poe = ephemeris.part_longitude(
        chart.PART_OF_EROS, sun, moon, asc, venus, formula=calc.DAY_FORMULA
    )
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.LIBRA
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("07°34'"), 1)


def test_part_of_eros_night_formula(night_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc, venus = ephemeris.get_objects(
        (chart.SUN, chart.MOON, chart.ASC, chart.VENUS),
        night_jd,
        *coords,
        chart.PLACIDUS,
    ).values()
    poe = ephemeris.part_longitude(
        chart.PART_OF_EROS, sun, moon, asc, venus, formula=calc.NIGHT_FORMULA
    )
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.GEMINI
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("22°08'"), 1)


def test_is_daytime(day_jd, night_jd, coords):
    # Sun above ascendant in astro.com chart visual
    assert ephemeris.is_daytime(day_jd, *coords) is True
    # Sun below ascendant in astro.com chart visual
    assert ephemeris.is_daytime(night_jd, *coords) is False


def test_armc_is_daytime(day_jd, coords, armc):
    # Sun above ascendant in astro.com chart visual
    assert ephemeris.armc_is_daytime(day_jd, armc, coords[0], ephemeris.earth_obliquity(day_jd)) is True


def test_is_daytime_from(day_jd, night_jd, coords):
    sun, asc = ephemeris.get_objects(
        (chart.SUN, chart.ASC), day_jd, *coords, chart.PLACIDUS
    ).values()
    assert ephemeris.is_daytime_from(sun, asc) is True

    sun, asc = ephemeris.get_objects(
        (chart.SUN, chart.ASC), night_jd, *coords, chart.PLACIDUS
    ).values()
    assert ephemeris.is_daytime_from(sun, asc) is False


def test_moon_phase(jd):
    # Courtesy of https://stardate.org/nightsky/moon
    assert (
        ephemeris.moon_phase(jd) == calc.THIRD_QUARTER
    ) is True # third quarter = waning crescent


def test_moon_phase_from(jd):
    # Courtesy of https://stardate.org/nightsky/moon
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    assert (
        ephemeris.moon_phase_from(sun, moon) == calc.THIRD_QUARTER
    ) is True # third quarter = waning crescent


def test_earth_obliquity(jd):
    # Courtesy of http://neoprogrammics.com/obliquity_of_the_ecliptic/Obliquity_Of_The_Ecliptic_Calculator.php
    assert ephemeris.earth_obliquity(jd) == approx(23.4376888901)
    assert ephemeris.earth_obliquity(jd, True) == approx(23.4392911408)


def test_deltat(jd):
    # Courtesy of astro.com "Additional Tables"
    assert round(ephemeris.deltat(jd, True), 1) == 63.8


def test_sidereal_time(jd, coords):
    armc = ephemeris.get_angle(chart.ARMC, jd, *coords, chart.PLACIDUS)
    sidereal_time = ephemeris.sidereal_time(armc)
    assert convert.dec_to_string(sidereal_time, convert.FORMAT_TIME) == "16:54:13"


def test_object_movement(jd, coords):
    sun, moon, saturn, true_north_node, part_of_fortune = ephemeris.get_objects(
        (
            chart.SUN,
            chart.MOON,
            chart.SATURN,
            chart.TRUE_NORTH_NODE,
            chart.PART_OF_FORTUNE,
        ),
        jd,
        *coords,
        chart.PLACIDUS,
        calc.DAY_NIGHT_FORMULA,
    ).values()
    assert ephemeris.object_movement(sun) == calc.DIRECT
    assert ephemeris.object_movement(moon) == calc.DIRECT
    assert ephemeris.object_movement(saturn) == calc.RETROGRADE
    assert ephemeris.object_movement(true_north_node) == calc.RETROGRADE
    assert ephemeris.object_movement(part_of_fortune) == calc.STATIONARY


def test_is_object_movement_typical(jd, coords):
    sun, north_node, part_of_fortune = ephemeris.get_objects(
        (chart.SUN, chart.NORTH_NODE, chart.PART_OF_FORTUNE),
        jd,
        *coords,
        chart.PLACIDUS,
        calc.DAY_NIGHT_FORMULA,
    ).values()
    # Direct
    assert ephemeris.is_object_movement_typical(sun) == True
    sun["speed"] *= -1
    assert ephemeris.is_object_movement_typical(sun) == False
    # Retrograde
    assert ephemeris.is_object_movement_typical(north_node) == True
    north_node["speed"] *= -1
    assert ephemeris.is_object_movement_typical(north_node) == False
    # Stationed
    assert ephemeris.is_object_movement_typical(part_of_fortune) == True
    part_of_fortune["speed"] *= -1
    assert ephemeris.is_object_movement_typical(part_of_fortune) == True


def test_is_out_of_bounds(day_jd, coords):
    sun, mercury = ephemeris.get_objects(
        (chart.SUN, chart.MERCURY), day_jd, *coords, chart.PLACIDUS
    ).values()
    assert ephemeris.is_out_of_bounds(sun, day_jd) is False
    assert ephemeris.is_out_of_bounds(mercury, day_jd) is True


def test_is_in_sect_day(day_jd, coords):
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.get_objects(
        (
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
        ),
        day_jd,
        *coords,
    ).values()
    assert ephemeris.is_in_sect(sun, True) == True
    assert ephemeris.is_in_sect(jupiter, True) == True
    assert ephemeris.is_in_sect(saturn, True) == True
    assert ephemeris.is_in_sect(moon, True) == False
    assert ephemeris.is_in_sect(venus, True) == False
    assert ephemeris.is_in_sect(mars, True) == False
    assert ephemeris.is_in_sect(mercury, True, sun) == (
        ephemeris.relative_position(sun, mercury) == calc.ORIENTAL
    )


def test_is_in_sect_night(night_jd, coords):
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.get_objects(
        (
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
        ),
        night_jd,
        *coords,
    ).values()
    assert ephemeris.is_in_sect(sun, False) == False
    assert ephemeris.is_in_sect(jupiter, False) == False
    assert ephemeris.is_in_sect(saturn, False) == False
    assert ephemeris.is_in_sect(moon, False) == True
    assert ephemeris.is_in_sect(venus, False) == True
    assert ephemeris.is_in_sect(mars, False) == True
    assert ephemeris.is_in_sect(mercury, False, sun) == (
        ephemeris.relative_position(sun, mercury) == calc.OCCIDENTAL
    )


def test_relative_position(day_jd, coords):
    sun, mercury, neptune = ephemeris.get_objects(
        (chart.SUN, chart.MERCURY, chart.NEPTUNE), day_jd, *coords
    ).values()
    assert ephemeris.relative_position(sun, mercury) == calc.ORIENTAL
    assert ephemeris.relative_position(sun, neptune) == calc.OCCIDENTAL
    assert ephemeris.relative_position(mercury, neptune) == calc.OCCIDENTAL
    assert ephemeris.relative_position(neptune, mercury) == calc.ORIENTAL


def test_orbital_eccentricity():
    """Since it is difficult to find exact values in reliable 3rd-party sources
    I'll leave these tests for future-me to worry about."""
    pass


def test_sidereal_period():
    """See above."""
    pass


def test_tropical_period():
    """See above."""
    pass


def test_synodic_period():
    """See above."""
    pass


def test_synodic_period_between():
    """See above."""
    pass


def test_retrograde_period():
    """See above."""
    pass


def test_solar_year_length():
    """See above. Yes I'm lazy. Also we can leave it to the forecast module
    tests to check the correct progressed Julian dates that come from this
    function."""
    pass


"""
PREDICTIVE CALCULATIONS
--------------------------------------------------------------------------------
"""

def test_previous_aspect(jd, coords):
    # Check for previous Sun / Moon conjunction so we can use the same
    # test date/time as test_previous_new_moon()
    tr_jd = ephemeris.previous_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.to_datetime(tr_jd, *coords)
    assert tr_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-07 14:31"


def test_next_aspect(jd, coords):
    # Check for next Sun / Moon conjunction so we can use the same
    # test date/time as test_next_new_moon()
    tr_jd = ephemeris.next_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.to_datetime(tr_jd, *coords)
    assert tr_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-06 10:13"


def test_previous_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = ephemeris.previous_new_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-07 14:31"


def test_previous_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = ephemeris.previous_full_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-22 09:31"


def test_next_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = ephemeris.next_new_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-06 10:13"


def test_next_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = ephemeris.next_full_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-20 20:40"


def test_previous_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/solar/1999-august-11
    ec_type, ec_jd = ephemeris.previous_solar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "1999-08-11 04:03"


def test_previous_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/lunar/1999-july-28
    ec_type, ec_jd = ephemeris.previous_lunar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "1999-07-28 04:33"


def test_next_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/solar/2000-february-5
    ec_type, ec_jd = ephemeris.next_solar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "2000-02-05 04:49"


def test_next_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/lunar/2000-january-21
    ec_type, ec_jd = ephemeris.next_lunar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-20 20:43"
