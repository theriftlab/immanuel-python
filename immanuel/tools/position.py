"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to pyswisseph data.

    Basic positional data for a given longitude.

"""

from decimal import Decimal

from immanuel import options
from immanuel.const import dignities


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


def domiciled(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is domiciled within its sign. """
    return index == options.rulerships[sign(lon)]


def detriment(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is in detriment within its sign. """
    return opposite_sign(lon) == list(options.rulerships.values()).index(index) + 1


def exalted(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is exalted within its sign. """
    return index == dignities.EXALTATIONS[sign(lon)]


def fall(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is in fall within its sign. """
    return opposite_sign(lon) == list(dignities.EXALTATIONS.values()).index(index) + 1


def term_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is the term ruler
    within its sign. """
    planet_sign, planet_sign_lon = signlon(lon)

    if index not in options.terms[planet_sign]:
        return False

    return options.terms[planet_sign][index][0] <= planet_sign_lon < options.terms[planet_sign][index][1]


def triplicity_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is a triplicity ruler
    within its sign. """
    return index in options.triplicities[sign(lon)].values()


def face_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is the decan ruler
    within its sign. """
    return dignities.FACE_RULERS[sign(lon)][decan(lon)-1] == index
