"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Test dates compared against astro.com output.
    For solar return dates calculation, astro.com
    appears to have a wider margin of error. For
    progressions, astro.com tends to be a one or
    two arc-seconds ahead so we use approx() on
    the decimal conversion.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import approx, fixture

from immanuel.const import calc, chart
from immanuel.tools import convert, date, eph, forecast, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def pjd():
    # Input JD for all progression tests - must be in UT
    return date.to_jd(datetime(2025, 6, 21, tzinfo=ZoneInfo('UTC')))

@fixture
def astro():
    return {
        calc.DAILY_HOUSES: {
            chart.HOUSE1: {
                'sign': chart.VIRGO,
                'lon': '27°46\'45"',
            },
            chart.HOUSE2: {
                'sign': chart.LIBRA,
                'lon': '25°02\'08"',
            },
            chart.HOUSE3: {
                'sign': chart.SCORPIO,
                'lon': '25°26\'36"',
            },
            chart.HOUSE4: {
                'sign': chart.SAGITTARIUS,
                'lon': '27°36\'35"',
            },
            chart.HOUSE5: {
                'sign': chart.CAPRICORN,
                'lon': '29°46\'45"',
            },
            chart.HOUSE6: {
                'sign': chart.PISCES,
                'lon': '00°16\'09"',
            },
            chart.HOUSE7: {
                'sign': chart.PISCES,
                'lon': '27°46\'45"',
            },
            chart.HOUSE8: {
                'sign': chart.ARIES,
                'lon': '25°02\'08"',
            },
            chart.HOUSE9: {
                'sign': chart.TAURUS,
                'lon': '25°26\'36"',
            },
            chart.HOUSE10: {
                'sign': chart.GEMINI,
                'lon': '27°36\'35"',
            },
            chart.HOUSE11: {
                'sign': chart.CANCER,
                'lon': '29°46\'45"',
            },
            chart.HOUSE12: {
                'sign': chart.VIRGO,
                'lon': '00°16\'09"',
            },
        },
        calc.NAIBOD: {
            chart.HOUSE1: {
                'sign': chart.ARIES,
                'lon': '13°00\'29"',
            },
            chart.HOUSE2: {
                'sign': chart.TAURUS,
                'lon': '18°52\'16"',
            },
            chart.HOUSE3: {
                'sign': chart.GEMINI,
                'lon': '15°06\'02"',
            },
            chart.HOUSE4: {
                'sign': chart.CANCER,
                'lon': '07°57\'07"',
            },
            chart.HOUSE5: {
                'sign': chart.LEO,
                'lon': '01°57\'46"',
            },
            chart.HOUSE6: {
                'sign': chart.VIRGO,
                'lon': '01°58\'56"',
            },
            chart.HOUSE7: {
                'sign': chart.LIBRA,
                'lon': '13°00\'29"',
            },
            chart.HOUSE8: {
                'sign': chart.SCORPIO,
                'lon': '18°52\'16"',
            },
            chart.HOUSE9: {
                'sign': chart.SAGITTARIUS,
                'lon': '15°06\'02"',
            },
            chart.HOUSE10: {
                'sign': chart.CAPRICORN,
                'lon': '07°57\'07"',
            },
            chart.HOUSE11: {
                'sign': chart.AQUARIUS,
                'lon': '01°57\'46"',
            },
            chart.HOUSE12: {
                'sign': chart.PISCES,
                'lon': '01°58\'56"',
            },
        },
        calc.SOLAR_ARC: {
            chart.HOUSE1: {
                'sign': chart.ARIES,
                'lon': '17°32\'46"',
            },
            chart.HOUSE2: {
                'sign': chart.TAURUS,
                'lon': '22°20\'26"',
            },
            chart.HOUSE3: {
                'sign': chart.GEMINI,
                'lon': '18°01\'02"',
            },
            chart.HOUSE4: {
                'sign': chart.CANCER,
                'lon': '10°46\'59"',
            },
            chart.HOUSE5: {
                'sign': chart.LEO,
                'lon': '05°07\'03"',
            },
            chart.HOUSE6: {
                'sign': chart.VIRGO,
                'lon': '05°53\'34"',
            },
            chart.HOUSE7: {
                'sign': chart.LIBRA,
                'lon': '17°32\'46"',
            },
            chart.HOUSE8: {
                'sign': chart.SCORPIO,
                'lon': '22°20\'26"',
            },
            chart.HOUSE9: {
                'sign': chart.SAGITTARIUS,
                'lon': '18°01\'02"',
            },
            chart.HOUSE10: {
                'sign': chart.CAPRICORN,
                'lon': '10°46\'59"',
            },
            chart.HOUSE11: {
                'sign': chart.AQUARIUS,
                'lon': '05°07\'03"',
            },
            chart.HOUSE12: {
                'sign': chart.PISCES,
                'lon': '05°53\'34"',
            },
        },
    }


def test_solar_return_lon(jd):
    sr_jd = forecast.solar_return(jd, 2030)
    natal_sun = eph.planet(chart.SUN, jd)
    sr_sun = eph.planet(chart.SUN, sr_jd)
    assert natal_sun['lon'] == approx(sr_sun['lon'])


def test_solar_return_date(jd, coords):
    """ Solar return date copied from astro.com """
    sr_jd = forecast.solar_return(jd, 2030)
    astro_jd = date.to_jd(date.localize(datetime.fromisoformat('2029-12-31 16:30:16'), *coords))
    assert sr_jd == approx(astro_jd)


def test_progression_date(jd, pjd, coords):
    """ Progressed date copied from astro.com which returns UT date.
    Since the progressed date is always the same whatever method we
    use to calculate the houses, we can use any available method
    for this test. """
    progressed_dt = date.from_jd(forecast.progression(jd, *coords, pjd, chart.PLACIDUS, calc.NAIBOD)[forecast.JD])
    astro_dt = datetime(2000, 1, 27, 5, 14, 57, tzinfo=ZoneInfo('UTC'))
    assert progressed_dt.year == astro_dt.year
    assert progressed_dt.month == astro_dt.month
    assert progressed_dt.day == astro_dt.day
    assert progressed_dt.hour == astro_dt.hour
    assert progressed_dt.minute == astro_dt.minute
    assert progressed_dt.second == astro_dt.second


def test_progression(jd, pjd, coords, astro):
    """ Test all available types of house progression. """
    for method, results in astro.items():
        progressed_jd, progressed_armc = forecast.progression(jd, *coords, pjd, chart.PLACIDUS, method)

        for index, data in results.items():
            house = eph.armc_house(index, progressed_armc, coords[0], eph.obliquity(progressed_jd), chart.PLACIDUS)
            sign, lon = position.signlon(house['lon'])
            assert sign == data['sign']
            assert convert.to_string(lon) == data['lon']
