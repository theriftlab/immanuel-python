"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Defines essential dignities and their associated tables.

"""

from immanuel.const import chart


""" Indices for reference. """
RULER = 0
EXALTED = 1
TRIPLICITY_RULER = 2
TERM_RULER = 3
FACE_RULER = 4
MUTUAL_RECEPTION_RULER = 5
MUTUAL_RECEPTION_EXALTED = 6
MUTUAL_RECEPTION_TRIPLICITY_RULER = 7
MUTUAL_RECEPTION_TERM_RULER = 8
MUTUAL_RECEPTION_FACE_RULER = 9
IN_RULERSHIP_ELEMENT = 10
DETRIMENT = 11
FALL = 12
PEREGRINE = 13


""" Modern rulerships. """
MODERN_RULERSHIPS = {
    chart.ARIES: chart.MARS,
    chart.TAURUS: chart.VENUS,
    chart.GEMINI: chart.MERCURY,
    chart.CANCER: chart.MOON,
    chart.LEO: chart.SUN,
    chart.VIRGO: chart.MERCURY,
    chart.LIBRA: chart.VENUS,
    chart.SCORPIO: chart.PLUTO,
    chart.SAGITTARIUS: chart.JUPITER,
    chart.CAPRICORN: chart.SATURN,
    chart.AQUARIUS: chart.URANUS,
    chart.PISCES: chart.NEPTUNE,
}


""" Traditional rulerships. """
TRADITIONAL_RULERSHIPS = {
    chart.ARIES: chart.MARS,
    chart.TAURUS: chart.VENUS,
    chart.GEMINI: chart.MERCURY,
    chart.CANCER: chart.MOON,
    chart.LEO: chart.SUN,
    chart.VIRGO: chart.MERCURY,
    chart.LIBRA: chart.VENUS,
    chart.SCORPIO: chart.MARS,
    chart.SAGITTARIUS: chart.JUPITER,
    chart.CAPRICORN: chart.SATURN,
    chart.AQUARIUS: chart.SATURN,
    chart.PISCES: chart.JUPITER,
}


""" Planets in exaltation. """
EXALTATIONS = {
    chart.ARIES: chart.SUN,
    chart.TAURUS: chart.MOON,
    chart.GEMINI: None,
    chart.CANCER: chart.JUPITER,
    chart.LEO: chart.NEPTUNE,
    chart.VIRGO: chart.MERCURY,
    chart.LIBRA: chart.SATURN,
    chart.SCORPIO: chart.URANUS,
    chart.SAGITTARIUS: None,
    chart.CAPRICORN: chart.MARS,
    chart.AQUARIUS: None,
    chart.PISCES: chart.VENUS,
}


""" Face rulers. """
FACE_RULERS = {
    chart.ARIES: (chart.MARS, chart.SUN, chart.VENUS),
    chart.TAURUS: (chart.MERCURY, chart.MOON, chart.SATURN),
    chart.GEMINI: (chart.JUPITER, chart.MARS, chart.SUN),
    chart.CANCER: (chart.VENUS, chart.MERCURY, chart.MOON),
    chart.LEO: (chart.SATURN, chart.JUPITER, chart.MARS),
    chart.VIRGO: (chart.SUN, chart.VENUS, chart.MERCURY),
    chart.LIBRA: (chart.MOON, chart.SATURN, chart.JUPITER),
    chart.SCORPIO: (chart.MARS, chart.SUN, chart.VENUS),
    chart.SAGITTARIUS: (chart.MERCURY, chart.MOON, chart.SATURN),
    chart.CAPRICORN: (chart.JUPITER, chart.MARS, chart.SUN),
    chart.AQUARIUS: (chart.VENUS, chart.MERCURY, chart.MOON),
    chart.PISCES: (chart.SATURN, chart.JUPITER, chart.MARS),
}


""" Ptolemy's terms. """
PTOLEMAIC_TERMS = {
    chart.ARIES: {
        chart.JUPITER: (0, 6),
        chart.VENUS: (6, 14),
        chart.MERCURY: (14, 21),
        chart.MARS: (21, 26),
        chart.SATURN: (26, 30),
    },
    chart.TAURUS: {
        chart.VENUS: (0, 8),
        chart.MERCURY: (8, 15),
        chart.JUPITER: (15, 22),
        chart.SATURN: (22, 26),
        chart.MARS: (26, 30),
    },
    chart.GEMINI: {
        chart.MERCURY: (0, 7),
        chart.JUPITER: (7, 14),
        chart.VENUS: (14, 21),
        chart.SATURN: (21, 25),
        chart.MARS: (25, 30),
    },
    chart.CANCER: {
        chart.MARS: (0, 6),
        chart.JUPITER: (6, 13),
        chart.MERCURY: (13, 20),
        chart.VENUS: (20, 27),
        chart.SATURN: (27, 30),
    },
    chart.LEO: {
        chart.SATURN: (0, 6),
        chart.MERCURY: (6, 13),
        chart.VENUS: (13, 19),
        chart.JUPITER: (19, 25),
        chart.MARS: (25, 30),
    },
    chart.VIRGO: {
        chart.MERCURY: (0, 7),
        chart.VENUS: (7, 13),
        chart.JUPITER: (13, 18),
        chart.SATURN: (18, 24),
        chart.MARS: (24, 30),
    },
    chart.LIBRA: {
        chart.SATURN: (0, 6),
        chart.VENUS: (6, 11),
        chart.JUPITER: (11, 19),
        chart.MERCURY: (19, 24),
        chart.MARS: (24, 30),
    },
    chart.SCORPIO: {
        chart.MARS: (0, 6),
        chart.JUPITER: (6, 14),
        chart.VENUS: (14, 21),
        chart.MERCURY: (21, 27),
        chart.SATURN: (27, 30),
    },
    chart.SAGITTARIUS: {
        chart.JUPITER: (0, 8),
        chart.VENUS: (8, 14),
        chart.MERCURY: (14, 19),
        chart.SATURN: (19, 25),
        chart.MARS: (25, 30),
    },
    chart.CAPRICORN: {
        chart.VENUS: (0, 6),
        chart.MERCURY: (6, 12),
        chart.JUPITER: (12, 19),
        chart.MARS: (19, 25),
        chart.SATURN: (25, 30),
    },
    chart.AQUARIUS: {
        chart.SATURN: (0, 6),
        chart.MERCURY: (6, 12),
        chart.VENUS: (12, 20),
        chart.JUPITER: (20, 25),
        chart.MARS: (25, 30),
    },
    chart.PISCES: {
        chart.VENUS: (0, 8),
        chart.JUPITER: (8, 14),
        chart.MERCURY: (14, 20),
        chart.MARS: (20, 26),
        chart.SATURN: (26, 30),
    },
}


