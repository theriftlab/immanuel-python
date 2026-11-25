"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Transits, eclipses, moon phases, etc. are calculated in this module. The transit
searches began very simple and are as complex as they are now due to a lot of
edge cases which arose during testing with certain points.

"""

import bisect
import math
from collections.abc import Iterator

import swisseph as swe

from immanuel.const import calc, chart, motions
from immanuel.tools import position, sweph

PREVIOUS = -1
NEXT = 1

INGRESS = 1
EGRESS = 2

_MIN_STEP = 0.01  # Minimum degrees for transit search steps

_DAY_MINUTES = 1440  # Number of minutes in a day

_SPEED_DELTA = 0.05  # 5% of a Julian day = 72 mins

_SPEED_DELTAS = {
    chart.TRUE_LILITH: 0.02,  # True Lilith's speed changes way too quickly at stations
}

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


def can_aspect(index1: int, index2: int, aspect: float) -> bool:
    """Returns whether or not two moving chart objects can ever form
    the passed aspect."""
    if index1 == index2:
        return False
    max_separation = motions.MAX_SEPARATIONS.get(frozenset((index1, index2)))
    if max_separation is None:
        return True
    centre, half_width = max_separation
    targets = _aspect_targets(calc.CONJUNCTION, aspect)
    return any(abs(swe.difdeg2n(target, centre)) < half_width for target in targets)


def previous_retrograde_station(
    index: int, jd: float, limit: float | None = None
) -> float:
    """Returns the Julian date of the passed planet's previous station before
    turning retrograde."""
    return _station_search(index, jd, PREVIOUS, motions.RETROGRADE, limit)


def next_retrograde_station(index: int, jd: float, limit: float | None = None) -> float:
    """Returns the Julian date of the passed planet's next station before
    turning retrograde."""
    return _station_search(index, jd, NEXT, motions.RETROGRADE, limit)


def previous_direct_station(index: int, jd: float, limit: float | None = None) -> float:
    """Returns the Julian date of the passed planet's previous station before
    turning direct."""
    return _station_search(index, jd, PREVIOUS, motions.DIRECT, limit)


def next_direct_station(index: int, jd: float, limit: float | None = None) -> float:
    """Returns the Julian date of the passed planet's next station before
    turning direct."""
    return _station_search(index, jd, NEXT, motions.DIRECT, limit)


def can_station(index: int) -> bool:
    """Returns whether the given chart object can station. More accurately,
    whether it is an object this module can calculate stations for."""
    return index in motions.MAX_ACCELERATIONS


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
    between two planets. Raises ValueError if they can never form it."""
    if not can_aspect(index1, index2, aspect):
        raise ValueError(
            f"Impossible aspect {aspect} for chart objects {index1} and {index2}."
        )
    targets = _aspect_targets(calc.CONJUNCTION, aspect)
    return next(_crossings(index1, targets, jd, direction, NEXT, index2, limit))[0]


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
    return next(_crossings(index, targets, jd, direction, NEXT, limit=limit))[0]


def _sign_ingress_egress_search(
    index: int,
    sign: int,
    jd: float,
    direction: int,
    type: int,
    limit: float | None,
) -> float:
    """Returns the Julian date of the previous or next ingress into or egress
    out of the given sign. If the first crossing puts the planet in the wrong
    state, it continues the search to return the correct one."""
    sign_boundaries = {swe.degnorm((sign - 1) * 30.0), swe.degnorm(sign * 30.0)}
    crossings = _crossings(
        index, sign_boundaries, jd, direction, direction, limit=limit
    )
    jd, lon, _ = next(crossings)
    in_sign = position.sign(lon) == sign
    in_ingress = type == INGRESS
    if in_sign != in_ingress:
        jd = next(crossings)[0]
    return jd


def _station_search(
    index: int,
    jd: float,
    direction: int,
    movement: int,
    limit: float | None,
) -> float:
    """Returns the Julian date of the previous or next station before the
    passed planet turns retrograde or direct. If the first station found turns
    the wrong way, it continues the search to return the correct one."""
    if not can_station(index):
        raise ValueError(f"Chart object {index} never stations.")
    stations = _stations(index, jd, direction, limit)
    station_jd, _, station_movement = next(stations)
    if station_movement != movement:
        station_jd = next(stations)[0]
    return station_jd


