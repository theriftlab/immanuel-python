"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Tests the main chart classes. Most of the underlying functionality
    comes from the submodules which have their own tests, so this file
    focuses on testing that the classes are working with and returning
    the correct charts, rather than re-testing the minutiae of each of
    their data. If all spot-checks for a given chart return true, then
    we can safely assume we are looking at the correct chart and trust
    that the rest of the underlying data is correct based on the tests
    for the submodules.

"""


from pytest import fixture

from immanuel import charts
from immanuel.const import calc, chart, names
from immanuel.setup import settings


@fixture
def dob():
    return '2000-01-01 10:00:00'

@fixture
def lat():
    return '32N43.0'

@fixture
def lon():
    return '117W9.0'


def test_natal(dob, lat, lon):
    natal_chart = charts.Natal(dob, lat, lon)

    # Birth date tested against astro.com's JD
    assert round(natal_chart.natal_date.julian + natal_chart.natal_date.deltat, 6) == 2451545.250739
    assert natal_chart.natal_date.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert natal_chart.coords.lat_formatted == lat
    assert natal_chart.coords.lon_formatted == lon

    # Default house system
    assert natal_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    # Chart shape
    assert natal_chart.shape == names.CHART_SHAPES[calc.BOWL]

    # Daytime chart
    assert natal_chart.diurnal == True

    # Moon phase
    assert natal_chart.moon_phase.third_quarter == True

    # Spot-check for correct object positions against astro.com
    assert natal_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert natal_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.CAPRICORN]
    assert natal_chart.objects[chart.SUN].sign_longitude.formatted == '10°37\'26"'

    assert natal_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert natal_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SCORPIO]
    assert natal_chart.objects[chart.MOON].sign_longitude.formatted == '16°19\'29"'

    assert natal_chart.objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert natal_chart.objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.CAPRICORN]
    assert natal_chart.objects[chart.PARS_FORTUNA].sign_longitude.formatted == '11°18\'41"'

    # Spot-check for correct object data against astro.com & Astro Gold
    assert natal_chart.objects[chart.SATURN].movement.retrograde == True
    assert natal_chart.objects[chart.MARS].dignities.peregrine == True
    assert natal_chart.objects[chart.MARS].score == -5

    # Spot-check for correct angle positions against astro.com
    assert natal_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert natal_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.PISCES]
    assert natal_chart.objects[chart.ASC].sign_longitude.formatted == '05°36\'38"'

    assert natal_chart.objects[chart.MC].name == names.ANGLES[chart.MC]
    assert natal_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert natal_chart.objects[chart.MC].sign_longitude.formatted == '14°50\'44"'

    # Spot-check for correct 2nd house position against astro.com
    assert natal_chart.houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert natal_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.ARIES]
    assert natal_chart.houses[chart.HOUSE2].sign_longitude.formatted == '17°59\'40"'

    # Spot-check for correct aspects against astro.com
    assert chart.SUN in natal_chart.aspects
    assert chart.MOON in natal_chart.aspects[chart.SUN]
    assert natal_chart.aspects[chart.SUN][chart.MOON].aspect == calc.SEXTILE

    assert chart.MOON in natal_chart.aspects
    assert chart.SATURN in natal_chart.aspects[chart.MOON]
    assert natal_chart.aspects[chart.MOON][chart.SATURN].aspect == calc.OPPOSITION

    # Spot-check for correct weightings against astro.com
    assert chart.JUPITER in natal_chart.weightings['elements'].fire
    assert chart.JUPITER in natal_chart.weightings['modalities'].cardinal
    assert chart.JUPITER in natal_chart.weightings['quadrants'].first
