"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    User-facing names for chart data items.

"""

from immanuel.const import calc, chart


SIGNS = {
    chart.ARIES: 'Aries',
    chart.TAURUS: 'Taurus',
    chart.GEMINI: 'Gemini',
    chart.CANCER: 'Cancer',
    chart.LEO: 'Leo',
    chart.VIRGO: 'Virgo',
    chart.LIBRA: 'Libra',
    chart.SCORPIO: 'Scorpio',
    chart.SAGITTARIUS: 'Sagittarius',
    chart.CAPRICORN: 'Capricorn',
    chart.AQUARIUS: 'Aquarius',
    chart.PISCES: 'Pisces',
}

ANGLES = {
    chart.ASC: 'Asc',
    chart.DESC: 'Desc',
    chart.MC: 'MC',
    chart.IC: 'IC',
    chart.ARMC: 'ARMC',
}

PLANETS = {
    chart.SUN: 'Sun',
    chart.MOON: 'Moon',
    chart.MERCURY: 'Mercury',
    chart.VENUS: 'Venus',
    chart.MARS: 'Mars',
    chart.JUPITER: 'Jupiter',
    chart.SATURN: 'Saturn',
    chart.URANUS: 'Uranus',
    chart.NEPTUNE: 'Neptune',
    chart.PLUTO: 'Pluto',
}

ASPECTS = {
    calc.CONJUNCTION: 'Conjunction',
    calc.OPPOSITION: 'Opposition',
    calc.SQUARE: 'Square',
    calc.TRINE: 'Trine',
    calc.SEXTILE: 'Sextile',
    calc.SEPTILE: 'Septile',
    calc.SEMISQUARE: 'Semisquare',
    calc.SESQUISQUARE: 'Sesquisquare',
    calc.SEMISEXTILE: 'Semisextile',
    calc.QUINCUNX: 'Quincunx',
    calc.QUINTILE: 'Quintile',
    calc.BIQUINTILE: 'Biquintile',
}
