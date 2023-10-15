"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides basic positional data for a given longitude.

    Sign, decan, and various dignity states can be calculated with the
    functions found here.

"""

import json

import swisseph as swe

from immanuel.const import chart


SIGN = 0
LON = 1

_house = {}


def sign(lon: float) -> int:
    """ Returns the index of the zodiac sign the
    passed longitude belongs to. """
    return int(lon/30) + 1


def signlon(lon: float) -> tuple:
    """ Returns the index of the zodiac sign the passed longitude
    belongs to, and the sign-specific longitude inside it. """
    return sign(lon), lon%30


def opposite_sign(lon: float) -> int:
    """ Returns the index of the zodiac sign opposite
    where the passed longitude belongs to. """
    sign_number = sign(lon)
    return sign_number + (6 if sign_number <= 6 else -6)


def decan(lon: float) -> int:
    """ Returns which decan the passed longitude is within its sign. """
    return int(lon%30) // 10 + 1


def house(lon: float, houses: dict) -> int:
    """ Given a longitude and a dict of houses from the ephemeris module, this
    returns which house the longitude is in. Basic dict caching is used. """
    key = json.dumps([lon, houses])
    if key in _house:
        return _house[key]

    for house in houses.values():
        lon_diff = swe.difdeg2n(lon, house['lon'])
        next_cusp_diff = swe.difdeg2n(house['lon'] + house['size'], house['lon'])

        if 0 <= lon_diff < next_cusp_diff:
            _house[key] = house
            return house


def opposite_house(lon: float, houses: dict) -> int:
    """ Given a longitude and a dict of houses from the ephemeris
    module, this returns the house opposite where the longitude is. """
    house_number = house(lon, houses)['number']
    index = chart.HOUSE + house_number + (6 if house_number <= 6 else -6)
    return houses[index]


def element(lon: float) -> int:
    """ Returns the element associated with the sign
    which the passed longitude belongs to. """
    return int(lon/30) % 4 + 1


def modality(lon: float) -> int:
    """ Returns the modality associated with the sign
    which the passed longitude belongs to. """
    return int(lon/30) % 3 + 1
