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


from zoneinfo import ZoneInfo

from pytest import fixture

from immanuel import charts
from immanuel.const import calc, chart, names
from immanuel.setup import settings


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
def solar_return_year():
    return 2030

@fixture
def pdt():
    # We compare against astro.com which assumes UTC for progressions date
    # so we knock 8 hours off midnight 2023-06-21 to account for Pacific Time
    return '2025-06-20 17:00:00'


def test_natal(dob, lat, lon):
    natal_chart = charts.Natal(dob, lat, lon)

    assert natal_chart.type == names.CHART_TYPES[chart.NATAL]

    # Birth date tested against astro.com's JD
    assert round(natal_chart.natal_date.julian + natal_chart.natal_date.deltat, 6) == 2451545.250739
    assert natal_chart.natal_date.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert natal_chart.coordinates.latitude.formatted == lat
    assert natal_chart.coordinates.longitude.formatted == lon

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

    assert solar_return_chart.type == names.CHART_TYPES[chart.SOLAR_RETURN]

    # Birth date tested against astro.com's JD
    assert round(solar_return_chart.natal_date.julian + solar_return_chart.natal_date.deltat, 6) == 2451545.250739
    assert solar_return_chart.natal_date.timezone == 'PST'

    # Solar return date tested against astro.com
    assert round(solar_return_chart.solar_return_date.julian + solar_return_chart.solar_return_date.deltat, 6) == 2462502.521823
    assert solar_return_chart.solar_return_date.timezone == 'PST'

    # Ensure coords have been converted back into correct string
    assert solar_return_chart.coordinates.latitude.formatted == lat
    assert solar_return_chart.coordinates.longitude.formatted == lon

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
    settings.mc_progression_method = calc.NAIBOD
    progressed_chart = charts.Progressed(dob, lat, lon, pdt)

    assert progressed_chart.type == names.CHART_TYPES[chart.PROGRESSED]
    assert progressed_chart.progression_method == names.PROGRESSION_METHODS[settings.mc_progression_method]

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
    assert progressed_chart.coordinates.latitude.formatted == lat
    assert progressed_chart.coordinates.longitude.formatted == lon

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


