"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module takes much of the mess of pure
calculation away from the ephemeris files.

"""

import math

import swisseph as swe

from immanuel.classes.cache import cache
from immanuel.const import calc, chart
from immanuel.tools import sweph


DAYS = 0
TROPICAL_YEARS = 1

SYNODIC_MIN = -1
SYNODIC_AVG = 0
SYNODIC_MAX = 1


"""
TIME OF DAY CALCULATIONS
--------------------------------------------------------------------------------
"""


def is_in_sect(object: dict, is_daytime: bool, sun: dict | float | None = None) -> bool:
    """Returns whether the passed planet is in sect."""
    if object["index"] in (chart.SUN, chart.JUPITER, chart.SATURN):
        return is_daytime
    if object["index"] in (chart.MOON, chart.VENUS, chart.MARS):
        return not is_daytime
    if object["index"] == chart.MERCURY and sun is not None:
        sun_mercury_position = relative_position(sun, object)
        return (
            sun_mercury_position == calc.ORIENTAL
            if is_daytime
            else sun_mercury_position == calc.OCCIDENTAL
        )
    return False


def is_daytime(jd: float, lat: float, lon: float) -> bool:
    """Returns whether the sun is above the horizon line at the time and
    place specified."""
    return _is_daytime(jd=jd, lat=lat, lon=lon, armc=None, armc_obliquity=None)


def armc_is_daytime(jd: float, armc: float, lat: float, obliquity: float) -> bool:
    """Returns whether the sun is above the horizon line at the time and
    place specified, as calculated by the passed ARMC."""
    return _is_daytime(jd=jd, lat=lat, lon=None, armc=armc, armc_obliquity=obliquity)


def is_daytime_from(sun: dict | float, asc: dict | float) -> bool:
    """Returns whether the sun is above the ascendant."""
    sun_lon, asc_lon = (
        object["lon"] if isinstance(object, dict) else object for object in (sun, asc)
    )
    return swe.difdeg2n(sun_lon, asc_lon) < 0


def _is_daytime(
    jd: float,
    lat: float,
    lon: float | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> bool:
    """Function for is_daytime() and armc_is_daytime()."""
    sun = sweph.planet(chart.SUN, jd)
    asc = sweph.angle(chart.ASC, jd, lat, lon, chart.PLACIDUS, armc, armc_obliquity)
    return is_daytime_from(sun, asc)


"""
OBJECT MOVEMENT
--------------------------------------------------------------------------------
"""


def object_movement(object: dict | float) -> int:
    """Returns whether a chart object is direct, stationary or retrograde."""
    speed = object["speed"] if isinstance(object, dict) else object
    if -calc.STATION_SPEED <= speed <= calc.STATION_SPEED:
        return calc.STATIONARY
    return calc.DIRECT if speed > calc.STATION_SPEED else calc.RETROGRADE


def is_object_movement_typical(object: dict) -> bool:
    """Returns whether an object's movement is typical, ie. direct for planets,
    retrograde for nodes, stationary for Parts and eclipses."""
    if object["index"] in (
        chart.PART_OF_FORTUNE,
        chart.PART_OF_SPIRIT,
        chart.PART_OF_EROS,
        chart.PRE_NATAL_SOLAR_ECLIPSE,
        chart.PRE_NATAL_LUNAR_ECLIPSE,
        chart.POST_NATAL_SOLAR_ECLIPSE,
        chart.POST_NATAL_LUNAR_ECLIPSE,
    ):
        return object["speed"] == 0.0
    movement = object_movement(object)
    is_node = object["index"] in (
        chart.NORTH_NODE,
        chart.SOUTH_NODE,
        chart.TRUE_NORTH_NODE,
        chart.TRUE_SOUTH_NODE,
    )
    return movement == calc.RETROGRADE if is_node else movement == calc.DIRECT


"""
OBJECT RELATIVE POSITIONING
--------------------------------------------------------------------------------
"""


def relative_position(object1: dict | float, object2: dict | float) -> int:
    """Calculate which side of object1 object2 is."""
    lon1, lon2 = (
        object["lon"] if isinstance(object, dict) else object
        for object in (object1, object2)
    )
    return calc.OCCIDENTAL if swe.difdegn(lon1, lon2) > 180 else calc.ORIENTAL


@cache
def moon_phase(jd: float) -> int:
    """Returns the moon phase at the given Julian date."""
    sun = sweph.planet(chart.SUN, jd)
    moon = sweph.planet(chart.MOON, jd)
    return moon_phase_from(sun, moon)


def moon_phase_from(sun: dict | float, moon: dict | float) -> int:
    """Returns the moon phase given the positions of the Sun and Moon."""
    sun_lon, moon_lon = (
        object["lon"] if isinstance(object, dict) else object for object in (sun, moon)
    )
    distance = swe.difdegn(moon_lon, sun_lon)
    for angle in range(45, 361, 45):
        if distance < angle:
            return angle
    raise ValueError(f"Unexpected distance value: {distance}")


def moon_sun_distance(jd: float) -> float:
    """Returns the distance between the Moon and Sun at the given Julian date."""
    sun = sweph.planet(chart.SUN, jd)
    moon = sweph.planet(chart.MOON, jd)
    return swe.difdeg2n(moon["lon"], sun["lon"])


def is_out_of_bounds(
    object: dict | float, jd: float | None = None, obliquity: float | None = None
) -> bool:
    """Returns whether the passed object is out of bounds either on the passed
    Julian date or relative to the passed obliquity."""
    if isinstance(object, dict):
        if "dec" not in object:
            return False
        dec = object["dec"]
    else:
        dec = object
    if jd is not None:
        obliquity = sweph.true_earth_obliquity(jd)
    if obliquity is None:
        raise TypeError("Either jd or obliquity must be provided.")
    return not -obliquity < dec < obliquity


"""
ORBITAL MECHANICS
--------------------------------------------------------------------------------
"""


def orbital_eccentricity(index: int, jd: float) -> float:
    """Returns the passed object's orbital eccentricity."""
    return sweph.orbital_elements(index, jd)[1]


