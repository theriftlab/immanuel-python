"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module calculates solar returns and secondary progressions.

"""

import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import calculate, date, ephemeris


JD = 0
ARMC = 1


def solar_return(jd: float, year: int) -> float:
    """ Returns the Julian date of the given year's solar return. """
    dt = date.from_jd(jd)
    year_diff = year - dt.year
    sr_jd = jd + year_diff * calc.YEAR_DAYS
    natal_sun = ephemeris.planet(chart.SUN, jd)

    while True:
        sr_sun = ephemeris.planet(chart.SUN, sr_jd)
        distance = swe.difdeg2n(natal_sun['lon'], sr_sun['lon'])
        if abs(distance) <= calc.MAX_ERROR:
            break
        sr_jd += distance / sr_sun['speed']

    return sr_jd


def progression(jd: float, lat: float, lon: float, pjd: float, house_system: int, method: int) -> tuple:
    """ Returns the progressed Julian date and MC right ascension. """
    year_days = calculate.solar_year_length(jd)
    years = (pjd - jd) / year_days
    progressed_jd = jd + years

    match method:
        case calc.DAILY_HOUSES:
            progressed_armc_lon = ephemeris.angle(chart.ARMC, progressed_jd, lat, lon, house_system)['lon']
        case calc.NAIBOD:
            natal_armc = ephemeris.angle(chart.ARMC, jd, lat, lon, house_system)['lon']
            progressed_armc_lon = swe.degnorm(natal_armc + years * calc.MEAN_MOTIONS[chart.SUN])
        case calc.SOLAR_ARC:
            natal_mc = ephemeris.angle(chart.MC, jd, lat, lon, house_system)
            natal_sun = ephemeris.planet(chart.SUN, jd)
            progressed_sun = ephemeris.planet(chart.SUN, progressed_jd)
            distance = swe.difdeg2n(progressed_sun['lon'], natal_sun['lon'])
            obliquity = ephemeris.obliquity(progressed_jd)
            progressed_armc_lon = swe.cotrans((natal_mc['lon'] + distance, 0, 1), -obliquity)[0]

    return progressed_jd, progressed_armc_lon
