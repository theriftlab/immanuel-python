"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Provides a simple set of default settings that can be overridden.
    Also allows filepath(s) to ephermeris files to be changed or added.

"""

import os
from typing import Any

import swisseph as swe

from immanuel.const import calc, chart, data, dignities


_file_path = None

_settings = {}


""" Data that should be included for each chart type's output. """
_settings['chart_data'] = {
    chart.NATAL: [
        data.NATAL_DATE,
        data.COORDINATES,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.SOLAR_RETURN: [
        data.NATAL_DATE,
        data.SOLAR_RETURN_YEAR,
        data.SOLAR_RETURN_DATE,
        data.COORDINATES,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.PROGRESSED: [
        data.NATAL_DATE,
        data.PROGRESSION_DATE,
        data.PROGRESSED_DATE,
        data.PROGRESSION_METHOD,
        data.COORDINATES,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.SYNASTRY: [
        data.NATAL_DATE,
        data.COORDINATES,
        data.PARTNER_DATE,
        data.PARTNER_COORDINATES,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.PARTNER_SHAPE,
        data.DIURNAL,
        data.PARTNER_DIURNAL,
        data.MOON_PHASE,
        data.PARTNER_MOON_PHASE,
        data.OBJECTS,
        data.PARTNER_OBJECTS,
        data.HOUSES,
        data.PARTNER_HOUSES,
        data.ASPECTS,
        data.PARTNER_ASPECTS,
        data.WEIGHTINGS,
        data.PARTNER_WEIGHTINGS,
    ],
    chart.COMPOSITE: [
        data.NATAL_DATE,
        data.COORDINATES,
        data.PARTNER_DATE,
        data.PARTNER_COORDINATES,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
}


""" House system as supported by pyswisseph. """
_settings['house_system'] = chart.PLACIDUS

""" Which planets, points etc. to show. """
_settings['objects'] = [
    chart.ASC, chart.DESC, chart.MC, chart.IC,
    chart.TRUE_NORTH_NODE, chart.TRUE_SOUTH_NODE,
    chart.VERTEX, chart.PARS_FORTUNA,
    chart.TRUE_LILITH,
    chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
    chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
    chart.CHIRON,
]

""" Which planets, points etc. to use in chart shape calculations. """
_settings['chart_shape_objects'] = [
    chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
    chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
]

""" Which aspects to calculate. """
_settings['aspects'] = [
    calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
    calc.QUINCUNX,
]

""" Rules for what chart objects can initiate or receive which aspects. """
_settings['default_aspect_rule'] = {
    'initiate': _settings['aspects'],
    'receive': _settings['aspects'],
}

_settings['planet_aspect_rule'] = {
    'initiate': _settings['aspects'],
    'receive': _settings['aspects'],
}

_settings['point_aspect_rule'] = {
    'initiate': (calc.CONJUNCTION,),
    'receive': _settings['aspects'],
}

_settings['aspect_rules'] = {
    chart.ASC: _settings['point_aspect_rule'],
    chart.DESC: _settings['point_aspect_rule'],
    chart.MC: _settings['point_aspect_rule'],
    chart.IC: _settings['point_aspect_rule'],

    chart.SUN: _settings['planet_aspect_rule'],
    chart.MOON: _settings['planet_aspect_rule'],
    chart.MERCURY: _settings['planet_aspect_rule'],
    chart.VENUS: _settings['planet_aspect_rule'],
    chart.MARS: _settings['planet_aspect_rule'],
    chart.JUPITER: _settings['planet_aspect_rule'],
    chart.SATURN: _settings['planet_aspect_rule'],
    chart.URANUS: _settings['planet_aspect_rule'],
    chart.NEPTUNE: _settings['planet_aspect_rule'],
    chart.PLUTO: _settings['planet_aspect_rule'],

    chart.NORTH_NODE: _settings['point_aspect_rule'],
    chart.SOUTH_NODE: _settings['point_aspect_rule'],
    chart.TRUE_NORTH_NODE: _settings['point_aspect_rule'],
    chart.TRUE_SOUTH_NODE: _settings['point_aspect_rule'],
    chart.SYZYGY: _settings['point_aspect_rule'],
    chart.PARS_FORTUNA: _settings['point_aspect_rule'],
    chart.VERTEX: _settings['point_aspect_rule'],
    chart.LILITH: _settings['point_aspect_rule'],
    chart.TRUE_LILITH: _settings['point_aspect_rule'],
}


""" Orbs for chart objects and their aspects. """
_settings['default_orb'] = 1.0

_settings['exact_orb'] = 0.3

_settings['orb_calculation'] = calc.MEAN

_settings['planet_orbs'] = {
    calc.CONJUNCTION: 10.0,
    calc.OPPOSITION: 10.0,
    calc.SQUARE: 10.0,
    calc.TRINE: 10.0,
    calc.SEXTILE: 6.0,
    calc.SEPTILE: 3.0,
    calc.SEMISQUARE: 3.0,
    calc.SESQUISQUARE: 3.0,
    calc.SEMISEXTILE: 3.0,
    calc.QUINCUNX: 3.0,
    calc.QUINTILE: 2.0,
    calc.BIQUINTILE: 2.0,
}

_settings['point_orbs'] = {
    calc.CONJUNCTION: 0.0,
    calc.OPPOSITION: 0.0,
    calc.SQUARE: 0.0,
    calc.TRINE: 0.0,
    calc.SEXTILE: 0.0,
    calc.SEPTILE: 0.0,
    calc.SEMISQUARE: 0.0,
    calc.SESQUISQUARE: 0.0,
    calc.SEMISEXTILE: 0.0,
    calc.QUINCUNX: 0.0,
    calc.QUINTILE: 0.0,
    calc.BIQUINTILE: 0.0,
}

_settings['orbs'] = {
    chart.ASC: _settings['planet_orbs'],
    chart.DESC: _settings['planet_orbs'],
    chart.MC: _settings['planet_orbs'],
    chart.IC: _settings['planet_orbs'],

    chart.SUN: _settings['planet_orbs'],
    chart.MOON: _settings['planet_orbs'],
    chart.MERCURY: _settings['planet_orbs'],
    chart.VENUS: _settings['planet_orbs'],
    chart.MARS: _settings['planet_orbs'],
    chart.JUPITER: _settings['planet_orbs'],
    chart.SATURN: _settings['planet_orbs'],
    chart.URANUS: _settings['planet_orbs'],
    chart.NEPTUNE: _settings['planet_orbs'],
    chart.PLUTO: _settings['planet_orbs'],

    chart.NORTH_NODE: _settings['point_orbs'],
    chart.SOUTH_NODE: _settings['point_orbs'],
    chart.TRUE_NORTH_NODE: _settings['point_orbs'],
    chart.TRUE_SOUTH_NODE: _settings['point_orbs'],
    chart.SYZYGY: _settings['point_orbs'],
    chart.PARS_FORTUNA: _settings['point_orbs'],
    chart.VERTEX: _settings['point_orbs'],
    chart.LILITH: _settings['point_orbs'],
    chart.TRUE_LILITH: _settings['point_orbs'],
}


""" Orb for calculating chart shapes. """
_settings['chart_shape_orb'] = 5.0


""" MC progression formula for secondary progressions. """
_settings['mc_progression_method'] = calc.NAIBOD


""" Part of Fortune formula. """
_settings['pars_fortuna_formula'] = calc.DAY_NIGHT_FORMULA


""" Composite Part of Fortune calculation. """
_settings['composite_pars_fortuna'] = calc.MIDPOINT


""" Composite house cusp calculation. """
_settings['composite_houses'] = calc.MIDPOINT


""" Dignity settings. """
_settings['rulerships'] = dignities.MODERN_RULERSHIPS

_settings['triplicities'] = dignities.PTOLEMAIC_TRIPLICITIES

_settings['terms'] = dignities.EGYPTIAN_TERMS

_settings['include_participatory_triplicities'] = False

_settings['include_mutual_receptions'] = True

_settings['dignity_scores'] = {
    dignities.RULER: 5,
    dignities.EXALTED: 4,
    dignities.TRIPLICITY_RULER: 3,
    dignities.TERM_RULER: 2,
    dignities.FACE_RULER: 1,
    dignities.MUTUAL_RECEPTION_RULER: 5,
    dignities.MUTUAL_RECEPTION_EXALTED: 4,
    dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER: 3,
    dignities.MUTUAL_RECEPTION_TERM_RULER: 2,
    dignities.MUTUAL_RECEPTION_FACE_RULER: 1,
    dignities.DETRIMENT: -5,
    dignities.FALL: -4,
    dignities.PEREGRINE: -5,
}


def set_filepath(path) -> None:
    """ Set the main file path for ephemeris files. """
    global _file_path
    _file_path = path
    swe.set_ephe_path(_file_path)


def add_filepath(path) -> None:
    """ Append a file path to the main one for custom extras. """
    global _file_path
    extra_path = f'{os.pathsep}{path}'

    if _file_path.endswith(extra_path):
        return

    _file_path += extra_path
    swe.set_ephe_path(_file_path)


class settings(type):
    """ Very simple class to keep track of settings. Default settings are preset
    and can be overridden in bulk with set() or singly attribute-style. """
    def dict(self) -> dict:
        return _settings

    def set(self, settings: dict) -> None:
        _settings.update(settings)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in _settings:
            self.set({
                name: value
            })

    def __getattr__(self, name) -> Any:
        return _settings[name]


class settings(metaclass=settings):
    pass