def sidereal_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's sidereal orbital period."""
    sidereal_period = sweph.orbital_elements(index, jd)[10]
    return sidereal_period * solar_year_length(jd) if unit == DAYS else sidereal_period


def tropical_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's tropical orbital period."""
    tropical_period = sweph.orbital_elements(index, jd)[12]
    return tropical_period * solar_year_length(jd) if unit == DAYS else tropical_period


def synodic_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's synodic period."""
    synodic_period = sweph.orbital_elements(index, jd)[13]
    return synodic_period if unit == DAYS else synodic_period / solar_year_length(jd)


def synodic_period_between(
    index1: int, index2: int, jd: float, type: int = SYNODIC_AVG, unit: int = DAYS
) -> float:
    """Returns the approximate synodic period between two objects."""
    sidereal_period1 = sidereal_period(index1, jd)
    sidereal_period2 = sidereal_period(index2, jd)
    synodic_period = 1 / abs(1 / sidereal_period1 - 1 / sidereal_period2)
    if type in (SYNODIC_MIN, SYNODIC_MAX):
        orbital_eccentricity1 = orbital_eccentricity(index1, jd)
        orbital_eccentricity2 = orbital_eccentricity(index2, jd)
        synodic_period *= (
            1 + ((orbital_eccentricity1 + orbital_eccentricity2) * type) / 2
        )
    return synodic_period if unit == DAYS else synodic_period / solar_year_length(jd)


def retrograde_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns an approximate estimate of a planet's retrograde period. This is
    very approximate and should not be used for anything precise since it is
    based on Newtonian mechanics and perfect-circle orbit calculations. Formula
    borrowed from https://physics.stackexchange.com/a/476286."""
    if index in (chart.SUN, chart.MOON):
        return 0.0
    a1, *_, t1 = sweph.orbital_elements(chart.TERRA, jd)[:11]
    a2 = sweph.orbital_elements(index, jd)[0]
    r = a2 / a1
    num = math.acos((math.sqrt(r) + 1) / (r + (1 / math.sqrt(r))))
    den = math.pi * (1 - (1 / (r ** (3 / 2))))
    t_retro = t1 * (num / den)
    retrograde_period = abs(t_retro)
    return (
        retrograde_period * solar_year_length(jd) if unit == DAYS else retrograde_period
    )


def solar_year_length(jd: float) -> float:
    """Returns the tropical year length in days of the given Julian date.
    This is a direct copy of astro.com's calculations."""
    t = (jd - calc.J2000) / 365250
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # Arcsec per millennium
    dvel = (
        1296027711.03429
        + 2 * 109.15809 * t
        + 3 * 0.07207 * t2
        - 4 * 0.23530 * t3
        - 5 * 0.00180 * t4
        + 6 * 0.00020 * t5
    )
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel
