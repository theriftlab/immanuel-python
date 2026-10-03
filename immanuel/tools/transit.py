"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Transits, eclipses, moon phases, etc. are calculated in this module.
Several of the transit searches are not used by the chart classes,
such as sign ingress / egress.

"""

import math

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import position, sweph

PREVIOUS = -1
NEXT = 1

INGRESS = 1
EGRESS = 2

_MIN_STEP = 0.01

_SWE_ECLIPSES = {
    swe.ECL_TOTAL: chart.TOTAL,
    swe.ECL_ANNULAR: chart.ANNULAR,
    swe.ECL_PARTIAL: chart.PARTIAL,
    swe.ECL_ANNULAR_TOTAL: chart.ANNULAR_TOTAL,
    swe.ECL_PENUMBRAL: chart.PENUMBRAL,
}


def previous_sign_ingress(index: int, sign: int, jd: float) -> float:
    """Returns the Julian date of the passed planet's previous ingress into
    the given sign."""
    return _sign_ingress_egress_search(index, sign, jd, PREVIOUS, INGRESS)


def next_sign_ingress(index: int, sign: int, jd: float) -> float:
    """Returns the Julian date of the passed planet's next ingress into
    the given sign."""
    return _sign_ingress_egress_search(index, sign, jd, NEXT, INGRESS)


def previous_sign_egress(index: int, sign: int, jd: float) -> float:
    """Returns the Julian date of the passed planet's previous egress from
    the given sign."""
    return _sign_ingress_egress_search(index, sign, jd, PREVIOUS, EGRESS)


def next_sign_egress(index: int, sign: int, jd: float) -> float:
    """Returns the Julian date of the passed planet's next egress from
    the given sign."""
    return _sign_ingress_egress_search(index, sign, jd, NEXT, EGRESS)


def previous_aspect_between(
    index1: int, index2: int, jd: float, aspect: float
) -> float:
    """Returns the Julian day of the requested aspect between two moving planets
    previous to the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, PREVIOUS)


def next_aspect_between(index1: int, index2: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested aspect between two moving planets
    after the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, NEXT)


