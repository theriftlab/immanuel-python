"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to fairly standardised pyswisseph data.

    Relevant data on the main angles, houses, points and planets are
    available using the module's functions, many of which are cached.

    Many of the functions here, including angle, house and vertex functions,
    have an "armc_"-prefixed alternative if they are required to calculate
    from an ARMC.

"""

from decimal import Decimal
from functools import cache

import swisseph as swe

from immanuel.const import chart, names
from immanuel.tools import calculate, find


ALL = -1

_SWE = {
    chart.ALCABITUS: b'B',
    chart.AZIMUTHAL: b'H',
    chart.CAMPANUS: b'C',
    chart.EQUAL: b'A',
    chart.KOCH: b'K',
    chart.MERIDIAN: b'X',
    chart.MORINUS: b'M',
    chart.PLACIDUS: b'P',
    chart.POLICH_PAGE: b'T',
    chart.PORPHYRIUS: b'O',
    chart.REGIOMONTANUS: b'R',
    chart.VEHLOW_EQUAL: b'V',
    chart.WHOLE_SIGN: b'W',

    chart.ASC: swe.ASC,
    chart.DESC: swe.ASC,
    chart.MC: swe.MC,
    chart.IC: swe.MC,
    chart.ARMC: swe.ARMC,

    chart.SUN: swe.SUN,
    chart.MOON: swe.MOON,
    chart.MERCURY: swe.MERCURY,
    chart.VENUS: swe.VENUS,
    chart.MARS: swe.MARS,
    chart.JUPITER: swe.JUPITER,
    chart.SATURN: swe.SATURN,
    chart.URANUS: swe.URANUS,
    chart.NEPTUNE: swe.NEPTUNE,
    chart.PLUTO: swe.PLUTO,
    chart.CHIRON: swe.CHIRON,
    chart.PHOLUS: swe.PHOLUS,
    chart.CERES: swe.CERES,
    chart.PALLAS: swe.PALLAS,
    chart.JUNO: swe.JUNO,
    chart.VESTA: swe.VESTA,

    chart.NORTH_NODE: swe.MEAN_NODE,
    chart.SOUTH_NODE: swe.MEAN_NODE,
    chart.TRUE_NORTH_NODE: swe.TRUE_NODE,
    chart.TRUE_SOUTH_NODE: swe.TRUE_NODE,
    chart.VERTEX: swe.VERTEX,
    chart.LILITH: swe.MEAN_APOG,
    chart.TRUE_LILITH: swe.OSCU_APOG,
    chart.SYZYGY: chart.SYZYGY,
    chart.PARS_FORTUNA: chart.PARS_FORTUNA,
}


def items(item_list: tuple, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function returns a dict of all passed chart items. """
    return _items(item_list, jd, lat, lon, house_system, pars_fortuna_formula, False)


