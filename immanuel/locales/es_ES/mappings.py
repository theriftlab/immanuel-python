"""
    This file is part of immanuel - (C) The Rift Lab
    Authors: Robert Davies (robert@theriftlab.com) and Nathan Octavio


    Gendered list of relevant nouns for correct adjective translation.

"""

from immanuel.const import calc, chart, genders


GENDERS = {
    chart.ASC: genders.MASCULINE,
    chart.DESC: genders.MASCULINE,
    chart.MC: genders.MASCULINE,
    chart.IC: genders.MASCULINE,
    chart.ARMC: genders.MASCULINE,

    chart.SUN: genders.MASCULINE,
    chart.MOON: genders.FEMININE,
    chart.MERCURY: genders.MASCULINE,
    chart.VENUS: genders.FEMININE,
    chart.MARS: genders.MASCULINE,
    chart.JUPITER: genders.MASCULINE,
    chart.SATURN: genders.MASCULINE,
    chart.URANUS: genders.MASCULINE,
    chart.NEPTUNE: genders.MASCULINE,
    chart.PLUTO: genders.MASCULINE,

    chart.CHIRON: genders.MASCULINE,
    chart.PHOLUS: genders.MASCULINE,
    chart.CERES: genders.FEMININE,
    chart.PALLAS: genders.FEMININE,
    chart.JUNO: genders.FEMININE,
    chart.VESTA: genders.FEMININE,

    chart.NORTH_NODE: genders.MASCULINE,
    chart.SOUTH_NODE: genders.MASCULINE,
    chart.TRUE_NORTH_NODE: genders.MASCULINE,
    chart.TRUE_SOUTH_NODE: genders.MASCULINE,
    chart.VERTEX: genders.MASCULINE,
    chart.LILITH: genders.FEMININE,
    chart.TRUE_LILITH: genders.FEMININE,
    chart.INTERPOLATED_LILITH: genders.FEMININE,
    chart.SYZYGY: genders.FEMININE,
    chart.PART_OF_FORTUNE: genders.FEMININE,
    chart.PART_OF_SPIRIT: genders.FEMININE,
    chart.PART_OF_EROS: genders.FEMININE,

    chart.PRE_NATAL_SOLAR_ECLIPSE: genders.MASCULINE,
    chart.PRE_NATAL_LUNAR_ECLIPSE: genders.MASCULINE,
    chart.POST_NATAL_SOLAR_ECLIPSE: genders.MASCULINE,
    chart.POST_NATAL_LUNAR_ECLIPSE: genders.MASCULINE,

    calc.CONJUNCTION: genders.FEMININE,
    calc.OPPOSITION: genders.FEMININE,
    calc.SQUARE: genders.FEMININE,
    calc.TRINE: genders.MASCULINE,
    calc.SEXTILE: genders.MASCULINE,
    calc.SEPTILE: genders.MASCULINE,
    calc.SEMISQUARE: genders.FEMININE,
    calc.SESQUISQUARE: genders.FEMININE,
    calc.SEMISEXTILE: genders.MASCULINE,
    calc.QUINCUNX: genders.MASCULINE,
    calc.QUINTILE: genders.MASCULINE,
    calc.BIQUINTILE: genders.MASCULINE,
}
