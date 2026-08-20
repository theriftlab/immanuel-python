"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The sweph module's output is compared to the output of
astro.com's Additional Tables with the chart generated
using the default Placidus house system.

This is not a comprehensive test of every chart object
of every kind, but a spot-check of one of each type to
guarantee we're getting both the correct types of data
and the correct values.

Yes I like to write comment blocks where the lines end
with the same character count, apart from the last one
which is always shorter.

"""

import os

import pytest
from pytest import approx, fixture
from pytest_lazy_fixtures import lf

from immanuel import settings
from immanuel.const import calc, chart
from immanuel.tools import condition, convert, date, part, position, sweph, transit


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def armc():
    # ARMC longitude on the above jd
    return 253.55348499294269


@fixture
def astro():
    """Results copied from astro.com chart table. We spot-check
    chart objects by picking one or a few of each type."""
    return {
        # angle
        chart.ASC: {
            "lon": "05°36'38\"",
            # This is the only figure disagreeing with astro.com (~1 arcsec) and nobody knows why
            # It is not mean vs true obliquty, or a Delta-T thing
            # "dec": "-09°27'13\"",
        },
        # house
        chart.HOUSE2: {
            "lon": "17°59'40\"",
            "dec": "07°03'29\"",
        },
        # planet
        chart.SUN: {
            "lon": "10°37'26\"",
            "lat": "00°00'01\"",
            "speed": "01°01'10\"",
            "dec": "-23°00'45\"",
        },
        # points
        chart.PART_OF_FORTUNE: {
            "lon": "11°18'41\"",
            "dec": "-22°57'22\"",
        },
        chart.TRUE_NORTH_NODE: {
            "lon": "03°56'24\"",
            "speed": "-00°03'28\"",
            "dec": "19°16'04\"",
        },
        chart.VERTEX: {
            "lon": "19°18'19\"",
            "dec": "04°13'59\"",
        },
        # default asteroid
        chart.JUNO: {
            "lon": "08°05'21\"",
            "lat": "09°26'57\"",
            "speed": "00°22'21\"",
            "dec": "-13°45'30\"",
        },
        # external asteroid
        1181: {
            "lon": "18°16'47\"",
            "lat": "04°49'07\"",
            "speed": "00°24'37\"",
            "dec": "-00°11'50\"",
        },
        # fixed star
        "Antares": {
            "lon": "09°45'12\"",
            "lat": "-04°34'11\"",
        },
        # eclipses
        chart.PRE_NATAL_SOLAR_ECLIPSE: {
            "lon": "18°20'59\"",
            "lat": "00°00'00\"",
            "speed": "00°00'00\"",
            "dec": "15°19'40\"",
            "eclipse_type": chart.TOTAL,
            "date": "11 August",
        },
        chart.PRE_NATAL_LUNAR_ECLIPSE: {
            "lon": "05°02'21\"",
            "lat": "00°43'35\"",
            "speed": "00°00'00\"",
            "dec": "-18°18'03\"",
            "eclipse_type": chart.PARTIAL,
            "date": "28 July",
        },
        chart.POST_NATAL_SOLAR_ECLIPSE: {
            "lon": "16°01'14\"",
            "lat": "00°00'00\"",
            "speed": "00°00'00\"",
            "dec": "-16°02'00\"",
            "eclipse_type": chart.PARTIAL,
            "date": "05 February",
        },
        chart.POST_NATAL_LUNAR_ECLIPSE: {
            "lon": "00°28'04\"",
            "lat": "-00°17'53\"",
            "speed": "00°00'00\"",
            "dec": "19°45'29\"",
            "eclipse_type": chart.TOTAL,
            "date": "20 January",
        },
    }


def test_planet(jd, astro):
    # Standard planet
    sun = sweph.planet(chart.SUN, jd)
    assert sun["index"] == chart.SUN
    assert sun["type"] == chart.PLANET
    assert (
        convert.dec_to_string(position.sign_longitude(sun)) == astro[chart.SUN]["lon"]
    )
    assert convert.dec_to_string(sun["lat"]) == astro[chart.SUN]["lat"]
    assert convert.dec_to_string(sun["speed"]) == astro[chart.SUN]["speed"]
    assert convert.dec_to_string(sun["dec"]) == astro[chart.SUN]["dec"]

    # Ensure our bundled asteroids still masquerade as planets
    juno = sweph.planet(chart.JUNO, jd)
    assert juno["index"] == chart.JUNO
    assert juno["type"] == chart.ASTEROID
    assert (
        convert.dec_to_string(position.sign_longitude(juno)) == astro[chart.JUNO]["lon"]
    )
    assert convert.dec_to_string(juno["lat"]) == astro[chart.JUNO]["lat"]
    assert convert.dec_to_string(juno["speed"]) == astro[chart.JUNO]["speed"]
    assert convert.dec_to_string(juno["dec"]) == astro[chart.JUNO]["dec"]


def test_asteroid(jd, astro):
    settings.add_filepath(os.path.dirname(__file__))
    lilith = sweph.asteroid(1181, jd)
    assert lilith["index"] == 1181
    assert lilith["type"] == chart.ASTEROID
    assert convert.dec_to_string(position.sign_longitude(lilith)) == astro[1181]["lon"]
    assert convert.dec_to_string(lilith["lat"]) == astro[1181]["lat"]
    assert convert.dec_to_string(lilith["speed"]) == astro[1181]["speed"]
    assert convert.dec_to_string(lilith["dec"]) == astro[1181]["dec"]


def test_fixed_star(jd, astro):
    antares = sweph.fixed_star("Antares", jd)
    assert antares["index"] == "Antares"
    assert antares["type"] == chart.FIXED_STAR
    assert (
        convert.dec_to_string(position.sign_longitude(antares))
        == astro["Antares"]["lon"]
    )
    assert convert.dec_to_string(antares["lat"]) == astro["Antares"]["lat"]


def test_pre_post_natal_eclipse(jd, coords, astro):
    # This is a weird one since it relies on the transits module to calcuate the
    # eclipse date and type, so it's half-testing another module altogether,
    # but we can still check for the correct keys and values.
    eclipse_functions = {
        chart.PRE_NATAL_SOLAR_ECLIPSE: transit.previous_solar_eclipse,
        chart.PRE_NATAL_LUNAR_ECLIPSE: transit.previous_lunar_eclipse,
        chart.POST_NATAL_SOLAR_ECLIPSE: transit.next_solar_eclipse,
        chart.POST_NATAL_LUNAR_ECLIPSE: transit.next_lunar_eclipse,
    }

    for index, eclipse_function in eclipse_functions.items():
        eclipse_type, eclipse_jd = eclipse_function(jd)
        eclipse = sweph.pre_post_natal_eclipse(index, jd, eclipse_type, eclipse_jd)
        assert eclipse["index"] == index
        assert eclipse["type"] == chart.ECLIPSE
        assert (
            convert.dec_to_string(position.sign_longitude(eclipse))
            == astro[index]["lon"]
        )
        assert convert.dec_to_string(eclipse["lat"]) == astro[index]["lat"]
        assert convert.dec_to_string(eclipse["speed"]) == astro[index]["speed"]
        assert convert.dec_to_string(eclipse["dec"]) == astro[index]["dec"]
        assert eclipse["eclipse_type"] == astro[index]["eclipse_type"]
        assert (
            date.to_datetime(eclipse["jd"], *coords).strftime("%d %B")
            == astro[index]["date"]
        )


def test_syzygy(jd, coords):
    # Same again - syzygy calculations are made in the transits module.
    # Ecliptic longitude courtesy of https://horoscopes.astro-seek.com
    # astro.com does not support syzygy and astro-seek only provides longitude in degrees and minutes
    syzygy_jd = (
        transit.previous_new_moon(jd)
        if condition.moon_sun_distance(jd) > 0
        else transit.previous_full_moon(jd)
    )
    date_time = date.to_datetime(syzygy_jd, *coords)
    assert date_time.year == 1999
    assert date_time.month == 12
    assert date_time.day == 22
    assert date_time.hour == 9
    assert date_time.minute == 31
    assert condition.moon_phase(syzygy_jd) == calc.FULL_MOON
    syzygy = sweph.syzygy(syzygy_jd)
    lon = convert.dec_to_dms(position.sign_longitude(syzygy))
    assert syzygy["index"] == chart.SYZYGY
    assert syzygy["type"] == chart.POINT
    assert lon[1] == 0
    assert lon[2] == 24


def test_part(jd, coords, astro):
    lat, lon = coords
    # Same again - part calculations are made in the part module.
    # We're only testing for the Part of Fortune here since the other parts
    # are derived from it and astro.com doesn't support them and I'm tired.
    part_lon = part.longitude(
        chart.PART_OF_FORTUNE, jd, lat, lon, calc.DAY_NIGHT_FORMULA
    )
    pars_fortuna = sweph.part(chart.PART_OF_FORTUNE, jd, part_lon)
    assert pars_fortuna["index"] == chart.PART_OF_FORTUNE
    assert pars_fortuna["type"] == chart.POINT
    assert (
        convert.dec_to_string(position.sign_longitude(pars_fortuna["lon"]))
        == astro[chart.PART_OF_FORTUNE]["lon"]
    )
    assert pars_fortuna["lat"] == 0.0
    assert pars_fortuna["speed"] == 0.0
    assert (
        convert.dec_to_string(pars_fortuna["dec"])
        == astro[chart.PART_OF_FORTUNE]["dec"]
    )


def test_point(jd, astro):
    true_north_node = sweph.point(chart.TRUE_NORTH_NODE, jd)
    assert true_north_node["index"] == chart.TRUE_NORTH_NODE
    assert true_north_node["type"] == chart.POINT
    assert (
        convert.dec_to_string(position.sign_longitude(true_north_node["lon"]))
        == astro[chart.TRUE_NORTH_NODE]["lon"]
    )
    assert (
        convert.dec_to_string(true_north_node["speed"])
        == astro[chart.TRUE_NORTH_NODE]["speed"]
    )
    assert (
        convert.dec_to_string(true_north_node["dec"])
        == astro[chart.TRUE_NORTH_NODE]["dec"]
    )


@pytest.mark.parametrize(
    "p_jd, p_coords, p_armc, p_astro",
    [
        (lf("jd"), lf("coords"), None, lf("astro")),
        (lf("jd"), lf("coords"), lf("armc"), lf("astro")),
    ],
)
def test_angle(p_jd, p_coords, p_armc, p_astro):
    jd, coords, armc, astro = p_jd, p_coords, p_armc, p_astro
    lat, lon = coords[0], (coords[1] if armc is None else None)
    armc_obliquity = sweph.true_earth_obliquity(jd) if armc is not None else None
    asc = sweph.angle(chart.ASC, jd, lat, lon, chart.PLACIDUS, armc, armc_obliquity)
    assert asc["index"] == chart.ASC
    assert asc["type"] == chart.ANGLE
    assert (
        convert.dec_to_string(position.sign_longitude(asc["lon"]))
        == astro[chart.ASC]["lon"]
    )
    # assert convert.dec_to_string(asc["dec"]) == astro[chart.ASC]["dec"]


@pytest.mark.parametrize(
    "p_jd, p_coords, p_armc, p_astro",
    [
        (lf("jd"), lf("coords"), None, lf("astro")),
        (lf("jd"), lf("coords"), lf("armc"), lf("astro")),
    ],
)
def test_angles_houses_vertex(p_jd, p_coords, p_armc, p_astro):
    jd, coords, armc, astro = p_jd, p_coords, p_armc, p_astro
    lat, lon = coords[0], (coords[1] if armc is None else None)
    armc_obliquity = sweph.true_earth_obliquity(jd) if armc is not None else None
    jd_angles_houses_vertex = sweph.angles_houses_vertex(
        lat, chart.PLACIDUS, None, jd, lon, armc, armc_obliquity
    )
    assert sorted(("angles", "houses", "vertex")) == sorted(jd_angles_houses_vertex)
    assert sorted(
        (
            chart.ASC,
            chart.DESC,
            chart.MC,
            chart.IC,
            chart.ARMC,
        )
    ) == sorted(jd_angles_houses_vertex["angles"])
    assert sorted(
        (
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
    ) == sorted(jd_angles_houses_vertex["houses"])
    assert isinstance(jd_angles_houses_vertex["vertex"], dict)

    assert jd_angles_houses_vertex["angles"][chart.ASC]["index"] == chart.ASC
    assert jd_angles_houses_vertex["angles"][chart.ASC]["type"] == chart.ANGLE
    assert (
        convert.dec_to_string(
            position.sign_longitude(jd_angles_houses_vertex["angles"][chart.ASC]["lon"])
        )
        == astro[chart.ASC]["lon"]
    )
    assert jd_angles_houses_vertex["houses"][chart.HOUSE2]["index"] == chart.HOUSE2
    assert jd_angles_houses_vertex["houses"][chart.HOUSE2]["type"] == chart.HOUSE
    assert (
        convert.dec_to_string(
            position.sign_longitude(
                jd_angles_houses_vertex["houses"][chart.HOUSE2]["lon"]
            )
        )
        == astro[chart.HOUSE2]["lon"]
    )
    assert (
        convert.dec_to_string(jd_angles_houses_vertex["houses"][chart.HOUSE2]["dec"])
        == astro[chart.HOUSE2]["dec"]
    )
    assert jd_angles_houses_vertex["vertex"]["index"] == chart.VERTEX
    assert jd_angles_houses_vertex["vertex"]["type"] == chart.POINT
    assert (
        convert.dec_to_string(
            position.sign_longitude(jd_angles_houses_vertex["vertex"]["lon"])
        )
        == astro[chart.VERTEX]["lon"]
    )
    assert (
        convert.dec_to_string(jd_angles_houses_vertex["vertex"]["dec"])
        == astro[chart.VERTEX]["dec"]
    )


def test_true_earth_obliquity(jd):
    # Courtesy of http://neoprogrammics.com/obliquity_of_the_ecliptic/Obliquity_Of_The_Ecliptic_Calculator.php
    assert sweph.true_earth_obliquity(jd) == approx(23.4376888901)


def test_mean_earth_obliquity(jd):
    # Courtesy of http://neoprogrammics.com/obliquity_of_the_ecliptic/Obliquity_Of_The_Ecliptic_Calculator.php
    assert sweph.mean_earth_obliquity(jd) == approx(23.4392911408)


def test_orbital_elements(jd):
    # Courtesy of https://ssd.jpl.nasa.gov/horizons/app.html#/
    jpl_orbital_elements = {
        "EC": 9.331535194932011e-02,
        "QR": 1.381496721175504e00,
        "IN": 1.849876347263833e00,
        "OM": 4.956201046382952e01,
        "W": 2.865373929182661e02,
        "Tp": 2451508.062951021828,
        "N": 5.240391695239175e-01,
        "MA": 1.948747026345698e01,
        "TA": 2.348962906506885e01,
        "A": 1.523679400710757e00,
        "AD": 1.665862080246011e00,
        "PR": 6.869715489532111e02,
    }
    # Not all settings line up exactly between the Swiss Ephemeris functions and JPL Horizons,
    # so we allow for some margin of error in a few of these values and hope nobody notices.
    orbital_elements = sweph.orbital_elements(chart.MARS, jd)
    assert orbital_elements["semimajor_axis"] == approx(jpl_orbital_elements["A"])
    assert orbital_elements["eccentricity"] == approx(jpl_orbital_elements["EC"])
    assert orbital_elements["inclination"] == approx(
        jpl_orbital_elements["IN"], abs=1e-4
    )
    assert orbital_elements["longitude_of_ascending_node"] == approx(
        jpl_orbital_elements["OM"], abs=1e-3
    )
    assert orbital_elements["argument_of_periapsis"] == approx(
        jpl_orbital_elements["W"]
    )
    assert orbital_elements["mean_anomaly_at_epoch"] == approx(
        jpl_orbital_elements["MA"], abs=1e-3
    )
    assert orbital_elements["true_anomaly_at_epoch"] == approx(
        jpl_orbital_elements["TA"], abs=1e-3
    )
    assert orbital_elements["sidereal_orbital_period"] * calc.YEAR_DAYS == approx(
        jpl_orbital_elements["PR"], abs=1e-3
    )
    assert orbital_elements["mean_daily_motion"] == approx(jpl_orbital_elements["N"])
    assert orbital_elements["time_of_perihelion_passage"] == approx(
        jpl_orbital_elements["Tp"]
    )
    assert orbital_elements["perihelion_distance"] == approx(jpl_orbital_elements["QR"])
    assert orbital_elements["aphelion_distance"] == approx(jpl_orbital_elements["AD"])


def test_type_of():
    object_types = {
        chart.HOUSE: [
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
        ],
        chart.ANGLE: [chart.ASC, chart.DESC, chart.MC, chart.IC, chart.ARMC],
        chart.PLANET: [
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
        ],
        chart.ASTEROID: [
            chart.CHIRON,
            chart.PHOLUS,
            chart.CERES,
            chart.PALLAS,
            chart.JUNO,
            chart.VESTA,
            1181,
        ],
        chart.POINT: [
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
            chart.PART_OF_SPIRIT,
            chart.PART_OF_EROS,
        ],
        chart.FIXED_STAR: [
            "Antares",
            "Aldebaran",
            "Regulus",
        ],
        chart.ECLIPSE: [
            chart.PRE_NATAL_SOLAR_ECLIPSE,
            chart.PRE_NATAL_LUNAR_ECLIPSE,
            chart.POST_NATAL_SOLAR_ECLIPSE,
            chart.POST_NATAL_LUNAR_ECLIPSE,
        ],
    }
    for object_type, objects in object_types.items():
        for obj in objects:
            assert sweph.type_of(obj) == object_type


def test_is_external():
    # I'm losing steam, let's keep this simple
    assert sweph.is_external(chart.SUN) == False
    assert sweph.is_external("Antares") == False
    assert sweph.is_external(1181) == True
