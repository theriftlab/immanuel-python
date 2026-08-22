"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module provides the orbital mechanics of chart objects. Obliquity,
eccentricity, and various kinds of orbital period are calculated here.

"""


from immanuel.const import calc
from immanuel.tools import sweph

DAYS = 0
TROPICAL_YEARS = 1

SYNODIC_MIN = -1
SYNODIC_AVG = 0
SYNODIC_MAX = 1


def earth_obliquity(jd: float, mean: bool = False) -> float:
    """Returns the true or mean obliquity of the ecliptic for the given
    Julian date."""
    return sweph.mean_earth_obliquity(jd) if mean else sweph.true_earth_obliquity(jd)


def orbital_eccentricity(index: int, jd: float) -> float:
    """Returns the passed object's orbital eccentricity."""
    return sweph.orbital_elements(index, jd)["eccentricity"]


def sidereal_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's sidereal orbital period."""
    sidereal_period = sweph.orbital_elements(index, jd)["sidereal_orbital_period"]
    return sidereal_period * solar_year_length(jd) if unit == DAYS else sidereal_period


def tropical_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's tropical orbital period."""
    tropical_period = sweph.orbital_elements(index, jd)["tropical_period"]
    return tropical_period * solar_year_length(jd) if unit == DAYS else tropical_period


def synodic_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's synodic period."""
    synodic_period = sweph.orbital_elements(index, jd)["synodic_period"]
    return synodic_period if unit == DAYS else synodic_period / solar_year_length(jd)


def solar_year_length(jd: float) -> float:
    """Returns the tropical year length in days of the given Julian date.
    This is a direct copy of astro.com's calculations."""
    t = (jd - calc.J2000) / 365250
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # Arcsec per millennium
    dvel = (
        1296027711.03429
        + 2 * 109.15809 * t
        + 3 * 0.07207 * t2
        - 4 * 0.23530 * t3
        - 5 * 0.00180 * t4
        + 6 * 0.00020 * t5
    )
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel
