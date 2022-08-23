"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Gregorian UTC / Julian Day conversions ran against
    figures from direct swisseph functions.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import approx, fixture
import swisseph as swe

from immanuel.tools import date
from immanuel.tools.date import DateTime


@fixture
def utc_date_tuple():
    return (2000, 1, 1, 18, 0, 0)

@fixture
def utc_date():
    return datetime(2000, 1, 1, 18, tzinfo=ZoneInfo('UTC'))

@fixture
def pst_date():
    return datetime(2000, 1, 1, 10, tzinfo=ZoneInfo('America/Los_Angeles'))

@fixture
def ambiguous_date():
    return datetime(2022, 11, 6, 1, 30, tzinfo=ZoneInfo('America/Los_Angeles'))

@fixture
def utc_coords():
    return 51.509865, -0.118092     # London lat/lon

@fixture
def pst_coords():
    return 32.715736, -117.161087   # San Diego lat/lon

@fixture
def jd():
    return 2451545.1250041085       # 2000-01-01 15:00 UTC


def test_datetime_to_jd_calc(utc_date_tuple, utc_date, pst_date):
    jd_utc = date.datetime_to_jd(utc_date)
    jd_pst = date.datetime_to_jd(pst_date)
    jd_utc_swe = swe.utc_to_jd(*utc_date_tuple)[1]
    assert jd_utc == jd_utc_swe
    assert jd_pst == jd_utc_swe


def test_jd_to_datetime(jd):
    dt = date.jd_to_datetime(jd)
    assert dt.year == 2000
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 15
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.tzinfo == ZoneInfo('UTC')


def test_datetime_class_timezone(utc_date, pst_coords):
    dt = DateTime(utc_date, *pst_coords)
    assert dt.timezone == 'America/Los_Angeles'


def test_datetime_class_ambiguity_check(ambiguous_date, pst_date, pst_coords):
    ambiguous_dt = DateTime(ambiguous_date, *pst_coords)
    unambiguous_dt = DateTime(pst_date, *pst_coords)
    assert ambiguous_dt.ambiguous()
    assert not unambiguous_dt.ambiguous()


def test_datetime_class_dst(ambiguous_date, pst_coords):
    dt_no_dst = DateTime(ambiguous_date, *pst_coords, False)
    dt_dst = DateTime(ambiguous_date, *pst_coords, True)
    assert dt_no_dst.jd - dt_dst.jd == approx(1/24)


def test_datetime_class_jd_calc(utc_date_tuple, utc_date, utc_coords, pst_date, pst_coords):
    jd_utc = DateTime(utc_date, *utc_coords).jd
    jd_pst = DateTime(pst_date, *pst_coords).jd
    jd_utc_swe = swe.utc_to_jd(*utc_date_tuple)[1]
    assert jd_utc == jd_utc_swe
    assert jd_pst == jd_utc_swe


def test_datetime_class_from_jd(jd, pst_coords):
    dt = DateTime(jd, *pst_coords)
    assert dt.datetime.year == 2000
    assert dt.datetime.month == 1
    assert dt.datetime.day == 1
    assert dt.datetime.hour == 7
    assert dt.datetime.minute == 0
    assert dt.datetime.second == 0
    assert dt.timezone == 'America/Los_Angeles'
