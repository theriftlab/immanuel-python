"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module calculates dates for forecast methods such as
    solar returns and secondary progressions.

"""

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import date, eph


JD = 0
ARMC = 1


def solar_return(jd: float, year: int) -> float:
    """ Returns the Julian date of the given year's solar return. """
    dt = date.from_jd(jd)
    year_diff = year - dt.year
    sr_jd = jd + year_diff * calc.YEAR_DAYS
    natal_sun = eph.planet(chart.SUN, jd)

    while True:
        sr_sun = eph.planet(chart.SUN, sr_jd)
        distance = swe.difdeg2n(natal_sun['lon'], sr_sun['lon'])
        if abs(distance) <= calc.MAX_ERROR:
            break
        sr_jd += distance / sr_sun['speed']

    return sr_jd


def progression(jd: float, lat: float, lon: float, pjd: float, method: int) -> tuple:
    """ Returns the progressed Julian date and MC right ascension. """
    days = (pjd - jd) / calc.YEAR_DAYS
    progressed_jd = jd + days

    if method in (calc.DAILY_HOUSES, calc.NAIBOD):
        natal_armc = eph.angle(chart.ARMC, jd, lat, lon)
        multiplier = calc.SUN_MEAN_MOTION if method == calc.NAIBOD else natal_armc['speed']
        progressed_armc = swe.degnorm(natal_armc['lon'] + days * multiplier)
    elif method == calc.SOLAR_ARC:
        natal_mc = eph.angle(chart.MC, jd, lat, lon)
        natal_sun = eph.planet(chart.SUN, jd)
        progressed_sun = eph.planet(chart.SUN, progressed_jd)
        distance = swe.difdeg2n(progressed_sun['lon'], natal_sun['lon'])
        obliquity = eph.obliquity(jd)
        progressed_armc = swe.cotrans((natal_mc['lon'] + distance, 0, 1), -obliquity)[0]

    return progressed_jd, progressed_armc
