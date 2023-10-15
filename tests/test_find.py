"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Courtesy of timeanddate.com.
    Moon phase data: https://www.timeanddate.com/moon/phases
    Eclipse data: https://www.timeanddate.com/eclipse/list.html

"""


from datetime import datetime

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.tools import convert, date, find


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))


def test_previous(jd, coords):
    # Check for previous Sun / Moon conjunction so we can use the same
    # test date/time as test_previous_new_moon()
    tr_jd = find.previous(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.from_jd(tr_jd, *coords)
    assert tr_dt.strftime('%Y-%m-%d %H:%M') == '1999-12-07 14:31'


def test_next(jd, coords):
    # Check for next Sun / Moon conjunction so we can use the same
    # test date/time as test_next_new_moon()
    tr_jd = find.next(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.from_jd(tr_jd, *coords)
    assert tr_dt.strftime('%Y-%m-%d %H:%M') == '2000-01-06 10:13'


def test_previous_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = find.previous_new_moon(jd)
    nm_dt = date.from_jd(nm_jd, *coords)
    assert nm_dt.strftime('%Y-%m-%d %H:%M') == '1999-12-07 14:31'


def test_previous_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = find.previous_full_moon(jd)
    nm_dt = date.from_jd(nm_jd, *coords)
    assert nm_dt.strftime('%Y-%m-%d %H:%M') == '1999-12-22 09:31'


def test_next_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = find.next_new_moon(jd)
    nm_dt = date.from_jd(nm_jd, *coords)
    assert nm_dt.strftime('%Y-%m-%d %H:%M') == '2000-01-06 10:13'


def test_next_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = find.next_full_moon(jd)
    nm_dt = date.from_jd(nm_jd, *coords)
    assert nm_dt.strftime('%Y-%m-%d %H:%M') == '2000-01-20 20:40'


def test_previous_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/solar/1999-august-11
    ec_type, ec_jd = find.previous_solar_eclipse(jd)
    ec_dt = date.from_jd(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime('%Y-%m-%d %H:%M') == '1999-08-11 04:03'


def test_previous_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/lunar/1999-july-28
    ec_type, ec_jd = find.previous_lunar_eclipse(jd)
    ec_dt = date.from_jd(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime('%Y-%m-%d %H:%M') == '1999-07-28 04:33'


def test_next_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/solar/2000-february-5
    ec_type, ec_jd = find.next_solar_eclipse(jd)
    ec_dt = date.from_jd(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime('%Y-%m-%d %H:%M') == '2000-02-05 04:49'


def test_next_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/lunar/2000-january-21
    ec_type, ec_jd = find.next_lunar_eclipse(jd)
    ec_dt = date.from_jd(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime('%Y-%m-%d %H:%M') == '2000-01-20 20:43'