def test_synastry(dob, lat, lon, partner_dob, partner_lat, partner_lon):
    # Test for partner coordinates being copied to that of main chart
    synastry_chart = charts.Synastry(dob, lat, lon, partner_dob)

    assert synastry_chart.partner_coordinates.latitude.raw == synastry_chart.coordinates.latitude.raw
    assert synastry_chart.partner_coordinates.longitude.raw == synastry_chart.coordinates.longitude.raw

    # Now continue with the rest of the tests
    synastry_chart = charts.Synastry(dob, lat, lon, partner_dob, partner_lat, partner_lon)

    assert synastry_chart.type == names.CHART_TYPES[chart.SYNASTRY]

    # Natal birth date tested against astro.com's JD
    assert round(synastry_chart.natal_date.julian + synastry_chart.natal_date.deltat, 6) == 2451545.250739
    assert synastry_chart.natal_date.timezone == 'PST'

    # Partner birth date tested against astro.com's JD
    assert round(synastry_chart.partner_date.julian + synastry_chart.partner_date.deltat, 6) == 2451957.084075
    assert synastry_chart.partner_date.timezone == 'PST'

    # Ensure natal coords have been converted back into correct string
    assert synastry_chart.coordinates.latitude.formatted == lat
    assert synastry_chart.coordinates.longitude.formatted == lon

    # Ensure partner coords have been converted back into correct string
    assert synastry_chart.partner_coordinates.latitude.formatted == partner_lat
    assert synastry_chart.partner_coordinates.longitude.formatted == partner_lon

    # Default house system
    assert synastry_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    # Natal chart shape
    assert synastry_chart.shape == names.CHART_SHAPES[calc.BOWL]

    # Partner chart shape
    assert synastry_chart.partner_shape == names.CHART_SHAPES[calc.BOWL]

    # Natal daytime chart
    assert synastry_chart.diurnal == True

    # Partner daytime chart
    assert synastry_chart.partner_diurnal == False

    # Natal moon phase
    assert synastry_chart.moon_phase.third_quarter == True

    # Partner moon phase
    assert synastry_chart.partner_moon_phase.third_quarter == True

    # Spot-check for correct natal object positions against astro.com
    assert synastry_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert synastry_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.CAPRICORN]
    assert synastry_chart.objects[chart.SUN].sign_longitude.formatted == '10°37\'26"'

    assert synastry_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert synastry_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SCORPIO]
    assert synastry_chart.objects[chart.MOON].sign_longitude.formatted == '16°19\'29"'

    assert synastry_chart.objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert synastry_chart.objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.CAPRICORN]
    assert synastry_chart.objects[chart.PARS_FORTUNA].sign_longitude.formatted == '11°18\'41"'

    # Spot-check for correct partner object positions against astro.com
    assert synastry_chart.partner_objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert synastry_chart.partner_objects[chart.SUN].sign.name == names.SIGNS[chart.AQUARIUS]
    assert synastry_chart.partner_objects[chart.SUN].sign_longitude.formatted == '27°57\'45"'

    assert synastry_chart.partner_objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert synastry_chart.partner_objects[chart.MOON].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert synastry_chart.partner_objects[chart.MOON].sign_longitude.formatted == '14°25\'41"'

    assert synastry_chart.partner_objects[chart.PARS_FORTUNA].name == names.POINTS[chart.PARS_FORTUNA]
    assert synastry_chart.partner_objects[chart.PARS_FORTUNA].sign.name == names.SIGNS[chart.ARIES]
    assert synastry_chart.partner_objects[chart.PARS_FORTUNA].sign_longitude.formatted == '20°49\'15"'

    # Spot-check for correct natal object data against astro.com & Astro Gold
    assert synastry_chart.objects[chart.SATURN].movement.retrograde == True
    assert synastry_chart.objects[chart.MARS].dignities.peregrine == True
    assert synastry_chart.objects[chart.MARS].score == -5

    # Spot-check for correct partner object data against astro.com & Astro Gold
    assert synastry_chart.partner_objects[chart.MERCURY].movement.retrograde == True
    assert synastry_chart.partner_objects[chart.SUN].dignities.peregrine == True
    assert synastry_chart.partner_objects[chart.SUN].score == -10

    # Spot-check for correct natal angle positions against astro.com
    assert synastry_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert synastry_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.PISCES]
    assert synastry_chart.objects[chart.ASC].sign_longitude.formatted == '05°36\'38"'

    assert synastry_chart.objects[chart.MC].name == names.ANGLES[chart.MC]
    assert synastry_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert synastry_chart.objects[chart.MC].sign_longitude.formatted == '14°50\'44"'

    # Spot-check for correct partner angle positions against astro.com
    assert synastry_chart.partner_objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert synastry_chart.partner_objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert synastry_chart.partner_objects[chart.ASC].sign_longitude.formatted == '07°17\'12"'

    assert synastry_chart.partner_objects[chart.MC].name == names.ANGLES[chart.MC]
    assert synastry_chart.partner_objects[chart.MC].sign.name == names.SIGNS[chart.SCORPIO]
    assert synastry_chart.partner_objects[chart.MC].sign_longitude.formatted == '27°24\'13"'

    # Spot-check for correct natal 2nd house position against astro.com
    assert synastry_chart.houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert synastry_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.ARIES]
    assert synastry_chart.houses[chart.HOUSE2].sign_longitude.formatted == '17°59\'40"'

    # Spot-check for correct partner 2nd house position against astro.com
    assert synastry_chart.partner_houses[chart.HOUSE2].name == names.HOUSES[chart.HOUSE2]
    assert synastry_chart.partner_houses[chart.HOUSE2].sign.name == names.SIGNS[chart.PISCES]
    assert synastry_chart.partner_houses[chart.HOUSE2].sign_longitude.formatted == '23°06\'14"'

    # Spot-check for correct natal weightings against astro.com
    assert chart.JUPITER in synastry_chart.weightings['elements'].fire
    assert chart.JUPITER in synastry_chart.weightings['modalities'].cardinal
    assert chart.JUPITER in synastry_chart.weightings['quadrants'].first

    # Spot-check for correct partner weightings against astro.com
    assert chart.JUPITER in synastry_chart.partner_weightings['elements'].air
    assert chart.JUPITER in synastry_chart.partner_weightings['modalities'].mutable
    assert chart.JUPITER in synastry_chart.partner_weightings['quadrants'].second

    # Spot-check for correct natal aspects against astro.com
    assert chart.SUN in synastry_chart.aspects
    assert chart.VENUS in synastry_chart.aspects[chart.SUN]
    assert synastry_chart.aspects[chart.SUN][chart.VENUS].aspect == calc.SQUARE

    assert chart.MOON in synastry_chart.aspects
    assert chart.MERCURY in synastry_chart.aspects[chart.MOON]
    assert synastry_chart.aspects[chart.MOON][chart.MERCURY].aspect == calc.SQUARE

    # Spot-check for correct partner aspects against astro.com
    assert chart.SUN in synastry_chart.partner_aspects
    assert chart.MERCURY in synastry_chart.partner_aspects[chart.SUN]
    assert synastry_chart.partner_aspects[chart.SUN][chart.MERCURY].aspect == calc.SEXTILE

    assert chart.MOON in synastry_chart.partner_aspects
    assert chart.URANUS in synastry_chart.partner_aspects[chart.MOON]
    assert synastry_chart.partner_aspects[chart.MOON][chart.URANUS].aspect == calc.SEXTILE


def test_composite(dob, lat, lon, partner_dob, partner_lat, partner_lon):
    # Test for partner coordinates being copied to that of main chart
    composite_chart = charts.Synastry(dob, lat, lon, partner_dob)

    assert composite_chart.partner_coordinates.latitude.raw == composite_chart.coordinates.latitude.raw
    assert composite_chart.partner_coordinates.longitude.raw == composite_chart.coordinates.longitude.raw

    # Now continue with the rest of the tests
    composite_chart = charts.Composite(dob, lat, lon, partner_dob, partner_lat, partner_lon)

    assert composite_chart.type == names.CHART_TYPES[chart.COMPOSITE]

    # Natal birth date tested against astro.com's JD
    assert round(composite_chart.natal_date.julian + composite_chart.natal_date.deltat, 6) == 2451545.250739
    assert composite_chart.natal_date.timezone == 'PST'

    # Partner birth date tested against astro.com's JD
    assert round(composite_chart.partner_date.julian + composite_chart.partner_date.deltat, 6) == 2451957.084075
    assert composite_chart.partner_date.timezone == 'PST'

    # Ensure natal coords have been converted back into correct string
    assert composite_chart.coordinates.latitude.formatted == lat
    assert composite_chart.coordinates.longitude.formatted == lon

    # Ensure partner coords have been converted back into correct string
    assert composite_chart.partner_coordinates.latitude.formatted == partner_lat
    assert composite_chart.partner_coordinates.longitude.formatted == partner_lon

    # Default house system
    assert composite_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]

    # Daytime chart
    assert composite_chart.diurnal == True

    # Moon phase
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
