import swisseph as swe
from pytest import fixture

from immanuel.const import calc, chart
from immanuel.tools import condition, convert, date, ephemeris, orbit


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
def armc():
    # ARMC longitude on the above jd / day_jd
    return 253.55348499294269


def test_is_daytime(day_jd, night_jd, coords):
    # Sun above ascendant in astro.com chart visual
    assert condition.is_daytime(day_jd, *coords) is True
    # Sun below ascendant in astro.com chart visual
    assert condition.is_daytime(night_jd, *coords) is False


def test_armc_is_daytime(day_jd, coords, armc):
    # Sun above ascendant in astro.com chart visual
    assert (
        condition.armc_is_daytime(
            day_jd, armc, coords[0], orbit.earth_obliquity(day_jd)
        )
        is True
    )


def test_is_daytime_from(day_jd, night_jd, coords):
    lat, lon = coords
    sun, asc = ephemeris.get_objects(
        [chart.SUN, chart.ASC],
        day_jd,
        lat,
        lon,
        chart.PLACIDUS,
    ).values()
    assert condition.is_daytime_from(sun, asc) is True
    sun, asc = ephemeris.get_objects(
        [chart.SUN, chart.ASC], night_jd, lat, lon, chart.PLACIDUS
    ).values()
    assert condition.is_daytime_from(sun, asc) is False


def test_object_motion(jd, coords):
    lat, lon = coords
    sun, moon, saturn, true_north_node, part_of_fortune = ephemeris.get_objects(
        [
            chart.SUN,
            chart.MOON,
            chart.SATURN,
            chart.TRUE_NORTH_NODE,
            chart.PART_OF_FORTUNE,
        ],
        jd,
        lat,
        lon,
        chart.PLACIDUS,
        calc.DAY_NIGHT_FORMULA,
    ).values()
    assert condition.object_motion(sun) == calc.DIRECT
    assert condition.object_motion(moon) == calc.DIRECT
    assert condition.object_motion(saturn) == calc.RETROGRADE
    assert condition.object_motion(true_north_node) == calc.RETROGRADE
    assert condition.object_motion(part_of_fortune) == calc.STATIONARY


def test_is_object_motion_typical(jd, coords):
    lat, lon = coords
    sun, north_node, part_of_fortune = ephemeris.get_objects(
        [chart.SUN, chart.NORTH_NODE, chart.PART_OF_FORTUNE],
        jd,
        lat,
        lon,
        chart.PLACIDUS,
        calc.DAY_NIGHT_FORMULA,
    ).values()
    # Direct
    assert condition.is_object_motion_typical(sun)
    sun["speed"] *= -1
    assert not condition.is_object_motion_typical(sun)
    # Retrograde
    assert condition.is_object_motion_typical(north_node)
    north_node["speed"] *= -1
    assert not condition.is_object_motion_typical(north_node)
    # Stationed
    assert condition.is_object_motion_typical(part_of_fortune)
    part_of_fortune["speed"] *= -1
    assert condition.is_object_motion_typical(part_of_fortune)


def test_is_object_out_of_bounds(day_jd, coords):
    lat, lon = coords
    sun, mercury = ephemeris.get_objects(
        [chart.SUN, chart.MERCURY], day_jd, lat, lon, chart.PLACIDUS
    ).values()
    assert condition.is_object_out_of_bounds(sun, day_jd) is False
    assert condition.is_object_out_of_bounds(mercury, day_jd) is True


def test_is_object_in_sect_day(day_jd, coords):
    lat, lon = coords
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.get_objects(
        [
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
        ],
        day_jd,
        lat,
        lon,
    ).values()
    assert condition.is_object_in_sect(sun, True)
    assert condition.is_object_in_sect(jupiter, True)
    assert condition.is_object_in_sect(saturn, True)
    assert not condition.is_object_in_sect(moon, True)
    assert not condition.is_object_in_sect(venus, True)
    assert not condition.is_object_in_sect(mars, True)
    assert condition.is_object_in_sect(mercury, True, sun) == (
        condition.relative_object_position(sun, mercury) == calc.ORIENTAL
    )


def test_is_object_in_sect_night(night_jd, coords):
    lat, lon = coords
    sun, moon, mercury, venus, mars, jupiter, saturn = ephemeris.get_objects(
        [
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
        ],
        night_jd,
        lat,
        lon,
    ).values()
    assert not condition.is_object_in_sect(sun, False)
    assert not condition.is_object_in_sect(jupiter, False)
    assert not condition.is_object_in_sect(saturn, False)
    assert condition.is_object_in_sect(moon, False)
    assert condition.is_object_in_sect(venus, False)
    assert condition.is_object_in_sect(mars, False)
    assert condition.is_object_in_sect(mercury, False, sun) == (
        condition.relative_object_position(sun, mercury) == calc.OCCIDENTAL
    )


def test_relative_object_position(day_jd, coords):
    lat, lon = coords
    sun, mercury, neptune = ephemeris.get_objects(
        [chart.SUN, chart.MERCURY, chart.NEPTUNE], day_jd, lat, lon
    ).values()
    assert condition.relative_object_position(sun, mercury) == calc.ORIENTAL
    assert condition.relative_object_position(sun, neptune) == calc.OCCIDENTAL
    assert condition.relative_object_position(mercury, neptune) == calc.OCCIDENTAL
    assert condition.relative_object_position(neptune, mercury) == calc.ORIENTAL


def test_moon_phase(jd):
    # Courtesy of https://stardate.org/moon-phase-calculator
    assert (
        condition.moon_phase(jd) == calc.THIRD_QUARTER
    ) is True  # third quarter = waning crescent


def test_moon_phase_from(jd):
    # Courtesy of https://stardate.org/moon-phase-calculator
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    assert (
        condition.moon_phase_from(sun, moon) == calc.THIRD_QUARTER
    ) is True  # third quarter = waning crescent


def test_moon_sun_distance(jd):
    sun = ephemeris.get_planet(chart.SUN, jd)
    moon = ephemeris.get_planet(chart.MOON, jd)
    assert condition.moon_sun_distance(jd) == swe.difdeg2n(moon["lon"], sun["lon"])
