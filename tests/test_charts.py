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


from datetime import datetime
from zoneinfo import ZoneInfo

from pytest import fixture

from immanuel import charts
from immanuel.const import calc, chart, names
from immanuel.tools import date
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

@fixture
def solar_return_year():
    return 2030

@fixture
def pdt():
    # We compare against astro.com which assumes UTC for progressions date
    # so we knock 8 hours off midnight 2023-06-21 to account for PDT
    return '2025-06-20 17:00:00'


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


def test_solar_return(dob, lat, lon, solar_return_year):
    solar_return_chart = charts.SolarReturn(dob, lat, lon, solar_return_year)

    # Birth date tested against astro.com's JD
    assert round(solar_return_chart.natal_date.julian + solar_return_chart.natal_date.deltat, 6) == 2451545.250739
    assert solar_return_chart.natal_date.timezone == 'PST'

    # Solar return date tested against astro.com
    assert round(solar_return_chart.solar_return_date.julian + solar_return_chart.solar_return_date.deltat, 6) == 2462502.521823
    assert solar_return_chart.solar_return_date.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert solar_return_chart.coords.lat_formatted == lat
    assert solar_return_chart.coords.lon_formatted == lon

    # Default house system
    assert solar_return_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    # Chart shape
    assert solar_return_chart.shape == names.CHART_SHAPES[calc.LOCOMOTIVE]

    # Daytime chart
    assert solar_return_chart.diurnal == True

    # Moon phase
    assert solar_return_chart.moon_phase.balsamic == True

    # Spot-check for correct object positions against astro.com
    assert solar_return_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert solar_return_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.CAPRICORN]
    assert solar_return_chart.objects[chart.SUN].sign_longitude.formatted == '10°37\'26"'

    assert solar_return_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert solar_return_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SCORPIO]
    assert solar_return_chart.objects[chart.MOON].sign_longitude.formatted == '28°43\'43"'

    assert solar_return_chart.objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert solar_return_chart.objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.TAURUS]
    assert solar_return_chart.objects[chart.PARS_FORTUNA].sign_longitude.formatted == '24°41\'28"'

    # Spot-check for correct object data against astro.com & Astro Gold
    assert solar_return_chart.objects[chart.SATURN].movement.retrograde == True
    assert solar_return_chart.objects[chart.MARS].dignities.peregrine == True
    assert solar_return_chart.objects[chart.MARS].score == -5

    # Spot-check for correct angle positions against astro.com
    assert solar_return_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert solar_return_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.CANCER]
    assert solar_return_chart.objects[chart.ASC].sign_longitude.formatted == '06°35\'11"'

    assert solar_return_chart.objects[chart.MC].name == names.ANGLES[chart.MC]
    assert solar_return_chart.objects[chart.MC].sign.name == names.SIGNS[chart.PISCES]
    assert solar_return_chart.objects[chart.MC].sign_longitude.formatted == '20°21\'06"'

    # Spot-check for correct 2nd house position against astro.com
    assert solar_return_chart.houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert solar_return_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.CANCER]
    assert solar_return_chart.houses[chart.HOUSE2].sign_longitude.formatted == '28°17\'34"'

    # Spot-check for correct aspects against astro.com
    assert chart.SUN in solar_return_chart.aspects
    assert chart.SATURN in solar_return_chart.aspects[chart.SUN]
    assert solar_return_chart.aspects[chart.SUN][chart.SATURN].aspect == calc.TRINE

    assert chart.MOON in solar_return_chart.aspects
    assert chart.NEPTUNE in solar_return_chart.aspects[chart.MOON]
    assert solar_return_chart.aspects[chart.MOON][chart.NEPTUNE].aspect == calc.TRINE

    # Spot-check for correct weightings against astro.com
    assert chart.JUPITER in solar_return_chart.weightings['elements'].water
    assert chart.JUPITER in solar_return_chart.weightings['modalities'].fixed
    assert chart.JUPITER in solar_return_chart.weightings['quadrants'].second


def test_progressed(dob, lat, lon, pdt):
    settings.mc_progression = calc.NAIBOD
    progressed_chart = charts.Progressed(dob, lat, lon, pdt)

    # Birth date tested against astro.com's JD
    assert round(progressed_chart.natal_date.julian + progressed_chart.natal_date.deltat, 6) == 2451545.250739
    assert progressed_chart.natal_date.timezone == 'PST'

    # Progression date tested against astro.com
    assert progressed_chart.progression_date.timezone == 'PDT'
    pdt_utc = progressed_chart.progression_date.datetime.astimezone(ZoneInfo('UTC'))
    assert (pdt_utc.year, pdt_utc.month, pdt_utc.day, pdt_utc.hour) == (2025, 6, 21, 0)

    # Progressed date tested against astro.com
    assert round(progressed_chart.progressed_date.julian + progressed_chart.progressed_date.deltat, 6) == 2451570.719456
    assert progressed_chart.progressed_date.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert progressed_chart.coords.lat_formatted == lat
    assert progressed_chart.coords.lon_formatted == lon

    # Default house system
    assert progressed_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    # Chart shape
    assert progressed_chart.shape == names.CHART_SHAPES[calc.LOCOMOTIVE]

    # Daytime chart
    assert progressed_chart.diurnal == True

    # Moon phase
    assert progressed_chart.moon_phase.disseminating == True

    # Spot-check for correct object positions against astro.com
    assert progressed_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert progressed_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.AQUARIUS]
    assert progressed_chart.objects[chart.SUN].sign_longitude.formatted == '06°33\'41"'

    assert progressed_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert progressed_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.LIBRA]
    assert progressed_chart.objects[chart.MOON].sign_longitude.formatted == '23°50\'57"'

    assert progressed_chart.objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert progressed_chart.objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.CAPRICORN]
    assert progressed_chart.objects[chart.PARS_FORTUNA].sign_longitude.formatted == '00°17\'45"'

    # Spot-check for correct object data against astro.com & Astro Gold
    assert progressed_chart.objects[chart.SUN].dignities.detriment == True
    assert progressed_chart.objects[chart.SUN].dignities.peregrine == True
    assert progressed_chart.objects[chart.SUN].score == -10

    # Spot-check for correct angle positions against astro.com
    assert progressed_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert progressed_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.ARIES]
    assert progressed_chart.objects[chart.ASC].sign_longitude.formatted == '13°00\'29"'

    assert progressed_chart.objects[chart.MC].name == names.ANGLES[chart.MC]
    assert progressed_chart.objects[chart.MC].sign.name == names.SIGNS[chart.CAPRICORN]
    assert progressed_chart.objects[chart.MC].sign_longitude.formatted == '07°57\'07"'

    # Spot-check for correct 2nd house position against astro.com
    assert progressed_chart.houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert progressed_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.TAURUS]
    assert progressed_chart.houses[chart.HOUSE2].sign_longitude.formatted == '18°52\'16"'

    # Spot-check for correct aspects against astro.com
    assert chart.SUN in progressed_chart.aspects
    assert chart.SATURN in progressed_chart.aspects[chart.SUN]
    assert progressed_chart.aspects[chart.SUN][chart.SATURN].aspect == calc.SQUARE

    assert chart.MOON in progressed_chart.aspects
    assert chart.URANUS in progressed_chart.aspects[chart.MOON]
    assert progressed_chart.aspects[chart.MOON][chart.URANUS].aspect == calc.TRINE

    # Spot-check for correct weightings against astro.com
    assert chart.VENUS in progressed_chart.weightings['elements'].earth
    assert chart.VENUS in progressed_chart.weightings['modalities'].cardinal
    assert chart.VENUS in progressed_chart.weightings['quadrants'].third
