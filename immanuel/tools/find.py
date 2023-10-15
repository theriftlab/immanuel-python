"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module calculates past and future transits relative
    to a passed Julian day.

    previous() and next() take two planets, a Julian day, and an aspect.
    The functions will then find & return the last/next Julian day
    before/after the passed one where the requested aspect took place.
    This calculation can be expensive for slow planets, and is currently
    not flexible enough to use with non-planetary objects or points.

    The previous/next new and full moon functions are designed to
    fast-rewind and fast-forward to a close approximation of each aspect
    before handing off to _find()'s loop. Since the Sun and Moon have
    relatively stable daily motions and never retrograde, these are the only
    two bodies predictable enough to safely perform this with.

    The eclipse functions hand off directly to pyswisseph's own functions.

"""

import math

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import ephemeris


PREVIOUS = 0
NEXT = 1

_SWE = {
    swe.ECL_TOTAL: chart.TOTAL,
    swe.ECL_ANNULAR: chart.ANNULAR,
    swe.ECL_PARTIAL: chart.PARTIAL,
    swe.ECL_ANNULAR_TOTAL: chart.ANNULAR_TOTAL,
    swe.ECL_PENUMBRAL: chart.PENUMBRAL,
}


def previous(first: int, second: int, jd: float, aspect: float) -> float:
    """ Returns the Julian day of the requested transit previous
    to the passed Julian day. """
    return _find(first, second, jd, aspect, PREVIOUS)


def next(first: int, second: int, jd: float, aspect: float) -> float:
    """ Returns the Julian day of the requested transit after
    the passed Julian day. """
    return _find(first, second, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """ Fast rewind to approximate conjunction. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(moon['lon'], sun['lon'])
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def previous_full_moon(jd: float) -> float:
    """ Fast rewind to approximate opposition. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(moon['lon'], sun['lon']+180)
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def next_new_moon(jd: float) -> float:
    """ Fast forward to approximate conjunction. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(sun['lon'], moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def next_full_moon(jd: float) -> float:
    """ Fast forward to approximate opposition. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(sun['lon']+180, moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def previous_solar_eclipse(jd: float) -> tuple:
    """ Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent global solar eclipse that occurred before the
    passed Julian date. """
    res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR, True)
    return _eclipse_type(res), tret[0]


def previous_lunar_eclipse(jd: float) -> float:
    """ Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent lunar eclipse that occurred before the
    passed Julian date. """
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR, True)
    return _eclipse_type(res), tret[0]


def next_solar_eclipse(jd: float) -> float:
    """ Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next global solar eclipse that occurred after the
    passed Julian date. """
    res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR)
    return _eclipse_type(res), tret[0]


def next_lunar_eclipse(jd: float) -> float:
    """ Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next lunar eclipse that occurred after the
    passed Julian date. """
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR)
    return _eclipse_type(res), tret[0]


def _find(first: int, second: int, jd: float, aspect: float, direction: int) -> float:
    """ Returns the Julian date of the previous/next requested aspect.
    Accurate to within one arc-second. """
    multiplier = 1 if direction == NEXT else -1

    while True:
        first_object = ephemeris.get(first, jd)
        second_object = ephemeris.get(second, jd)
        distance = abs(swe.difdeg2n(first_object['lon'], second_object['lon']))
        diff = abs(aspect - distance)

        if diff <= calc.MAX_ERROR:
            return jd

        add = 1 * multiplier
        speed = abs(max(first_object['speed'], second_object['speed']) - min(first_object['speed'], second_object['speed']))

        if diff < speed:
            add *= diff / 180

        jd += add


def _eclipse_type(swe_index: int) -> int:
    """ Returns the internal index of an eclipse type based on swisseph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag. """
    return _SWE[(swe_index >> 2) << 2]
