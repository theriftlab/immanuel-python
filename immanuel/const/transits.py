"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Defines constants and data structures for transit calculations.
    These constants are used by the transit calculation modules.

"""

from datetime import timedelta
from typing import Union

""" Transit event types """
EVENT_ASPECT = "aspect"
EVENT_INGRESS_SIGN = "ingress_sign"
EVENT_INGRESS_HOUSE = "ingress_house"
EVENT_STATION = "station"
EVENT_ECLIPSE = "eclipse"
EVENT_PLANETARY_RETURN = "planetary_return"

""" Station types """
STATION_RETROGRADE = "retrograde"
STATION_DIRECT = "direct"

""" Eclipse types """
ECLIPSE_SOLAR = "solar_eclipse"
ECLIPSE_LUNAR = "lunar_eclipse"
ECLIPSE_TOTAL = "total"
ECLIPSE_PARTIAL = "partial"
ECLIPSE_ANNULAR = "annular"
ECLIPSE_PENUMBRAL = "penumbral"

""" Transit precision levels """
PRECISION_MINUTE = "minute"  # ±1 minute
PRECISION_SECOND = "second"  # ±1 second
PRECISION_HIGH = "high"      # ±0.1 second

""" Default time intervals - can be used with string names """
INTERVAL_MAPPINGS = {
    'hourly': timedelta(hours=1),
    'daily': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'monthly': timedelta(days=30),  # Approximate
    'yearly': timedelta(days=365),  # Approximate
}

""" Type definition for intervals """
IntervalType = Union[str, timedelta, int, float]

""" Default settings """
DEFAULT_PRECISION = PRECISION_SECOND
DEFAULT_INTERVAL = 'daily'
DEFAULT_SEARCH_STEP = 1.0  # days for initial bracketing
MAX_ITERATIONS = 50  # for convergence algorithms
CONVERGENCE_TOLERANCE = 1.0 / 86400  # 1 second in days

""" Transit search window defaults (in days) """
DEFAULT_SEARCH_WINDOW = 365  # 1 year
MAX_SEARCH_WINDOW = 36525    # 100 years

""" Swiss Ephemeris planet mappings for cross functions """
SWE_PLANET_MAP = {
    4000001: 0,  # SUN
    4000002: 1,  # MOON
    4000003: 2,  # MERCURY
    4000004: 3,  # VENUS
    4000006: 4,  # MARS
    4000007: 5,  # JUPITER
    4000008: 6,  # SATURN
    4000009: 7,  # URANUS
    4000010: 8,  # NEPTUNE
    4000011: 9,  # PLUTO
}