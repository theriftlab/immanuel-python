"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides a simple class and helper functions for converting
    between location-specific Gregorian dates and times, and universal
    Julian dates.

    The class and functions essentially wrap pyswisseph's utc_to_jd() and
    jdut1_to_utc() functions but take into account timezones based on
    lat/long coordinates and do the heavy lifting for you.

"""

from datetime import datetime
from dateutil import tz
from zoneinfo import ZoneInfo

import swisseph as swe
from timezonefinder import TimezoneFinder


class DateTime:
    """ This class is instatiated with either a standard Python datetime
    object or a Julian day as a float, and decimal lat / lon coordinates
    as floats. is_dst can be True or False to clarify ambiguous datetimes
    (eg. 01:30 when DST ends). If is_dst omitted, datetime's fold is used.

    """

    def __init__(self, dt_jd: datetime | float, lat: float, lon: float, is_dst: bool = None) -> None:
        self.datetime = None
        self.jd = None
        self.timezone = TimezoneFinder().timezone_at(lat=lat, lng=lon)
        self.lat = lat
        self.lon = lon

        if isinstance(dt_jd, datetime):
            self.datetime = dt_jd.replace(tzinfo=ZoneInfo(self.timezone), fold=1 if is_dst == False else 0)
            self.jd = datetime_to_jd(self.datetime)
        else:
            self.datetime = jd_to_datetime(dt_jd).astimezone(ZoneInfo(self.timezone)).replace(fold=1 if is_dst == False else 0)
            self.jd = dt_jd

    def ambiguous(self) -> bool:
        """ Check whether this is an ambiguous DST transition. """
        return tz.datetime_ambiguous(self.datetime)

    def isoformat(self) -> str:
        """ Returns the underlying datetime object's ISO format. """
        return self.datetime.isoformat()

    def __str__(self) -> str:
        """ Returns the full date with timezone string. """
        return f'{self.datetime.strftime("%a %d %b %Y %H:%M:%S")} {self.timezone}'


def datetime_to_jd(dt: datetime) -> float:
    """ Convert localised datetime into universal Julian day. """
    utc_dt = dt.datetime.astimezone(ZoneInfo('UTC')) if isinstance(dt, DateTime) else dt.astimezone(ZoneInfo('UTC'))
    return swe.utc_to_jd(*utc_dt.timetuple()[0:6])[1]


def jd_to_datetime(jd: float) -> datetime:
    """ Convert Julian day into UTC datetime object. """
    swe_utc = swe.jdut1_to_utc(jd)
    seconds_float = swe_utc[5]
    seconds = int(seconds_float)
    microseconds = round((seconds_float - seconds) * 1000000)
    dt_utc = swe_utc[:5] + (seconds, microseconds)
    return datetime(*dt_utc, tzinfo=ZoneInfo('UTC'))
