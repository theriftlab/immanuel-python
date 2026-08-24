"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The Parts of Fortune, Spirit, and Eros are calculated here. This singular
function returns the part's ecliptic longitude only.

"""

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import condition, sweph


def longitude(
    index: int,
    jd: float,
    lat: float,
    lon: float | None,
    formula: int | None,
    armc: float | None = None,
    armc_obliquity: float | None = None,
) -> float:
    """Returns the ecliptic longitude of the passed part, calculated from
    either a Julian date or the passed ARMC."""
    sun = sweph.planet(chart.SUN, jd)
    moon = sweph.planet(chart.MOON, jd)
    if armc is not None and armc_obliquity is not None:
        asc = sweph.angle(
            chart.ASC,
            lat=lat,
            armc=armc,
            armc_obliquity=armc_obliquity,
            house_system=chart.PLACIDUS,
        )
    else:
        asc = sweph.angle(
            chart.ASC, jd=jd, lat=lat, lon=lon, house_system=chart.PLACIDUS
        )
    night = formula == calc.NIGHT_FORMULA or (
        formula == calc.DAY_NIGHT_FORMULA and not condition.is_daytime_from(sun, asc)
    )
    if index == chart.PART_OF_FORTUNE:
        part_lon = (
            asc["lon"] + sun["lon"] - moon["lon"]
            if night
            else asc["lon"] + moon["lon"] - sun["lon"]
        )
    elif index == chart.PART_OF_SPIRIT or index == chart.PART_OF_EROS:
        part_lon = (
            asc["lon"] + moon["lon"] - sun["lon"]
            if night
            else asc["lon"] + sun["lon"] - moon["lon"]
        )
        if index == chart.PART_OF_EROS:
            venus = sweph.planet(chart.VENUS, jd)
            part_lon = (
                asc["lon"] + part_lon - venus["lon"]
                if night
                else asc["lon"] + venus["lon"] - part_lon
            )
    else:
        raise ValueError("Invalid index.")
    return swe.degnorm(part_lon)
