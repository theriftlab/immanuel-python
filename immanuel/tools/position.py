"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides basic positional data for a given longitude.

    Sign, decan, and various dignity states can be calculated with the
    functions found here.

"""

from decimal import Decimal

import swisseph as swe


SIGN = 0
LON = 1


def sign(lon: float) -> int:
    """ Returns the index of the zodiac sign the
    passed longitude belongs to. """
    return int(lon/30) + 1


def signlon(lon: float) -> tuple:
    """ Returns the index of the zodiac sign the passed longitude
    belongs to, and the sign-specific longitude inside it. """
    return int(lon/30) + 1, float(Decimal(str(lon)) % 30)


def opposite_sign(lon: float) -> int:
    """ Returns the index of the zodiac sign opposite
    where the passed longitude belongs to. """
    return (int(lon/30) + 7) % 12


def decan(lon: float) -> int:
    """ Returns which decan the passed longitude is within its sign. """
    return int(lon%30) // 10 + 1


def house(lon: float, houses: dict) -> int:
    """ Given a longitude and a dict of houses from the eph
    module, this returns which house the longitude is in. """
    for house_number, house in houses.items():
        lon_diff = swe.difdeg2n(lon, house['lon'])
        next_cusp_diff = swe.difdeg2n(house['lon'] + house['size'], house['lon'])

        if 0 < lon_diff < next_cusp_diff:
            return house_number
