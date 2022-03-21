"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Provides a simple set of default options that can be overridden.

"""

import os

import swisseph as swe

from immanuel.const import calc, chart, dignities


_file_path = None


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


""" House system as supported by pyswisseph. """
house_system = chart.PLACIDUS


""" Which planets, points etc. to show. """
chart_items = {
    chart.POINTS: (
        chart.TRUE_NORTH_NODE, chart.TRUE_SOUTH_NODE,
        chart.VERTEX, chart.PARS_FORTUNA,
        chart.TRUE_LILITH,
    ),
    chart.PLANETS: (
        chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
        chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
        chart.CHIRON,
    ),
}


""" Which aspects to calculate. """
aspects = (
    calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
    calc.SQUARE, calc.QUINCUNX,
)


""" Rules for what chart items can initiate or receive which aspects. """
default_aspect_rule = {
    'initiate': aspects,
    'receive': aspects,
}

planet_aspect_rule = {
    'initiate': aspects,
    'receive': aspects,
}

point_aspect_rule = {
    'initiate': (calc.CONJUNCTION,),
    'receive': aspects,
}

aspect_rules = {
    chart.ANGLES: {
        chart.ASC: point_aspect_rule,
        chart.DESC: point_aspect_rule,
        chart.MC: point_aspect_rule,
        chart.IC: point_aspect_rule,
    },

    chart.PLANETS: {
        chart.SUN: planet_aspect_rule,
        chart.MOON: planet_aspect_rule,
        chart.MERCURY: planet_aspect_rule,
        chart.VENUS: planet_aspect_rule,
        chart.MARS: planet_aspect_rule,
        chart.JUPITER: planet_aspect_rule,
        chart.SATURN: planet_aspect_rule,
        chart.URANUS: planet_aspect_rule,
        chart.NEPTUNE: planet_aspect_rule,
        chart.PLUTO: planet_aspect_rule,
    },

    chart.POINTS: {
        chart.NORTH_NODE: point_aspect_rule,
        chart.SOUTH_NODE: point_aspect_rule,
        chart.TRUE_NORTH_NODE: point_aspect_rule,
        chart.TRUE_SOUTH_NODE: point_aspect_rule,
        chart.SYZYGY: point_aspect_rule,
        chart.PARS_FORTUNA: point_aspect_rule,
        chart.VERTEX: point_aspect_rule,
        chart.LILITH: point_aspect_rule,
        chart.TRUE_LILITH: point_aspect_rule,
    },
}


""" Orbs for chart items and their aspects. """
default_orb = 1.0

exact_orb = 0.3

orb_calculation = calc.MEAN

planet_orbs = {
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

point_orbs = {
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

orbs = {
    chart.ANGLES: {
        chart.ASC: planet_orbs,
        chart.DESC: planet_orbs,
        chart.MC: planet_orbs,
        chart.IC: planet_orbs,
    },

    chart.PLANETS: {
        chart.SUN: planet_orbs,
        chart.MOON: planet_orbs,
        chart.MERCURY: planet_orbs,
        chart.VENUS: planet_orbs,
        chart.MARS: planet_orbs,
        chart.JUPITER: planet_orbs,
        chart.SATURN: planet_orbs,
        chart.URANUS: planet_orbs,
        chart.NEPTUNE: planet_orbs,
        chart.PLUTO: planet_orbs,
    },

    chart.POINTS: {
        chart.NORTH_NODE: point_orbs,
        chart.SOUTH_NODE: point_orbs,
        chart.TRUE_NORTH_NODE: point_orbs,
        chart.TRUE_SOUTH_NODE: point_orbs,
        chart.SYZYGY: point_orbs,
        chart.PARS_FORTUNA: point_orbs,
        chart.VERTEX: point_orbs,
        chart.LILITH: point_orbs,
        chart.TRUE_LILITH: point_orbs,
    },
}


""" MC progression formula for secondary progressions. """
mc_progression = calc.NAIBOD


""" Part of fortune formula. """
pars_fortuna = calc.DAY_NIGHT_FORMULA


""" Dignity settings. """
rulerships = dignities.MODERN_RULERSHIPS

triplicities = dignities.PTOLEMAIC_TRIPLICITIES

terms = dignities.EGYPTIAN_TERMS

peregrine = dignities.INCLUDE_MUTUAL_RECEPTIONS

dignity_scores = {
    dignities.RULER: 5,
    dignities.MUTUAL_RECEPTION_HOUSE: 5,
    dignities.EXALTED: 4,
    dignities.MUTUAL_RECEPTION_EXALTATION: 4,
    dignities.TRIPLICITY_RULER_DAY: 3,
    dignities.TRIPLICITY_RULER_NIGHT: 3,
    dignities.TRIPLICITY_RULER_PARTICIPATORY: 3,
    dignities.TERM_RULER: 2,
    dignities.FACE_RULER: 1,
    dignities.FALL: -4,
    dignities.DETRIMENT: -5,
    dignities.PEREGRINE: -5,
}
