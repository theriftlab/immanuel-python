"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module largely acts as a wrapper for the sweph module, offering
convenience functions for chart assembly that dispatch to sweph's more
granular and technical functions.

"""

import swisseph as swe

from immanuel.const import chart
from immanuel.tools import condition, part, sweph, transit

ALL = -1


def get_objects(
    object_list: list[int],
    jd: float,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function returns a dict of all passed chart objects."""
    return _get_objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def armc_get_objects(
    object_list: list[int],
    jd: float,
    armc: float,
    lat: float | None = None,
    lon: float | None = None,
    obliquity: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function returns a dict of all passed chart objects
    with points & angles calculated from the passed ARMC."""
    return _get_objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get(
    index: int | str,
    jd: float,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star."""
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def armc_get(
    index: int | str,
    jd: float,
    armc: float,
    lat: float | None = None,
    lon: float | None = None,
    obliquity: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star with houses & angles calculated from the
    passed ARMC."""
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_angles(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns all four main chart angles & ARMC."""
    return sweph.angle(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
    )


def armc_get_angles(
    armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns all four main chart angles calculated from the
    passed ARMC."""
    return sweph.angle(
        index=ALL,
        lat=lat,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_angle(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns one of the four main chart angles & its speed.
    Returns all if index == ALL."""
    return sweph.angle(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def armc_get_angle(
    index: int, armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns one of the four main chart angles & its speed, calculated from
    the passed ARMC. Returns all if index == ALL."""
    return sweph.angle(
        index=index,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_houses(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns all houses."""
    return _get_house(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def armc_get_houses(
    armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns all houses calculated from the passed ARMC."""
    return _get_house(
        index=ALL,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_house(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns a house cusp & its speed, or all houses if index == ALL."""
    return _get_house(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def armc_get_house(
    index: int, armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns a house cusp & its speed, calculated from the passed ARMC.
    Returns all if index == ALL."""
    return _get_house(
        index=index,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_point(
    index: int,
    jd: float,
    lat: float,
    lon: float,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Returns a calculated point by Julian date, and additionally by lat / lon
    coordinates."""
    return _get_point(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def armc_get_point(
    index: int,
    jd: float,
    armc: float,
    lat: float,
    obliquity: float,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Returns a calculated point by Julian date, and additionally by the
    passed ARMC."""
    return _get_point(
        index=index,
        jd=jd,
        lat=lat,
        lon=None,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_planet(index: int, jd: float) -> dict:
    """Returns a planet by Julian date. Can be used to return the six
    major asteroids supported by pysweph without using a separate file."""
    return sweph.planet(index, jd)


def get_asteroid(index: int, jd: float) -> dict:
    """Returns an asteroid by Julian date, either one of the major asteroids
    bundled with pysweph, or one read from an ephemeris file the user has
    added and addressed by its own number."""
    if sweph.is_external(index):
        return sweph.asteroid(index, jd)
    return sweph.planet(index, jd)


def get_fixed_star(name: str, jd: float) -> dict:
    """Returns a fixed star by Julian date and name."""
    return sweph.fixed_star(name, jd)


def get_eclipse(index: int, jd: float) -> dict:
    """Returns a calculated object based on the Moon's or Sun's position
    during a pre or post-natal lunar or solar eclipse. The declination
    value is based on the natal date."""
    eclipse_function = {
        chart.PRE_NATAL_SOLAR_ECLIPSE: transit.previous_solar_eclipse,
        chart.PRE_NATAL_LUNAR_ECLIPSE: transit.previous_lunar_eclipse,
        chart.POST_NATAL_SOLAR_ECLIPSE: transit.next_solar_eclipse,
        chart.POST_NATAL_LUNAR_ECLIPSE: transit.next_lunar_eclipse,
    }.get(index)
    if eclipse_function is None:
        raise ValueError("Invalid eclipse type.")
    eclipse_type, eclipse_jd = eclipse_function(jd)
    return sweph.pre_post_natal_eclipse(index, jd, eclipse_type, eclipse_jd)


def _get_objects(
    object_list: list[int],
    jd: float,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for get_objects() and armc_get_objects()."""
    objects = {}
    for index in object_list:
        objects[index] = _get(
            index=index,
            jd=jd,
            lat=lat,
            lon=lon,
            house_system=house_system,
            part_formula=part_formula,
            armc=armc,
            armc_obliquity=armc_obliquity,
        )
    return objects


def _get(
    index: int | str,
    jd: float,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for get() and armc_get()."""
    if armc is not None and armc_obliquity is None:
        armc_obliquity = sweph.true_earth_obliquity(jd)
    if index == chart.ANGLE:
        return sweph.angle(ALL, jd, lat, lon, house_system, armc, armc_obliquity)
    if index == chart.HOUSE:
        return _get_house(ALL, jd, lat, lon, house_system, armc, armc_obliquity)
    object_type = sweph.type_of(index)
    if isinstance(index, int):
        match object_type:
            case chart.ANGLE:
                return sweph.angle(
                    index, jd, lat, lon, house_system, armc, armc_obliquity
                )
            case chart.HOUSE:
                return _get_house(
                    index, jd, lat, lon, house_system, armc, armc_obliquity
                )
            case chart.POINT:
                return _get_point(
                    index,
                    jd,
                    lat,
                    lon,
                    house_system,
                    part_formula,
                    armc,
                    armc_obliquity,
                )
            case chart.ECLIPSE:
                return get_eclipse(index, jd)
            case chart.PLANET:
                return get_planet(index, jd)
            case chart.ASTEROID:
                return get_asteroid(index, jd)
    if isinstance(index, str) and object_type == chart.FIXED_STAR:
        try:
            return get_fixed_star(index, jd)
        except swe.Error as e:
            raise ValueError("Invalid object index.") from e
    raise ValueError("Invalid object index.")


def _get_house(
    index: int,
    jd: float | None,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for house() and armc_house()."""
    if lat is None or house_system is None:
        raise TypeError("Latitude and house system must be provided.")
    first_house_lon = (
        get_planet(house_system - chart.PLANET_ON_FIRST, jd)["lon"]
        if house_system > chart.PLANET_ON_FIRST and jd is not None
        else None
    )
    if armc is not None:
        houses = sweph.angles_houses_vertex(
            lat=lat,
            house_system=house_system,
            first_house_lon=first_house_lon,
            armc=armc,
            armc_obliquity=armc_obliquity,
        )["houses"]
    else:
        houses = sweph.angles_houses_vertex(
            jd=jd,
            lat=lat,
            lon=lon,
            house_system=house_system,
            first_house_lon=first_house_lon,
        )["houses"]
    if index == ALL:
        return houses
    return houses[index]


def _get_point(
    index: int,
    jd: float,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for point() and armc_point()."""
    if lat is None:
        raise TypeError("Latitude must be provided.")
    if index == chart.VERTEX and house_system is not None:
        if armc is not None:
            return sweph.angles_houses_vertex(
                lat=lat,
                house_system=house_system,
                armc=armc,
                armc_obliquity=armc_obliquity,
            )["vertex"]
        else:
            return sweph.angles_houses_vertex(
                jd=jd, lat=lat, lon=lon, house_system=house_system
            )["vertex"]
    if index == chart.SYZYGY:
        syzygy_jd = (
            transit.previous_new_moon(jd)
            if condition.moon_sun_distance(jd) > 0
            else transit.previous_full_moon(jd)
        )
        return sweph.syzygy(syzygy_jd)
    if index in (chart.PART_OF_FORTUNE, chart.PART_OF_SPIRIT, chart.PART_OF_EROS):
        part_lon = part.longitude(
            index, jd, lat, lon, part_formula, armc, armc_obliquity
        )
        return sweph.part(index, jd, part_lon)
    return sweph.point(index, jd)
