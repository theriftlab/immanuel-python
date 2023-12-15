"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Basic midpoint calculations for chart objects. Two options exist for
    house-based objects such as the Vertex or primary angles: either allow
    them to be midpoint-calculated along with the other objects, or recalculate
    them based on a composite ARMC.

"""

import swisseph as swe

from immanuel.tools import ephemeris


def all(objects1: dict, objects2: dict, obliquity: float = None) -> dict:
    """ Takes two dicts of chart objects typically returned by the ephemeris
    module and returns the averaged data for both sets as a third dict of
    composite objects. """
    objects = {}

    for index, object in objects1.items():
        objects[index] = composite(object, objects2[index], obliquity)

    return objects


def composite(object1: dict, object2: dict, obliquity: float = None) -> dict:
    """ Given two chart objects typically returned by the ephemeris module,
    this function will return a composite object. """
    object = object1 | {
        'lon': swe.deg_midp(object1['lon'], object2['lon']),
        'speed': (object1['speed'] + object2['speed']) / 2,
    }

    if 'lat' in object1 and 'lat' in object2:
        object['lat'] = 0.0

    if 'dist' in object1 and 'dist' in object2:
        object['dist'] = 0.0

    if 'size' in object1 and 'size' in object2:
        object['size'] = (object1['size'] + object2['size']) / 2

    if 'dec' in object1 and obliquity is not None:
        object['dec'] = swe.cotrans((object['lon'], 0, 1), -obliquity)[1]

    return object


def obliquity(jd1: float, jd2: float, mean: bool = False) -> float:
    """ Returns the mean obliquity of two dates. """
    return (ephemeris.obliquity(jd1, mean) + ephemeris.obliquity(jd2, mean)) / 2
