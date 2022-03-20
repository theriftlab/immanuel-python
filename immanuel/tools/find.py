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
from immanuel.tools import eph


PREVIOUS = 0
NEXT = 1


def previous(first: int, second: int, aspect: float, jd: float) -> float:
    """ Returns the Julian day of the requested transit previous
    to the passed Julian day. """
    return _find(first, second, aspect, jd, PREVIOUS)


def next(first: int, second: int, aspect: float, jd: float) -> float:
    """ Returns the Julian day of the requested transit after
    the passed Julian day. """
    return _find(first, second, aspect, jd, NEXT)


def previous_new_moon(jd: float) -> float:
    """ Fast rewind to approximate conjunction. """
    sun = eph.planet(jd, chart.SUN)
    moon = eph.planet(jd, chart.MOON)
    distance = swe.difdegn(moon['lon'], sun['lon'])
    jd -= math.floor(distance) / math.ceil(calc.MOON_MEAN_MOTION)
    return previous(chart.SUN, chart.MOON, calc.CONJUNCTION, jd)


def previous_full_moon(jd: float) -> float:
    """ Fast rewind to approximate opposition. """
    sun = eph.planet(jd, chart.SUN)
    moon = eph.planet(jd, chart.MOON)
    distance = swe.difdegn(moon['lon'], sun['lon']+180)
    jd -= math.floor(distance) / math.ceil(calc.MOON_MEAN_MOTION)
    return previous(chart.SUN, chart.MOON, calc.OPPOSITION, jd)


def next_new_moon(jd: float) -> float:
    """ Fast forward to approximate conjunction. """
    sun = eph.planet(jd, chart.SUN)
    moon = eph.planet(jd, chart.MOON)
    distance = swe.difdegn(sun['lon'], moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MOON_MEAN_MOTION)
    return next(chart.SUN, chart.MOON, calc.CONJUNCTION, jd)


def next_full_moon(jd: float) -> float:
    """ Fast forward to approximate opposition. """
    sun = eph.planet(jd, chart.SUN)
    moon = eph.planet(jd, chart.MOON)
    distance = swe.difdegn(sun['lon']+180, moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MOON_MEAN_MOTION)
    return next(chart.SUN, chart.MOON, calc.OPPOSITION, jd)


def previous_solar_eclipse(jd: float) -> float:
    """ Returns the Julian date of the moment of maximum eclipse for the
    most recent global total solar eclipse that occurred before the
    passed Julian date. """
    return swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_TOTAL, True)[1][0]


def previous_lunar_eclipse(jd: float) -> float:
    """ Returns the Julian date of the moment of maximum eclipse for the
    most recent global total lunar eclipse that occurred before the
    passed Julian date. """
    return swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_TOTAL, True)[1][0]


def next_solar_eclipse(jd: float) -> float:
    """ Returns the Julian date of the moment of maximum eclipse for the
    next global total solar eclipse that occurred after the passed
    Julian date. """
    return swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_TOTAL)[1][0]


def next_lunar_eclipse(jd: float) -> float:
    """ Returns the Julian date of the moment of maximum eclipse for the
    next global total lunar eclipse that occurred after the passed
    Julian date. """
    return swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_TOTAL)[1][0]


def _find(first: int, second: int, aspect: float, jd: float, direction: int) -> float:
    """ Returns the Julian date of the previous/next requested aspect.
    Accurate to within one second of a degree. """
    while True:
        first_obj = eph.planet(jd, first)
        second_obj = eph.planet(jd, second)
        distance = abs(swe.difdeg2n(first_obj['lon'], second_obj['lon']))
        diff = abs(aspect - distance)

        if diff <= calc.MAX_ERROR:
            return jd

        jd += (1 if direction == NEXT else -1) / max(180 / diff, 24)
