"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module contains miscellaneous calculations to ascertain basic chart
    and object information from the data returned from the ephemeris module.
    These functions will accept both an object and a float.

"""

import swisseph as swe

from immanuel.const import calc, chart
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


def part_longitude(index: int, sun: dict | float, moon: dict | float, asc: dict | float, venus: dict | float = None, formula: int = calc.DAY_NIGHT_FORMULA) -> float:
    """ Returns the longitude of the given Part - currently supports Parts of
    Fortune, Spirit and Eros. """
    sun_lon, moon_lon, asc_lon = (object['lon'] if isinstance(object, dict) else object for object in (sun, moon, asc))
    night = formula == calc.NIGHT_FORMULA or (formula == calc.DAY_NIGHT_FORMULA and not is_daytime(sun_lon, asc_lon))

    if index == chart.PART_OF_FORTUNE:
        lon = _part_of_fortune(sun_lon, moon_lon, asc_lon, night)
    elif index == chart.PART_OF_SPIRIT:
        lon = _part_of_spirit(sun_lon, moon_lon, asc_lon, night)
    elif index == chart.PART_OF_EROS:
        venus_lon = venus['lon'] if isinstance(venus, dict) else venus
        spirit_lon = _part_of_spirit(sun_lon, moon_lon, asc_lon, night)
        lon = _part_of_eros(venus_lon, spirit_lon, asc_lon, night)

    return swe.degnorm(lon)


def _part_of_fortune(sun_lon: float, moon_lon: float, asc_lon: float, night: bool) -> float:
    """ Night & day calculations for Part of Fortune. """
    return asc_lon + sun_lon - moon_lon if night else asc_lon + moon_lon - sun_lon


def _part_of_spirit(sun_lon: float, moon_lon: float, asc_lon: float, night: bool) -> float:
    """ Night & day calculations for Part of Spirit. """
    return asc_lon + moon_lon - sun_lon if night else asc_lon + sun_lon - moon_lon


def _part_of_eros(venus_lon: float, spirit_lon: float, asc_lon: float, night: bool) -> float:
    """ Night & day calculations for Part of Eros. """
    return asc_lon + spirit_lon - venus_lon if night else asc_lon + venus_lon - spirit_lon


def sidereal_time(armc: dict | float) -> float:
    """ Returns sidereal time based on ARMC longitude. """
    return (armc['lon'] if isinstance(armc, dict) else armc) / 15


def object_movement(object: dict | float) -> int:
    """ Returns whether a chart object is direct, stationary or retrograde. """
    speed = object['speed'] if isinstance(object, dict) else object

    if -calc.STATION_SPEED <= speed <= calc.STATION_SPEED:
        return calc.STATIONARY

    return calc.DIRECT if speed > calc.STATION_SPEED else calc.RETROGRADE


def is_object_movement_typical(object: dict) -> bool:
    """ Returns whether an object's movement is typical, ie. direct for planets,
    retrograde for nodes, stationary for Parts and eclipses. """
    if object['index'] in (
            chart.PART_OF_FORTUNE,
            chart.PART_OF_SPIRIT,
            chart.PART_OF_EROS,
            chart.PRE_NATAL_SOLAR_ECLIPSE,
            chart.PRE_NATAL_LUNAR_ECLIPSE,
            chart.POST_NATAL_SOLAR_ECLIPSE,
            chart.POST_NATAL_SOLAR_ECLIPSE,
        ):
        return object['speed'] == 0.0

    movement = object_movement(object)

    is_node = object['index'] in (
            chart.NORTH_NODE,
            chart.SOUTH_NODE,
            chart.TRUE_NORTH_NODE,
            chart.TRUE_SOUTH_NODE,
        )

    return movement == calc.RETROGRADE if is_node else movement == calc.DIRECT


def relative_position(object1: dict | float, object2: dict | float) -> int:
    """ Calculate which side of object1 object2 is. """
    lon1 = object1['lon'] if isinstance(object1, dict) else object1
    lon2 = object2['lon'] if isinstance(object2, dict) else object2

    return calc.OCCIDENTAL if swe.difdegn(lon1, lon2) > 180 else calc.ORIENTAL


def is_in_sect(object: dict, is_daytime: bool, sun: dict | float = None) -> bool:
    """ Returns whether the passed planet is in sect. """
    if object['index'] in (chart.SUN, chart.JUPITER, chart.SATURN):
        return is_daytime

    if object['index'] in (chart.MOON, chart.VENUS, chart.MARS):
        return not is_daytime

    if object['index'] == chart.MERCURY:
        sun_mercury_position = relative_position(sun, object)
        return sun_mercury_position == calc.ORIENTAL if is_daytime else sun_mercury_position == calc.OCCIDENTAL

    return False


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
    # Arcsec per millennium
    dvel = 1296027711.03429 + 2 * 109.15809 * t + 3 * 0.07207 * t2 - 4 * 0.23530 * t3 - 5 * 0.00180 * t4 + 6 * 0.00020 * t5
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel
