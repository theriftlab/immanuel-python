"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The calculate module's figures are tested against output
    from astro.com and https://stardate.org/nightsky/moon
    for the moon_phase() function.

"""

from datetime import datetime

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.tools import calculate, convert, date, ephemeris, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def day_jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def night_jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 00:00'), *coords))


def test_moon_phase(day_jd):
    # Courtesy of https://stardate.org/nightsky/moon
    sun = ephemeris.planet(chart.SUN, day_jd)
    moon = ephemeris.planet(chart.MOON, day_jd)
    assert calculate.moon_phase(sun, moon) == calc.THIRD_QUARTER             # third quarter = waning crescent


def test_is_daytime(day_jd, night_jd, coords):
    sun, asc = ephemeris.objects((chart.SUN, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun, asc) == True
    sun, asc = ephemeris.objects((chart.SUN, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun, asc) == False


def test_pars_fortuna_day_formula(day_jd, coords):
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.pars_fortuna_longitude(sun, moon, asc, calc.DAY_FORMULA)
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.CAPRICORN
    assert convert.dec_to_string(lon) == '11°18\'41"'


def test_pars_fortuna_night_formula(night_jd, coords):
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.pars_fortuna_longitude(sun, moon, asc, calc.NIGHT_FORMULA)
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.SAGITTARIUS
    assert convert.dec_to_string(lon) == '10°04\'30"'


def test_sidereal_time(day_jd, coords):
    armc = ephemeris.angle(chart.ARMC, day_jd, *coords, chart.PLACIDUS)
    sidereal_time = calculate.sidereal_time(armc)
    assert convert.dec_to_string(sidereal_time, convert.FORMAT_TIME) == '16:54:13'


def test_object_movement(day_jd, coords):
    sun, moon, saturn, true_north_node, pars_fortuna = ephemeris.objects((chart.SUN, chart.MOON, chart.SATURN, chart.TRUE_NORTH_NODE, chart.PARS_FORTUNA), day_jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA).values()
    assert calculate.object_movement(sun) == calc.DIRECT
    assert calculate.object_movement(moon) == calc.DIRECT
    assert calculate.object_movement(saturn) == calc.RETROGRADE
    assert calculate.object_movement(true_north_node) == calc.RETROGRADE
    assert calculate.object_movement(pars_fortuna) == calc.STATIONARY


def test_is_out_of_bounds(day_jd, coords):
    sun, mercury = ephemeris.objects((chart.SUN, chart.MERCURY), day_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_out_of_bounds(sun, day_jd) == False
    assert calculate.is_out_of_bounds(mercury, day_jd) == True


def test_solar_year_length():
    """ This one is difficult to test in isolatioon since it's only used for
    secondary progressions. For now we'll leave it to the forecast module
    tests to check the correct progressed Julian dates. """
    pass
