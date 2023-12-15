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
from immanuel.setup import settings
from immanuel.tools import convert


@fixture
def dob():
    return '2000-01-01 10:00'

@fixture
def partner_dob():
    return '2001-02-16 06:00'

@fixture
def lat():
    return '32N43.0'

@fixture
def partner_lat():
    return '38N35.0'

@fixture
def lon():
    return '117W9.0'

@fixture
def partner_lon():
    return '121W30.0'

@fixture
def native(dob, lat, lon):
    return charts.Subject(dob, lat, lon)

@fixture
def partner(partner_dob, partner_lat, partner_lon):
    return charts.Subject(partner_dob, partner_lat, partner_lon)

@fixture
def solar_return_year():
    return 2030

@fixture
def pdt():
    # We compare against astro.com which assumes UTC for progressions date
    # so we knock 8 hours off midnight 2023-06-21 to account for Pacific Time
    return '2025-06-20 17:00:00'


def test_subject(dob, lat, lon, native):
    date_time = datetime.fromisoformat(f'{dob} -08:00')
    latitude, longitude = (convert.string_to_dec(v) for v in (lat, lon))
    assert native.date_time.year == date_time.year
    assert native.date_time.month == date_time.month
    assert native.date_time.day == date_time.day
    assert native.date_time.hour == date_time.hour
    assert native.date_time.minute == date_time.minute
    assert native.date_time.second == date_time.second
    assert native.latitude == latitude
    assert native.longitude == longitude


def test_natal(native, lat, lon):
    natal_chart = charts.Natal(native)

    assert natal_chart.type == names.CHART_TYPES[chart.NATAL]

    assert round(natal_chart.native.date_time.julian + natal_chart.native.date_time.deltat, 6) == 2451545.250739
    assert natal_chart.native.date_time.timezone == 'PST'

    assert natal_chart.native.coordinates.latitude.formatted == lat
    assert natal_chart.native.coordinates.longitude.formatted == lon

    assert natal_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]
    assert natal_chart.shape == names.CHART_SHAPES[calc.BOWL]
    assert natal_chart.diurnal == True
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


def test_solar_return(native, lat, lon, solar_return_year):
    solar_return_chart = charts.SolarReturn(native, solar_return_year)

    assert solar_return_chart.type == names.CHART_TYPES[chart.SOLAR_RETURN]

    assert round(solar_return_chart.native.date_time.julian + solar_return_chart.native.date_time.deltat, 6) == 2451545.250739
    assert solar_return_chart.native.date_time.timezone == 'PST'

    assert round(solar_return_chart.solar_return_date_time.julian + solar_return_chart.solar_return_date_time.deltat, 6) == 2462502.521823
    assert solar_return_chart.solar_return_date_time.timezone == 'PST'

    assert solar_return_chart.native.coordinates.latitude.formatted == lat
    assert solar_return_chart.native.coordinates.longitude.formatted == lon

    assert solar_return_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]
    assert solar_return_chart.shape == names.CHART_SHAPES[calc.LOCOMOTIVE]
    assert solar_return_chart.diurnal == True
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


def test_progressed(native, lat, lon, pdt):
    settings.mc_progression_method = calc.NAIBOD
    progressed_chart = charts.Progressed(native, pdt)

    assert progressed_chart.type == names.CHART_TYPES[chart.PROGRESSED]
    assert progressed_chart.progression_method == names.PROGRESSION_METHODS[settings.mc_progression_method]

    assert round(progressed_chart.native.date_time.julian + progressed_chart.native.date_time.deltat, 6) == 2451545.250739
    assert progressed_chart.native.date_time.timezone == 'PST'

    assert progressed_chart.progression_date_time.timezone == 'PDT'
    pdt_utc = progressed_chart.progression_date_time.datetime.astimezone(ZoneInfo('UTC'))
    assert (pdt_utc.year, pdt_utc.month, pdt_utc.day, pdt_utc.hour) == (2025, 6, 21, 0)

    # Progressed date tested against astro.com
    assert round(progressed_chart.progressed_date_time.julian + progressed_chart.progressed_date_time.deltat, 6) == 2451570.719456
    assert progressed_chart.progressed_date_time.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert progressed_chart.native.coordinates.latitude.formatted == lat
    assert progressed_chart.native.coordinates.longitude.formatted == lon

    assert progressed_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]
    assert progressed_chart.shape == names.CHART_SHAPES[calc.LOCOMOTIVE]
    assert progressed_chart.diurnal == True
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

    # Spot-check for correct object data against Astro Gold
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


