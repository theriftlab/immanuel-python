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

from immanuel import options
from immanuel.const import calc, chart, names
from immanuel.tools import find


ALL = -1
ANGLES = 0
HOUSES = 1
VERTEX = 2


def angles(jd: float, lat: float, lon: float) -> dict:
    """ Returns all four main chart angles & ARMC. """
    return angle(jd, lat, lon, ALL)


def angle(jd: float, lat: float, lon: float, index: int) -> dict:
    """ Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index == ALL. """
    angles = _angles_houses_vertex(jd, lat, lon, options.house_system)[ANGLES]

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def houses(jd: float, lat: float, lon: float) -> dict:
    """ Returns all houses. """
    return house(jd, lat, lon, ALL)


def house(jd: float, lat: float, lon: float, index: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL. """
    houses = _angles_houses_vertex(jd, lat, lon, options.house_system)[HOUSES]

    if index == ALL:
        return houses

    if index in houses:
        return houses[index]

    return None


@cache
def point(jd: float, index: int, **kwargs) -> dict:
    """ Returns a calculated point by Julian date, and additionally by
    coordinates if the calculations are based on house cusps / angles. """
    lat = kwargs.get('lat', None)
    lon = kwargs.get('lon', None)

    if index == chart.VERTEX:
        # Get Vertex from house/ascmc calculation
        return _angles_houses_vertex(jd, lat, lon, options.house_system)[VERTEX]

    if index == chart.SYZYGY:
        # Calculate prenatal full/new moon
        sun = planet(jd, chart.SUN)
        moon = planet(jd, chart.MOON)
        distance = swe.difdeg2n(moon['lon'], sun['lon'])
        syzygy_jd = find.previous_new_moon(jd) if distance > 0 else find.previous_full_moon(jd)
        syzygy_moon = planet(syzygy_jd, chart.MOON)

        return {
            'index': index,
            'type': chart.POINTS,
            'name': names.POINTS[index],
            'lon': syzygy_moon['lon'],
            'speed': syzygy_moon['speed'],
        }

    if index == chart.PARS_FORTUNA:
        # Calculate part of furtune
        asc = angle(jd, lat, lon, chart.ASC)
        moon = planet(jd, chart.MOON)
        sun = planet(jd, chart.SUN)

        if options.pars_fortuna == calc.DAY_FORMULA or (options.pars_fortuna == calc.DAY_NIGHT_FORMULA and is_daytime(jd, lat, lon)):
            formula = (asc['lon'] + moon['lon'] - sun['lon'])
        else:
            formula = (asc['lon'] + sun['lon'] - moon['lon'])

        return {
            'index': index,
            'type': chart.POINTS,
            'name': names.POINTS[index],
            'lon': swe.degnorm(formula),
            'speed': 0.0,
        }

    # Get other available points
    calculated = index in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE)
    swe_index = index if not calculated else index - chart.CALCULATED_OFFSET
    res = swe.calc_ut(jd, swe_index)[0]

    return {
        'index': index,
        'type': chart.POINTS,
        'name': names.POINTS[index],
        'lon': res[0] if not calculated else swe.degnorm(Decimal(str(res[0])) - 180),
        'speed': res[3],
    }


def chart_items(jd, lat, lon) -> dict:
    """ Helper function returns a dict of all chart items requested
    by the options module. """
    items = {}

    for type, item_list in options.chart_items.items():
        for index in item_list:
            match type:
                case chart.POINTS:
                    item = point(jd, index, lat=lat, lon=lon)
                case chart.PLANETS:
                    item = planet(jd, index)
                case (chart.ASTEROIDS|chart.EXTRA_ASTEROIDS):
                    item = asteroid(jd, index)
                case chart.FIXED_STARS:
                    item = fixed_star(jd, index)

            if type not in items:
                items[type] = {}

            items[type][index] = item

    return items


@cache
def planet(jd: float, index: int) -> dict:
    """ Returns a pyswisseph object by Julian date. This can be used to
    find more than planets only since calc_ut() is used for many other
    objects too. """
    ec_res = swe.calc_ut(jd, index)[0]
    eq_res = swe.calc_ut(jd, index, swe.FLG_EQUATORIAL)[0]

    return {
        'index': index,
        'type': chart.PLANETS,
        'name': names.PLANETS[index],
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def asteroid(jd: float, index: int) -> dict:
    """ Returns an asteroid by Julian date and pyswisseph index.
    This will likely require extra ephemeris files. """
    if index in (chart.CHIRON, chart.PHOLUS, chart.CERES, chart.PALLAS, chart.JUNO, chart.VESTA):
        type = chart.ASTEROIDS
        name = names.ASTEROIDS[index]
    else:
        index += swe.AST_OFFSET
        type = chart.EXTRA_ASTEROIDS
        name = swe.get_planet_name(index)

    ec_res = swe.calc_ut(jd, index)[0]
    eq_res = swe.calc_ut(jd, index, swe.FLG_EQUATORIAL)[0]

    return {
        'index': index,
        'type': type,
        'name': name,
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def fixed_star(jd: float, name: str) -> dict:
    """ Returns a fixed star by Julian date and name. """
    res, stnam = swe.fixstar2_ut(name, jd)[:2]
    name = stnam.partition(',')[0]

    return {
        'index': name,
        'type': chart.FIXED_STARS,
        'name': name,
        'lon': res[0],
        'lat': res[1],
        'dist': res[2],
        'speed': res[3],
    }


@cache
def moon_phase(jd: float) -> int:
    """ Returns the moon phase at the given Julian date. """
    sun = planet(jd, chart.SUN)
    moon = planet(jd, chart.MOON)
    distance = swe.difdegn(moon['lon'], sun['lon'])

    for angle in range(45, 361, 45):
        if distance < angle:
            return angle


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
    sun = planet(jd, chart.SUN)
    asc = angle(jd, lat, lon, chart.ASC)
    return swe.difdeg2n(sun['lon'], asc['lon']) < 0


@cache
def _angles_houses_vertex(jd: float, lat: float, lon: float, house_system: bytes) -> tuple:
    """ Returns ecliptic longitudes for the houses, main angles, and the
    vertex, along with their speeds. """
    cusps, ascmc, cuspsspeed, ascmcspeed = swe.houses_ex2(jd, lat, lon, house_system)

    # Angles
    angles = {}
    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[i]
        angles[i] = {
            'index': i,
            'type': chart.ANGLES,
            'name': names.ANGLES[i],
            'lon': lon,
            'speed': ascmcspeed[i],
        }
        if i in (chart.ASC, chart.MC):
            index = i + chart.CALCULATED_OFFSET
            angles[index] = {
                'index': index,
                'type': chart.ANGLES,
                'name': names.ANGLES[index],
                'lon': swe.degnorm(Decimal(str(lon)) - 180),
                'speed': ascmcspeed[i],
            }

    # Houses
    houses = {}
    for i, lon in enumerate(cusps):
        house = i + 1
        size = swe.difdeg2n(cusps[i+1 if i < 11 else 0], lon)
        houses[house] = {
            'index': house,
            'type': chart.HOUSES,
            'name': str(house),
            'lon': lon,
            'size': size,
            'speed': cuspsspeed[i],
        }

    # Vertex
    vertex = {
        'index': chart.VERTEX,
        'type': chart.POINTS,
        'name': names.POINTS[chart.VERTEX],
        'lon': ascmc[chart.VERTEX],
        'speed': ascmcspeed[chart.VERTEX],
    }

    return angles, houses, vertex
