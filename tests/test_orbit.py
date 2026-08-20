"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Many of the orbit module's functions wrap and dispatch to functions in the
sweph module whose output is covered by its own test file. For these we can
simply check the orbit module's functions output the same values as the sweph
module's functions.


"""

from pytest import approx, fixture

from immanuel.const import chart
from immanuel.tools import orbit, sweph


@fixture
def jd():
    return 2451545.25  # 2000-01-01 18:00 UT


def test_earth_obliquity(jd):
    """Simple dispatch to sweph module."""
    assert orbit.earth_obliquity(jd) == sweph.true_earth_obliquity(jd)
    assert orbit.earth_obliquity(jd, True) == sweph.mean_earth_obliquity(jd)


def test_orbital_eccentricity(jd):
    """Simple dispatch to sweph module."""
    assert (
        orbit.orbital_eccentricity(chart.MARS, jd)
        == sweph.orbital_elements(chart.MARS, jd)["eccentricity"]
    )


def test_sidereal_period(jd):
    """Simple dispatch to sweph module."""
    assert (
        orbit.sidereal_period(chart.MARS, jd, unit=orbit.TROPICAL_YEARS)
        == sweph.orbital_elements(chart.MARS, jd)["sidereal_orbital_period"]
    )


def test_tropical_period(jd):
    """Simple dispatch to sweph module."""
    assert (
        orbit.tropical_period(chart.MARS, jd, unit=orbit.TROPICAL_YEARS)
        == sweph.orbital_elements(chart.MARS, jd)["tropical_period"]
    )


def test_synodic_period(jd):
    """Simple dispatch to sweph module."""
    assert (
        orbit.synodic_period(chart.MARS, jd, unit=orbit.DAYS)
        == sweph.orbital_elements(chart.MARS, jd)["synodic_period"]
    )


def test_solar_year_length(jd):
    """This is a direct copy of astro.com's solar year formula, so there's
    not much we can test it against. The forecast module's tests will
    check progression formulae based on this figure, so those will at least
    ensure this function's output creates the same results as astro.com."""
    assert orbit.solar_year_length(jd) == approx(
        365.25, rel=1e-2
    )  # check the year is at least pretty much a year long