def test_composite(native, lat, lon, partner, partner_lat, partner_lon):
    composite_chart = charts.Composite(native, partner)

    assert composite_chart.type == names.CHART_TYPES[chart.COMPOSITE]

    assert round(composite_chart.native.date_time.julian + composite_chart.native.date_time.deltat, 6) == 2451545.250739
    assert composite_chart.native.date_time.timezone == 'PST'

    assert round(composite_chart.partner.date_time.julian + composite_chart.partner.date_time.deltat, 6) == 2451957.084075
    assert composite_chart.partner.date_time.timezone == 'PST'

    assert composite_chart.native.coordinates.latitude.formatted == lat
    assert composite_chart.native.coordinates.longitude.formatted == lon

    assert composite_chart.partner.coordinates.latitude.formatted == partner_lat
    assert composite_chart.partner.coordinates.longitude.formatted == partner_lon

    assert composite_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]
    assert composite_chart.diurnal == True
    assert composite_chart.moon_phase.third_quarter == True

    # Spot-check for correct object positions against astro.com
    assert composite_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert composite_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.SUN].sign_longitude.formatted == '04°17\'35"'

    assert composite_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert composite_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MOON].sign_longitude.formatted == '00°22\'35"'

    assert composite_chart.objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert composite_chart.objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.PISCES]
    assert composite_chart.objects[chart.PARS_FORTUNA].sign_longitude.formatted == '01°03\'58"'

    # Spot-check for correct object data against Astro Gold
    assert composite_chart.objects[chart.SUN].dignities.detriment == True
    assert composite_chart.objects[chart.SUN].dignities.peregrine == True
    assert composite_chart.objects[chart.SUN].score == -10

    # Spot-check for correct angle positions against astro.com
    assert composite_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert composite_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.ASC].sign_longitude.formatted == '21°26\'55"'

    assert composite_chart.objects[chart.MC].name == names.ANGLES[chart.MC]
    assert composite_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MC].sign_longitude.formatted == '06°07\'28"'

    # Spot-check for correct 2nd house position against astro.com
    assert composite_chart.houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert composite_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.ARIES]
    assert composite_chart.houses[chart.HOUSE2].sign_longitude.formatted == '05°32\'57"'

    # Spot-check for correct aspects against astro.com
    assert chart.SUN in composite_chart.aspects
    assert chart.MOON in composite_chart.aspects[chart.SUN]
    assert composite_chart.aspects[chart.SUN][chart.MOON].aspect == calc.SEXTILE

    assert chart.MOON in composite_chart.aspects
    assert chart.VENUS in composite_chart.aspects[chart.MOON]
    assert composite_chart.aspects[chart.MOON][chart.VENUS].aspect == calc.SEXTILE

    # Spot-check for correct weightings against astro.com
    assert chart.JUPITER in composite_chart.weightings['elements'].earth
    assert chart.JUPITER in composite_chart.weightings['modalities'].fixed
    assert chart.JUPITER in composite_chart.weightings['quadrants'].first


def test_transits(lat, lon):
    transits_chart = charts.Transits(lat, lon)

    assert transits_chart.type == names.CHART_TYPES[chart.TRANSITS]

    assert transits_chart.native.coordinates.latitude.formatted == lat
    assert transits_chart.native.coordinates.longitude.formatted == lon

    assert transits_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    default_transits_chart = charts.Transits()

    assert default_transits_chart.native.coordinates.latitude.raw == settings.default_latitude
    assert default_transits_chart.native.coordinates.longitude.raw == settings.default_longitude


def test_synastry(native, partner):
    partner_chart = charts.Natal(partner)
    native_chart = charts.Natal(native, aspects_to=partner_chart)

    # Spot-check for correct aspects against astro.com
    assert chart.SUN in native_chart.aspects
    assert chart.VENUS in native_chart.aspects[chart.SUN]
    assert native_chart.aspects[chart.SUN][chart.VENUS].aspect == calc.SQUARE

    assert chart.MOON in native_chart.aspects
    assert chart.MERCURY in native_chart.aspects[chart.MOON]
    assert native_chart.aspects[chart.MOON][chart.MERCURY].aspect == calc.SQUARE
