"""
This file is part of immanuel - (C) The Rift Lab
Authors: Robert Davies (robert@theriftlab.com) and Nathan Octavio


Gendered list of relevant nouns for correct adjective translation.

"""

from immanuel.const import calc, chart, contexts

CONTEXTS = {
    contexts.GENDERS: {
        chart.ASC: contexts.MASCULINE,
        chart.DESC: contexts.MASCULINE,
        chart.MC: contexts.MASCULINE,
        chart.IC: contexts.MASCULINE,
        chart.ARMC: contexts.MASCULINE,
        chart.SUN: contexts.MASCULINE,
        chart.MOON: contexts.FEMININE,
        chart.MERCURY: contexts.MASCULINE,
        chart.VENUS: contexts.FEMININE,
        chart.MARS: contexts.MASCULINE,
        chart.JUPITER: contexts.MASCULINE,
        chart.SATURN: contexts.MASCULINE,
        chart.URANUS: contexts.MASCULINE,
        chart.NEPTUNE: contexts.MASCULINE,
        chart.PLUTO: contexts.MASCULINE,
        chart.CHIRON: contexts.MASCULINE,
        chart.PHOLUS: contexts.MASCULINE,
        chart.CERES: contexts.FEMININE,
        chart.PALLAS: contexts.FEMININE,
        chart.JUNO: contexts.FEMININE,
        chart.VESTA: contexts.FEMININE,
        chart.NORTH_NODE: contexts.MASCULINE,
        chart.SOUTH_NODE: contexts.MASCULINE,
        chart.TRUE_NORTH_NODE: contexts.MASCULINE,
        chart.TRUE_SOUTH_NODE: contexts.MASCULINE,
        chart.VERTEX: contexts.MASCULINE,
        chart.LILITH: contexts.FEMININE,
        chart.TRUE_LILITH: contexts.FEMININE,
        chart.INTERPOLATED_LILITH: contexts.FEMININE,
        chart.SYZYGY: contexts.FEMININE,
        chart.PART_OF_FORTUNE: contexts.FEMININE,
        chart.PART_OF_SPIRIT: contexts.FEMININE,
        chart.PART_OF_EROS: contexts.FEMININE,
        chart.PRE_NATAL_SOLAR_ECLIPSE: contexts.MASCULINE,
        chart.PRE_NATAL_LUNAR_ECLIPSE: contexts.MASCULINE,
        chart.POST_NATAL_SOLAR_ECLIPSE: contexts.MASCULINE,
        chart.POST_NATAL_LUNAR_ECLIPSE: contexts.MASCULINE,
        calc.CONJUNCTION: contexts.FEMININE,
        calc.OPPOSITION: contexts.FEMININE,
        calc.SQUARE: contexts.FEMININE,
        calc.TRINE: contexts.MASCULINE,
        calc.SEXTILE: contexts.MASCULINE,
        calc.SEPTILE: contexts.MASCULINE,
        calc.SEMISQUARE: contexts.FEMININE,
        calc.SESQUISQUARE: contexts.FEMININE,
        calc.SEMISEXTILE: contexts.MASCULINE,
        calc.QUINCUNX: contexts.MASCULINE,
        calc.QUINTILE: contexts.MASCULINE,
        calc.BIQUINTILE: contexts.MASCULINE,
    }
}
