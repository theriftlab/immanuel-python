"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Basic midpoint calculations for chart objects.

"""

import swisseph as swe

from immanuel.const import calc, chart, names
from immanuel.tools import calculate


def all(objects1: dict, objects2: dict, pars_fortuna: int = calc.COMPOSITE, pars_fortuna_formula: int = None) -> dict:
    """ Takes two dicts of chart objects typically returned by eph.all()
    and returns the averaged data for both sets as a third set of
    composite objects. """
    objects = {}

    for index, object1 in objects1.items():
        # Skip Part of Fortune if we need to recalculate from composite Sun/Moon/Asc
        if index == chart.PARS_FORTUNA and pars_fortuna == calc.COMPOSITE:
            object = {}
        else:
            object = composite(object1, objects2[index])

        objects[index] = object

    # Now we have composite Sun/Moon/Asc, calculate Part of Fortune
    if pars_fortuna == calc.COMPOSITE and chart.PARS_FORTUNA in objects1:
        objects[chart.PARS_FORTUNA] = {
            'index': chart.PARS_FORTUNA,
            'type': chart.POINT,
            'name': names.POINTS[chart.PARS_FORTUNA],
            'lon': calculate.pars_fortuna(objects[chart.SUN]['lon'], objects[chart.MOON]['lon'], objects[chart.ASC]['lon'], pars_fortuna_formula),
            'speed': 0.0,
        }

    return objects


def composite(object1: dict, object2: dict) -> dict:
    """ Given two chart objects tpyically returned by the eph module, this
    function will return a composite object. """
    composite_object = {k: v for k, v in object1.items()}
    composite_object['lon'] = swe.deg_midp(object1['lon'], object2['lon'])

    for key in ('lat', 'dist', 'speed', 'dec'):
        if key in object1:
            composite_object[key] = (object1[key] + object2[key]) / 2

    return composite_object
