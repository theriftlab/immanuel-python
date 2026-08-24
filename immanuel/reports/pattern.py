"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Extracts the chart-shape pattern from a dict of chart objects provided
by the sweph or ephemeris modules.

"""

import swisseph as swe

from immanuel.const import calc
from immanuel.settings import DEFAULTS, ChartConfig


def chart_shape(objects: dict, config: ChartConfig = DEFAULTS) -> int:
    """Returns which of the predetermined shapes the passed
    chart objects form."""
    # Filter & sort objects by longitude
    longitudes = sorted(
        [v["lon"] for k, v in objects.items() if k in config.chart_shape_objects]
    )
    # Default to splash if the chart is unfeasibly small
    if len(longitudes) <= 1:
        return calc.SPLASH
    # Calculate the gaps between consecutive longitudes
    gaps = [swe.difdegn(next, lon) for lon, next in _wrapped(longitudes)]
    max_gap = max(gaps)
    chart_shape_orb = config.chart_shape_orb
    # All planets within 120º can only be a bundle
    if max_gap >= 240 - chart_shape_orb:
        return calc.BUNDLE
    # For a bucket to form, the handle planet(s) must be at least 90º from the
    # edges of the main cluster. We allow up to two planets (conjunct within
    # chart_shape_orb) to form the handle - any more and this will be
    # classified as a seesaw.
    for gap, next, second_next in _wrapped(gaps, steps=2):
        if gap >= 90 - chart_shape_orb and (
            next >= 90 - chart_shape_orb
            or (next <= chart_shape_orb and second_next >= 90 - chart_shape_orb)
        ):
            return calc.BUCKET
    # All planets being within 180º with no bucket handle means a bowl
    if max_gap >= 180 - chart_shape_orb:
        return calc.BOWL
    # All planets being within 240º with no bucket handle means a locomotive
    if max_gap >= 120 - chart_shape_orb:
        return calc.LOCOMOTIVE
    # Only two gaps of at least 60º mean a seesaw
    if sum(gap >= 60 - chart_shape_orb for gap in gaps) == 2:
        return calc.SEESAW
    # Three gaps of at least 30º mean a splay
    if sum(gap >= 30 - chart_shape_orb for gap in gaps) == 3:
        return calc.SPLAY
    # Default to no particular pattern
    return calc.SPLASH


def _wrapped(data: list, steps: int = 1) -> zip:
    """Returns a zip with each entry containing the current and next "steps"
    entries of the passed list, wrapping back to the start if the indices fall
    off the end."""
    return zip(*[data[i:] + data[:i] for i in range(0, steps + 1)])
