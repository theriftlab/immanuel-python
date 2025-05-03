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


def previous(first: int, second: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit previous
    to the passed Julian day."""
    return _search(first, second, jd, aspect, PREVIOUS)


def next(first: int, second: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit after
    the passed Julian day."""
    return _search(first, second, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """Fast rewind to approximate conjunction."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"])
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def previous_full_moon(jd: float) -> float:
    """Fast rewind to approximate opposition."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"] + 180)
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def next_new_moon(jd: float) -> float:
    """Fast forward to approximate conjunction."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"], moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def next_full_moon(jd: float) -> float:
    """Fast forward to approximate opposition."""
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"] + 180, moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def previous_solar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent global solar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(
        jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR, True
    )
    return _eclipse_type(res), tret[0]


def previous_lunar_eclipse(jd: float) -> float:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent lunar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR, True)
    return _eclipse_type(res), tret[0]


def next_solar_eclipse(jd: float) -> float:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next global solar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR)
    return _eclipse_type(res), tret[0]


def next_lunar_eclipse(jd: float) -> float:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next lunar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR)
    return _eclipse_type(res), tret[0]


def _eclipse_type(swe_index: int) -> int:
    """Returns the internal index of an eclipse type based on pyswisseph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag."""
    return _SWE[(swe_index >> 2) << 2]


def _search(
    object1: int, object2: int, jd: float, aspect: float, direction: int
) -> float:
    """Search for and return the Julian date of the previous or next requested
    aspect. Since the Sun, Moon, Mercury and Venus have movements that make
    our synodic bracketing difficult - and aspects involving them should only
    occur within approximately one year - we defer them to the linear search."""
    non_synodic = (chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS)

    if object1 in non_synodic or object2 in non_synodic:
        return _linear_search(object1, object2, jd, aspect, direction)

    return _advanced_search(object1, object2, jd, aspect, direction)


def _linear_search(
    object1: int, object2: int, jd: float, aspect: float, direction: int
) -> float:
    """Iteratively searches for and returns the Julian date of the previous
    or next requested aspect. Useful for short dates and fast planets but too
    expensive for anything more advanced."""
    while True:
        planet1 = ephemeris.get_planet(object1, jd)
        planet2 = ephemeris.get_planet(object2, jd)
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


def _advanced_search(
    object1: int, object2: int, jd: float, aspect: float, direction: int
) -> float:
    """Advanced find function that uses a more complex algorithm to find the
    Julian date of the previous or next requested aspect. Useful for long dates
    and slow planets."""
    sidereal_period1 = ephemeris.get_sidereal_period(object1, jd)
    sidereal_period2 = ephemeris.get_sidereal_period(object2, jd)

    if (sidereal_period1 < sidereal_period2 and direction == NEXT) or (
        sidereal_period1 > sidereal_period2 and direction == PREVIOUS
    ):
        object1, object2 = object2, object1

    diff = _diff(object1, object2, jd)

    max_retrograde_period = calculate.retrograde_period(
        object1, jd
    ) + calculate.retrograde_period(object2, jd)

    # If the aspect hasn't long passed, check for an upcoming retrograde
    if diff > 270 and max_retrograde_period > 0:
        buffer_days = max_retrograde_period * 365.25
        jd_start = jd - buffer_days if direction == PREVIOUS else jd
        jd_end = jd + buffer_days if direction == NEXT else jd

        transit_crossings = _transit_crossings(
            object1=object1,
            object2=object2,
            jd_start=jd_start,
            jd_end=jd_end,
            steps=100,
        )

        if len(transit_crossings) > 0:
            return transit_crossings[0] if direction == NEXT else transit_crossings[-1]

    # Bracket the conjunction date with min & max periods
    synodic_period_min = calculate.synodic_period(
        object1, object2, jd, calculate.SYNODIC_MIN
    )
    synodic_period_max = calculate.synodic_period(
        object1, object2, jd, calculate.SYNODIC_MAX
    )

    years_min = diff / 360 * synodic_period_min - max_retrograde_period
    years_max = diff / 360 * synodic_period_max + max_retrograde_period

    days_min = years_min * 365.25
    days_max = years_max * 365.25

    jd_start = jd - days_max if direction == PREVIOUS else max(jd, jd + days_min)
    jd_end = min(jd, jd - days_min) if direction == PREVIOUS else jd + days_max

    transit_crossings = _transit_crossings(
        object1=object1,
        object2=object2,
        jd_start=jd_start,
        jd_end=jd_end,
    )

    return transit_crossings[0] if direction == NEXT else transit_crossings[-1]


def _diff(object1: int, object2: int, jd: float) -> float:
    """Return the angular difference between two objects."""
    lon1 = ephemeris.get_planet(object1, jd)["lon"]
    lon2 = ephemeris.get_planet(object2, jd)["lon"]

    return swe.difdegn(lon1, lon2)


def _ndiff(jd: float, object1: int, object2: int) -> float:
    """Callback for brentq() - returns the normalized angular difference
    between two objects."""
    lon1 = ephemeris.get_planet(object1, jd)["lon"]
    lon2 = ephemeris.get_planet(object2, jd)["lon"]

    return swe.difdeg2n(lon1, lon2)


def _transit_bracket(
    object1: int, object2: int, jd_start: float, jd_end: float, steps: int
) -> tuple:
    """Returns a refined Julian date bracket of size step_size."""
    initial_ndiff = _ndiff(jd_start, object1, object2)
    jd_ingress = jd_egress = jd_start
    bracket_size = jd_end - jd_start
    step_size = bracket_size / steps
    iterations = 0

    while (
        (
            (ndiff := _ndiff(jd_egress, object1, object2)) * initial_ndiff > 0
            or abs(ndiff) > 170
        )
        and jd_egress < jd_end
        and iterations < steps
    ):
        jd_ingress = jd_egress
        jd_egress += step_size
        iterations += 1

    if jd_egress == jd_end:
        return None

    return jd_ingress, jd_egress


def _transit_crossings(
    object1: int,
    object2: int,
    jd_start: float,
    jd_end: float,
    steps: int = 1000,
) -> list:
    """Returns a list of Julian dates of diff value +/- sign changes within
    the time bracket."""
    jd_matches = []
    jd_bracket_start = jd_start

    while (
        bracket := _transit_bracket(object1, object2, jd_bracket_start, jd_end, steps)
    ) is not None and bracket[0] < bracket[1]:
        jd_matches.append(bracket)
        jd_bracket_start = bracket[1]

    matches = []

    for jd_ingress, jd_egress in jd_matches:
        try:
            jd_match = brentq(
                _ndiff,
                jd_ingress,
                jd_egress,
                args=(object1, object2),
                xtol=calc.MAX_ERROR,
            )

            matches.append(jd_match)
        except:
            pass

    return matches