def armc_items(item_list: tuple, jd: float, lat: float = None, armc: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function returns a dict of all passed chart items
    with houses & angles calculated from the passed ARMC. """
    return _items(item_list, jd, lat, armc, house_system, pars_fortuna_formula, True)


def _items(item_list: tuple, jd: float, lat: float = None, lon_armc: float = None, house_system: int = None, pars_fortuna_formula: int = None, armc: bool = False) -> dict:
    """ Function for items() and armc_items(). """
    items = {}

    for index in item_list:
        items[index] = _get(index, jd, lat, lon_armc, house_system, pars_fortuna_formula, armc)

    return items


def get(index: int | str, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star. """
    return _get(index, jd, lat, lon, house_system, pars_fortuna_formula, False)


def armc_get(index: int | str, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star with houses & angles calculated from the
    passed ARMC. """
    return _get(index, jd, lat, lon, house_system, pars_fortuna_formula, True)


def _get(index: int | str, jd: float, lat: float = None, lon_armc: float = None, house_system: int = None, pars_fortuna_formula: int = None, armc: bool = False) -> dict:
    """ Function for get() and armc_get(). """
    if isinstance(index, int):
        if index < chart.TYPE_MULTIPLIER:
            return asteroid(index, jd)

        if index == chart.ANGLE:
            return _angle(ALL, jd, lat, lon_armc, house_system, armc)

        if index == chart.HOUSE:
            return _house(ALL, jd, lat, lon_armc, house_system, armc)

        match _type(index):
            case chart.ANGLE:
                return _angle(index, jd, lat, lon_armc, house_system, armc)
            case chart.HOUSE:
                return _house(index, jd, lat, lon_armc, house_system, armc)
            case chart.POINT:
                return _point(index, jd, lat, lon_armc, house_system, pars_fortuna_formula, armc)
            case (chart.ASTEROID|chart.PLANET):
                return planet(index, jd)
    else:
        return fixed_star(index, jd)


def angles(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns all four main chart angles & ARMC. """
    return _angle(ALL, jd, lat, lon, house_system, False)


def armc_angles(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns all four main chart angles calculated from the
    passed ARMC. """
    return _angle(ALL, jd, lat, lon, house_system, True)


def angle(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index == ALL. """
    return _angle(index, jd, lat, lon, house_system, False)


def armc_angle(index: int, jd: float, lat: float, armc: float, house_system: int) -> dict:
    """ Returns one of the four main chart angles & its speed, calculated from
    the passed ARMC. Returns all if index == ALL. """
    return _angle(index, jd, lat, armc, house_system, True)


def _angle(index: int, jd: float, lat: float, lon_armc: float, house_system: int, armc: bool = False) -> dict:
    """ Function for angle() and armc_angle(). """
    if armc:
        angles = _angles_houses_vertex_armc(lon_armc, lat, obliquity(jd), house_system)['angles']
    else:
        angles = _angles_houses_vertex(jd, lat, lon_armc, house_system)['angles']

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def houses(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns all houses. """
    return _house(ALL, jd, lat, lon, house_system, False)


def armc_houses(jd: float, lat: float, armc: float, house_system: int) -> dict:
    """ Returns all houses calculated from the passed ARMC. """
    return _house(ALL, jd, lat, armc, house_system, True)


def house(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL. """
    return _house(index, jd, lat, lon, house_system, False)


def armc_house(index: int, jd: float, lat: float, armc: float, house_system: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL,
     calculated from passed ARMC. """
    return _house(index, jd, lat, armc, house_system, True)


def _house(index: int, jd: float, lat: float, lon_armc: float, house_system: int, armc: bool = False) -> dict:
    """ Function for house() and armc_house(). """
    if armc:
        houses = _angles_houses_vertex_armc(lon_armc, lat, obliquity(jd), house_system)['houses']
    else:
        houses = _angles_houses_vertex(jd, lat, lon_armc, house_system)['houses']

    if index == ALL:
        return houses

    if index in houses:
        return houses[index]

    return None


def point(index: int, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Returns a calculated point by Julian date, and additionally by lat / lon
    coordinates. """
    return _point(index, jd, lat, lon, house_system, pars_fortuna_formula, False)


def armc_point(index: int, jd: float, lat: float = None, armc: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Returns a calculated point by Julian date, and additionally by the
     passed ARMC. """
    return _point(index, jd, lat, armc, house_system, pars_fortuna_formula, True)


def _point(index: int, jd: float, lat: float = None, lon_armc: float = None, house_system: int = None, pars_fortuna_formula: int = None, armc: bool = False) -> dict:
    """ Function for point() and armc_point(). """
    if index == chart.VERTEX:
        if armc:
            return _angles_houses_vertex_armc(lon_armc, lat, obliquity(jd), house_system)['vertex']
        else:
            return _angles_houses_vertex(jd, lat, lon_armc, house_system)['vertex']

    if index == chart.SYZYGY:
        return _syzygy(jd)

    if index == chart.PARS_FORTUNA:
        return _pars_fortuna(jd, lat, lon_armc, pars_fortuna_formula)

    return _swisseph_point(index, jd)


@cache
def planet(index: int, jd: float) -> dict:
    """ Returns a pyswisseph object by Julian date. Can be used to
    return the six major asteroids supported by pyswisseph without using
    a separate ephemeris file. """
    ec_res = swe.calc_ut(jd, _SWE[index])[0]
    eq_res = swe.calc_ut(jd, _SWE[index], swe.FLG_EQUATORIAL)[0]
    asteroid = _type(index) == chart.ASTEROID

    return {
        'index': index,
        'type': chart.ASTEROID if asteroid else chart.PLANET,
        'name': names.ASTEROIDS[index] if asteroid else names.PLANETS[index],
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def asteroid(index: int, jd: float) -> dict:
    """ Returns an asteroid by Julian date and pyswisseph index
    from an external asteroid's ephmeris file as specified
    in the setup module. """
    if _type(index) == chart.ASTEROID:
        return planet(index, jd)

    swe_index = index + swe.AST_OFFSET
    name = swe.get_planet_name(swe_index)

    ec_res = swe.calc_ut(jd, swe_index)[0]
    eq_res = swe.calc_ut(jd, swe_index, swe.FLG_EQUATORIAL)[0]

    return {
        'index': index,
        'type': chart.ASTEROID,
        'name': name,
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def fixed_star(name: str, jd: float) -> dict:
    """ Returns a fixed star by Julian date and name. """
    res, stnam = swe.fixstar2_ut(name, jd)[:2]
    name = stnam.partition(',')[0]

    return {
        'index': name,
        'type': chart.FIXED_STAR,
        'name': name,
        'lon': res[0],
        'lat': res[1],
        'dist': res[2],
        'speed': res[3],
    }


@cache
def moon_phase(jd: float) -> int:
    """ Returns the moon phase at the given Julian date. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    return calculate.moon_phase(sun['lon'], moon['lon'])


@cache
def obliquity(jd: float, mean = False) -> float:
    """ Returns the earth's true or mean obliquity at the
    given Julian date. """
    ecl_nut = swe.calc_ut(jd, swe.ECL_NUT)[0]
    return ecl_nut[1] if mean else ecl_nut[0]


def is_daytime(jd: float, lat: float, lon: float) -> bool:
    """ Returns whether the sun is above the horizon line at the time and
    place specified. """
    return _is_daytime(jd, lat, lon, False)


def armc_is_daytime(jd: float, lat: float, armc: float) -> bool:
    """ Returns whether the sun is above the horizon line at the time and
    place specified, as calculated by the passed ARMC. """
    return _is_daytime(jd, lat, armc, True)


@cache
def _is_daytime(jd: float, lat: float, lon_armc: float, armc: bool = False) -> bool:
    """ Function for is_daytime() and armc_is_daytime(). """
    sun = planet(chart.SUN, jd)
    asc = _angle(chart.ASC, jd, lat, lon_armc, chart.PLACIDUS, armc)
    return calculate.is_daytime(sun['lon'], asc['lon'])


@cache
def _angles_houses_vertex(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles,
    and the vertex, along with their speeds. Based on Julian
    date and lat / lon coordinates. """
    return _angles_houses_vertex_from_swe(*swe.houses_ex2(jd, lat, lon, _SWE[house_system]))


@cache
def _angles_houses_vertex_armc(armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles,
    and the vertex, along with their speeds. Based on ARMC, latitude
    and ecliptic obliquity. """
    return _angles_houses_vertex_from_swe(*swe.houses_armc_ex2(armc, lat, obliquity, _SWE[house_system]))


def _angles_houses_vertex_from_swe(cusps: tuple, ascmc: tuple, cuspsspeed: tuple, ascmcspeed: tuple) -> dict:
    angles = {}
    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[_SWE[i]]
        angles[i] = {
            'index': i,
            'type': chart.ANGLE,
            'name': names.ANGLES[i],
            'lon': lon,
            'speed': ascmcspeed[_SWE[i]],
        }
        if i in (chart.ASC, chart.MC):
            index = chart.DESC if i == chart.ASC else chart.IC
            angles[index] = {
                'index': index,
                'type': chart.ANGLE,
                'name': names.ANGLES[index],
                'lon': swe.degnorm(Decimal(str(lon)) - 180),
                'speed': ascmcspeed[_SWE[i]],
            }

    houses = {}
    for i, lon in enumerate(cusps, start=1):
        index = chart.HOUSE + i
        size = swe.difdeg2n(cusps[i if i < 12 else 0], lon)
        houses[index] = {
            'index': index,
            'type': chart.HOUSE,
            'name': names.HOUSES[index],
            'number': i,
            'lon': lon,
            'size': size,
            'speed': cuspsspeed[i-1],
        }

    vertex = {
        'index': chart.VERTEX,
        'type': chart.POINT,
        'name': names.POINTS[chart.VERTEX],
        'lon': ascmc[_SWE[chart.VERTEX]],
        'speed': ascmcspeed[_SWE[chart.VERTEX]],
    }

    return {
        'angles': angles,
        'houses': houses,
        'vertex': vertex,
    }


@cache
def _syzygy(jd: float) -> dict:
    """ Calculate prenatal full/new moon - this can potentially
    be an expensive calculation so should be cached. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    distance = swe.difdeg2n(moon['lon'], sun['lon'])
    syzygy_jd = find.previous_new_moon(jd) if distance > 0 else find.previous_full_moon(jd)
    syzygy_moon = planet(chart.MOON, syzygy_jd)

    return {
        'index': chart.SYZYGY,
        'type': chart.POINT,
        'name': names.POINTS[chart.SYZYGY],
        'lon': syzygy_moon['lon'],
        'speed': syzygy_moon['speed'],
    }


@cache
def _pars_fortuna(jd: float, lat: float, lon: float, formula: int) -> dict:
    """ Calculate Part of Fortune - this only relies on the ascendant
    which will be consistent across all supported systems, so it is safe
    to pass Placidus as the default. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    asc = angle(chart.ASC, jd, lat, lon, chart.PLACIDUS)
    lon = calculate.pars_fortuna(sun['lon'], moon['lon'], asc['lon'], formula)

    return {
        'index': chart.PARS_FORTUNA,
        'type': chart.POINT,
        'name': names.POINTS[chart.PARS_FORTUNA],
        'lon': lon,
        'speed': 0.0,
    }


@cache
def _swisseph_point(index: int, jd: float) -> dict:
    """ Pull any remaining non-calculated points straight from swisseph. """
    res = swe.calc_ut(jd, _SWE[index])[0]

    return {
        'index': index,
        'type': chart.POINT,
        'name': names.POINTS[index],
        'lon': res[0] if index not in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE) else swe.degnorm(Decimal(str(res[0])) - 180),
        'speed': res[3],
    }


def _type(index: int) -> int:
    """ Return the type index of a give item's index. """
    return round(index, -2)