def previous_aspect_to(index: int, lon: float, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested aspect between a given longitude
    and a moving planet previous to the passed Julian day."""
    return _fixed_aspect_search(index, lon, jd, aspect, PREVIOUS)


def next_aspect_to(index: int, lon: float, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested aspect between a given longitude
    and a moving planet after the passed Julian day."""
    return _fixed_aspect_search(index, lon, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """Returns the Julian date of the previous Sun / Moon conjunction."""
    return previous_aspect_between(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def previous_full_moon(jd: float) -> float:
    """Returns the Julian date of the previous Sun / Moon opposition."""
    return previous_aspect_between(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def next_new_moon(jd: float) -> float:
    """Returns the Julian date of the next Sun / Moon conjunction."""
    return next_aspect_between(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def next_full_moon(jd: float) -> float:
    """Returns the Julian date of the next Sun / Moon opposition."""
    return next_aspect_between(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


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
    """Returns the internal index of an eclipse type based on pysweph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag."""
    return _SWE_ECLIPSES[(swe_index >> 2) << 2]


def _aspect_search(
    index1: int, index2: int, jd: float, aspect: float, direction: int
) -> float:
    """Returns the Julian date of the previous or next requested aspect
    between two planets."""
    targets = _aspect_targets(calc.CONJUNCTION, aspect)
    return _crossing(index1, targets, jd, direction, NEXT, index2=index2)[0]


def _fixed_aspect_search(
    index: int, lon: float, jd: float, aspect: float, direction: int
) -> float:
    """Returns the Julian date of the previous or next requested aspect
    between a planet and a given longitude."""
    targets = _aspect_targets(lon, aspect)
    return _crossing(index, targets, jd, direction, NEXT)[0]


def _sign_ingress_egress_search(
    index: int, sign: int, jd: float, direction: int, type: int
) -> float:
    """Returns the Julian date of the previous or next ingress into or egress
    out of the given sign. If the planet is already in the requested state,
    it runs the search again to find the next one in the given direction."""
    sign_boundaries = {swe.degnorm((sign - 1) * 30.0), swe.degnorm(sign * 30.0)}
    jd, lon = _crossing(index, sign_boundaries, jd, direction, direction)
    in_sign = position.sign(lon) == sign
    in_ingress = type == INGRESS
    if in_sign != in_ingress:
        jd = _crossing(index, sign_boundaries, jd, direction, direction)[0]
    return jd


def _crossing(
    index1: int,
    targets: set,
    jd: float,
    direction: int,
    side: int,
    index2: int | None = None,
) -> tuple:
    """Returns the Julian date and longitude of the passed planet's first
    crossing of any target longitude in the given direction. If a second planet
    is also passed, the first planet's longitude is measured relative to it."""

    def sample(jd: float) -> tuple:
        """Returns the longitude and speed at the Julian date, relative to the
        second planet if there is one, plus the distance from each target to
        that longitude."""
        planet1 = sweph.planet(index1, jd)
        lon, speed = planet1["lon"], planet1["speed"]
        if index2 is not None:
            planet2 = sweph.planet(index2, jd)
            lon, speed = swe.degnorm(lon - planet2["lon"]), speed - planet2["speed"]
        return lon, speed, {target: swe.difdeg2n(lon, target) for target in targets}

    def crossings(prev_offsets: dict, offsets: dict) -> list:
        """Returns the targets whose offsets changed mathematical sign between
        two samples, ignoring 180° crossings."""
        return [
            target
            for target, offset in offsets.items()
            if offset * prev_offsets[target] < 0
            and abs(offset) + abs(prev_offsets[target]) < 180
        ]

    max_speed = sum(
        calc.MAX_MOTIONS.get(index, calc.MAX_MOTIONS[chart.MOON])
        for index in (index1, index2)
        if index is not None
    )
    lon, speed, offsets = sample(jd)
    # Treat already being on target as being behind the search
    for target, offset in offsets.items():
        if abs(offset) <= calc.MAX_ERROR:
            offsets[target] = math.copysign(calc.MAX_ERROR, speed * direction)

    while True:
        # Store our old values
        prev_jd, prev_speed, prev_offsets = jd, speed, offsets
        # Update the current values
        distance = min(abs(offset) for offset in offsets.values())
        jd += direction * max(distance, _MIN_STEP) / max_speed
        lon, speed, offsets = sample(jd)
        # An offset that's exactly on target should never happen in practice
        # but if it does, the offset will be unsigned and therefore not be on
        # either side (- or +) so we need to step a tiny fraction further and
        # resample to get a bracket
        if 0 in offsets.values():
            jd += direction * calc.MAX_ERROR / max_speed
            lon, speed, offsets = sample(jd)
        # If a planet stations within a _MIN_STEP sized gap, we can end up
        # missing a crossing, so we do do an extra crossing check here
        if distance < _MIN_STEP and prev_speed * speed < 0:
            step = jd - prev_jd
            step_fraction = prev_speed / (prev_speed - speed)
            station_jd = prev_jd + step * step_fraction
            station = sample(station_jd)
            if crossings(prev_offsets, station[2]):
                jd, (lon, speed, offsets) = station_jd, station
        # See if any of our offsets have changed mathematical sign
        crossed = crossings(prev_offsets, offsets)
        if crossed:
            break
    # Crossing found, time to find & refine the root - first ensure there's
    # only one target (for most non-edge cases we will already only have one)
    target = min(crossed, key=lambda target: abs(prev_offsets[target]))
    # Here we aim to overshoot the target by a tiny fraction to ensure
    # we end up on the correct side of it
    overshoot_sign = math.copysign(1, side * direction * offsets[target])
    prev_overshoot = overshoot_sign * prev_offsets[target]
    overshoot = overshoot_sign * offsets[target]
    # Key the date brackets by which one is already overshooting
    ends = {
        prev_overshoot > 0: (prev_jd, prev_overshoot),
        overshoot > 0: (jd, overshoot),
    }
    # Keep interpolating until our sample only overshoots by <= calc.MAX_ERROR
    target_overshoot = calc.MAX_ERROR / 2
    while not 0 < overshoot <= calc.MAX_ERROR:
        before_jd, before_overshoot = ends[False]
        after_jd, after_overshoot = ends[True]
        # Step towards target_overshoot
        step = after_jd - before_jd
        overshoot_range = after_overshoot - before_overshoot
        step_fraction = (target_overshoot - before_overshoot) / overshoot_range
        jd = before_jd + step * step_fraction
        # Resample at the new jd
        lon, _, offsets = sample(jd)
        overshoot = overshoot_sign * offsets[target]
        ends[overshoot > 0] = (jd, overshoot)
    return jd, lon


def _aspect_targets(lon: float, aspect: float) -> set:
    """Returns the longitudes at which a planet makes the passed aspect to the
    passed longitude. Besides conjunctions and oppositions, there will be two
    target longitudes."""
    return {swe.degnorm(lon + aspect), swe.degnorm(lon - aspect)}
