"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module contains many of the calculations required to
    parse the raw numbers from pyswisseph into useable data.

    This is used in tandem with the eph module, but is separated out
    so that this data can be accessed without a specific date or location,
    most notably when generating a composite chart.

"""

from decimal import Decimal

import swisseph as swe

from immanuel.const import calc, chart, names
from immanuel.tools import eph
from immanuel import options


def moon_phase(sun_lon: float, moon_lon: float) -> int:
    """ Returns the moon phase given the positions of the Sun and Moon. """
    distance = swe.difdegn(moon_lon, sun_lon)

    for angle in range(45, 361, 45):
        if distance < angle:
            return angle


def is_daytime(sun_lon: float, asc_lon: float) -> bool:
    """ Returns whether the sun is above the ascendant. """
    return swe.difdeg2n(sun_lon, asc_lon) < 0


def pars_fortuna(sun_lon: float, moon_lon: float, asc_lon: float) -> float:
    """ Returns the Part of Fortune longitude. """
    if options.pars_fortuna == calc.DAY_FORMULA or (options.pars_fortuna == calc.DAY_NIGHT_FORMULA and is_daytime(sun_lon, asc_lon)):
        formula = (asc_lon + moon_lon - sun_lon)
    else:
        formula = (asc_lon + sun_lon - moon_lon)

    return swe.degnorm(formula)


def angles_houses_vertex(cusps: tuple, ascmc: tuple, cuspsspeed: tuple, ascmcspeed: tuple) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles, and the
        vertex, along with their speeds. """
    angles = {}

    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[eph.SWE[i]]
        angles[i] = {
            'index': i,
            'type': chart.ANGLE,
            'name': names.ANGLES[i],
            'lon': lon,
            'speed': ascmcspeed[eph.SWE[i]],
        }
        if i in (chart.ASC, chart.MC):
            index = chart.DESC if i == chart.ASC else chart.IC
            angles[index] = {
                'index': index,
                'type': chart.ANGLE,
                'name': names.ANGLES[index],
                'lon': swe.degnorm(Decimal(str(lon)) - 180),
                'speed': ascmcspeed[eph.SWE[i]],
            }

    houses = {}

    for i, lon in enumerate(cusps):
        index = chart.HOUSE + i + 1
        size = swe.difdeg2n(cusps[i+1 if i < 11 else 0], lon)
        houses[index] = {
            'index': index,
            'type': chart.HOUSE,
            'name': str(i+1),
            'lon': lon,
            'size': size,
            'speed': cuspsspeed[i],
        }

    vertex = {
        'index': chart.VERTEX,
        'type': chart.POINT,
        'name': names.POINTS[chart.VERTEX],
        'lon': ascmc[eph.SWE[chart.VERTEX]],
        'speed': ascmcspeed[eph.SWE[chart.VERTEX]],
    }

    return {
        'angles': angles,
        'houses': houses,
        'vertex': vertex,
    }
