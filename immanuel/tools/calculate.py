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
    if formula == calc.NIGHT_FORMULA or (formula == calc.DAY_NIGHT_FORMULA and not is_daytime(sun_lon, asc_lon)):
        lon = (asc_lon + sun_lon - moon_lon)
    else:
        lon = (asc_lon + moon_lon - sun_lon)

    return swe.degnorm(lon)


def solar_year_length(jd):
    """ Returns the length in days of the year passed in the given
    Julian date. This is a direct copy of astro.com's calculations. """
    t = (jd - calc.J2000) / 365250
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # Arcsec per milllennium
    dvel = 1296027711.03429 + 2 * 109.15809 * t + 3 * 0.07207 * t2 - 4 * 0.23530 * t3 - 5 * 0.00180 * t4 + 6 * 0.00020 * t5
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel
