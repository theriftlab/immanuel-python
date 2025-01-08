"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Gregorian UT / Julian Day conversions ran against
    figures from https://ssd.jpl.nasa.gov/tools/jdc/#/cd

"""

from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import approx, fixture

from immanuel.tools import date


@fixture
def gmt_date():
    return datetime(2000, 1, 1, 18, tzinfo=ZoneInfo('Europe/London'))

@fixture
def pst_date():
    return datetime(2000, 1, 1, 10, tzinfo=ZoneInfo('America/Los_Angeles'))

@fixture
def str_gmt_date():
    return '2000-01-01 18:00:00'

@fixture
def str_pst_date():
    return '2000-01-01 10:00:00'

@fixture
def ambiguous_date():
    return datetime(2022, 11, 6, 1, 30, tzinfo=ZoneInfo('America/Los_Angeles'))

@fixture
def gmt_coords():
    return 51.509865, -0.118092     # London lat/lon

@fixture
def pst_coords():
    return 32.715736, -117.161087   # San Diego lat/lon

@fixture
def jd():
    return 2451545.25               # 2000-01-01 18:00 UT


def test_timezone_name_gmt(gmt_coords):
    assert date.timezone_name(*gmt_coords) == 'Europe/London'


def test_timezone_name_pst(pst_coords):
    assert date.timezone_name(*pst_coords) == 'America/Los_Angeles'


def test_localize_coords(pst_coords):
    dt = datetime(2000, 1, 1, 18)
    aware = date.localize(dt, *pst_coords)
    assert aware.tzinfo == ZoneInfo('America/Los_Angeles')


def test_localize_offset(gmt_coords, jd):
    dt = datetime(2000, 1, 1, 10)
    aware = date.localize(dt, *gmt_coords, offset=-8.0)
    assert date.to_jd(aware) == jd


def test_localize_dst(ambiguous_date, pst_coords):
    dt_no_dst = date.localize(ambiguous_date, *pst_coords, is_dst=False)
    dt_dst = date.localize(ambiguous_date, *pst_coords, is_dst=True)
    jd_no_dst = date.to_jd(dt_no_dst)
    jd_dst = date.to_jd(dt_dst)
    assert dt_no_dst.hour == dt_dst.hour
    assert jd_no_dst - jd_dst == approx(1/24)


def test_ambiguous(ambiguous_date, pst_date):
    assert date.ambiguous(ambiguous_date) is True
    assert date.ambiguous(pst_date) is False


def test_to_jd(str_pst_date, gmt_date, pst_date, pst_coords, gmt_coords, jd):
    assert date.to_jd(jd) == jd
    assert date.to_jd(str_pst_date, *pst_coords) == jd
    assert date.to_jd(str_pst_date, *gmt_coords, offset=-8.0) == jd
    assert date.to_jd(gmt_date) == jd
    assert date.to_jd(pst_date) == jd


def test_to_datetime_gmt(gmt_date, str_gmt_date, gmt_coords, jd):
    dt_original = date.to_datetime(gmt_date)
    assert dt_original.year == 2000
    assert dt_original.month == 1
    assert dt_original.day == 1
    assert dt_original.hour == 18
    assert dt_original.minute == 0
    assert dt_original.second == 0
    assert dt_original.tzinfo == ZoneInfo('Europe/London')

    dt_from_str = date.to_datetime(str_gmt_date, *gmt_coords)
    assert dt_from_str.year == 2000
    assert dt_from_str.month == 1
    assert dt_from_str.day == 1
    assert dt_from_str.hour == 18
    assert dt_from_str.minute == 0
    assert dt_from_str.second == 0
    assert dt_from_str.tzinfo == ZoneInfo('Europe/London')

    dt_from_jd = date.to_datetime(jd, *gmt_coords)
    assert dt_from_jd.year == 2000
    assert dt_from_jd.month == 1
    assert dt_from_jd.day == 1
    assert dt_from_jd.hour == 18
    assert dt_from_jd.minute == 0
    assert dt_from_jd.second == 0
    assert dt_from_jd.tzinfo == ZoneInfo('Europe/London')

    utc_dt_from_jd = date.to_datetime(jd)
    assert utc_dt_from_jd.year == 2000
    assert utc_dt_from_jd.month == 1
    assert utc_dt_from_jd.day == 1
    assert utc_dt_from_jd.hour == 18
    assert utc_dt_from_jd.minute == 0
    assert utc_dt_from_jd.second == 0
    assert utc_dt_from_jd.tzinfo == ZoneInfo('UTC')


def test_to_datetime_pst(pst_date, str_pst_date, pst_coords, gmt_coords, jd):
    dt_original = date.to_datetime(pst_date)
    assert dt_original.year == 2000
    assert dt_original.month == 1
    assert dt_original.day == 1
    assert dt_original.hour == 10
    assert dt_original.minute == 0
    assert dt_original.second == 0
    assert dt_original.tzinfo == ZoneInfo('America/Los_Angeles')

    dt_from_str = date.to_datetime(str_pst_date, *pst_coords)
    assert dt_from_str.year == 2000
    assert dt_from_str.month == 1
    assert dt_from_str.day == 1
    assert dt_from_str.hour == 10
    assert dt_from_str.minute == 0
    assert dt_from_str.second == 0
    assert dt_from_str.tzinfo == ZoneInfo('America/Los_Angeles')

    dt_from_jd = date.to_datetime(jd, *pst_coords)
    assert dt_from_jd.year == 2000
    assert dt_from_jd.month == 1
    assert dt_from_jd.day == 1
    assert dt_from_jd.hour == 10
    assert dt_from_jd.minute == 0
    assert dt_from_jd.second == 0
    assert dt_from_jd.tzinfo == ZoneInfo('America/Los_Angeles')

    dt_from_offset = date.to_datetime(jd, *gmt_coords, offset=-8.0)
    assert dt_from_offset.year == 2000
    assert dt_from_offset.month == 1
    assert dt_from_offset.day == 1
    assert dt_from_offset.hour == 10
    assert dt_from_offset.minute == 0
    assert dt_from_offset.second == 0
