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
from immanuel.classes import wrap
from immanuel.const import calc, chart, dignities, names
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
def julian_date():
    return 2451545.25               # 2000-01-01 18:00 UT

@fixture
def solar_return_year():
    return 2030

@fixture
def pdt():
    # We compare against astro.com which assumes UTC for progressions date
    # so we knock 8 hours off midnight 2023-06-21 to account for Pacific Time
    return '2025-06-20 17:00:00'


def teardown_function():
    settings.reset()


def test_subject(dob, lat, lon, native, julian_date):
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
    assert native.date_time_ambiguous == False
    assert native.julian_date == julian_date

    ambiguous_date_time = datetime(2022, 11, 6, 1, 30)
    ambiguous_native = charts.Subject(ambiguous_date_time, lat, lon)
    assert ambiguous_native.date_time_ambiguous == True


def test_wrapped_data(native):
    settings.objects.append(chart.PRE_NATAL_LUNAR_ECLIPSE)
    natal_chart = charts.Natal(native)

    # Angle
    longitude = natal_chart.objects[chart.SUN].longitude
    assert longitude.raw == 280.6237802656368
    assert longitude.formatted == '280°37\'26"'
    assert longitude.direction == '+'
    assert longitude.degrees == 280
    assert longitude.minutes == 37
    assert longitude.seconds == 26

    # Aspect
    aspect = natal_chart.aspects[chart.SUN][chart.MOON]
    assert aspect.active == chart.MOON
    assert aspect.passive == chart.SUN
    assert aspect.type == names.ASPECTS[calc.SEXTILE]
    assert aspect.aspect == calc.SEXTILE
    assert aspect.orb == settings.planet_orbs[calc.SEXTILE]
    assert type(aspect.distance) is wrap.Angle                      # Tested separately, just ensure type
    assert type(aspect.difference) is wrap.Angle                    # Tested separately, just ensure type

    # AspectCondition
    assert aspect.condition.associate == True
    assert aspect.condition.dissociate == False
    assert aspect.condition.formatted == names.ASPECT_CONDITIONS[calc.ASSOCIATE]

    # AspectMovement
    assert aspect.movement.applicative == False
    assert aspect.movement.exact == False
    assert aspect.movement.separative == True
    assert aspect.movement.formatted == names.ASPECT_MOVEMENTS[calc.SEPARATIVE]

    # Coordinates
    assert type(natal_chart.native.coordinates.latitude) is wrap.Angle      # Tested separately, just ensure type
    assert type(natal_chart.native.coordinates.longitude) is wrap.Angle     # Tested separately, just ensure type

    # DateTime
    date_time = natal_chart.native.date_time
    assert type(date_time.datetime) is datetime
    assert date_time.timezone == 'PST'
    assert date_time.ambiguous == False
    assert date_time.julian == 2451545.25
    assert date_time.deltat == 0.0007387629899254968
    assert date_time.sidereal_time == '16:54:13'

    # MoonPhase
    moon_phase = natal_chart.moon_phase
    assert moon_phase.new_moon == False
    assert moon_phase.waxing_crescent == False
    assert moon_phase.first_quarter == False
    assert moon_phase.waxing_gibbous == False
    assert moon_phase.full_moon == False
    assert moon_phase.disseminating == False
    assert moon_phase.third_quarter == True
    assert moon_phase.balsamic == False
    assert moon_phase.formatted == names.MOON_PHASES[calc.THIRD_QUARTER]

    # Object
    sun = natal_chart.objects[chart.SUN]
    assert sun.index == chart.SUN
    assert sun.name == names.PLANETS[chart.SUN]
    assert sun.distance == 0.9833259257690341
    assert sun.speed == 1.0194579691359147
    assert sun.out_of_bounds == False
    assert sun.in_sect == True
    assert sun.score == 3

    assert type(sun.latitude) is wrap.Angle             # Tested separately, just ensure type
    assert type(sun.longitude) is wrap.Angle            # Tested separately, just ensure type
    assert type(sun.sign_longitude) is wrap.Angle       # Tested separately, just ensure type
    assert type(sun.declination) is wrap.Angle          # Tested separately, just ensure type

    # ObjectType
    assert sun.type.index == chart.PLANET
    assert sun.type.name == names.OBJECTS[chart.PLANET]

    # Sign
    assert sun.sign.number == chart.CAPRICORN
    assert sun.sign.name == names.SIGNS[chart.CAPRICORN]
    assert sun.sign.element == names.ELEMENTS[chart.EARTH]
    assert sun.sign.modality == names.MODALITIES[chart.CARDINAL]

    # Decan
    assert sun.decan.number == chart.DECAN2
    assert sun.decan.name == names.DECANS[chart.DECAN2]

    # House
    assert sun.house.index == chart.HOUSE11
    assert sun.house.number == 11
    assert sun.house.name == names.HOUSES[chart.HOUSE11]

    # ObjectMovement
    assert sun.movement.direct == True
    assert sun.movement.stationary == False
    assert sun.movement.retrograde == False
    assert sun.movement.typical == True
    assert sun.movement.formatted == names.OBJECT_MOVEMENTS[calc.DIRECT]

    # DignityState
    assert sun.dignities.ruler == False
    assert sun.dignities.exalted == False
    assert sun.dignities.triplicity_ruler == False
    assert sun.dignities.term_ruler == False
    assert sun.dignities.face_ruler == False
    assert sun.dignities.mutual_reception_ruler == False
    assert sun.dignities.mutual_reception_exalted == False
    assert sun.dignities.mutual_reception_triplicity_ruler == True
    assert sun.dignities.mutual_reception_term_ruler == False
    assert sun.dignities.mutual_reception_face_ruler == False
    assert sun.dignities.detriment == False
    assert sun.dignities.fall == False
    assert sun.dignities.peregrine == False
    assert sun.dignities.formatted == [
        names.DIGNITIES[dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER],
    ]

    # EclipseType
    eclipse = natal_chart.objects[chart.PRE_NATAL_LUNAR_ECLIPSE]
    assert eclipse.eclipse_type.total == False
    assert eclipse.eclipse_type.annular == False
    assert eclipse.eclipse_type.partial == True
    assert eclipse.eclipse_type.annular_total == False
    assert eclipse.eclipse_type.penumbral == False
    assert eclipse.eclipse_type.formatted == names.ECLIPSE_TYPES[chart.PARTIAL]

    assert type(eclipse.date_time) is wrap.DateTime         # Tested separately, just ensure type

    # Subject
    subject = natal_chart.native
    assert type(subject.date_time) is wrap.DateTime         # Tested separately, just ensure type
    assert type(subject.coordinates) is wrap.Coordinates    # Tested separately, just ensure type

    # Weightings
    weightings = natal_chart.weightings
    assert type(weightings.elements) is wrap.Elements       # Tested separately, just ensure type
    assert type(weightings.modalities) is wrap.Modalities   # Tested separately, just ensure type
    assert type(weightings.quadrants) is wrap.Quadrants     # Tested separately, just ensure type

    # Elements
    elements = natal_chart.weightings.elements
    assert type(elements.fire) is list
    assert type(elements.earth) is list
    assert type(elements.air) is list
    assert type(elements.water) is list

    # Modalities
    modalities = natal_chart.weightings.modalities
    assert type(modalities.cardinal) is list
    assert type(modalities.fixed) is list
    assert type(modalities.mutable) is list

    # Quadrants
    quadrants = natal_chart.weightings.quadrants
    assert type(quadrants.first) is list
    assert type(quadrants.second) is list
    assert type(quadrants.third) is list
    assert type(quadrants.fourth) is list


