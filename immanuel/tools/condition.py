"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module returns the various conditions of chart objects based
on their position and motion. The moon's phase is also calculated here.

"""

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import sweph


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


def object_motion(object: dict | float) -> int:
    """Returns whether a chart object's motion is direct,
    stationary or retrograde."""
    speed = object["speed"] if isinstance(object, dict) else object
    if -calc.STATION_SPEED <= speed <= calc.STATION_SPEED:
        return calc.STATIONARY
    return calc.DIRECT if speed > calc.STATION_SPEED else calc.RETROGRADE


def is_object_motion_typical(object: dict) -> bool:
    """Returns whether an object's motion is typical, ie. direct for planets,
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
    movement = object_motion(object)
    is_node = object["index"] in (
        chart.NORTH_NODE,
        chart.SOUTH_NODE,
        chart.TRUE_NORTH_NODE,
        chart.TRUE_SOUTH_NODE,
    )
    return movement == calc.RETROGRADE if is_node else movement == calc.DIRECT


def is_object_out_of_bounds(
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


def is_object_in_sect(
    object: dict, is_daytime: bool, sun: dict | float | None = None
) -> bool:
    """Returns whether the passed planet is in sect."""
    if object["index"] in (chart.SUN, chart.JUPITER, chart.SATURN):
        return is_daytime
    if object["index"] in (chart.MOON, chart.VENUS, chart.MARS):
        return not is_daytime
    if object["index"] == chart.MERCURY and sun is not None:
        sun_mercury_position = relative_object_position(sun, object)
        return (
            sun_mercury_position == calc.ORIENTAL
            if is_daytime
            else sun_mercury_position == calc.OCCIDENTAL
        )
    return False


def relative_object_position(object1: dict | float, object2: dict | float) -> int:
    """Calculate which side of object1 object2 is."""
    lon1, lon2 = (
        object["lon"] if isinstance(object, dict) else object
        for object in (object1, object2)
    )
    return calc.OCCIDENTAL if swe.difdegn(lon1, lon2) > 180 else calc.ORIENTAL


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
