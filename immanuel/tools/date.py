"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides simple helper functions for converting
    between location-specific Gregorian dates and times, and universal
    Julian dates.

    The conversion functions essentially wrap pyswisseph's utc_to_jd() and
    jdut1_to_utc() but take into account timezones based on lat/lon
    coordinates and do the heavy lifting for you.

"""

from datetime import datetime
from dateutil import tz
from zoneinfo import ZoneInfo

import swisseph as swe
from timezonefinder import TimezoneFinder


def ambiguous(dt: datetime) -> bool:
    """ Returns whether an aware datetime is ambiguous. """
    return tz.datetime_ambiguous(dt)


def timezone(lat: float, lon: float) -> str:
    """ Returns a timezone string based on decimal lat/lon coordinates. """
    return TimezoneFinder().timezone_at(lat=lat, lng=lon)


def localize(dt: datetime, lat: float, lon: float, is_dst = None) -> datetime:
    """ Localizes a naive datetime based on decimal lat/lon coordinates. """
    return dt.replace(tzinfo=ZoneInfo(timezone(lat, lon)), fold=1 if is_dst == False else 0)


def to_jd(dt: datetime) -> float:
    """ Convert aware datetime into UTC Julian day. """
    return swe.utc_to_jd(*dt.astimezone(ZoneInfo('UTC')).timetuple()[0:6])[1]


def from_jd(jd: float, lat: float = None, lon: float = None) -> datetime:
    """ Convert Julian day into UTC or aware datetime object. """
    swe_utc = swe.jdut1_to_utc(jd)
    seconds_float = swe_utc[5]
    seconds = int(seconds_float)
    microseconds = round((seconds_float - seconds) * 1000000)
    dt_utc = swe_utc[:5] + (seconds, microseconds)
    dt = datetime(*dt_utc, tzinfo=ZoneInfo('UTC'))
    return dt if lat is None or lon is None else dt.astimezone(ZoneInfo(timezone(lat, lon)))
