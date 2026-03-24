"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The transit module's figures are tested against the output of the websites
    cited in each test function's comments.

"""

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.tools import convert, date, transit


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


def test_previous_sign_ingress(jd, coords):
    # https://horoscopes.astro-seek.com reports 01:26 UTC for ingress into Taurus / egress from Aries
    # so when counting backwards this is the moment Saturn ingresses into Aries from Taurus
    # and we can accept 01:25:45 UTC as the last time Saturn was in Aries since it rounds to 26 minutes
    si_jd = transit.previous_sign_ingress(chart.SATURN, chart.ARIES, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "1999-02-28 17:25"


def test_next_sign_ingress(jd, coords):
    # https://horoscopes.astro-seek.com reports 02:27 UTC for ingress into Gemini
    # so we can accept 02:26:33 UTC as the next time Saturn will be in Gemini since it rounds to 27 minutes
    si_jd = transit.next_sign_ingress(chart.SATURN, chart.GEMINI, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "2000-08-09 19:26"


def test_previous_sign_egress(jd, coords):
    # https://horoscopes.astro-seek.com reports 01:26 UTC for ingress into Taurus / egress from Aries
    # so when counting backwards this is the moment Saturn egresses from Taurus into Aries
    # and we can accept 01:25:45 UTC as the last time Saturn was in Aries since it rounds to 26 minutes
    se_jd = transit.previous_sign_egress(chart.SATURN, chart.TAURUS, jd)
    se_dt = date.to_datetime(se_jd, *coords)
    assert se_dt.strftime("%Y-%m-%d %H:%M") == "1999-02-28 17:25"


def test_next_sign_egress(jd, coords):
    # https://horoscopes.astro-seek.com reports 02:27 UTC for ingress into Gemini / egress from Taurus
    # so we can accept 02:26:33 UTC as the last time Saturn was in Taurus since it rounds to 27 minutes
    se_jd = transit.next_sign_egress(chart.SATURN, chart.TAURUS, jd)
    se_dt = date.to_datetime(se_jd, *coords)
    assert se_dt.strftime("%Y-%m-%d %H:%M") == "2000-08-09 19:26"


def test_previous_aspect(jd, coords):
    # Check for previous Sun / Moon conjunction so we can use the same
    # test date/time as test_previous_new_moon()
    tr_jd = transit.previous_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.to_datetime(tr_jd, *coords)
    assert tr_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-07 14:31"


def test_next_aspect(jd, coords):
    # Check for next Sun / Moon conjunction so we can use the same
    # test date/time as test_next_new_moon()
    tr_jd = transit.next_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    tr_dt = date.to_datetime(tr_jd, *coords)
    assert tr_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-06 10:13"


def test_previous_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = transit.previous_new_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-07 14:31"


def test_previous_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    nm_jd = transit.previous_full_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-22 09:31"


def test_next_new_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = transit.next_new_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-06 10:13"


def test_next_full_moon(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=2000
    nm_jd = transit.next_full_moon(jd)
    nm_dt = date.to_datetime(nm_jd, *coords)
    assert nm_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-20 20:40"


def test_previous_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/solar/1999-august-11
    ec_type, ec_jd = transit.previous_solar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "1999-08-11 04:03"


def test_previous_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=1990
    # https://www.timeanddate.com/eclipse/lunar/1999-july-28
    ec_type, ec_jd = transit.previous_lunar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "1999-07-28 04:33"


def test_next_solar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/solar/2000-february-5
    ec_type, ec_jd = transit.next_solar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.PARTIAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "2000-02-05 04:49"


def test_next_lunar_eclipse(jd, coords):
    # https://www.timeanddate.com/eclipse/list.html?starty=2000
    # https://www.timeanddate.com/eclipse/lunar/2000-january-21
    ec_type, ec_jd = transit.next_lunar_eclipse(jd)
    ec_dt = date.to_datetime(ec_jd, *coords)
    assert ec_type == chart.TOTAL
    assert ec_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-20 20:43"
