"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to pyswisseph data.

    Relevant data on the main angles, houses, points and planets are
    available using the module's functions, most of which are cached.

    Names are returned for most of these objects, simply because some
    names are set locally by the const.names module, and others by
    pyswisseph's own files. Returning the name of each chart item
    regardless of where it came from keeps things uniform.

"""

from decimal import Decimal
from functools import cache

import swisseph as swe

from immanuel.const import chart, names
from immanuel.setup import options
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


@cache
def all(jd: float, lat: float, lon: float) -> dict:
    """ Helper function returns a dict of all chart items requested
    by the options module. """
    items = {}

    for index in options.items:
        items[index] = get(index, jd, lat, lon)

    return items


@cache
def get(index: int | str, jd: float, lat: float = None, lon: float = None) -> dict:
    """ Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star. """
    if isinstance(index, int):
        if index < chart.TYPE_MULTIPLIER:
            return asteroid(index, jd)

        if index == chart.ANGLE:
            return angles(jd, lat, lon)

        if index == chart.HOUSE:
            return houses(jd, lat, lon)

        match _type(index):
            case chart.ANGLE:
                return angle(index, jd, lat, lon)
            case chart.HOUSE:
                return house(index, jd, lat, lon)
            case chart.POINT:
                return point(index, jd, lat, lon)
            case (chart.ASTEROID|chart.PLANET):
                return planet(index, jd)
    else:
        return fixed_star(index, jd)


def angles(jd: float, lat: float, lon: float) -> dict:
    """ Returns all four main chart angles & ARMC. """
    return angle(ALL, jd, lat, lon)


def angle(index: int, jd: float, lat: float, lon: float) -> dict:
    """ Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index == ALL. """
    angles = _angles_houses_vertex(jd, lat, lon, options.house_system)['angles']

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def houses(jd: float, lat: float, lon: float) -> dict:
    """ Returns all houses. """
    return house(ALL, jd, lat, lon)


def house(index: int, jd: float, lat: float, lon: float) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL. """
    houses = _angles_houses_vertex(jd, lat, lon, options.house_system)['houses']

    if index == ALL:
        return houses

    if index in houses:
        return houses[index]

    return None


@cache
def point(index: int, jd: float, lat = None, lon = None) -> dict:
    """ Returns a calculated point by Julian date, and additionally by
    coordinates if the calculations are based on house cusps / angles. """
    if index == chart.VERTEX:
        # Get Vertex from house/ascmc calculation
        return _angles_houses_vertex(jd, lat, lon, options.house_system)['vertex']

    if index == chart.SYZYGY:
        # Calculate prenatal full/new moon
        sun = planet(chart.SUN, jd)
        moon = planet(chart.MOON, jd)
        distance = swe.difdeg2n(moon['lon'], sun['lon'])
        syzygy_jd = find.previous_new_moon(jd) if distance > 0 else find.previous_full_moon(jd)
        syzygy_moon = planet(chart.MOON, syzygy_jd)

        return {
            'index': index,
            'type': chart.POINT,
            'name': names.POINTS[index],
            'lon': syzygy_moon['lon'],
            'speed': syzygy_moon['speed'],
        }

    if index == chart.PARS_FORTUNA:
        # Calculate part of furtune
        sun = planet(chart.SUN, jd)
        moon = planet(chart.MOON, jd)
        asc = angle(chart.ASC, jd, lat, lon)
        lon = calculate.pars_fortuna(sun['lon'], moon['lon'], asc['lon'])

        return {
            'index': index,
            'type': chart.POINT,
            'name': names.POINTS[index],
            'lon': lon,
            'speed': 0.0,
        }

    # Get other available points
    res = swe.calc_ut(jd, _SWE[index])[0]

    return {
        'index': index,
        'type': chart.POINT,
        'name': names.POINTS[index],
        'lon': res[0] if index not in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE) else swe.degnorm(Decimal(str(res[0])) - 180),
        'speed': res[3],
    }


@cache
def planet(index: int, jd: float) -> dict:
    """ Returns a pyswisseph object by Julian date. Can also be used to
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
    in the options module. """
    index += swe.AST_OFFSET
    name = swe.get_planet_name(index)

    ec_res = swe.calc_ut(jd, index)[0]
    eq_res = swe.calc_ut(jd, index, swe.FLG_EQUATORIAL)[0]

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


@cache
def is_daytime(jd: float, lat: float, lon: float) -> bool:
    """ Returns whether the sun is above the ascendant at the time
    and place specified. """
    sun = planet(chart.SUN, jd)
    asc = angle(chart.ASC, jd, lat, lon)
    return calculate.is_daytime(sun['lon'], asc['lon'])


@cache
def _angles_houses_vertex(jd: float, lat: float, lon: float, house_system: bytes) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles, and the
    vertex, along with their speeds. """
    cusps, ascmc, cuspsspeed, ascmcspeed = swe.houses_ex2(jd, lat, lon, _SWE[house_system])

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


def _type(index: int) -> int:
    """ Return the type index of a give item's index. """
    return round(index, -2)
