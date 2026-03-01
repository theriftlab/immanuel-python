"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Transits, eclipses, moon phases, etc. are calculated in this module.

"""

import math

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import ephemeris
from immanuel.tools import position


PREVIOUS = -1
NEXT = 1

_SWE_ECLIPSES = {
    swe.ECL_TOTAL: chart.TOTAL,
    swe.ECL_ANNULAR: chart.ANNULAR,
    swe.ECL_PARTIAL: chart.PARTIAL,
    swe.ECL_ANNULAR_TOTAL: chart.ANNULAR_TOTAL,
    swe.ECL_PENUMBRAL: chart.PENUMBRAL,
}


def previous_aspect(index1: int, index2: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit previous
    to the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, PREVIOUS)


def next_aspect(index1: int, index2: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit after
    the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """Fast rewind to approximate conjunction."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"])
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def previous_full_moon(jd: float) -> float:
    """Fast rewind to approximate opposition."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"] + 180)
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous_aspect(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def next_new_moon(jd: float) -> float:
    """Fast forward to approximate conjunction."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"], moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def next_full_moon(jd: float) -> float:
    """Fast forward to approximate opposition."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"] + 180, moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next_aspect(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def previous_solar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent global solar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(
        jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR, True
    )
    return _eclipse_type(res), tret[0]


def previous_lunar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent lunar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR, True)
    return _eclipse_type(res), tret[0]


def next_solar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next global solar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR)
    return _eclipse_type(res), tret[0]


def next_lunar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next lunar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR)
    return _eclipse_type(res), tret[0]


def _eclipse_type(swe_index: int) -> int:
    """Returns the internal index of an eclipse type based on pyswisseph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag."""
    return _SWE_ECLIPSES[(swe_index >> 2) << 2]


def _aspect_search(
    index1: int, index2: int, jd: float, aspect: float, direction: int
) -> float:
    """Iteratively searches for and returns the Julian date of the previous
    or next requested aspect. Useful for short dates and fast planets but too
    expensive for anything more advanced."""
    while True:
        planet1 = ephemeris.get_planet(index1, jd)
        planet2 = ephemeris.get_planet(index2, jd)
        distance = abs(swe.difdeg2n(planet1["lon"], planet2["lon"]))
        diff = abs(aspect - distance)

        if diff <= calc.MAX_ERROR:
            return jd

        add = direction
        speed = abs(
            max(planet1["speed"], planet2["speed"])
            - min(planet1["speed"], planet2["speed"])
        )

        if diff < speed:
            add *= diff / 180

        jd += add
