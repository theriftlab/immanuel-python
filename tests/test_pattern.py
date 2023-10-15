"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Test various birth charts with known chart shapes.
    Celebrity natal chart data & chart shapes courtesy of
    https://horoscopes.astro-seek.com

"""

from datetime import datetime

from pytest import fixture

from immanuel.const import calc, chart
from immanuel.reports import pattern
from immanuel.tools import convert, date, ephemeris


@fixture
def object_indices():
    return (
        chart.SUN,
        chart.MOON,
        chart.MERCURY,
        chart.VENUS,
        chart.MARS,
        chart.JUPITER,
        chart.SATURN,
        chart.URANUS,
        chart.NEPTUNE,
        chart.PLUTO,
    )

@fixture
def birth_data():
    return {
        # Harrison Ford
        calc.BUNDLE: {
            'latitude': '41n51',
            'longitude': '87w39',
            'dob': '1942-07-13 11:41:00',
        },
        # Clint Eastwood
        calc.BUCKET: {
            'latitude': '37n47',
            'longitude': '122w25',
            'dob': '1930-05-31 17:35:00',
        },
        # Alfred Hitchcock
        calc.BOWL: {
            'latitude': '51n30',
            'longitude': '0w10',
            'dob': '1899-08-13 20:00:00',
        },
        # Isaac Newton
        calc.LOCOMOTIVE: {
            'latitude': '52n49',
            'longitude': '0w38',
            'dob': '1643-01-04 01:38:00',
        },
        # William Blake
        calc.SEESAW: {
            'latitude': '51n30',
            'longitude': '0w08',
            'dob': '1757-11-28 19:45:00',
        },
        # Carl Jung
        calc.SPLASH: {
            'latitude': '46n36',
            'longitude': '9e19',
            'dob': '1875-07-26 19:29:00',
        },
        # Random DOB to get a non-shape
        calc.SPLAY: {
            'latitude': '32n43',
            'longitude': '117w09',
            'dob': '1902-01-01 10:00:00',
        }
    }


def test_chart_shape(object_indices, birth_data):
    for chart_shape, data in birth_data.items():
        lat, lon = (convert.string_to_dec(v) for v in (data['latitude'], data['longitude']))
        dob_dt = date.localize(datetime.fromisoformat(data['dob']), lat, lon)
        jd = date.to_jd(dob_dt)
        objects = ephemeris.objects(object_indices, jd, lat, lon, chart.PLACIDUS)
        assert pattern.chart_shape(objects) == chart_shape
