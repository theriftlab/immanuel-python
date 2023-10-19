"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides basic positional data for a given object's longitude.
    Since longitudes can either be extracted from objects or calculated
    directly, these functions will accept both an object and a float.

"""

import json

import swisseph as swe

from immanuel.const import chart


_house = {}


def sign(object: dict | float) -> int:
    """ Returns the index of the zodiac sign the
    passed object belongs to. """
    return int((object['lon'] if isinstance(object, dict) else object) / 30) + 1


def sign_longitude(object: dict | float) -> tuple:
    """ Returns the index of the zodiac sign the passed object
    belongs to, and the sign-specific longitude inside it. """
    return (object['lon'] if isinstance(object, dict) else object) % 30


def opposite_sign(object: dict | float) -> int:
    """ Returns the index of the zodiac sign opposite
    where the passed object belongs to. """
    sign_number = sign(object)
    return sign_number + (6 if sign_number <= 6 else -6)


def decan(object: dict | float) -> int:
    """ Returns which decan the passed object is within its sign. """
    return int((object['lon'] if isinstance(object, dict) else object) % 30) // 10 + 1


def house(object: dict | float, houses: dict) -> int:
    """ Given a object and a dict of houses from the ephemeris module, this
    returns which house the object is in. Basic dict caching is used. """
    lon = object['lon'] if isinstance(object, dict) else object
    key = json.dumps([lon, houses])

    if key in _house:
        return _house[key]

    for house in houses.values():
        lon_diff = swe.difdeg2n(lon, house['lon'])
        next_cusp_diff = swe.difdeg2n(house['lon'] + house['size'], house['lon'])

        if 0 <= lon_diff < next_cusp_diff:
            _house[key] = house
            return house


def opposite_house(object: dict | float, houses: dict) -> int:
    """ Given a object and a dict of houses from the ephemeris
    module, this returns the house opposite where the object is. """
    house_number = house((object['lon'] if isinstance(object, dict) else object), houses)['number']
    index = chart.HOUSE + house_number + (6 if house_number <= 6 else -6)
    return houses[index]


def element(object: dict | float) -> int:
    """ Returns the element associated with the sign
    which the passed object belongs to. """
    return int((object['lon'] if isinstance(object, dict) else object) / 30) % 4 + 1


def modality(object: dict | float) -> int:
    """ Returns the modality associated with the sign
    which the passed object belongs to. """
    return int((object['lon'] if isinstance(object, dict) else object) / 30) % 3 + 1
