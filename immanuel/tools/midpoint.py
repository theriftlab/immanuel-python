"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Basic midpoint calculations for chart objects.

"""

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import calculate, ephemeris


def all(objects1: dict, objects2: dict, obliquity: float = None, pars_fortuna: int = calc.MIDPOINT, pars_fortuna_formula: int = None) -> dict:
    """ Takes two dicts of chart objects typically returned by the
    ephemeris module and returns the averaged data for both sets as
    a third dict of composite objects. """
    objects = {}

    for index, object1 in objects1.items():
        objects[index] = composite(object1, objects2[index], obliquity)

    # If we have composite Sun/Moon/Asc, calculate Part of Fortune
    if pars_fortuna == calc.COMPOSITE and objects.keys() >= {chart.PARS_FORTUNA, chart.SUN, chart.MOON, chart.ASC}:
        objects[chart.PARS_FORTUNA]['lon'] = calculate.pars_fortuna_longitude(objects[chart.SUN], objects[chart.MOON], objects[chart.ASC], pars_fortuna_formula)

    return objects


def composite(object1: dict, object2: dict, obliquity: float = None) -> dict:
    """ Given two chart objects typically returned by the ephemeris module,
    this function will return a composite object. """
    composite_object = object1 | {
        'lon': swe.deg_midp(object1['lon'], object2['lon']),
        'lat': 0.0,
        'dist': 0.0,
        'speed': (object1['speed'] + object2['speed']) / 2,
    }

    if 'size' in object1 and 'size' in object2:
        composite_object['size'] = (object1['size'] + object2['size']) / 2

    if 'dec' in object1 and obliquity is not None:
        composite_object['dec'] = swe.cotrans((composite_object['lon'], 0, 1), -obliquity)[1]

    return composite_object


def obliquity(jd1: float, jd2: float, mean: bool = False) -> float:
    return (ephemeris.obliquity(jd1, mean) + ephemeris.obliquity(jd2, mean)) / 2
