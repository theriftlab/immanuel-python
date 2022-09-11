"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module contains many of the calculations required to
    parse the raw numbers from pyswisseph into useable data.

    This is used in tandem with the eph module, but is separated out
    so that this data can be accessed without a specific date or location,
    most notably when generating a composite chart.

"""

import swisseph as swe

from immanuel.const import calc


def moon_phase(sun_lon: float, moon_lon: float) -> int:
    """ Returns the moon phase given the positions of the Sun and Moon. """
    distance = swe.difdegn(moon_lon, sun_lon)

    for angle in range(45, 361, 45):
        if distance < angle:
            return angle


def is_daytime(sun_lon: float, asc_lon: float) -> bool:
    """ Returns whether the sun is above the ascendant. """
    return swe.difdeg2n(sun_lon, asc_lon) < 0


def pars_fortuna(sun_lon: float, moon_lon: float, asc_lon: float, formula: int) -> float:
    """ Returns the Part of Fortune longitude. """
    if formula == calc.DAY_FORMULA or (formula == calc.DAY_NIGHT_FORMULA and is_daytime(sun_lon, asc_lon)):
        lon = (asc_lon + moon_lon - sun_lon)
    else:
        lon = (asc_lon + sun_lon - moon_lon)

    return swe.degnorm(lon)
