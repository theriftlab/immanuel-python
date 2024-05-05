"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Test the localization works when a translation file is present. These tests
    use the pt_BR language as it's the first translation to go in. Translations
    for Brazilian Portuguese are courtesy of Nathan Octavio.

"""

from pytest import fixture

from immanuel import charts
from immanuel.classes import wrap
from immanuel.classes.cache import FunctionCache
from immanuel.classes.localize import _
from immanuel.const import calc, chart, dignities
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
def native(dob, lat, lon):
    return charts.Subject(dob, lat, lon)

@fixture
def partner(partner_dob, partner_lat, partner_lon):
    return charts.Subject(partner_dob, partner_lat, partner_lon)

@fixture
def object_names():
    return {
        chart.ASC: 'Ascendente',
        chart.DESC: 'Descendente',
        chart.MC: 'Meio do Céu',
        chart.IC: 'Fundo do Céu',
        chart.ARMC: 'ARMC',

        chart.SUN: 'Sol',
        chart.MOON: 'Lua',
        chart.MERCURY: 'Mercúrio',
        chart.VENUS: 'Vênus',
        chart.MARS: 'Marte',
        chart.JUPITER: 'Júpiter',
        chart.SATURN: 'Saturno',
        chart.URANUS: 'Urano',
        chart.NEPTUNE: 'Netuno',
        chart.PLUTO: 'Plutão',

        chart.CHIRON: 'Quiron',
        chart.PHOLUS: 'Pholus',
        chart.CERES: 'Ceres',
        chart.PALLAS: 'Pallas',
        chart.JUNO: 'Juno',
        chart.VESTA: 'Vesta',

        chart.NORTH_NODE: 'Nodo Norte',
        chart.SOUTH_NODE: 'Nodo Sul',
        chart.TRUE_NORTH_NODE: 'Nodo Norte Verdadeiro',
        chart.TRUE_SOUTH_NODE: 'Nodo Sul Verdadeiro',
        chart.VERTEX: 'Vertex',
        chart.LILITH: 'Lilith',
        chart.TRUE_LILITH: 'Lilith Verdadeira',
        chart.SYZYGY: 'Sizígia',
        chart.PART_OF_FORTUNE: 'Roda da Fortuna',

        chart.PRE_NATAL_LUNAR_ECLIPSE: 'Eclipse Lunar Pré-natal',
        chart.PRE_NATAL_SOLAR_ECLIPSE: 'Eclipse Solar Pré-natal',
        chart.POST_NATAL_LUNAR_ECLIPSE: 'Eclipse Lunar Pós-natal',
        chart.POST_NATAL_SOLAR_ECLIPSE: 'Eclipse Solar Pós-natal',
    }

@fixture
def aspects():
    return [
        calc.CONJUNCTION,
        calc.OPPOSITION,
        calc.SQUARE,
        calc.TRINE,
        calc.SEXTILE,
        calc.SEPTILE,
        calc.SEMISQUARE,
        calc.SESQUISQUARE,
        calc.SEMISEXTILE,
        calc.QUINCUNX,
        calc.QUINTILE,
        calc.BIQUINTILE,
    ]

@fixture
def chart_pattern_birth_data():
    return {
        # Harrison Ford
        calc.BUNDLE: {
            'latitude': '41n51',
            'longitude': '87w39',
            'dob': '1942-07-13 11:41:00',
            'shape': 'Feixe',
        },
        # Clint Eastwood
        calc.BUCKET: {
            'latitude': '37n47',
            'longitude': '122w25',
            'dob': '1930-05-31 17:35:00',
            'shape': 'Balde',
        },
        # Alfred Hitchcock
        calc.BOWL: {
            'latitude': '51n30',
            'longitude': '0w10',
            'dob': '1899-08-13 20:00:00',
            'shape': 'Tigela',
        },
        # Isaac Newton
        calc.LOCOMOTIVE: {
            'latitude': '52n49',
            'longitude': '0w38',
            'dob': '1643-01-04 01:38:00',
            'shape': 'Locomotiva',
        },
        # William Blake
        calc.SEESAW: {
            'latitude': '51n30',
            'longitude': '0w08',
            'dob': '1757-11-28 19:45:00',
            'shape': 'Gangorra',
        },
        # Carl Jung
        calc.SPLASH: {
            'latitude': '46n36',
            'longitude': '9e19',
            'dob': '1875-07-26 19:29:00',
            'shape': 'Salpicado',
        },
        # Random DOB to get a non-shape
        calc.SPLAY: {
            'latitude': '32n43',
            'longitude': '117w09',
            'dob': '1902-01-01 10:00:00',
            'shape': 'Espalhado',
        }
    }


def teardown_function():
    settings.reset()
    FunctionCache.clear_all()


def test_date_locale(native):
    settings.locale = 'pt_BR'
    assert str(wrap.Subject(native)) == 'Sáb Jan 01 2000 10:00:00 PST em 32N43.0, 117W9.0'


def test_properties_chart_type(native, partner):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert natal.type == 'Natal'
    solar_return = charts.SolarReturn(native, 2024)
    assert solar_return.type == 'Retorno Solar'
    progressed = charts.Progressed(native, '2024-01-01')
    assert progressed.type == 'Progredido'
    composite = charts.Composite(native, partner)
    assert composite.type == 'Composto'


def test_properties_object_house_types(native):
    settings.locale = 'pt_BR'
    settings.objects += [chart.PRE_NATAL_SOLAR_ECLIPSE, 'Antares']
    natal = charts.Natal(native)
    assert natal.houses[chart.HOUSE1].type.name == 'Casa'
    assert natal.objects[chart.ASC].type.name == 'Ângulo'
    assert natal.objects[chart.CHIRON].type.name == 'Asteróide'
    assert natal.objects[chart.TRUE_NORTH_NODE].type.name == 'Ponto'
    assert natal.objects[chart.PRE_NATAL_SOLAR_ECLIPSE].type.name == 'Eclipse'
    assert natal.objects['Antares'].type.name == 'Estrela fixa'


def test_properties_signs(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert natal.houses[chart.HOUSE1].sign.name == 'Peixes'
    assert natal.houses[chart.HOUSE2].sign.name == 'Áries'
    assert natal.houses[chart.HOUSE3].sign.name == 'Touro'
    assert natal.houses[chart.HOUSE4].sign.name == 'Gêmeos'
    assert natal.houses[chart.HOUSE5].sign.name == 'Câncer'
    assert natal.houses[chart.HOUSE6].sign.name == 'Leão'
    assert natal.houses[chart.HOUSE7].sign.name == 'Virgem'
    assert natal.houses[chart.HOUSE8].sign.name == 'Libra'
    assert natal.houses[chart.HOUSE9].sign.name == 'Escorpião'
    assert natal.houses[chart.HOUSE10].sign.name == 'Sagitário'
    assert natal.houses[chart.HOUSE11].sign.name == 'Capricórnio'
    assert natal.houses[chart.HOUSE12].sign.name == 'Aquário'


def test_properties_decans(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert natal.objects[chart.MERCURY].decan.name == '1º Decanato'
    assert natal.objects[chart.SUN].decan.name == '2º Decanato'
    assert natal.objects[chart.MARS].decan.name == '3º Decanato'


def test_properties_elements(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert natal.objects[chart.VENUS].sign.element == 'Fogo'
    assert natal.objects[chart.SUN].sign.element == 'Terra'
    assert natal.objects[chart.MARS].sign.element == 'Ar'
    assert natal.objects[chart.MOON].sign.element == 'Água'


def test_properties_modalities(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert natal.objects[chart.SUN].sign.modality == 'Cardinal'
    assert natal.objects[chart.MOON].sign.modality == 'Fixo'
    assert natal.objects[chart.VENUS].sign.modality == 'Mutável'


def test_properties_house_system(native):
    settings.locale = 'pt_BR'

    settings.house_system = chart.ALCABITUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Alcabitius'

    settings.house_system = chart.AZIMUTHAL
    natal = charts.Natal(native)
    assert natal.house_system == 'Azimutal'

    settings.house_system = chart.CAMPANUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Campanus'

    settings.house_system = chart.EQUAL
    natal = charts.Natal(native)
    assert natal.house_system == 'Casas iguais'

    settings.house_system = chart.KOCH
    natal = charts.Natal(native)
    assert natal.house_system == 'Koch'

    settings.house_system = chart.MERIDIAN
    natal = charts.Natal(native)
    assert natal.house_system == 'Meridiano'

    settings.house_system = chart.MORINUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Morinus'

    settings.house_system = chart.PLACIDUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Placidus'

    settings.house_system = chart.POLICH_PAGE
    natal = charts.Natal(native)
    assert natal.house_system == 'Polich Page'

    settings.house_system = chart.PORPHYRIUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Porfírio'

    settings.house_system = chart.REGIOMONTANUS
    natal = charts.Natal(native)
    assert natal.house_system == 'Regiomontanus'

    settings.house_system = chart.VEHLOW_EQUAL
    natal = charts.Natal(native)
    assert natal.house_system == 'Vehlow'

    settings.house_system = chart.WHOLE_SIGN
    natal = charts.Natal(native)
    assert natal.house_system == 'Signos Inteiros'


def test_properties_house_names(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)

    for house in natal.houses.values():
        assert house.name == f'Casa {house.number}'


def test_properties_object_names(native, object_names):
    settings.locale = 'pt_BR'
    settings.objects = object_names.keys()
    natal = charts.Natal(native)

    for object in natal.objects.values():
        assert object.name == object_names[object.index]


def test_properties_eclipse_types(lat, lon):
    settings.locale = 'pt_BR'
    settings.objects = [chart.PRE_NATAL_LUNAR_ECLIPSE, chart.PRE_NATAL_SOLAR_ECLIPSE]

    total_native = charts.Subject('2025-03-14 12:00:00', lat, lon)
    natal = charts.Natal(total_native)
    assert natal.objects[chart.PRE_NATAL_LUNAR_ECLIPSE].eclipse_type.formatted == 'Total'

    annular_native = charts.Subject('2024-10-02 12:00:00', lat, lon)
    natal = charts.Natal(annular_native)
    assert natal.objects[chart.PRE_NATAL_SOLAR_ECLIPSE].eclipse_type.formatted == 'Anelar'

    partial_native = charts.Subject('2024-09-18 12:00:00', lat, lon)
    natal = charts.Natal(partial_native)
    assert natal.objects[chart.PRE_NATAL_LUNAR_ECLIPSE].eclipse_type.formatted == 'Parcial'

    annular_total_native = charts.Subject('2023-04-20 12:00:00', lat, lon)
    natal = charts.Natal(annular_total_native)
    assert natal.objects[chart.PRE_NATAL_SOLAR_ECLIPSE].eclipse_type.formatted == 'Anelar Total'

    penumbral_native = charts.Subject('2024-03-25 12:00:00', lat, lon)
    natal = charts.Natal(penumbral_native)
    assert natal.objects[chart.PRE_NATAL_LUNAR_ECLIPSE].eclipse_type.formatted == 'Penumbral'


def test_properties_aspects(native, aspects):
    settings.locale = 'pt_BR'
    settings.aspects = aspects

    natal = charts.Natal(native)

    assert natal.aspects[chart.SUN][chart.PART_OF_FORTUNE].type == 'Conjunção'
    assert natal.aspects[chart.MOON][chart.SATURN].type == 'Oposição'
    assert natal.aspects[chart.MOON][chart.URANUS].type == 'Quadratura'
    assert natal.aspects[chart.SATURN][chart.PART_OF_FORTUNE].type == 'Trígono'
    assert natal.aspects[chart.MOON][chart.SUN].type == 'Sextil'
    assert natal.aspects[chart.NEPTUNE][chart.PLUTO].type == 'Septil'
    assert natal.aspects[chart.SUN][chart.MARS].type == 'Semi-quadratura'
    assert natal.aspects[chart.JUPITER][chart.PLUTO].type == 'Sesqui-quadratura'
    assert natal.aspects[chart.PLUTO][chart.PART_OF_FORTUNE].type == 'Semi-sextil'
    assert natal.aspects[chart.PLUTO][chart.SATURN].type == 'Quincúncio'
    assert natal.aspects[chart.VENUS][chart.URANUS].type == 'Quintil'
    assert natal.aspects[chart.VENUS][chart.JUPITER].type == 'Biquintil'


def test_properties_aspect_movements(native, aspects):
    settings.locale = 'pt_BR'
    settings.aspects = aspects

    natal = charts.Natal(native)

    assert natal.aspects[chart.SUN][chart.PART_OF_FORTUNE].movement.formatted == 'Aplicativa'
    assert natal.aspects[chart.PLUTO][chart.PART_OF_FORTUNE].movement.formatted == 'Exacto'
    assert natal.aspects[chart.MOON][chart.SUN].movement.formatted == 'Separativo'


def test_properties_aspect_conditions(native, aspects):
    settings.locale = 'pt_BR'
    settings.aspects = aspects

    natal = charts.Natal(native)

    assert natal.aspects[chart.SUN][chart.PART_OF_FORTUNE].condition.formatted == 'Associada'
    assert natal.aspects[chart.MERCURY][chart.MARS].condition.formatted == 'Dissociado'


def test_properties_dignities(native):
    settings.locale = 'pt_BR'

    natal = charts.Natal(native)

    # Since it is near impossible to calculate a chart with every dignity, we invent some
    natal.objects[chart.SUN].dignities = wrap.DignityState({ 'index': chart.SUN }, { v: True for v in [
        dignities.RULER,
        dignities.EXALTED,
        dignities.TRIPLICITY_RULER,
        dignities.TERM_RULER,
        dignities.FACE_RULER,
        dignities.MUTUAL_RECEPTION_RULER,
        dignities.MUTUAL_RECEPTION_EXALTED,
        dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER,
        dignities.MUTUAL_RECEPTION_TERM_RULER,
        dignities.MUTUAL_RECEPTION_FACE_RULER,
        dignities.IN_RULERSHIP_ELEMENT,
        dignities.DETRIMENT,
        dignities.FALL,
        dignities.PEREGRINE,
    ]})

    assert 'Regente' in natal.objects[chart.SUN].dignities.formatted
    assert 'Exaltado' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Triplicidade' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Termo' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Face' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente por recepção mútua' in natal.objects[chart.SUN].dignities.formatted
    assert 'Exaltado por recepção mútua' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Triplicidade por recepção mútua' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Termo por recepção mútua' in natal.objects[chart.SUN].dignities.formatted
    assert 'Regente de Face por recepção mútua' in natal.objects[chart.SUN].dignities.formatted
    assert 'No elemento de regência' in natal.objects[chart.SUN].dignities.formatted
    assert 'Em Exílio' in natal.objects[chart.SUN].dignities.formatted
    assert 'Em Queda' in natal.objects[chart.SUN].dignities.formatted
    assert 'Peregrino' in natal.objects[chart.SUN].dignities.formatted


def test_properties_moon_phases(lat, lon):
    settings.locale = 'pt_BR'

    natal_new = charts.Natal(charts.Subject('2024-01-11 04:00', lat, lon))
    assert natal_new.moon_phase.formatted == 'Nova'

    natal_waxing = charts.Natal(charts.Subject('2024-01-14 12:00', lat, lon))
    assert natal_waxing.moon_phase.formatted == 'Crescente'

    natal_first_quarter = charts.Natal(charts.Subject('2024-01-17 20:00', lat, lon))
    assert natal_first_quarter.moon_phase.formatted == 'Quarto Crescente'

    natal_first_quarter = charts.Natal(charts.Subject('2024-01-22 12:00', lat, lon))
    assert natal_first_quarter.moon_phase.formatted == 'Crescente Gibosa'

    natal_full = charts.Natal(charts.Subject('2024-01-25 10:00', lat, lon))
    assert natal_full.moon_phase.formatted == 'Cheia'

    natal_disseminating = charts.Natal(charts.Subject('2024-01-30 12:00', lat, lon))
    assert natal_disseminating.moon_phase.formatted == 'Minguante Gibosa'

    natal_third_quarter = charts.Natal(charts.Subject('2024-02-02 15:30', lat, lon))
    assert natal_third_quarter.moon_phase.formatted == 'Quarto Minguante'

    natal_third_quarter = charts.Natal(charts.Subject('2024-02-07 12:00', lat, lon))
    assert natal_third_quarter.moon_phase.formatted == 'Minguante'


def test_properties_object_movement(native):
    settings.locale = 'pt_BR'

    natal = charts.Natal(native)

    assert natal.objects[chart.SUN].movement.formatted == 'Direto'
    assert natal.objects[chart.PART_OF_FORTUNE].movement.formatted == 'Estacionária'
    assert natal.objects[chart.SATURN].movement.formatted == 'Retrógrado'


def test_properties_chart_shape(chart_pattern_birth_data):
    settings.locale = 'pt_BR'

    for data in chart_pattern_birth_data.values():
        natal = charts.Natal(charts.Subject(data['dob'], data['latitude'], data['longitude']))
        assert natal.shape == data['shape']


def test_properties_progression_method(native):
    settings.locale = 'pt_BR'

    settings.mc_progression_method = calc.NAIBOD
    progressed_naibod = charts.Progressed(native, '2030-01-01 00:00')
    assert progressed_naibod.progression_method == 'Naibod'

    settings.mc_progression_method = calc.SOLAR_ARC
    progressed_solar_arc = charts.Progressed(native, '2030-01-01 00:00')
    assert progressed_solar_arc.progression_method == 'Arco Solar'

    settings.mc_progression_method = calc.DAILY_HOUSES
    progressed_daily_houses = charts.Progressed(native, '2030-01-01 00:00')
    assert progressed_daily_houses.progression_method == 'Casas Diárias'


def test_formatted_ambiguous_datetime(lat, lon):
    settings.locale = 'pt_BR'
    ambiguous_native = charts.Subject('2022-11-06 01:30', lat, lon)
    natal = charts.Natal(ambiguous_native)
    assert str(natal.native.date_time) == 'Dom Nov 06 2022 01:30:00 PDT (ambíguo)'


def test_formatted_aspect(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert str(natal.aspects[chart.SUN][chart.PART_OF_FORTUNE]) == 'Conjunção entre Sol e Roda da Fortuna dentro de 00°41\'15" (Aplicativa, Associada)'


def test_formatted_object(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert str(natal.objects[chart.SUN]) == 'Sol 10°37\'26" em Capricórnio, Casa 11'
    assert str(natal.objects[chart.ASC]) == 'Ascendente 05°36\'38" em Peixes, Casa 1'
    assert str(natal.houses[chart.HOUSE2]) == 'Casa 2 17°59\'40" em Áries'


def test_formatted_subject(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    assert str(natal.native) == 'Sáb Jan 01 2000 10:00:00 PST em 32N43.0, 117W9.0'


def test_formatted_weightings_elements(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    chart_elements = str(natal.weightings.elements)

    assert 'Fogo' in chart_elements
    assert 'Terra' in chart_elements
    assert 'Ar' in chart_elements
    assert 'Água' in chart_elements


def test_formatted_weightings_modalities(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    chart_modalities = str(natal.weightings.modalities)

    assert 'Cardinal' in chart_modalities
    assert 'Fixo' in chart_modalities
    assert 'Mutável' in chart_modalities


def test_formatted_weightings_quadrants(native):
    settings.locale = 'pt_BR'
    natal = charts.Natal(native)
    chart_quadrants = str(natal.weightings.quadrants)

    assert 'Primeiro' in chart_quadrants
    assert 'Segundo' in chart_quadrants
    assert 'Terceiro' in chart_quadrants
    assert 'Quarto' in chart_quadrants
