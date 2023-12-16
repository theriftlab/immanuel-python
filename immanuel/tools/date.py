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
from zoneinfo import ZoneInfo

import swisseph as swe
from dateutil import tz
from timezonefinder import TimezoneFinder

from immanuel.tools import convert


def ambiguous(dt: datetime) -> bool:
    """ Returns whether an aware datetime is ambiguous. """
    return tz.datetime_ambiguous(dt)


def timezone(lat: float, lon: float) -> str:
    """ Returns a timezone string based on decimal lat/lon coordinates. """
    return TimezoneFinder().timezone_at(lat=lat, lng=lon)


def localize(dt: datetime, lat: float, lon: float, is_dst: bool = None) -> datetime:
    """ Localizes a naive datetime based on decimal lat/lon coordinates. """
    return dt.replace(tzinfo=ZoneInfo(timezone(lat, lon)), fold=1 if is_dst == False else 0)


def to_datetime(dt: str | float | datetime, lat: float = None, lon: float = None, is_dst: bool = None) -> datetime:
    """ Convert an unknown into a datetime. Unknowns can be either an
    ISO-formatted string, a Julian Date, or already a datetime. """
    no_coords = lat is None or lon is None
    if isinstance(dt, str):
        date_time = datetime.fromisoformat(dt)
        return date_time.replace(tzinfo=ZoneInfo('UTC')) if no_coords else localize(date_time, lat, lon, is_dst)
    if isinstance(dt, float):
        ut = swe.revjul(dt)
        time = convert.dec_to_dms(ut[3])[1:]
        date_time = datetime(*ut[:3], *time, tzinfo=ZoneInfo('UTC'))
        return date_time if no_coords else date_time.astimezone(ZoneInfo(timezone(lat, lon)))
    if isinstance(dt, datetime):
        if no_coords:
            return dt.replace(tzinfo=ZoneInfo('UTC')) if dt.tzinfo is None else dt
        else:
            return localize(dt, lat, lon, is_dst)
    return None


def to_jd(dt: str | float | datetime, lat: float = None, lon: float = None, is_dst: bool = None) -> float:
    """ Convert an unknown into a Julian date. Unknowns can be either an
    ISO-formatted string, already a Julian Date, or a datetime. """
    if isinstance(dt, float):
        return dt
    if isinstance(dt, str):
        date_time = datetime.fromisoformat(dt)
    elif isinstance(dt, datetime):
        date_time = dt
    else:
        return None

    if lat is not None and lon is not None:
        date_time = localize(date_time, lat, lon, is_dst)
    elif date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=ZoneInfo('UTC'))

    date_time_utc = date_time.astimezone(ZoneInfo('UTC'))
    hour = convert.dms_to_dec(('+', date_time_utc.hour, date_time_utc.minute, date_time_utc.second))
    return swe.julday(*date_time_utc.timetuple()[0:3], hour)