""" Egyptian terms. """
EGYPTIAN_TERMS = {
    chart.ARIES: {
        chart.JUPITER: (0, 6),
        chart.VENUS: (6, 12),
        chart.MERCURY: (12, 20),
        chart.MARS: (20, 25),
        chart.SATURN: (25, 30),
    },
    chart.TAURUS: {
        chart.VENUS: (0, 8),
        chart.MERCURY: (8, 14),
        chart.JUPITER: (14, 22),
        chart.SATURN: (22, 27),
        chart.MARS: (27, 30),
    },
    chart.GEMINI: {
        chart.MERCURY: (0, 6),
        chart.JUPITER: (6, 12),
        chart.VENUS: (12, 17),
        chart.MARS: (17, 24),
        chart.SATURN: (24, 30),
    },
    chart.CANCER: {
        chart.MARS: (0, 7),
        chart.VENUS: (7, 13),
        chart.MERCURY: (13, 19),
        chart.JUPITER: (19, 26),
        chart.SATURN: (26, 30),
    },
    chart.LEO: {
        chart.JUPITER: (0, 6),
        chart.VENUS: (6, 11),
        chart.SATURN: (11, 18),
        chart.MERCURY: (18, 24),
        chart.MARS: (24, 30),
    },
    chart.VIRGO: {
        chart.MERCURY: (0, 7),
        chart.VENUS: (7, 17),
        chart.JUPITER: (17, 21),
        chart.MARS: (21, 28),
        chart.SATURN: (28, 30),
    },
    chart.LIBRA: {
        chart.SATURN: (0, 6),
        chart.MERCURY: (6, 14),
        chart.JUPITER: (14, 21),
        chart.VENUS: (21, 28),
        chart.MARS: (28, 30),
    },
    chart.SCORPIO: {
        chart.MARS: (0, 7),
        chart.VENUS: (7, 11),
        chart.MERCURY: (11, 19),
        chart.JUPITER: (19, 24),
        chart.SATURN: (24, 30),
    },
    chart.SAGITTARIUS: {
        chart.JUPITER: (0, 12),
        chart.VENUS: (12, 17),
        chart.MERCURY: (17, 21),
        chart.SATURN: (21, 26),
        chart.MARS: (26, 30),
    },
    chart.CAPRICORN: {
        chart.MERCURY: (0, 7),
        chart.JUPITER: (7, 14),
        chart.VENUS: (14, 22),
        chart.SATURN: (22, 26),
        chart.MARS: (26, 30),
    },
    chart.AQUARIUS: {
        chart.MERCURY: (0, 7),
        chart.VENUS: (7, 13),
        chart.JUPITER: (13, 20),
        chart.MARS: (20, 25),
        chart.SATURN: (25, 30),
    },
    chart.PISCES: {
        chart.VENUS: (0, 12),
        chart.JUPITER: (12, 16),
        chart.MERCURY: (16, 19),
        chart.MARS: (19, 28),
        chart.SATURN: (28, 30),
    },
}


