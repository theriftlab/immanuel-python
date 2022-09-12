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
from immanuel.tools import calculate, convert, date, eph, position


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
    assert eph.moon_phase(day_jd) == calc.THIRD_QUARTER             # third quarter = waning crescent


def test_is_daytime(day_jd, night_jd, coords):
    sun, asc = eph.items((chart.SUN, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun['lon'], asc['lon']) == True
    sun, asc = eph.items((chart.SUN, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun['lon'], asc['lon']) == False


def test_pars_fortuna_day_formula(day_jd, coords):
    # Result copied from astro.com
    sun, moon, asc = eph.items((chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.pars_fortuna(sun['lon'], moon['lon'], asc['lon'], calc.DAY_FORMULA)
    sign, lon = position.signlon(pof)
    assert sign == chart.CAPRICORN
    assert convert.dec_to_string(lon) == '11°18\'41"'


def test_pars_fortuna_night_formula(night_jd, coords):
    # Result copied from astro.com
    sun, moon, asc = eph.items((chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.pars_fortuna(sun['lon'], moon['lon'], asc['lon'], calc.NIGHT_FORMULA)
    sign, lon = position.signlon(pof)
    assert sign == chart.SAGITTARIUS
    assert convert.dec_to_string(lon) == '10°04\'30"'
