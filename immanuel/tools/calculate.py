"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module contains miscellaneous calculations to ascertain basic chart
    and object information from the data returned from the ephemeris module.
    These functions will accept both an object and a float.

"""

import swisseph as swe

from immanuel.const import calc
from immanuel.tools import ephemeris


def moon_phase(sun: dict | float, moon: dict | float) -> int:
    """ Returns the moon phase given the positions of the Sun and Moon. """
    sun_lon, moon_lon = (object['lon'] if isinstance(object, dict) else object for object in (sun, moon))
    distance = swe.difdegn(moon_lon, sun_lon)

    for angle in range(45, 361, 45):
        if distance < angle:
            return angle


def is_daytime(sun: dict | float, asc: dict | float) -> bool:
    """ Returns whether the sun is above the ascendant. """
    sun_lon, asc_lon = (object['lon'] if isinstance(object, dict) else object for object in (sun, asc))
    return swe.difdeg2n(sun_lon, asc_lon) < 0


def pars_fortuna_longitude(sun: dict | float, moon: dict | float, asc: dict | float, formula: int) -> float:
    """ Returns the Part of Fortune longitude. """
    sun_lon, moon_lon, asc_lon = (object['lon'] if isinstance(object, dict) else object for object in (sun, moon, asc))

    if formula == calc.NIGHT_FORMULA or (formula == calc.DAY_NIGHT_FORMULA and not is_daytime(sun_lon, asc_lon)):
        lon = asc_lon + sun_lon - moon_lon
    else:
        lon = asc_lon + moon_lon - sun_lon

    return swe.degnorm(lon)


def sidereal_time(armc: dict | float) -> float:
    """ Returns sidereal time based on ARMC longitude. """
    return (armc['lon'] if isinstance(armc, dict) else armc) / 15


def object_movement(object: dict | float) -> int:
    """ Returns whether a chart object is direct, stationary or retrograde. """
    speed = object['speed'] if isinstance(object, dict) else object

    if -calc.STATION_SPEED <= speed <= calc.STATION_SPEED:
        return calc.STATIONARY

    return calc.DIRECT if speed > calc.STATION_SPEED else calc.RETROGRADE


def is_out_of_bounds(object: dict | float, jd: float = None, obliquity: float = None) -> bool:
    """ Returns whether the passed object is out of bounds either on the passed
    Julian date or relative to the passed obliquity. """
    if isinstance(object, dict):
        if 'dec' not in object:
            return None
        dec = object['dec']
    else:
        dec = object

    if jd is not None:
        obliquity = ephemeris.obliquity(jd)
    elif obliquity is None:
        return None

    return not -obliquity < dec < obliquity


def solar_year_length(jd: float) -> float:
    """ Returns the length in days of the year passed in the given
    Julian date. This is a direct copy of astro.com's calculations. """
    t = (jd - calc.J2000) / 365250
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # Arcsec per milllennium
    dvel = 1296027711.03429 + 2 * 109.15809 * t + 3 * 0.07207 * t2 - 4 * 0.23530 * t3 - 5 * 0.00180 * t4 + 6 * 0.00020 * t5
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel
