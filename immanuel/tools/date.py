"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides simple helper functions for converting
    between location-specific Gregorian dates and times, and universal
    Julian dates.

    The conversion functions essentially wrap pyswisseph's julday() and
    revjul() to work with date/times in UT, but they take into account
    timezones based on lat/lon coordinates for the purposes of time offsets.
    This means that datetime objects expressing UT times will be zoned as UTC.

"""

from datetime import datetime
from dateutil import tz
from zoneinfo import ZoneInfo

import swisseph as swe
from timezonefinder import TimezoneFinder

from immanuel.tools import convert


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
    """ Convert aware datetime into UT1 Julian day. """
    dt_utc = dt.astimezone(ZoneInfo('UTC'))
    hour = convert.dms_to_dec(('+', dt_utc.hour, dt_utc.minute, dt_utc.second))
    return swe.julday(*dt_utc.timetuple()[0:3], hour)


def from_jd(jd: float, lat: float = None, lon: float = None) -> datetime:
    """ Convert Julian day into UTC or localized datetime object. """
    ut = swe.revjul(jd)
    time = convert.dec_to_dms(ut[3])[1:]
    dt = datetime(*ut[:3], *time, tzinfo=ZoneInfo('UTC'))
    return dt if lat is None or lon is None else dt.astimezone(ZoneInfo(timezone(lat, lon)))
