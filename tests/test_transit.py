"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The transit module's figures are tested against the output of the websites
cited in each test function's comments.

"""

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.tools import condition, convert, date, position, sweph, transit


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


def test_previous_sign_ingress(jd, coords):
    # https://horoscopes.astro-seek.com reports 01:26 UTC for ingress into
    # Taurus / egress from Aries so when counting backwards this is the moment Saturn
    # ingresses into Aries from Taurus and we can accept 01:25:45 UTC as the last time
    # Saturn was in Aries since it rounds to 26 minutes
    si_jd = transit.previous_sign_ingress(chart.SATURN, chart.ARIES, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "1999-02-28 17:25"
    assert position.sign(sweph.planet(chart.SATURN, si_jd)) == chart.ARIES


def test_next_sign_ingress(jd, coords):
    # https://horoscopes.astro-seek.com reports 02:27 UTC for ingress into Gemini
    # so we can accept 02:26:33 UTC as the next time Saturn will be in Gemini since
    # it rounds to 27 minutes
    si_jd = transit.next_sign_ingress(chart.SATURN, chart.GEMINI, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "2000-08-09 19:26"
    assert position.sign(sweph.planet(chart.SATURN, si_jd)) == chart.GEMINI


def test_previous_sign_egress(jd, coords):
    # https://horoscopes.astro-seek.com reports 01:26 UTC for ingress into
    # Taurus / egress from Aries so when counting backwards this is the moment Saturn
    # egresses from Taurus into Aries and we can accept 01:25:45 UTC as the last time
    # Saturn was in Aries since it rounds to 26 minutes
    se_jd = transit.previous_sign_egress(chart.SATURN, chart.TAURUS, jd)
    se_dt = date.to_datetime(se_jd, *coords)
    assert se_dt.strftime("%Y-%m-%d %H:%M") == "1999-02-28 17:25"
    assert position.sign(sweph.planet(chart.SATURN, se_jd)) == chart.ARIES


def test_next_sign_egress(jd, coords):
    # https://horoscopes.astro-seek.com reports 02:27 UTC for ingress into
    # Gemini / egress from Taurus so we can accept 02:26:33 UTC as the last time Saturn
    # was in Taurus since it rounds to 27 minutes
    se_jd = transit.next_sign_egress(chart.SATURN, chart.TAURUS, jd)
    se_dt = date.to_datetime(se_jd, *coords)
    assert se_dt.strftime("%Y-%m-%d %H:%M") == "2000-08-09 19:26"
    assert position.sign(sweph.planet(chart.SATURN, se_jd)) == chart.GEMINI


def test_next_sign_ingress_long_period(jd, coords):
    # https://horoscopes.astro-seek.com reports Pluto changing signs 5 times
    # starting with an ingress into Aquarius on 2023-03-23 12:24 UTC. However,
    # astro.com's swetest reports 12:22 UTC. With astro-seek not giving us
    # seconds, we use swetest's time in case this is a Delta-T difference.
    # Either way, we need to ensure our stepping code does not skip any sign
    # changes when searching over long periods / taking large steps.
    si_jd = transit.next_sign_ingress(chart.PLUTO, chart.AQUARIUS, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "2023-03-23 05:22"


def test_next_sign_egress_during_station(coords):
    # https://horoscopes.astro-seek.com reports Saturn retrograding just inside
    # Gemini back into Taurus at 2000-09-12 11:34 UTC. We need to ensure our
    # stepping code works even for miniscule speeds and small distances. A day
    # either side should still find the same egress.
    station_jd = date.to_jd("2000-09-12 04:34", *coords)
    for day_offset in (-1, 0, 1):
        se_jd = transit.next_sign_egress(
            chart.SATURN, chart.GEMINI, station_jd + day_offset
        )
        se_dt = date.to_datetime(se_jd, *coords)
        assert se_dt.strftime("%Y-%m-%d %H:%M") == "2000-10-15 17:44"


def test_sign_ingress_egress_retrograde(jd, coords):
    # https://horoscopes.astro-seek.com reports Mercury entering Scorpio
    # on 2000-09-28 13:28 UTC and later retrograding back into Libra before
    # re-entering Scorpio. There is once again a minute discrepancy between
    # astro-seek.com and swetest, possibly from Delta-T, so we go with swetest.
    si_jd = transit.next_sign_ingress(chart.MERCURY, chart.SCORPIO, jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "2000-09-28 06:27"
    se_jd = transit.next_sign_egress(chart.MERCURY, chart.SCORPIO, si_jd)
    se_dt = date.to_datetime(se_jd, *coords)
    assert se_dt.strftime("%Y-%m-%d %H:%M") == "2000-11-06 23:27"
    si_jd = transit.next_sign_ingress(chart.MERCURY, chart.SCORPIO, se_jd)
    si_dt = date.to_datetime(si_jd, *coords)
    assert si_dt.strftime("%Y-%m-%d %H:%M") == "2000-11-08 13:42"


def test_previous_aspect_between(jd, coords):
    # Check for previous Sun / Moon conjunction so we can use the same
    # test date/time as test_previous_new_moon()
    ab_jd = transit.previous_aspect_between(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    ab_dt = date.to_datetime(ab_jd, *coords)
    assert ab_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-07 14:31"


def test_next_aspect_between(jd, coords):
    # Check for next Sun / Moon conjunction so we can use the same
    # test date/time as test_next_new_moon()
    ab_jd = transit.next_aspect_between(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)
    ab_dt = date.to_datetime(ab_jd, *coords)
    assert ab_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-06 10:13"


def test_aspect_between_either_side(jd, coords):
    # https://www.timeanddate.com/moon/phases/?year=1999
    # https://www.timeanddate.com/moon/phases/?year=2000
    # Aspects outside of conjunctions and oppositions can happen in 2 places
    # on either side of the aspecting planet. Here we use first & third quarter
    # moon phases to test that both sides' squares are being picked up.
    ab_jd = transit.previous_aspect_between(chart.SUN, chart.MOON, jd, calc.SQUARE)
    ab_dt = date.to_datetime(ab_jd, *coords)
    assert ab_dt.strftime("%Y-%m-%d %H:%M") == "1999-12-29 06:04"
    ab_jd = transit.next_aspect_between(chart.SUN, chart.MOON, jd, calc.SQUARE)
    ab_dt = date.to_datetime(ab_jd, *coords)
    assert ab_dt.strftime("%Y-%m-%d %H:%M") == "2000-01-14 05:34"


def test_previous_aspect_to(jd, coords):
    # Check for previous Saturn / end-of-Aries conjunction so we can use the
    # same test date/time as test_previous_sign_ingress()
    at_jd = transit.previous_aspect_to(chart.SATURN, 30.0, jd, calc.CONJUNCTION)
    at_dt = date.to_datetime(at_jd, *coords)
    assert at_dt.strftime("%Y-%m-%d %H:%M") == "1999-02-28 17:25"


def test_next_aspect_to(jd, coords):
    # Check for next Saturn / start-of-Gemini conjunction so we can use the same
    # test date/time as test_next_sign_ingress()
    at_jd = transit.next_aspect_to(chart.SATURN, 60.0, jd, calc.CONJUNCTION)
    at_dt = date.to_datetime(at_jd, *coords)
    assert at_dt.strftime("%Y-%m-%d %H:%M") == "2000-08-09 19:26"


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


def test_syzygy_moon_phases(jd):
    # Our aspect search aims to always fall on the side on just-after rather
    # than just-before. Moon phases are a good test to ensure this happens.
    assert condition.moon_phase(transit.previous_new_moon(jd)) == calc.NEW_MOON
    assert condition.moon_phase(transit.next_new_moon(jd)) == calc.NEW_MOON
    assert condition.moon_phase(transit.previous_full_moon(jd)) == calc.FULL_MOON
    assert condition.moon_phase(transit.next_full_moon(jd)) == calc.FULL_MOON


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