def _crossings(
    index1: int,
    targets: set,
    jd: float,
    direction: int,
    side: int,
    index2: int | None = None,
    limit: float | None = None,
) -> Iterator[tuple]:
    """Yields the Julian date, longitude, and target of every crossing of any of
    the target longitudes by the passed planet, in the given direction and in
    the order they happen. If a second planet is also passed, the first planet's
    longitude is measured relative to it. NotFoundError is raised if the search
    goes beyond the limit arg (if passed) or the end of the available ephemeris'
    supported date range."""

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

    def crossed_targets(from_lon: float, to_lon: float) -> list:
        """Returns the targets crossed in an arc between from_lon
        and to_lon, in the order they were crossed, using simple target
        list bisections."""
        # Ensure we're always searching forwards even if the arc went backwards
        if swe.difdeg2n(to_lon, from_lon) < 0:
            return crossed_targets(to_lon, from_lon)[::-1]
        # Find the indices of the start and end targets
        start = bisect.bisect_right(sorted_targets, from_lon)
        end = bisect.bisect_left(sorted_targets, to_lon)
        # Wrap our list if the current arc crosses 0°
        if from_lon - to_lon > 180:
            return sorted_targets[start:] + sorted_targets[:end]
        return sorted_targets[start:end]

    def crossing_point(target: float, start: tuple, end: tuple) -> tuple:
        """Returns the Julian date and longitude at the point between the
        start and end samples where the passed target was crossed. The result
        is ensured to be within calc.MAX_ERROR and on the required side
        of the target."""
        (start_jd, start_lon), (end_jd, end_lon) = start, end
        offset = swe.difdeg2n(end_lon, target)
        # Here we aim to overshoot the target by a tiny fraction to ensure
        # we end up on the correct side of it
        overshoot_sign = math.copysign(1, side * direction * offset)
        start_overshoot = overshoot_sign * swe.difdeg2n(start_lon, target)
        end_overshoot = overshoot_sign * offset
        # If a target is the same as the previous one crossed in this step
        # then we're already good to go
        if start_overshoot > 0 and end_overshoot > 0:
            return start
        # Key the date bracket's ends by which one is already overshooting
        bracket = {
            start_overshoot > 0: (start_jd, start_overshoot, start_lon),
            end_overshoot > 0: (end_jd, end_overshoot, end_lon),
        }
        # Keep interpolating until our sample only overshoots by <= calc.MAX_ERROR
        target_overshoot = calc.MAX_ERROR / 2
        previous_side = None
        repeated_side = False
        while bracket[True][1] > calc.MAX_ERROR:
            before_jd, before_overshoot, _ = bracket[False]
            after_jd, after_overshoot, _ = bracket[True]
            step = after_jd - before_jd
            if repeated_side:
                # In rare cases such as a Moon / True Lilith conjunction, we can
                # end up with 2 samples on the same side of the target, so we
                # simply halve the bracket here
                middle_jd = before_jd + step / 2
            else:
                # Step towards target_overshoot
                overshoot_range = after_overshoot - before_overshoot
                step_fraction = (target_overshoot - before_overshoot) / overshoot_range
                middle_jd = before_jd + step * step_fraction
            # Noisy ephemeris data can produce date differences too small to
            # work with, so here we check if either side rounds to the current
            # middle_jd and exit if there's a match
            if middle_jd in (before_jd, after_jd):
                break
            # Resample at the new middle_jd
            lon = sample(middle_jd)[0]
            overshoot = overshoot_sign * swe.difdeg2n(lon, target)
            bracket[overshoot > 0] = (middle_jd, overshoot, lon)
            current_side = overshoot > 0
            repeated_side = current_side == previous_side
            previous_side = current_side
        crossing_jd, _, crossing_lon = bracket[True]
        return crossing_jd, crossing_lon

    # Ensure we're starting ahead of any passed limit value
    if limit is not None and (limit - jd) * direction <= 0:
        raise ValueError(f"Limit date {limit} should be ahead of the start date.")
    sorted_targets = sorted(targets)
    max_speed = sum(
        # Default to the moon since this is usually the fastest
        motions.MAX_MOTIONS.get(index, motions.MAX_MOTIONS[chart.MOON])
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
            if distance < _MIN_STEP and (speed > 0) != (prev_speed > 0):
                step = jd - prev_jd
                step_fraction = prev_speed / (prev_speed - speed)
                station_jd = prev_jd + step * step_fraction
                station_lon, station_speed = sample(station_jd)
                if crossed_targets(from_lon, station_lon):
                    jd, lon, speed = station_jd, station_lon, station_speed
            # Refine all of our crossed targets
            start = prev_jd, prev_lon
            for target in crossed_targets(from_lon, lon):
                end = jd, lon
                crossing_jd, crossing_lon = crossing_point(target, start, end)
                # Our overshoot target means that a crossing right at the
                # limit can settle a fraction beyond it
                if limit is not None and (crossing_jd - limit) * direction > 0:
                    raise NotFoundError(f"No transit found before limit date {limit}.")
                yield crossing_jd, crossing_lon, target
                start = crossing_jd, crossing_lon
            from_lon = lon
    except swe.Error as error:
        raise NotFoundError(
            "No transit found before the end of the available ephemeris."
        ) from error


def _stations(
    index: int,
    jd: float,
    direction: int,
    limit: float | None = None,
) -> Iterator[tuple]:
    """Yields the Julian date, longitude, and movement of every station of the
    passed planet, in the given direction and in the order they happen.
    NotFoundError is raised if the search goes beyond the limit arg (if passed)
    or the end of the available ephemeris' supported date range."""

    def sample(minute: int) -> float:
        """Returns the approximate speed of the planet at the given Julian
        whole minute, calculated from the difference between two longitudes
        taken a fraction before and after the given date."""
        minute_jd = minute / _DAY_MINUTES
        before_lon = sweph.longitude(index, minute_jd - speed_delta, deflection=False)[0]
        after_lon = sweph.longitude(index, minute_jd + speed_delta, deflection=False)[0]
        return swe.difdeg2n(after_lon, before_lon) / (2 * speed_delta)

    def station_point(start: tuple, end: tuple) -> tuple:
        """Returns the moment between the start and end samples when the
        planet stations, and the direction it turns. This function always works
        forward in time (earlier -> later) regardless of the search direction.
        This guarantees previous and next searches will always agree."""
        (start_minute, start_speed), (end_minute, end_speed) = sorted((start, end))
        # If the gap is larger than a minute, we need to bisect - this shouldn't
        # happen in normal usage but in some edge cases where the ephemeris
        # internally switches data sources, it can happen
        while end_minute - start_minute > 1:
            middle_minute = (end_minute + start_minute) // 2
            middle_speed = sample(middle_minute)
            if (middle_speed > 0) != (start_speed > 0):
                end_minute, end_speed = middle_minute, middle_speed
            else:
                start_minute, start_speed = middle_minute, middle_speed
        # Since we're dealing with a tiny interval, we interpolate
        minute_fraction = start_speed / (start_speed - end_speed)
        station_jd = (start_minute + minute_fraction) / _DAY_MINUTES
        movement = motions.DIRECT if end_speed > 0 else motions.RETROGRADE
        return station_jd, movement

    # Ensure we're starting ahead of any passed limit value
    if limit is not None and (limit - jd) * direction <= 0:
        raise ValueError(f"Limit date {limit} should be ahead of the start date.")
    # Round the start and limit dates to whole minutes
    if direction == NEXT:
        minute = math.floor(jd * _DAY_MINUTES)
        limit_minute = None if limit is None else math.ceil(limit * _DAY_MINUTES)
    else:
        minute = math.ceil(jd * _DAY_MINUTES)
        limit_minute = None if limit is None else math.floor(limit * _DAY_MINUTES)
    # Set up our motion values for step calculation
    max_acceleration = motions.MAX_ACCELERATIONS[index]
    max_motion_noise = motions.MAX_MOTION_NOISE.get(index, 0)
    speed_delta = _SPEED_DELTAS.get(index, _SPEED_DELTA)
    speed = sample(minute)
    try:
        while True:
            # Store our old values
            prev_minute, prev_speed = minute, speed
            # Update the current values
            safe_speed = abs(speed) - 2 * max_motion_noise
            step = math.floor(safe_speed / max_acceleration * _DAY_MINUTES)
            minute += direction * max(step, 1)
            # If we have gone past the passed limit, we didn't find anything
            if limit_minute is not None and (minute - limit_minute) * direction > 0:
                if prev_minute == limit_minute:
                    raise NotFoundError(f"No station found before limit date {limit}.")
                minute = limit_minute
            speed = sample(minute)
            # Check if a station has switched directions
            if (speed > 0) != (prev_speed > 0):
                station_jd, movement = station_point(
                    (prev_minute, prev_speed), (minute, speed)
                )
                # The first and last minutes searched might have a station
                # just short of the start, or just past the limit
                if (station_jd - jd) * direction <= 0:
                    continue
                if limit is not None and (station_jd - limit) * direction > 0:
                    raise NotFoundError(f"No station found before limit date {limit}.")
                # A valid station has been found, return its information
                station_lon = sweph.longitude(index, station_jd)[0]
                yield station_jd, station_lon, movement
    except swe.Error as error:
        raise NotFoundError(
            "No station found before the end of the available ephemeris."
        ) from error


def _aspect_targets(lon: float, aspect: float) -> set:
    """Returns the longitudes at which a planet makes the passed aspect to the
    passed longitude. Besides conjunctions and oppositions, there will be two
    target longitudes."""
    return {swe.degnorm(lon + aspect), swe.degnorm(lon - aspect)}
