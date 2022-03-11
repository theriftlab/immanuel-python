from dateutil.relativedelta import relativedelta

import swisseph as swe

from immanuel import options
from immanuel.const import calc, chart
from immanuel.tools import convert, dates, eph
from immanuel.tools.dates import DateTime


def solar_return(jd: float, year: int) -> float:
    """ Returns the Julian date of the given year's solar return. """
    dt = dates.jd_to_datetime(jd)
    year_diff = year - dt.year
    sr_jd = jd + year_diff * calc.YEAR_DAYS
    natal_sun = eph.planet(jd, chart.SUN)

    while True:
        sr_sun = eph.planet(sr_jd, chart.SUN)
        distance = swe.difdeg2n(natal_sun['lon'], sr_sun['lon'])
        if abs(distance) <= calc.MAX_ERROR:
            break
        sr_jd += distance / sr_sun['speed']

    return sr_jd


def progression(jd: float, lat: float, lon: float, pjd: float, plat = None, plon = None):
    """ Returns the progressed Julian date and MC right ascension. """
    plat, plon = (convert.string_to_dec(v) for v in (plat, plon)) if plat and plon else (lat, lon)
    dt = DateTime(jd, lat, lon)
    days = (pjd - jd) / calc.YEAR_DAYS
    progressed_jd = dates.datetime_to_jd(dt.datetime + relativedelta(days=days))

    match options.mc_progression:
        case calc.DAILY_HOUSES:
            progressed_armc = eph.angle(progressed_jd, plat, plon, chart.ARMC)['lon']
        case calc.NAIBOD:
            natal_armc = eph.angle(jd, lat, lon, chart.ARMC)
            progressed_armc = natal_armc['lon'] + days * calc.SUN_MEAN_MOTION
        case calc.SOLAR_ARC:
            natal_mc = eph.angle(jd, lat, lon, chart.MC)
            natal_sun = eph.planet(jd, chart.SUN)
            progressed_sun = eph.planet(progressed_jd, chart.SUN)
            distance = swe.difdeg2n(progressed_sun, natal_sun)
            obliquity = eph.obliquity(progressed_jd)
            progressed_armc = swe.cotrans((natal_mc['lon'] + distance, 0, 1), -obliquity)[0]

    return progressed_jd, progressed_armc
