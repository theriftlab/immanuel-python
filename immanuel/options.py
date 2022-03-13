"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Provides a simple set of default options that can be overridden.

"""

import os

import swisseph as swe

from immanuel.const import calc, chart, dignities


""" Paths to default & additional ephemeris files for extra chart items,
eg. asteroids or far-out dates. """
default_eph_filepath = f'{os.path.dirname(__file__)}{os.sep}resources{os.sep}ephemeris'

def set_eph_path(path: str = None) -> None:
    eph_filepath = default_eph_filepath

    if path:
        eph_filepath += f';{path}'

    swe.set_ephe_path(eph_filepath)


""" House system as supported by pyswisseph. """
house_system = chart.CAMPANUS


""" Which planets, points etc. to show. """
chart_items = {
    'planets': (
        chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
        chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
    ),
    'asteroids': {
        chart.CHIRON,
    },
    'points': (
        chart.TRUE_NORTH_NODE, chart.TRUE_SOUTH_NODE,
        chart.VERTEX, chart.PARS_FORTUNA,
        chart.TRUE_LILITH,
    ),
}


""" Which aspects to calculate. """
chart_aspects = (
    calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
    calc.SQUARE, calc.QUINCUNX,
)


""" Rules for what chart items can initiate or receive which aspects. """
all_aspects = (
    calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
    calc.SEPTILE, calc.SEMISQUARE, calc.SESQUISQUARE, calc.SEMISEXTILE,
    calc.QUINCUNX, calc.QUINTILE, calc.BIQUINTILE,
)

default_aspect_rule = {
    'initiate': all_aspects,
    'receive': all_aspects,
}

planet_aspect_rule = {
    'initiate': all_aspects,
    'receive': all_aspects,
}

point_aspect_rule = {
    'initiate': (calc.CONJUNCTION,),
    'receive': all_aspects,
}

aspect_rules = {
    chart.ASC: point_aspect_rule,
    chart.DESC: point_aspect_rule,
    chart.MC: point_aspect_rule,
    chart.IC: point_aspect_rule,

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

    chart.NORTH_NODE: point_aspect_rule,
    chart.SOUTH_NODE: point_aspect_rule,
    chart.TRUE_NORTH_NODE: point_aspect_rule,
    chart.TRUE_SOUTH_NODE: point_aspect_rule,
    chart.SYZYGY: point_aspect_rule,
    chart.PARS_FORTUNA: point_aspect_rule,
    chart.VERTEX: point_aspect_rule,
    chart.LILITH: point_aspect_rule,
    chart.TRUE_LILITH: point_aspect_rule,
}


""" Orbs for chart items and their aspects. """
default_orb = 1.0

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
    chart.ASC: planet_orbs,
    chart.DESC: planet_orbs,
    chart.MC: planet_orbs,
    chart.IC: planet_orbs,

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

    chart.NORTH_NODE: point_orbs,
    chart.SOUTH_NODE: point_orbs,
    chart.TRUE_NORTH_NODE: point_orbs,
    chart.TRUE_SOUTH_NODE: point_orbs,
    chart.SYZYGY: point_orbs,
    chart.PARS_FORTUNA: point_orbs,
    chart.VERTEX: point_orbs,
    chart.LILITH: point_orbs,
    chart.TRUE_LILITH: point_orbs,
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
    dignities.DOMICILE: 5,
    dignities.MUTUAL_RECEPTION_HOUSE: 5,
    dignities.EXALTED: 4,
    dignities.MUTUAL_RECEPTION_EXALTATION: 4,
    dignities.TRIPLICITY_RULER: 3,
    dignities.TERM_RULER: 2,
    dignities.FACE_RULER: 1,
    dignities.FALL: -4,
    dignities.DETRIMENT: -5,
    dignities.PEREGRINE: -5,
}
