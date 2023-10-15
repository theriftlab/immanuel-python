"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Defines indices for the main chart objects supported by pyswisseph,
    along with custom-calculated objects based on pyswisseph. These
    constants are mainly used by the ephemeris module.

"""


""" Determine object type by dividing index by this. Since asteroids are passed
by number, this must be higher than the highest-numbered asteroid. """
TYPE_MULTIPLIER = 1000000

""" Supported chart types. """
NATAL = 1
SOLAR_RETURN = 2
PROGRESSED = 3
SYNASTRY = 4
COMPOSITE = 5

""" Signs. """
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

""" Decans. """
DECAN1 = 1
DECAN2 = 2
DECAN3 = 3

""" Elements. """
FIRE = 1
EARTH = 2
AIR = 3
WATER = 4

""" Modalities. """
CARDINAL = 1
FIXED = 2
MUTABLE = 3

""" House systems. """
ALCABITUS = 101
AZIMUTHAL = 102
CAMPANUS = 103
EQUAL = 104
KOCH = 105
MERIDIAN = 106
MORINUS = 107
PLACIDUS = 108
POLICH_PAGE = 109
PORPHYRIUS = 110
REGIOMONTANUS = 111
VEHLOW_EQUAL = 112
WHOLE_SIGN = 113

""" Houses. """
HOUSE = 2 * TYPE_MULTIPLIER
HOUSE1 = HOUSE + 1
HOUSE2 = HOUSE + 2
HOUSE3 = HOUSE + 3
HOUSE4 = HOUSE + 4
HOUSE5 = HOUSE + 5
HOUSE6 = HOUSE + 6
HOUSE7 = HOUSE + 7
HOUSE8 = HOUSE + 8
HOUSE9 = HOUSE + 9
HOUSE10 = HOUSE + 10
HOUSE11 = HOUSE + 11
HOUSE12 = HOUSE + 12

""" Major chart angles. """
ANGLE = 3 * TYPE_MULTIPLIER
ASC = ANGLE + 1
DESC = ANGLE + 2
MC = ANGLE + 3
IC = ANGLE + 4
ARMC = ANGLE + 5

""" Planets. """
PLANET = 4 * TYPE_MULTIPLIER
SUN = PLANET + 1
MOON = PLANET + 2
MERCURY = PLANET + 3
VENUS = PLANET + 4
MARS = PLANET + 5
JUPITER = PLANET + 6
SATURN = PLANET + 7
URANUS = PLANET + 8
NEPTUNE = PLANET + 9
PLUTO = PLANET + 10

""" Major asteroids. """
ASTEROID = 5 * TYPE_MULTIPLIER
CHIRON = ASTEROID + 1
PHOLUS = ASTEROID + 2
CERES = ASTEROID + 3
PALLAS = ASTEROID + 4
JUNO = ASTEROID + 5
VESTA = ASTEROID + 6

""" Main calculated points. """
POINT = 6 * TYPE_MULTIPLIER
NORTH_NODE = POINT + 1
SOUTH_NODE = POINT + 2
TRUE_NORTH_NODE = POINT + 3
TRUE_SOUTH_NODE = POINT + 4
VERTEX = POINT + 5
LILITH = POINT + 6
TRUE_LILITH = POINT + 7
SYZYGY = POINT + 8
PARS_FORTUNA = POINT + 9

""" Fixed stars. """
FIXED_STAR = 7 * TYPE_MULTIPLIER

""" Pre & post-natal eclipses. """
ECLIPSE = 8 * TYPE_MULTIPLIER
PRE_NATAL_SOLAR_ECLIPSE = ECLIPSE + 1
PRE_NATAL_LUNAR_ECLIPSE = ECLIPSE + 2
POST_NATAL_SOLAR_ECLIPSE = ECLIPSE + 3
POST_NATAL_LUNAR_ECLIPSE = ECLIPSE + 4

""" Eclipse types. """
TOTAL = 1
ANNULAR = 2
PARTIAL = 3
ANNULAR_TOTAL = 4
PENUMBRAL = 5
