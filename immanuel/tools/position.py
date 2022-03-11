"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to pyswisseph data.

    Basic positional data for a given longitude.

"""

from decimal import Decimal


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