def test_natal(native, lat, lon):
    natal_chart = charts.Natal(native)

    assert natal_chart.type == names.CHART_TYPES[chart.NATAL]

    assert round(natal_chart.native.date_time.julian + natal_chart.native.date_time.deltat, 6) == 2451545.250739
    assert natal_chart.native.date_time.timezone == 'PST'

    assert natal_chart.native.coordinates.latitude.formatted == lat
    assert natal_chart.native.coordinates.longitude.formatted == lon

    assert natal_chart.house_system == names.HOUSE_SYSTEMS[settings.house_system]
    assert natal_chart.shape == names.CHART_SHAPES[calc.BOWL]
    assert natal_chart.diurnal is True
    assert natal_chart.moon_phase.third_quarter is True

    # Spot-check for correct object positions against astro.com
    assert natal_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert natal_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.CAPRICORN]
    assert natal_chart.objects[chart.SUN].sign_longitude.formatted == '10°37\'26"'

    assert natal_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert natal_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SCORPIO]
    assert natal_chart.objects[chart.MOON].sign_longitude.formatted == '16°19\'29"'

    assert natal_chart.objects[chart.PART_OF_FORTUNE].name == names.POINTS[chart.PART_OF_FORTUNE]
    assert natal_chart.objects[chart.PART_OF_FORTUNE].sign.name == names.SIGNS[chart.CAPRICORN]
    assert natal_chart.objects[chart.PART_OF_FORTUNE].sign_longitude.formatted == '11°18\'41"'

    # Spot-check for correct object data against astro.com & Astro Gold
    assert natal_chart.objects[chart.SATURN].movement.retrograde is True
    assert natal_chart.objects[chart.MARS].dignities.peregrine is True
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
    assert chart.JUPITER in natal_chart.weightings.elements.fire
    assert chart.JUPITER in natal_chart.weightings.modalities.cardinal
    assert chart.JUPITER in natal_chart.weightings.quadrants.first


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
    assert solar_return_chart.diurnal is True
    assert solar_return_chart.moon_phase.balsamic is True

    # Spot-check for correct object positions against astro.com
    assert solar_return_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert solar_return_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.CAPRICORN]
    assert solar_return_chart.objects[chart.SUN].sign_longitude.formatted == '10°37\'26"'

    assert solar_return_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert solar_return_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SCORPIO]
    assert solar_return_chart.objects[chart.MOON].sign_longitude.formatted == '28°43\'43"'

    assert solar_return_chart.objects[chart.PART_OF_FORTUNE].name == names.POINTS[chart.PART_OF_FORTUNE]
    assert solar_return_chart.objects[chart.PART_OF_FORTUNE].sign.name == names.SIGNS[chart.TAURUS]
    assert solar_return_chart.objects[chart.PART_OF_FORTUNE].sign_longitude.formatted == '24°41\'28"'

    # Spot-check for correct object data against astro.com & Astro Gold
    assert solar_return_chart.objects[chart.SATURN].movement.retrograde is True
    assert solar_return_chart.objects[chart.MARS].dignities.peregrine is True
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
    assert chart.JUPITER in solar_return_chart.weightings.elements.water
    assert chart.JUPITER in solar_return_chart.weightings.modalities.fixed
    assert chart.JUPITER in solar_return_chart.weightings.quadrants.second


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
    assert progressed_chart.diurnal is True
    assert progressed_chart.moon_phase.disseminating is True

    # Spot-check for correct object positions against astro.com
    assert progressed_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert progressed_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.AQUARIUS]
    assert progressed_chart.objects[chart.SUN].sign_longitude.formatted == '06°33\'41"'

    assert progressed_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert progressed_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.LIBRA]
    assert progressed_chart.objects[chart.MOON].sign_longitude.formatted == '23°50\'57"'

    assert progressed_chart.objects[chart.PART_OF_FORTUNE].name == names.POINTS[chart.PART_OF_FORTUNE]
    assert progressed_chart.objects[chart.PART_OF_FORTUNE].sign.name == names.SIGNS[chart.CAPRICORN]
    assert progressed_chart.objects[chart.PART_OF_FORTUNE].sign_longitude.formatted == '00°17\'45"'

    # Spot-check for correct object data against Astro Gold
    assert progressed_chart.objects[chart.SUN].dignities.detriment is True
    assert progressed_chart.objects[chart.SUN].dignities.peregrine is True
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
    assert chart.VENUS in progressed_chart.weightings.elements.earth
    assert chart.VENUS in progressed_chart.weightings.modalities.cardinal
    assert chart.VENUS in progressed_chart.weightings.quadrants.third


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
    assert composite_chart.diurnal is True
    assert composite_chart.moon_phase.third_quarter is True

    # Spot-check for correct object positions against astro.com
    assert composite_chart.objects[chart.ASC].name == names.ANGLES[chart.ASC]
    assert composite_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.ASC].sign_longitude.formatted == '21°26\'55"'

    assert composite_chart.objects[chart.SUN].name == names.PLANETS[chart.SUN]
    assert composite_chart.objects[chart.SUN].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.SUN].sign_longitude.formatted == '04°17\'35"'

    assert composite_chart.objects[chart.MOON].name == names.PLANETS[chart.MOON]
    assert composite_chart.objects[chart.MOON].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MOON].sign_longitude.formatted == '00°22\'35"'

    assert composite_chart.objects[chart.PART_OF_FORTUNE].name == names.POINTS[chart.PART_OF_FORTUNE]
    assert composite_chart.objects[chart.PART_OF_FORTUNE].sign.name == names.SIGNS[chart.PISCES]
    assert composite_chart.objects[chart.PART_OF_FORTUNE].sign_longitude.formatted == '01°03\'58"'

    # Spot-check for correct object data against Astro Gold
    assert composite_chart.objects[chart.SUN].dignities.detriment is True
    assert composite_chart.objects[chart.SUN].dignities.peregrine is True
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
    assert chart.JUPITER in composite_chart.weightings.elements.earth
    assert chart.JUPITER in composite_chart.weightings.modalities.fixed
    assert chart.JUPITER in composite_chart.weightings.quadrants.first

    # Ensure more quirky house systems work
    settings.house_system = chart.EQUAL

    composite_chart = charts.Composite(native, partner)

    assert composite_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.ASC].sign_longitude.formatted == '21°26\'55"'
    assert composite_chart.objects[chart.ASC].declination.formatted == '-14°21\'10"'

    assert composite_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MC].sign_longitude.formatted == '06°07\'28"'
    assert composite_chart.objects[chart.MC].declination.formatted == '-21°19\'44"'

    assert composite_chart.houses[chart.HOUSE1].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.houses[chart.HOUSE1].sign_longitude.formatted == '21°26\'55"'
    assert composite_chart.houses[chart.HOUSE1].declination.formatted == '-14°21\'10"'

    assert composite_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.PISCES]
    assert composite_chart.houses[chart.HOUSE2].sign_longitude.formatted == '21°26\'55"'
    assert composite_chart.houses[chart.HOUSE2].declination.formatted == '-03°23\'27"'

    settings.house_system = chart.VEHLOW_EQUAL

    composite_chart = charts.Composite(native, partner)

    assert composite_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.ASC].sign_longitude.formatted == '21°26\'55"'
    assert composite_chart.objects[chart.ASC].declination.formatted == '-14°21\'10"'

    assert composite_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MC].sign_longitude.formatted == '06°07\'28"'
    assert composite_chart.objects[chart.MC].declination.formatted == '-21°19\'44"'

    assert composite_chart.houses[chart.HOUSE1].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.houses[chart.HOUSE1].sign_longitude.formatted == '06°26\'55"'
    assert composite_chart.houses[chart.HOUSE1].declination.formatted == '-18°39\'36"'

    assert composite_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.PISCES]
    assert composite_chart.houses[chart.HOUSE2].sign_longitude.formatted == '06°26\'55"'
    assert composite_chart.houses[chart.HOUSE2].declination.formatted == '-09°08\'42"'

    settings.house_system = chart.WHOLE_SIGN

    composite_chart = charts.Composite(native, partner)

    assert composite_chart.objects[chart.ASC].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.objects[chart.ASC].sign_longitude.formatted == '21°26\'55"'
    assert composite_chart.objects[chart.ASC].declination.formatted == '-14°21\'10"'

    assert composite_chart.objects[chart.MC].sign.name == names.SIGNS[chart.SAGITTARIUS]
    assert composite_chart.objects[chart.MC].sign_longitude.formatted == '06°07\'28"'
    assert composite_chart.objects[chart.MC].declination.formatted == '-21°19\'44"'

    assert composite_chart.houses[chart.HOUSE1].sign.name == names.SIGNS[chart.AQUARIUS]
    assert composite_chart.houses[chart.HOUSE1].sign_longitude.formatted == '00°00\'00"'
    assert composite_chart.houses[chart.HOUSE1].declination.formatted == '-20°08\'58"'

    assert composite_chart.houses[chart.HOUSE2].sign.name == names.SIGNS[chart.PISCES]
    assert composite_chart.houses[chart.HOUSE2].sign_longitude.formatted == '00°00\'00"'
    assert composite_chart.houses[chart.HOUSE2].declination.formatted == '-11°28\'17"'

    settings.house_system = chart.PLACIDUS


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

    # Spot-check house_for() against astro.com
    assert native_chart.house_for(partner_chart.objects[chart.SUN]) == chart.HOUSE12
    assert partner_chart.house_for(native_chart.objects[chart.SUN]) == chart.HOUSE11

    assert native_chart.house_for(partner_chart.objects[chart.MOON]) == chart.HOUSE9
    assert partner_chart.house_for(native_chart.objects[chart.MOON]) == chart.HOUSE9
