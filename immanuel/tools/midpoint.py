"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Basic midpoint calculations for chart items.

"""

import swisseph as swe

from immanuel.const import calc, chart, names
from immanuel.tools import calculate
from immanuel import options


def all(items1: dict, items2: dict) -> dict:
    """ Takes two dicts of chart items typically returned by eph.all()
    and returns the averaged data for both sets as a third set of
    composite items. """
    items = {}

    for index, item1 in items1.items():
        # Skip Part of Fortune if we need to recalculate from composite Sun/Moon/Asc
        if index == chart.PARS_FORTUNA and options.composite_pars_fortuna == calc.COMPOSITE:
            item = {}
        else:
            item = composite(item1, items2[index])

        items[index] = item

    # Now we have composite Sun/Moon/Asc, calculate Part of Fortune
    if options.composite_pars_fortuna == calc.COMPOSITE and chart.PARS_FORTUNA in items1:
        items[chart.PARS_FORTUNA] = {
            'index': chart.PARS_FORTUNA,
            'type': chart.POINT,
            'name': names.POINTS[chart.PARS_FORTUNA],
            'lon': calculate.pars_fortuna(items[chart.SUN]['lon'], items[chart.MOON]['lon'], items[chart.ASC]['lon']),
            'speed': 0.0,
        }

    return items


def composite(item1: dict, item2: dict) -> dict:
    """ Given two chart items tpyically returned by the eph module, this
    function will return a composite item. """
    composite_item = {k: v for k, v in item1.items()}
    composite_item['lon'] = swe.deg_midp(item1['lon'], item2['lon'])

    for key in ('lat', 'dist', 'speed', 'dec'):
        if key in item1:
            composite_item[key] = (item1[key] + item2[key]) / 2

    return composite_item
