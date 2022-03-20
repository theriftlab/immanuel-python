"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Defines indices for the main chart items supported by pyswisseph,
    along with custom-calculated items based on pyswisseph. These
    constants are mainly used by the eph module.

"""

import swisseph as swe


""" When items not supported by pyswisseph need to be custom-calculated
based on its supported items (eg. IC from MC) Immanuel creates its own index
by adding this offset. """
CALCULATED_OFFSET = 100

""" Signs. """
SIGNS = 0
ARIES = 1
TAURUS = 2
GEMINI = 3
CANCER = 4
LEO = 5
VIRGO = 6
LIBRA = 7
SCORPIO = 8
SAGITTARIUS = 9
CAPRICORN = 10
AQUARIUS = 11
PISCES = 12

""" Houses. """
HOUSES = 1

""" House systems. """
HOUSE_SYSTEMS = 2
ALCABITUS = b'B'
AZIMUTHAL = b'H'
CAMPANUS = b'C'
EQUAL = b'A'
KOCH = b'K'
MERIDIAN = b'X'
MORINUS = b'M'
PLACIDUS = b'P'
POLICH_PAGE = b'T'
PORPHYRIUS = b'O'
REGIOMONTANUS = b'R'
VEHLOW_EQUAL = b'V'
WHOLE_SIGN = b'W'

""" Major chart angles. """
ANGLES = 3
ASC = swe.ASC
DESC = swe.ASC + CALCULATED_OFFSET
MC = swe.MC
IC = swe.MC + CALCULATED_OFFSET
ARMC = swe.ARMC

""" Planets & major asteroids we treat as planets. """
PLANETS = 4
SUN = swe.SUN
MOON = swe.MOON
MERCURY = swe.MERCURY
VENUS = swe.VENUS
MARS = swe.MARS
JUPITER = swe.JUPITER
SATURN = swe.SATURN
URANUS = swe.URANUS
NEPTUNE = swe.NEPTUNE
PLUTO = swe.PLUTO
CHIRON = swe.CHIRON
PHOLUS = swe.PHOLUS
CERES = swe.CERES
PALLAS = swe.PALLAS
JUNO = swe.JUNO
VESTA = swe.VESTA

""" Custom asteroids. """
ASTEROIDS = 5

""" Main calculated points. """
POINTS = 6
NORTH_NODE = swe.MEAN_NODE
SOUTH_NODE = swe.MEAN_NODE + CALCULATED_OFFSET
TRUE_NORTH_NODE = swe.TRUE_NODE
TRUE_SOUTH_NODE = swe.TRUE_NODE + CALCULATED_OFFSET
VERTEX = swe.VERTEX
LILITH = swe.MEAN_APOG
TRUE_LILITH = swe.OSCU_APOG
SYZYGY = 101
PARS_FORTUNA = 102

""" Custom fixed stars. """
FIXED_STARS = 7
