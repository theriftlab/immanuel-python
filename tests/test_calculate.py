"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The calculate module's figures are tested against output
    from astro.com and https://stardate.org/nightsky/moon
    for the moon_phase() function.

"""

from pytest import approx, fixture

from immanuel.const import calc, chart
from immanuel.tools import calculate, convert, date, ephemeris, position


@fixture
def coords():
    # San Diego coords as used by astro.com
    return [convert.string_to_dec(v) for v in ('32n43', '117w09')]

@fixture
def day_jd(coords):
    return date.to_jd('2000-01-01 10:00', *coords)

@fixture
def night_jd(coords):
    return date.to_jd('2000-01-01 00:00', *coords)


def test_moon_phase(day_jd):
    # Courtesy of https://stardate.org/nightsky/moon
    sun = ephemeris.planet(chart.SUN, day_jd)
    moon = ephemeris.planet(chart.MOON, day_jd)
    assert calculate.moon_phase(sun, moon) == calc.THIRD_QUARTER             # third quarter = waning crescent


def test_is_daytime(day_jd, night_jd, coords):
    sun, asc = ephemeris.objects((chart.SUN, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun, asc) is True
    sun, asc = ephemeris.objects((chart.SUN, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_daytime(sun, asc) is False


def test_part_of_fortune_day_formula(day_jd, coords):
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.part_longitude(chart.PART_OF_FORTUNE, sun, moon, asc, formula=calc.DAY_FORMULA)
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.CAPRICORN
    assert convert.dec_to_string(lon) == '11°18\'41"'


def test_part_of_fortune_night_formula(night_jd, coords):
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    pof = calculate.part_longitude(chart.PART_OF_FORTUNE, sun, moon, asc, formula=calc.NIGHT_FORMULA)
    sign = position.sign(pof)
    lon = position.sign_longitude(pof)
    assert sign == chart.SAGITTARIUS
    assert convert.dec_to_string(lon) == '10°04\'30"'


def test_part_of_spirit_day_formula(day_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), day_jd, *coords, chart.PLACIDUS).values()
    pos = calculate.part_longitude(chart.PART_OF_SPIRIT, sun, moon, asc, formula=calc.DAY_FORMULA)
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.ARIES
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec('29°54\''), 1)


def test_part_of_spirit_night_formula(night_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC), night_jd, *coords, chart.PLACIDUS).values()
    pos = calculate.part_longitude(chart.PART_OF_SPIRIT, sun, moon, asc, formula=calc.NIGHT_FORMULA)
    sign = position.sign(pos)
    lon = position.sign_longitude(pos)
    assert sign == chart.LEO
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec('12°18\''), 1)


def test_part_of_eros_day_formula(day_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc, venus = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC, chart.VENUS), day_jd, *coords, chart.PLACIDUS).values()
    poe = calculate.part_longitude(chart.PART_OF_EROS, sun, moon, asc, venus, formula=calc.DAY_FORMULA)
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.LIBRA
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec('07°34\''), 1)


def test_part_of_eros_night_formula(night_jd, coords):
    # Courtesy of astro-seek.com which does not include arc-seconds
    sun, moon, asc, venus = ephemeris.objects((chart.SUN, chart.MOON, chart.ASC, chart.VENUS), night_jd, *coords, chart.PLACIDUS).values()
    poe = calculate.part_longitude(chart.PART_OF_EROS, sun, moon, asc, venus, formula=calc.NIGHT_FORMULA)
    sign = position.sign(poe)
    lon = position.sign_longitude(poe)
    assert sign == chart.GEMINI
    # Since astro-seek does all its calculations without arc-seconds, we will have to be approximate
    assert round(lon, 1) == round(convert.to_dec('22°08\''), 1)


def test_sidereal_time(day_jd, coords):
    armc = ephemeris.angle(chart.ARMC, day_jd, *coords, chart.PLACIDUS)
    sidereal_time = calculate.sidereal_time(armc)
    assert convert.dec_to_string(sidereal_time, convert.FORMAT_TIME) == '16:54:13'


def test_object_movement(day_jd, coords):
    sun, moon, saturn, true_north_node, part_of_fortune = ephemeris.objects((chart.SUN, chart.MOON, chart.SATURN, chart.TRUE_NORTH_NODE, chart.PART_OF_FORTUNE), day_jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA).values()
    assert calculate.object_movement(sun) == calc.DIRECT
    assert calculate.object_movement(moon) == calc.DIRECT
    assert calculate.object_movement(saturn) == calc.RETROGRADE
    assert calculate.object_movement(true_north_node) == calc.RETROGRADE
    assert calculate.object_movement(part_of_fortune) == calc.STATIONARY


def test_is_object_movement_typical(day_jd, coords):
    sun, north_node, part_of_fortune = ephemeris.objects((chart.SUN, chart.NORTH_NODE, chart.PART_OF_FORTUNE), day_jd, *coords, chart.PLACIDUS, calc.DAY_NIGHT_FORMULA).values()
    # Direct
    assert calculate.is_object_movement_typical(sun) == True
    sun['speed'] *= -1
    assert calculate.is_object_movement_typical(sun) == False
    # Retrograde
    assert calculate.is_object_movement_typical(north_node) == True
    north_node['speed'] *= -1
    assert calculate.is_object_movement_typical(north_node) == False
    # Stationed
    assert calculate.is_object_movement_typical(part_of_fortune) == True
    part_of_fortune['speed'] *= -1
    assert calculate.is_object_movement_typical(part_of_fortune) == True


def test_relative_position(day_jd, coords):
    sun, mercury, neptune = ephemeris.objects((chart.SUN, chart.MERCURY, chart.NEPTUNE), day_jd, *coords).values()
    assert calculate.relative_position(sun, mercury) == calc.ORIENTAL
    assert calculate.relative_position(sun, neptune) == calc.OCCIDENTAL
    assert calculate.relative_position(mercury, neptune) == calc.OCCIDENTAL
    assert calculate.relative_position(neptune, mercury) == calc.ORIENTAL


def test_is_in_sect_day(day_jd, coords):
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.objects((chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS, chart.JUPITER, chart.SATURN), day_jd, *coords).values()
    assert calculate.is_in_sect(sun, True) == True
    assert calculate.is_in_sect(jupiter, True) == True
    assert calculate.is_in_sect(saturn, True) == True
    assert calculate.is_in_sect(moon, True) == False
    assert calculate.is_in_sect(venus, True) == False
    assert calculate.is_in_sect(mars, True) == False
    assert calculate.is_in_sect(mercury, True, sun) == (calculate.relative_position(sun, mercury) == calc.ORIENTAL)


def test_is_in_sect_night(night_jd, coords):
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.objects((chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS, chart.JUPITER, chart.SATURN), night_jd, *coords).values()
    assert calculate.is_in_sect(sun, False) == False
    assert calculate.is_in_sect(jupiter, False) == False
    assert calculate.is_in_sect(saturn, False) == False
    assert calculate.is_in_sect(moon, False) == True
    assert calculate.is_in_sect(venus, False) == True
    assert calculate.is_in_sect(mars, False) == True
    assert calculate.is_in_sect(mercury, False, sun) == (calculate.relative_position(sun, mercury) == calc.OCCIDENTAL)


def test_is_out_of_bounds(day_jd, coords):
    sun, mercury = ephemeris.objects((chart.SUN, chart.MERCURY), day_jd, *coords, chart.PLACIDUS).values()
    assert calculate.is_out_of_bounds(sun, day_jd) is False
    assert calculate.is_out_of_bounds(mercury, day_jd) is True


def test_solar_year_length():
    """ This one is difficult to test in isolation since it's only used for
    secondary progressions. For now we'll leave it to the forecast module
    tests to check the correct progressed Julian dates. """
    pass
