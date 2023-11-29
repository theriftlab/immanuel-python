"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Extracts chart-shape and aspect patterns from a dict of chart objects
    provided by the ephemeris module.

"""

import swisseph as swe

from immanuel.const import calc
from immanuel.setup import settings


def chart_shape(objects: dict) -> int:
    # Filter objects
    objects = { k: v for k, v in objects.items() if k in settings.chart_shape_objects }

    # Sort objects by longitude
    longitudes = sorted([v['lon'] for v in objects.values()])
    diffs = [swe.difdegn(_next(longitudes, k), v) for k, v in enumerate(longitudes)]
    max_diff = max(diffs)

    # All planets within 120º can only be a bundle
    if max_diff >= 240-settings.chart_shape_orb:
        return calc.BUNDLE

    # Bucket handle planet(s) must be at least 90º from edges of main cluster
    for k, v in enumerate(diffs):
        next = _next(diffs, k)
        second_next = _next(diffs, k, 2)

        if v >= 90-settings.chart_shape_orb and (next >= 90-settings.chart_shape_orb or (next <= settings.chart_shape_orb and second_next >= 90-settings.chart_shape_orb)):
            return calc.BUCKET

    # All planets being within 180º with no bucket handle means a bowl
    if max_diff >= 180-settings.chart_shape_orb:
        return calc.BOWL

    # All planets being within 240º with no bucket handle means a locomotive
    if max_diff >= 120-settings.chart_shape_orb:
        return calc.LOCOMOTIVE

    diffs.sort()

    # Only two gaps of at least 60º mean a seesaw
    if len([v for v in diffs if v >= 60-settings.chart_shape_orb]) == 2:
        return calc.SEESAW

    # Three gaps of at least 30º mean a splay
    if len([v for v in diffs if v >= 30-settings.chart_shape_orb]) == 3:
        return calc.SPLAY

    # Default to no particular pattern
    return calc.SPLASH


def _next(data: list, key: int, step: int = 1) -> float:
    return data[(key+step)%(len(data))]
