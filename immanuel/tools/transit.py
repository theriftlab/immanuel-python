"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Transits, eclipses, moon phases, etc. are calculated in this module.
Several of the transit searches are not used by the chart classes,
such as sign ingress / egress.

"""

import bisect
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


class NotFoundError(Exception):
    """Raised when a search reaches either its passed-in limit date,
    or the end of the available ephemeris."""


def previous_sign_ingress(
    index: int, sign: int, jd: float, limit: float | None = None
) -> float:
    """Returns the Julian date of the passed planet's previous ingress into the
    given sign."""
    return _sign_ingress_egress_search(index, sign, jd, PREVIOUS, INGRESS, limit)


def next_sign_ingress(
    index: int, sign: int, jd: float, limit: float | None = None
) -> float:
    """Returns the Julian date of the passed planet's next ingress into the
    given sign."""
    return _sign_ingress_egress_search(index, sign, jd, NEXT, INGRESS, limit)


def previous_sign_egress(
    index: int, sign: int, jd: float, limit: float | None = None
) -> float:
    """Returns the Julian date of the passed planet's previous egress from the
    given sign."""
    return _sign_ingress_egress_search(index, sign, jd, PREVIOUS, EGRESS, limit)


def next_sign_egress(
    index: int, sign: int, jd: float, limit: float | None = None
) -> float:
    """Returns the Julian date of the passed planet's next egress from the
    given sign."""
    return _sign_ingress_egress_search(index, sign, jd, NEXT, EGRESS, limit)


def previous_aspect_between(
    index1: int, index2: int, jd: float, aspect: float, limit: float | None = None
) -> float:
    """Returns the Julian day of the requested aspect between two moving
    planets previous to the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, PREVIOUS, limit)


def next_aspect_between(
    index1: int, index2: int, jd: float, aspect: float, limit: float | None = None
) -> float:
    """Returns the Julian day of the requested aspect between two moving
    planets after the passed Julian day."""
    return _aspect_search(index1, index2, jd, aspect, NEXT, limit)


def previous_aspect_to(
    index: int, lon: float, jd: float, aspect: float, limit: float | None = None
) -> float:
    """Returns the Julian day of the requested aspect between a given longitude
    and a moving planet previous to the passed Julian day."""
    return _fixed_aspect_search(index, lon, jd, aspect, PREVIOUS, limit)


def next_aspect_to(
    index: int, lon: float, jd: float, aspect: float, limit: float | None = None
) -> float:
    """Returns the Julian day of the requested aspect between a given longitude
    and a moving planet after the passed Julian day."""
    return _fixed_aspect_search(index, lon, jd, aspect, NEXT, limit)


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
    index1: int,
    index2: int,
    jd: float,
    aspect: float,
    direction: int,
    limit: float | None,
) -> float:
    """Returns the Julian date of the previous or next requested aspect
    between two planets."""
    targets = _aspect_targets(calc.CONJUNCTION, aspect)
    return _crossing(index1, targets, jd, direction, NEXT, index2, limit)[0]


def _fixed_aspect_search(
    index: int,
    lon: float,
    jd: float,
    aspect: float,
    direction: int,
    limit: float | None,
) -> float:
    """Returns the Julian date of the previous or next requested aspect
    between a planet and a given longitude."""
    targets = _aspect_targets(lon, aspect)
    return _crossing(index, targets, jd, direction, NEXT, limit=limit)[0]


def _sign_ingress_egress_search(
    index: int,
    sign: int,
    jd: float,
    direction: int,
    type: int,
    limit: float | None,
) -> float:
    """Returns the Julian date of the previous or next ingress into or egress
    out of the given sign. If the planet is already in the requested state,
    it runs the search again to find the next one in the given direction."""
    sign_boundaries = {swe.degnorm((sign - 1) * 30.0), swe.degnorm(sign * 30.0)}
    jd, lon, _ = _crossing(
        index, sign_boundaries, jd, direction, direction, limit=limit
    )
    in_sign = position.sign(lon) == sign
    in_ingress = type == INGRESS
    if in_sign != in_ingress:
        jd = _crossing(index, sign_boundaries, jd, direction, direction, limit=limit)[0]
    return jd


