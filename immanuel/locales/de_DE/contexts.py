"""
This file is part of immanuel - (C) The Rift Lab
Authors: Robert Davies (robert@theriftlab.com) and @cosmosandapi


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
        chart.SUN: contexts.FEMININE,
        chart.MOON: contexts.MASCULINE,
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
        chart.PART_OF_FORTUNE: contexts.MASCULINE,
        chart.PART_OF_SPIRIT: contexts.MASCULINE,
        chart.PART_OF_EROS: contexts.MASCULINE,
        chart.PRE_NATAL_SOLAR_ECLIPSE: contexts.FEMININE,
        chart.PRE_NATAL_LUNAR_ECLIPSE: contexts.FEMININE,
        chart.POST_NATAL_SOLAR_ECLIPSE: contexts.FEMININE,
        chart.POST_NATAL_LUNAR_ECLIPSE: contexts.FEMININE,
        calc.CONJUNCTION: contexts.FEMININE,
        calc.OPPOSITION: contexts.FEMININE,
        calc.SQUARE: contexts.NEUTER,
        calc.TRINE: contexts.NEUTER,
        calc.SEXTILE: contexts.NEUTER,
        calc.SEPTILE: contexts.NEUTER,
        calc.SEMISQUARE: contexts.NEUTER,
        calc.SESQUISQUARE: contexts.NEUTER,
        calc.SEMISEXTILE: contexts.NEUTER,
        calc.QUINCUNX: contexts.NEUTER,
        calc.QUINTILE: contexts.NEUTER,
        calc.BIQUINTILE: contexts.NEUTER,
    }
}
