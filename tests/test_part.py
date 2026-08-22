"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The part module is currently pretty simple and only calculates the
longitude of the parts of Fortune, Spirit, and Eros. Part of Fortune
is tested against astro.com's output, but astro.com does not support
other two parts, so we test those against astro-seek.com and forgo
arcsecond-level accuracy.

"""

import pytest
from pytest import fixture
from pytest_lazy_fixtures import lf

from immanuel.const import calc, chart
from immanuel.tools import convert, date, part, position, sweph


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ("32n43", "117w09")]


@fixture
def jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def day_jd(coords):
    return date.to_jd("2000-01-01 10:00", *coords)


@fixture
def night_jd(coords):
    return date.to_jd("2000-01-01 00:00", *coords)


@fixture
def day_armc():
    # ARMC longitude on the above jd / day_jd
    return 253.55348499294269


@fixture
def night_armc():
    # ARMC longitude on the above night_jd
    return 103.14279774641


@pytest.mark.parametrize(
    "p_day_jd, p_coords, p_day_armc",
    [
        (lf("day_jd"), lf("coords"), None),
        (lf("day_jd"), lf("coords"), lf("day_armc")),
    ],
)
def test_part_of_fortune_day_formula(p_day_jd, p_coords, p_day_armc):
    day_jd, coords, day_armc = p_day_jd, p_coords, p_day_armc
    lat, lon = coords[0], (coords[1] if day_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(day_jd) if day_armc is not None else None
    )
    pof = part.longitude(
        chart.PART_OF_FORTUNE,
        day_jd,
        lat,
        lon,
        calc.DAY_FORMULA,
        day_armc,
        armc_obliquity,
    )
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.CAPRICORN
    assert convert.dec_to_string(lon) == "11°18'41\""


@pytest.mark.parametrize(
    "p_night_jd, p_coords, p_night_armc",
    [
        (lf("night_jd"), lf("coords"), None),
        (lf("night_jd"), lf("coords"), lf("night_armc")),
    ],
)
def test_part_of_fortune_night_formula(p_night_jd, p_coords, p_night_armc):
    night_jd, coords, night_armc = p_night_jd, p_coords, p_night_armc
    lat, lon = coords[0], (coords[1] if night_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(night_jd) if night_armc is not None else None
    )
    pof = part.longitude(
        chart.PART_OF_FORTUNE,
        night_jd,
        lat,
        lon,
        calc.NIGHT_FORMULA,
        night_armc,
        armc_obliquity,
    )
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.SAGITTARIUS
    assert convert.dec_to_string(lon) == "10°04'30\""


@pytest.mark.parametrize(
    "p_day_jd, p_coords, p_day_armc",
    [
        (lf("day_jd"), lf("coords"), None),
        (lf("day_jd"), lf("coords"), lf("day_armc")),
    ],
)
def test_part_of_spirit_day_formula(p_day_jd, p_coords, p_day_armc):
    # Courtesy of astro-seek.com which does not include arc-seconds
    day_jd, coords, day_armc = p_day_jd, p_coords, p_day_armc
    lat, lon = coords[0], (coords[1] if day_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(day_jd) if day_armc is not None else None
    )
    pos = part.longitude(
        chart.PART_OF_SPIRIT,
        day_jd,
        lat,
        lon,
        calc.DAY_FORMULA,
        day_armc,
        armc_obliquity,
    )
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.ARIES
    # Since astro-seek does all its calculations without arc-seconds,
    # we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("29°54'"), 1)


@pytest.mark.parametrize(
    "p_night_jd, p_coords, p_night_armc",
    [
        (lf("night_jd"), lf("coords"), None),
        (lf("night_jd"), lf("coords"), lf("night_armc")),
    ],
)
def test_part_of_spirit_night_formula(p_night_jd, p_coords, p_night_armc):
    # Courtesy of astro-seek.com which does not include arc-seconds
    night_jd, coords, night_armc = p_night_jd, p_coords, p_night_armc
    lat, lon = coords[0], (coords[1] if night_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(night_jd) if night_armc is not None else None
    )
    pos = part.longitude(
        chart.PART_OF_SPIRIT,
        night_jd,
        lat,
        lon,
        calc.NIGHT_FORMULA,
        night_armc,
        armc_obliquity,
    )
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.LEO
    # Since astro-seek does all its calculations without arc-seconds,
    # we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("12°18'"), 1)


@pytest.mark.parametrize(
    "p_day_jd, p_coords, p_day_armc",
    [
        (lf("day_jd"), lf("coords"), None),
        (lf("day_jd"), lf("coords"), lf("day_armc")),
    ],
)
def test_part_of_eros_day_formula(p_day_jd, p_coords, p_day_armc):
    # Courtesy of astro-seek.com which does not include arc-seconds
    day_jd, coords, day_armc = p_day_jd, p_coords, p_day_armc
    lat, lon = coords[0], (coords[1] if day_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(day_jd) if day_armc is not None else None
    )
    poe = part.longitude(
        chart.PART_OF_EROS, day_jd, lat, lon, calc.DAY_FORMULA, day_armc, armc_obliquity
    )
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.LIBRA
    # Since astro-seek does all its calculations without arc-seconds,
    # we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("07°34'"), 1)


@pytest.mark.parametrize(
    "p_night_jd, p_coords, p_night_armc",
    [
        (lf("night_jd"), lf("coords"), None),
        (lf("night_jd"), lf("coords"), lf("night_armc")),
    ],
)
def test_part_of_eros_night_formula(p_night_jd, p_coords, p_night_armc):
    # Courtesy of astro-seek.com which does not include arc-seconds
    night_jd, coords, night_armc = p_night_jd, p_coords, p_night_armc
    lat, lon = coords[0], (coords[1] if night_armc is None else None)
    armc_obliquity = (
        sweph.true_earth_obliquity(night_jd) if night_armc is not None else None
    )
    poe = part.longitude(
        chart.PART_OF_EROS,
        night_jd,
        lat,
        lon,
        calc.NIGHT_FORMULA,
        night_armc,
        armc_obliquity,
    )
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.GEMINI
    # Since astro-seek does all its calculations without arc-seconds,
    # we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec("22°08'"), 1)
