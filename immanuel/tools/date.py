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

import swisseph as swe
from pytz import exceptions, timezone, UTC
from timezonefinder import TimezoneFinder


class DateTime:
    """ This class is instatiated with either a standard Python datetime
    object or a Julian day as a float, and decimal lat / lon coordinates
    as floats. is_dst can be True or False to clarify ambiguous datetimes
    (eg. 01:30 when DST ends).

    """

    def __init__(self, dt_jd: datetime | float, lat: float, lon: float, is_dst: bool = None) -> None:
        self.datetime = None
        self.lat = lat
        self.lon = lon
        self.timezone = timezone(TimezoneFinder().certain_timezone_at(lat=lat, lng=lon))
        self.dst_ambiguous = None
        self.jd = None

        if isinstance(dt_jd, datetime):
            try:
                self.datetime = self.timezone.localize(dt_jd, is_dst) if dt_jd.tzinfo is None else dt_jd.astimezone(self.timezone)
                self.jd = datetime_to_jd(self.datetime)
                self.dst_ambiguous = False
            except exceptions.AmbiguousTimeError:
                self.dst_ambiguous = True
        else:
            self.jd = dt_jd
            self.datetime = jd_to_datetime(dt_jd).astimezone(self.timezone)
            self.dst_ambiguous = False

    def isoformat(self) -> str:
        """ Returns the underlying datetime object's ISO format. """
        return self.datetime.isoformat()

    def __str__(self) -> str:
        """ Returns the full date with timezone string. """
        if self.dst_ambiguous:
            return 'Ambiguous Time Error'

        return f'{self.datetime.strftime("%a %d %b %Y %H:%M:%S")} {self.timezone.zone}'


def datetime_to_jd(dt: datetime) -> float:
    """ Convert localised datetime into universal Julian day. """
    utc_dt = dt.datetime.astimezone(UTC) if isinstance(dt, DateTime) else dt.astimezone(UTC)
    return swe.utc_to_jd(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)[1]


def jd_to_datetime(jd: float) -> datetime:
    """ Convert Julian day into UTC datetime object. """
    swe_utc = swe.jdut1_to_utc(jd)
    seconds_float = swe_utc[5]
    seconds = int(seconds_float)
    microseconds = round((seconds_float - seconds) * 1000000)
    dt_utc = swe_utc[:5] + (seconds, microseconds)
    return datetime(*dt_utc, tzinfo=UTC)