""" Ptolemy's triplicities. """
PTOLEMAIC_TRIPLICITIES = {
    chart.ARIES: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.MARS,
    },
    chart.TAURUS: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.SATURN,
    },
    chart.GEMINI: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.CANCER: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
    chart.LEO: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.MARS,
    },
    chart.VIRGO: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.SATURN,
    },
    chart.LIBRA: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.SCORPIO: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
    chart.SAGITTARIUS: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.MARS,
    },
    chart.CAPRICORN: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.SATURN,
    },
    chart.AQUARIUS: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.PISCES: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
}


""" Lilly's triplicities. """
LILLEAN_TRIPLICITIES = {
    chart.ARIES: {
        'day': chart.SUN,
        'night': chart.JUPITER,
    },
    chart.TAURUS: {
        'day': chart.VENUS,
        'night': chart.MOON,
    },
    chart.GEMINI: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
    },
    chart.CANCER: {
        'day': chart.MARS,
        'night': chart.MARS,
    },
    chart.LEO: {
        'day': chart.SUN,
        'night': chart.JUPITER,
    },
    chart.VIRGO: {
        'day': chart.VENUS,
        'night': chart.MOON,
    },
    chart.LIBRA: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
    },
    chart.SCORPIO: {
        'day': chart.MARS,
        'night': chart.MARS,
    },
    chart.SAGITTARIUS: {
        'day': chart.SUN,
        'night': chart.JUPITER,
    },
    chart.CAPRICORN: {
        'day': chart.VENUS,
        'night': chart.MOON,
    },
    chart.AQUARIUS: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
    },
    chart.PISCES: {
        'day': chart.MARS,
        'night': chart.MARS,
    },
}


""" Dorotheus' triplicities. """
DOROTHEAN_TRIPLICITIES = {
    chart.ARIES: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.SATURN,
    },
    chart.TAURUS: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
    chart.GEMINI: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.CANCER: {
        'day': chart.VENUS,
        'night': chart.MARS,
        'participatory': chart.MOON,
    },
    chart.LEO: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.SATURN,
    },
    chart.VIRGO: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
    chart.LIBRA: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.SCORPIO: {
        'day': chart.VENUS,
        'night': chart.MARS,
        'participatory': chart.MOON,
    },
    chart.SAGITTARIUS: {
        'day': chart.SUN,
        'night': chart.JUPITER,
        'participatory': chart.SATURN,
    },
    chart.CAPRICORN: {
        'day': chart.VENUS,
        'night': chart.MOON,
        'participatory': chart.MARS,
    },
    chart.AQUARIUS: {
        'day': chart.SATURN,
        'night': chart.MERCURY,
        'participatory': chart.JUPITER,
    },
    chart.PISCES: {
        'day': chart.VENUS,
        'night': chart.MARS,
        'participatory': chart.MOON,
    },
}
