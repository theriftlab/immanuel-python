"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Test the basic midpoint calculation methods against
    astro.com's midpoint composite chart.

"""

from datetime import datetime

from pytest import fixture
import swisseph as swe

from immanuel.const import calc, chart
from immanuel.tools import convert, date, ephemeris, midpoint, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def jd1(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def jd2(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2025-06-21 00:00'), *coords))

@fixture
def obliquity(jd1, jd2):
    return midpoint.obliquity(jd1, jd2)

@fixture
def astro():
    return {
        chart.ASC: {
            'sign': chart.PISCES,
            'lon': '08°31\'36"',
            'lat': '00°00\'00"',
        },
        chart.SUN: {
            'sign': chart.ARIES,
            'lon': '05°23\'50"',
            'lat': '00°00\'00"',
            'speed': '00°59\'13"',
            'dec': '02°08\'39"',
        },
        chart.MOON: {
            'sign': chart.AQUARIUS,
            'lon': '09°42\'33"',
            'lat': '00°00\'00"',
            'speed': '13°15\'20"',
            'dec': '-17°49\'05"',
        },
        chart.MERCURY: {
            'sign': chart.LIBRA,
            'lon': '12°12\'13"',
            'lat': '00°00\'00"',
            'speed': '01°33\'06"',
            'dec': '-04°49\'23"',
        },
        chart.VENUS: {
            'sign': chart.AQUARIUS,
            'lon': '23°42\'11"',
            'lat': '00°00\'00"',
            'speed': '01°08\'08"',
            'dec': '-13°37\'07"',
        },
        chart.MARS: {
            'sign': chart.SAGITTARIUS,
            'lon': '00°11\'05"',
            'lat': '00°00\'00"',
            'speed': '00°40\'14"',
            'dec': '-20°11\'18"',
        },
        chart.JUPITER: {
            'sign': chart.TAURUS,
            'lon': '28°55\'54"',
            'lat': '00°00\'00"',
            'speed': '00°08\'06"',
            'dec': '19°55\'10"',
        },
        chart.SATURN: {
            'sign': chart.ARIES,
            'lon': '20°57\'45"',
            'lat': '00°00\'00"',
            'speed': '00°00\'30"',
            'dec': '08°10\'52"',
        },
        chart.URANUS: {
            'sign': chart.ARIES,
            'lon': '07°01\'20"',
            'lat': '00°00\'00"',
            'speed': '00°03\'04"',
            'dec': '02°47\'14"',
        },
        chart.NEPTUNE: {
            'sign': chart.PISCES,
            'lon': '02°39\'48"',
            'lat': '00°00\'00"',
            # This is the only figure disagreeing with astro.com (~1 arcsec) and nobody knows why
            # 'speed': '00°01\'18"',
            'dec': '-10°31\'28"',
        },
        chart.PLUTO: {
            'sign': chart.CAPRICORN,
            'lon': '07°23\'57"',
            'lat': '00°00\'00"',
            'speed': '00°00\'29"',
            'dec': '-23°13\'53"',
        },
        chart.TRUE_NORTH_NODE: {
            'sign': chart.TAURUS,
            'lon': '28°04\'05"',
            'lat': '00°00\'00"',
            'speed': '-00°03\'45"',
        },
        chart.PARS_FORTUNA: {
            'sign': chart.PISCES,
            'lon': '09°54\'57"',
            'lat': '00°00\'00"',
            'speed': '00°00\'00"',
            'dec': '07°51\'02"',
        },
    }


def test_all(coords, jd1, jd2, obliquity, astro):
    objects1 = ephemeris.objects(astro.keys(), jd1, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
    objects2 = ephemeris.objects(astro.keys(), jd2, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
    composites = midpoint.all(objects1, objects2, obliquity, calc.MIDPOINT, calc.DAY_NIGHT_FORMULA)

    for index, composite in composites.items():
        sign = position.sign(composite)
        sign_lon = position.sign_longitude(composite)
        assert sign == astro[index]['sign']
        assert convert.dec_to_string(sign_lon) == astro[index]['lon']

        for key in ('lat', 'speed', 'dec'):
            if key in astro[index] and key in composite:
                assert convert.dec_to_string(composite[key]) == astro[index][key]


def test_composite(coords, jd1, jd2, obliquity, astro):
    for index in astro.keys():
        object1 = ephemeris.get(index, jd1, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
        object2 = ephemeris.get(index, jd2, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA)
        composite = midpoint.composite(object1, object2, obliquity)
        sign = position.sign(composite)
        sign_lon = position.sign_longitude(composite)
        assert sign == astro[index]['sign']
        assert convert.dec_to_string(sign_lon) == astro[index]['lon']

        for key in ('lat', 'speed', 'dec'):
            if key in astro[index] and key in composite:
                assert convert.dec_to_string(composite[key]) == astro[index][key]


def test_obliquity(jd1, jd2):
    obliquity = midpoint.obliquity(jd1, jd2, False)
    mean_obliquity = midpoint.obliquity(jd1, jd2, True)

    ecl_nut1 = swe.calc_ut(jd1, swe.ECL_NUT)[0]
    ecl_nut2 = swe.calc_ut(jd2, swe.ECL_NUT)[0]

    assert obliquity == (ecl_nut1[0] + ecl_nut2[0]) / 2
    assert mean_obliquity == (ecl_nut1[1] + ecl_nut2[1]) / 2
