"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to pyswisseph data.

    Relevant data on the main angles, houses, points and planets are
    available using the module's functions, most of which are cached.

"""

from decimal import Decimal
from functools import cache

import swisseph as swe

from immanuel import options
from immanuel.const import calc, chart
from immanuel.tools import find


ALL = -1


def angles(jd: float, lat: float, lon: float):
    """ Returns all four main chart angles & ARMC. """
    return angle(jd, lat, lon, ALL)


@cache
def angle(jd: float, lat: float, lon: float, index: int) -> dict:
    """ Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index = 0. """
    angles, _, _ = _angles_houses_vertex(jd, lat, lon)

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def houses(jd: float, lat: float, lon: float):
    """ Returns all houses. """
    return house(jd, lat, lon, ALL)


@cache
def house(jd: float, lat: float, lon: float, index: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index = 0. """
    _, houses, _ = _angles_houses_vertex(jd, lat, lon)

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
        return _angles_houses_vertex(jd, lat, lon)[2]

    if index == chart.SYZYGY:
        # Calculate prenatal full/new moon
        sun = planet(jd, chart.SUN)
        moon = planet(jd, chart.MOON)
        distance = swe.difdeg2n(moon['lon'], sun['lon'])
        syzygy_jd = find.previous_new_moon(jd) if distance > 0 else find.previous_full_moon(jd)
        syzygy_moon = planet(syzygy_jd, chart.MOON)

        return {
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
            'lon': swe.degnorm(formula),
            'speed': 0,
        }

    # Get other available points
    calculated = index in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE)
    swe_index = index if not calculated else index - chart.CALCULATED_OFFSET
    p = planet(jd, swe_index)

    return {
        'lon': p['lon'] if not calculated else swe.degnorm(Decimal(str(p['lon'])) - 180),
        'speed': p['speed'],
    }


@cache
def planet(jd: float, index: int) -> dict:
    """ Returns a pyswisseph object by Julian date. This can be used to
    find more than planets only since calc_ut() is used for many other
    objects too. """
    ec_res = swe.calc_ut(jd, index)[0]
    eq_res = swe.calc_ut(jd, index, swe.FLG_EQUATORIAL)[0]

    return {
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def is_daytime(jd: float, lat: float, lon: float) -> bool:
    sun = planet(jd, chart.SUN)
    asc = angle(jd, lat, lon, chart.ASC)
    return swe.difdeg2n(sun['lon'], asc['lon']) < 0


@cache
def _angles_houses_vertex(jd: float, lat: float, lon: float) -> dict:
    cusps, ascmc, cuspsspeed, ascmcspeed = swe.houses_ex2(jd, lat, lon, options.house_system)

    # Angles
    angles = {}
    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[i]
        angles[i] = {
            'lon': lon,
            'speed': ascmcspeed[i],
        }
        if i in (chart.ASC, chart.MC):
            angles[i + chart.CALCULATED_OFFSET] = {
                'lon': swe.degnorm(Decimal(str(lon)) - 180),
                'speed': ascmcspeed[i],
            }

    # Houses
    houses = {}
    for i, lon in enumerate(cusps):
        houses[i+1] = {
            'lon': lon,
            'speed': cuspsspeed[i],
        }

    # Vertex
    vertex = {
        'lon': ascmc[chart.VERTEX],
        'speed': ascmcspeed[chart.VERTEX],
    }

    return angles, houses, vertex
