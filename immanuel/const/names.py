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

HOUSE_SYSTEMS = {
    chart.ALCABITUS: 'Alcabitus',
    chart.AZIMUTHAL: 'Azimuthal',
    chart.CAMPANUS: 'Campanus',
    chart.EQUAL: 'Equal House',
    chart.KOCH: 'Koch',
    chart.MERIDIAN: 'Meridian',
    chart.MORINUS: 'Morinus',
    chart.PLACIDUS: 'Placidus',
    chart.POLICH_PAGE: 'Polich Page',
    chart.PORPHYRIUS: 'Porphyrius',
    chart.REGIOMONTANUS: 'Regiomontanus',
    chart.VEHLOW_EQUAL: 'Vehlow Equal House',
    chart.WHOLE_SIGN: 'Whole Sign',
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
    chart.CHIRON: 'Chiron',
    chart.PHOLUS: 'Pholus',
    chart.CERES: 'Ceres',
    chart.PALLAS: 'Pallas',
    chart.JUNO: 'Juno',
    chart.VESTA: 'Vesta',
}

POINTS = {
    chart.NORTH_NODE: 'North Node',
    chart.SOUTH_NODE: 'South Node',
    chart.TRUE_NORTH_NODE: 'True North Node',
    chart.TRUE_SOUTH_NODE: 'True South Node',
    chart.VERTEX: 'Vertex',
    chart.LILITH: 'Lilith',
    chart.TRUE_LILITH: 'True Lilith',
    chart.SYZYGY: 'Syzygy',
    chart.PARS_FORTUNA: 'Part of Fortune',
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

MOON_PHASES = {
    calc.NEW_MOON: 'New',
    calc.WAXING_CRESCENT: 'Waxing Crescent',
    calc.FIRST_QUARTER: 'First Quarter',
    calc.WAXING_GIBBOUS: 'Waxing Gibbous',
    calc.FULL_MOON: 'Full',
    calc.DISSEMINATING: 'Disseminating',
    calc.THIRD_QUARTER: 'Third Quarter',
    calc.BALSAMIC: 'Balsamic',
}

CHART_SHAPES = {
    calc.BUNDLE: 'Bundle',
    calc.LOCOMOTIVE: 'Locomotive',
    calc.SPLAY: 'Splay',
    calc.BOWL: 'Bowl',
    calc.BUCKET: 'Bucket',
    calc.SEESAW: 'Seesaw',
    calc.SPLASH: 'Splash',
}