def _crossing(
    index1: int,
    targets: set,
    jd: float,
    direction: int,
    side: int,
    index2: int | None = None,
    limit: float | None = None,
) -> tuple:
    """Returns the Julian date, longitude and target of the passed planet's
    first crossing of any target longitude in the given direction. If a second
    planet is also passed, the first planet's longitude is measured relative to
    it. If a limit arg is present, NotFoundError will be raised when it is
    exceeded."""

    def sample(jd: float) -> tuple:
        """Returns the longitude and speed at the Julian date, relative to the
        second planet if there is one."""
        lon, speed = sweph.longitude(index1, jd)
        if index2 is not None:
            lon2, speed2 = sweph.longitude(index2, jd)
            lon, speed = swe.degnorm(lon - lon2), speed - speed2
        return lon, speed

    def nearest_distance(lon: float) -> float:
        """Returns the distance from the passed longitude to the nearest target,
        which will be one of its two neighbors in sorted_targets."""
        lon_index = bisect.bisect_left(sorted_targets, lon)
        nearest_targets = (
            sorted_targets[lon_index % len(sorted_targets)],
            sorted_targets[lon_index - 1],
        )
        return min(abs(swe.difdeg2n(lon, target)) for target in nearest_targets)

    def crossings(from_lon: float, to_lon: float) -> list:
        """Returns the targets crossed in an arc between from_lon
        and to_lon, in the order they were crossed, using simple bisection."""
        # Ensure we're always searching forwards even if the arc went backwards
        if swe.difdeg2n(to_lon, from_lon) < 0:
            return crossings(to_lon, from_lon)[::-1]
        # Find the indices of the start and end targets
        start = bisect.bisect_right(sorted_targets, from_lon)
        end = bisect.bisect_left(sorted_targets, to_lon)
        # If start > end we'll get an empty list
        if from_lon <= to_lon:
            return sorted_targets[start:end]
        # Wrap our list if the current arc crosses 0°
        return sorted_targets[start:] + sorted_targets[:end]

    # Ensure we're starting ahead of any passed limit value
    if limit is not None and (limit - jd) * direction <= 0:
        raise NotFoundError(f"Limit date {limit} should be ahead of the start date.")
    sorted_targets = sorted(targets)
    max_speed = sum(
        # Default to the moon since this is usually the fastest
        calc.MAX_MOTIONS.get(index, calc.MAX_MOTIONS[chart.MOON])
        for index in (index1, index2)
        if index is not None
    )
    lon, speed = sample(jd)
    # Start the search a fraction ahead
    from_lon = swe.degnorm(lon + math.copysign(calc.MAX_ERROR, speed * direction))
    # Catch any searches that attempt to step past the available ephemeris limits
    try:
        while True:
            # Store our old values
            prev_jd, prev_lon, prev_speed = jd, lon, speed
            # Update the current values
            distance = nearest_distance(lon)
            jd += direction * max(distance, _MIN_STEP) / max_speed
            # If we have gone past the passed limit, we didn't find anything
            if limit is not None and (jd - limit) * direction > 0:
                if prev_jd == limit:
                    raise NotFoundError(f"No transit found before limit date {limit}.")
                jd = limit
            lon, speed = sample(jd)
            # A sample that's exactly on target should never happen in practice
            # but if it does, it will not be on either side (- or +) so we need
            # to step a tiny fraction further and resample to get a bracket
            if lon in targets:
                jd += direction * calc.MAX_ERROR / max_speed
                lon, speed = sample(jd)
            # If a planet stations within a _MIN_STEP sized gap, we can end up
            # missing a crossing, so we do an extra crossing check here
            if distance < _MIN_STEP and prev_speed * speed < 0:
                step = jd - prev_jd
                step_fraction = prev_speed / (prev_speed - speed)
                station_jd = prev_jd + step * step_fraction
                station_lon, station_speed = sample(station_jd)
                if crossings(from_lon, station_lon):
                    jd, lon, speed = station_jd, station_lon, station_speed
            # See if we have crossed any targets
            crossed = crossings(from_lon, lon)
            if crossed:
                break
            from_lon = lon
        # Crossing found, time to find & refine the root - the first target
        # along the arc is the first one crossed
        target = crossed[0]
        offset = swe.difdeg2n(lon, target)
        # Here we aim to overshoot the target by a tiny fraction to ensure
        # we end up on the correct side of it
        overshoot_sign = math.copysign(1, side * direction * offset)
        prev_overshoot = overshoot_sign * swe.difdeg2n(prev_lon, target)
        overshoot = overshoot_sign * offset
        # Key the date brackets by which one is already overshooting
        ends = {
            prev_overshoot > 0: (prev_jd, prev_overshoot, prev_lon),
            overshoot > 0: (jd, overshoot, lon),
        }
        # Keep interpolating until our sample only overshoots by <= calc.MAX_ERROR
        target_overshoot = calc.MAX_ERROR / 2
        previous_side = None
        repeated_side = False
        while ends[True][1] > calc.MAX_ERROR:
            before_jd, before_overshoot, _ = ends[False]
            after_jd, after_overshoot, _ = ends[True]
            step = after_jd - before_jd
            if repeated_side:
                # In rare cases such as a Moon / True Lilith conjunction, we can
                # end up with 2 samples on the same side of the target, so we
                # simply halve the bracket here
                jd = before_jd + step / 2
            else:
                # Step towards target_overshoot
                overshoot_range = after_overshoot - before_overshoot
                step_fraction = (target_overshoot - before_overshoot) / overshoot_range
                jd = before_jd + step * step_fraction
            # Jittery ephemeris data can produce date differences too small to
            # work with, so here we check if either side rounds to the current
            # jd and exit if there's a match
            if jd in (before_jd, after_jd):
                break
            # Resample at the new jd
            lon = sample(jd)[0]
            overshoot = overshoot_sign * swe.difdeg2n(lon, target)
            ends[overshoot > 0] = (jd, overshoot, lon)
            current_side = overshoot > 0
            repeated_side = current_side == previous_side
            previous_side = current_side
    except swe.Error as error:
        raise NotFoundError(
            "No transit found before the end of the available ephemeris."
        ) from error
    jd, _, lon = ends[True]
    # Our overshoot target means that a crossing right at the limit
    # can settle a fraction beyond it
    if limit is not None and (jd - limit) * direction > 0:
        raise NotFoundError(f"No transit found before limit date {limit}.")
    return jd, lon, target


def _aspect_targets(lon: float, aspect: float) -> set:
    """Returns the longitudes at which a planet makes the passed aspect to the
    passed longitude. Besides conjunctions and oppositions, there will be two
    target longitudes."""
    return {swe.degnorm(lon + aspect), swe.degnorm(lon - aspect)}
