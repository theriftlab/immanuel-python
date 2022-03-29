"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Extracts chart-shape and aspect patterns from a dict of chart items
    provided by the eph module.

"""

import swisseph as swe

from immanuel import options
from immanuel.const import chart, calc


def chart_shape(items: dict) -> int:
    longitudes = sorted([v['lon'] for k, v in items[chart.PLANETS].items() if k in chart.MAIN_PLANETS])
    gaps = [swe.difdegn(_next(longitudes, k), v) for k, v in enumerate(longitudes)]
    max_gap = max(gaps)

    # All planets within 120º can only be a bundle
    if max_gap >= 240-options.chart_shape_orb:
        return calc.BUNDLE

    # Bucket handle planet(s) must be at least 90º from edges of main cluster
    for k, v in enumerate(gaps):
        next = _next(gaps, k)
        second_next = _next(gaps, k, 2)

        if v >= 90-options.chart_shape_orb and (next >= 90-options.chart_shape_orb or (next <= options.chart_shape_orb and second_next >= 90-options.chart_shape_orb)):
            return calc.BUCKET

    # All planets being within 180º with no bucket handle means a bowl
    if max_gap >= 180-options.chart_shape_orb:
        return calc.BOWL

    # All planets being within 240º with no bucket handle means a bowl
    if max_gap >= 120-options.chart_shape_orb:
        return calc.LOCOMOTIVE

    gaps.sort()

    # Only two gaps of at least 60º mean a seesaw
    if (len([v for v in gaps if v >= 60-options.chart_shape_orb]) == 2):
        return calc.SEESAW

    # Three gaps of at least 30º mean a splay
    if (len([v for v in gaps if v >= 30-options.chart_shape_orb]) == 3):
        return calc.SPLAY

    # Default to no particular patten
    return calc.SPLASH


def _next(data: list, key: int, step: int = 1) -> float:
    return data[(key+step)%(len(data))]
