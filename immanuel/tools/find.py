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
    before handing off to _linear_find()'s loop. Since the Sun and Moon have
    relatively stable daily motions and never retrograde, these are the only
    two bodies predictable enough to safely perform this with.

    The eclipse functions hand off directly to pyswisseph's own functions.

"""

import math

import swisseph as swe
from scipy.optimize import brentq

from immanuel.const import calc, chart
from immanuel.tools import calculate, ephemeris


PREVIOUS = -1
NEXT = 1

_SWE = {
    swe.ECL_TOTAL: chart.TOTAL,
    swe.ECL_ANNULAR: chart.ANNULAR,
    swe.ECL_PARTIAL: chart.PARTIAL,
    swe.ECL_ANNULAR_TOTAL: chart.ANNULAR_TOTAL,
    swe.ECL_PENUMBRAL: chart.PENUMBRAL,
}


# def previous(first: int, second: int, jd: float, aspect: float) -> float:
#     """ Returns the Julian day of the requested transit previous
#     to the passed Julian day. """
#     return _find(first, second, jd, aspect, PREVIOUS)


# def next(first: int, second: int, jd: float, aspect: float) -> float:
#     """ Returns the Julian day of the requested transit after
#     the passed Julian day. """
#     return _find(first, second, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """ Fast rewind to approximate conjunction. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(moon['lon'], sun['lon'])
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return _linear_find(chart.SUN, chart.MOON, jd, calc.CONJUNCTION, PREVIOUS)


def previous_full_moon(jd: float) -> float:
    """ Fast rewind to approximate opposition. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(moon['lon'], sun['lon']+180)
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return _linear_find(chart.SUN, chart.MOON, jd, calc.OPPOSITION, PREVIOUS)


def next_new_moon(jd: float) -> float:
    """ Fast forward to approximate conjunction. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(sun['lon'], moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return _linear_find(chart.SUN, chart.MOON, jd, calc.CONJUNCTION, NEXT)


def next_full_moon(jd: float) -> float:
    """ Fast forward to approximate opposition. """
    sun = ephemeris.planet(chart.SUN, jd)
    moon = ephemeris.planet(chart.MOON, jd)
    distance = swe.difdegn(sun['lon']+180, moon['lon'])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return _linear_find(chart.SUN, chart.MOON, jd, calc.OPPOSITION, NEXT)


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


def next_conjunction(object1: int, object2: int, jd: float, direction: int = NEXT) -> list:
    """ Temp function - returns a list of Julian dates for the next conjunction
    between the two passed objects. If a retrograde will result in multiple
    conjunctions, this function attempts to return all three dates. """
    diff = _diff(object1, object2, jd)

    sidereal_period1 = ephemeris.sidereal_period(object1, jd)
    sidereal_period2 = ephemeris.sidereal_period(object2, jd)
    max_retrograde_period = calculate.retrograde_period(object1, jd) + calculate.retrograde_period(object2, jd)

    # Calculate how far the fastest object must travel
    if sidereal_period1 < sidereal_period2:
        diff = 360 - diff

    # If the fastest object hasn't long passed the slowest, check for a retrograde
    if diff > 270:
        jd_start = jd
        jd_end = jd + max_retrograde_period * 365
        sign_changes = _sign_changes(object1, object2, jd_start, jd_end, 100)

        if not all(x is None for x in sign_changes):
            return sign_changes

    # Bracket the conjunction date with min & max synodic periods
    synodic_period_min = calculate.synodic_period(object1, object2, jd, calculate.SYNODIC_MIN)
    years = diff / 360 * synodic_period_min
    years -= max_retrograde_period
    days = years * 365.25
    jd_start = max(jd, jd + days)

    synodic_period_max = calculate.synodic_period(object1, object2, jd, calculate.SYNODIC_MAX)
    years = diff / 360 * synodic_period_max
    years += max_retrograde_period
    days = years * 365.25
    jd_end = jd + days

    return _sign_changes(object1, object2, jd_start, jd_end)


def _linear_find(first: int, second: int, jd: float, aspect: float, direction: int) -> float:
    """ Iteratively searches for and returns the Julian date of the previous
    or next requested aspect. Useful for short dates and fast planets but too
    expensive for anything more advanced. """
    while True:
        first_object = ephemeris.get(first, jd)
        second_object = ephemeris.get(second, jd)
        distance = abs(swe.difdeg2n(first_object['lon'], second_object['lon']))
        diff = abs(aspect - distance)

        if diff <= calc.MAX_ERROR:
            return jd

        add = direction
        speed = abs(max(first_object['speed'], second_object['speed']) - min(first_object['speed'], second_object['speed']))

        if diff < speed:
            add *= diff / 180

        jd += add


def _diff(object1: int, object2: int, jd: float) -> float:
    """ Return the angular difference between two objects. """
    lon1 = ephemeris.get(object1, jd)['lon']
    lon2 = ephemeris.get(object2, jd)['lon']

    return swe.difdegn(lon1, lon2)


def _ndiff(jd: float, object1: int, object2: int) -> float:
    """ Callback for brentq() - returns the normalized angular difference
    between two objects. """
    lon1 = ephemeris.get(object1, jd)['lon']
    lon2 = ephemeris.get(object2, jd)['lon']

    return swe.difdeg2n(lon1, lon2)


def _ingress_egress_bracket(object1: int, object2: int, jd_start: float, jd_end: float, steps: int) -> tuple:
    """ Returns a refined Julian date bracket of size step_size. """
    initial_ndiff = _ndiff(jd_start, object1, object2)
    jd_ingress = jd_egress = jd_start
    bracket_size = jd_end - jd_start
    step_size = bracket_size / steps

    while _ndiff(jd_egress, object1, object2) * initial_ndiff > 0 and jd_egress < jd_end:
        jd_ingress = jd_egress
        jd_egress += step_size

    if jd_egress == jd_end:
        return None

    return jd_ingress, jd_egress


def _sign_changes(object1: int, object2: int, jd_start: float, jd_end: float, steps: int = 1000) -> list:
    """ Returns a list of Julian dates of diff value +/- sign changes within
    the time bracket. """
    jd_matches = []
    jd_bracket_start = jd_start

    while (bracket := _ingress_egress_bracket(object1, object2, jd_bracket_start, jd_end, steps)) is not None and len(jd_matches) < 3:
        jd_matches.append(bracket)
        jd_bracket_start = bracket[1]

    matches = []

    for jd_ingress, jd_egress in jd_matches:
        try:
            jd_match = brentq(_ndiff, jd_ingress, jd_egress, args=(object1, object2), xtol=calc.MAX_ERROR)
        except:
            jd_match = None

        matches.append(jd_match)

    return matches


def _eclipse_type(swe_index: int) -> int:
    """ Returns the internal index of an eclipse type based on pyswisseph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag. """
    return _SWE[(swe_index >> 2) << 2]
