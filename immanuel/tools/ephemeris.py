"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to relatively consistently standardized
    pyswisseph data for the main angles, houses, points and planets, as well as
    calculations based on that data. Transits, eclipses, moon phases, etc. are
    also calculated in this module.

    Many of the functions here, including angle, house and vertex functions,
    have an "armc_"-prefixed alternative if they are required to calculate
    from an ARMC.

"""

import math

import swisseph as swe

from immanuel.classes.cache import cache
from immanuel.classes.localize import localize as _
from immanuel.const import calc, chart, names


ALL = -1

PREVIOUS = -1
NEXT = 1

DAYS = 0
TROPICAL_YEARS = 1

SYNODIC_MIN = -1
SYNODIC_AVG = 0
SYNODIC_MAX = 1

_SWE = {
    chart.ALCABITUS: b"B",
    chart.AZIMUTHAL: b"H",
    chart.CAMPANUS: b"C",
    chart.EQUAL: b"A",
    chart.KOCH: b"K",
    chart.MERIDIAN: b"X",
    chart.MORINUS: b"M",
    chart.PLACIDUS: b"P",
    chart.POLICH_PAGE: b"T",
    chart.PORPHYRIUS: b"O",
    chart.REGIOMONTANUS: b"R",
    chart.VEHLOW_EQUAL: b"V",
    chart.WHOLE_SIGN: b"W",
    chart.ASC: swe.ASC,
    chart.DESC: swe.ASC,
    chart.MC: swe.MC,
    chart.IC: swe.MC,
    chart.ARMC: swe.ARMC,
    chart.SUN: swe.SUN,
    chart.MOON: swe.MOON,
    chart.MERCURY: swe.MERCURY,
    chart.VENUS: swe.VENUS,
    chart.TERRA: swe.EARTH,
    chart.MARS: swe.MARS,
    chart.JUPITER: swe.JUPITER,
    chart.SATURN: swe.SATURN,
    chart.URANUS: swe.URANUS,
    chart.NEPTUNE: swe.NEPTUNE,
    chart.PLUTO: swe.PLUTO,
    chart.CHIRON: swe.CHIRON,
    chart.PHOLUS: swe.PHOLUS,
    chart.CERES: swe.CERES,
    chart.PALLAS: swe.PALLAS,
    chart.JUNO: swe.JUNO,
    chart.VESTA: swe.VESTA,
    chart.NORTH_NODE: swe.MEAN_NODE,
    chart.SOUTH_NODE: swe.MEAN_NODE,
    chart.TRUE_NORTH_NODE: swe.TRUE_NODE,
    chart.TRUE_SOUTH_NODE: swe.TRUE_NODE,
    chart.VERTEX: swe.VERTEX,
    chart.LILITH: swe.MEAN_APOG,
    chart.TRUE_LILITH: swe.OSCU_APOG,
    chart.INTERPOLATED_LILITH: swe.INTP_APOG,
    chart.SYZYGY: chart.SYZYGY,
    chart.PART_OF_FORTUNE: chart.PART_OF_FORTUNE,
    chart.PART_OF_SPIRIT: chart.PART_OF_SPIRIT,
    chart.PART_OF_EROS: chart.PART_OF_EROS,
}

_SWE_ECLIPSES = {
    swe.ECL_TOTAL: chart.TOTAL,
    swe.ECL_ANNULAR: chart.ANNULAR,
    swe.ECL_PARTIAL: chart.PARTIAL,
    swe.ECL_ANNULAR_TOTAL: chart.ANNULAR_TOTAL,
    swe.ECL_PENUMBRAL: chart.PENUMBRAL,
}


"""
CHART OBJECTS
--------------------------------------------------------------------------------
These functions deal with returning formatted data for planets, asteroids,
angles, houses, etc. from pyswisseph.
"""


def get_objects(
    object_list: tuple,
    jd: float,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function returns a dict of all passed chart objects."""
    return _get_objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_objects(
    object_list: tuple,
    jd: float,
    armc: float,
    lat: float | None = None,
    lon: float | None = None,
    obliquity: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function returns a dict of all passed chart objects
    with points & angles calculated from the passed ARMC."""
    return _get_objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get(
    index: int | str,
    jd: float,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star."""
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def armc_get(
    index: int | str,
    jd: float,
    armc: float,
    lat: float | None = None,
    lon: float | None = None,
    obliquity: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star with houses & angles calculated from the
    passed ARMC."""
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_angles(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns all four main chart angles & ARMC."""
    return _get_angle(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_angles(
    armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns all four main chart angles calculated from the
    passed ARMC."""
    return _get_angle(
        index=ALL,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_angle(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index == ALL."""
    return _get_angle(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_angle(
    index: int, armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns one of the four main chart angles & its speed, calculated from
    the passed ARMC. Returns all if index == ALL."""
    return _get_angle(
        index=index,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_houses(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns all houses."""
    return _get_house(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_houses(
    armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns all houses calculated from the passed ARMC."""
    return _get_house(
        index=ALL,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_house(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """Returns a house cusp & its speed, or all houses if index == ALL."""
    return _get_house(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_house(
    index: int, armc: float, lat: float, obliquity: float, house_system: int
) -> dict:
    """Returns a house cusp & its speed, or all houses if index == ALL,
    calculated from passed ARMC."""
    return _get_house(
        index=index,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity,
    )


def get_point(
    index: int,
    jd: float,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Returns a calculated point by Julian date, and additionally by lat / lon
    coordinates."""
    return _get_point(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        part_formula=part_formula,
        armc=None,
        armc_obliquity=None,
    )


def get_armc_point(
    index: int,
    jd: float,
    armc: float,
    lat: float,
    obliquity: float,
    house_system: int | None = None,
    part_formula: int | None = None,
) -> dict:
    """Returns a calculated point by Julian date, and additionally by the
    passed ARMC."""
    return _get_point(
        index=index,
        jd=jd,
        lat=lat,
        lon=None,
        house_system=house_system,
        part_formula=part_formula,
        armc=armc,
        armc_obliquity=obliquity,
    )


@cache
def get_planet(index: int, jd: float) -> dict:
    """Returns a pyswisseph object by Julian date. Can be used to
    return the six major asteroids supported by pyswisseph without using
    a separate file."""
    ec_res = swe.calc_ut(jd, _SWE[index])[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -earth_obliquity(jd))
    asteroid = _type(index) == chart.ASTEROID

    return {
        "index": index,
        "type": chart.ASTEROID if asteroid else chart.PLANET,
        "name": _(names.ASTEROIDS[index] if asteroid else names.PLANETS[index]),
        "lon": ec_res[0],
        "lat": ec_res[1],
        "dist": ec_res[2],
        "speed": ec_res[3],
        "dec": eq_res[1],
    }


@cache
def get_asteroid(index: int, jd: float) -> dict:
    """Returns an asteroid by Julian date and pyswisseph index
    from an external asteroid's file as specified
    in the setup module."""
    if _type(index) == chart.ASTEROID:
        return get_planet(index, jd)

    swe_index = index + swe.AST_OFFSET
    name = swe.get_planet_name(swe_index)

    ec_res = swe.calc_ut(jd, swe_index)[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -earth_obliquity(jd))

    return {
        "index": index,
        "type": chart.ASTEROID,
        "name": name,
        "lon": ec_res[0],
        "lat": ec_res[1],
        "dist": ec_res[2],
        "speed": ec_res[3],
        "dec": eq_res[1],
    }


@cache
def get_fixed_star(name: str, jd: float) -> dict:
    """Returns a fixed star by Julian date and name."""
    res, stnam = swe.fixstar2_ut(name, jd)[:2]
    name = stnam.partition(",")[0]

    return {
        "index": name,
        "type": chart.FIXED_STAR,
        "name": name,
        "lon": res[0],
        "lat": res[1],
        "dist": res[2],
        "speed": res[3],
    }


@cache
def get_eclipse(index: int, jd: float) -> dict:
    """Returns a calculated object based on the moon's or sun's position
    during a pre or post-natal lunar or solar eclipse. The declination
    value is based on the natal date."""
    match index:
        case chart.PRE_NATAL_SOLAR_ECLIPSE:
            eclipse_type, eclipse_jd = previous_solar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.SUN)[0]
        case chart.PRE_NATAL_LUNAR_ECLIPSE:
            eclipse_type, eclipse_jd = previous_lunar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.MOON)[0]
        case chart.POST_NATAL_SOLAR_ECLIPSE:
            eclipse_type, eclipse_jd = next_solar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.SUN)[0]
        case chart.POST_NATAL_LUNAR_ECLIPSE:
            eclipse_type, eclipse_jd = next_lunar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.MOON)[0]

    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -earth_obliquity(jd))

    return {
        "index": index,
        "type": chart.ECLIPSE,
        "name": _(names.ECLIPSES[index]),
        "eclipse_type": eclipse_type,
        "jd": eclipse_jd,
        "lon": ec_res[0],
        "lat": ec_res[1],
        "dist": ec_res[2],
        "speed": 0.0,
        "dec": eq_res[1],
    }


def _get_objects(
    object_list: tuple,
    jd: float,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for items() and armc_items()."""
    objects = {}

    for index in object_list:
        objects[index] = _get(
            index=index,
            jd=jd,
            lat=lat,
            lon=lon,
            house_system=house_system,
            part_formula=part_formula,
            armc=armc,
            armc_obliquity=armc_obliquity,
        )

    return objects


def _get(
    index: int | str,
    jd: float,
    lat: float | None,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for get() and armc_get()."""
    if armc is not None and armc_obliquity is None:
        armc_obliquity = earth_obliquity(jd)

    if isinstance(index, int):
        if index < chart.TYPE_MULTIPLIER:
            return get_asteroid(index, jd)

        if index == chart.ANGLE:
            return _get_angle(ALL, jd, lat, lon, house_system, armc, armc_obliquity)

        if index == chart.HOUSE:
            return _get_house(ALL, jd, lat, lon, house_system, armc, armc_obliquity)

        match _type(index):
            case chart.ANGLE:
                return _get_angle(
                    index, jd, lat, lon, house_system, armc, armc_obliquity
                )
            case chart.HOUSE:
                return _get_house(
                    index, jd, lat, lon, house_system, armc, armc_obliquity
                )
            case chart.POINT:
                return _get_point(
                    index,
                    jd,
                    lat,
                    lon,
                    house_system,
                    part_formula,
                    armc,
                    armc_obliquity,
                )
            case chart.ECLIPSE:
                return get_eclipse(index, jd)
            case (chart.ASTEROID | chart.PLANET):
                return get_planet(index, jd)
    else:
        return get_fixed_star(index, jd)


def _get_angle(
    index: int,
    jd: float | None,
    lat: float,
    lon: float | None,
    house_system: int,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for angle() and armc_angle()."""
    if armc is not None:
        angles = _get_angles_houses_vertex_armc(
            armc, lat, armc_obliquity, house_system
        )["angles"]
    else:
        angles = _get_angles_houses_vertex(jd, lat, lon, house_system)["angles"]

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def _get_house(
    index: int,
    jd: float | None,
    lat: float,
    lon: float | None,
    house_system: int,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for house() and armc_house()."""
    first_house_lon = (
        get_planet(_first_house_planet_index(house_system), jd)["lon"]
        if house_system > chart.PLANET_ON_FIRST
        else None
    )

    if armc is not None:
        houses = _get_angles_houses_vertex_armc(
            armc, lat, armc_obliquity, house_system, first_house_lon
        )["houses"]
    else:
        houses = _get_angles_houses_vertex(jd, lat, lon, house_system, first_house_lon)[
            "houses"
        ]

    if index == ALL:
        return houses

    if index in houses:
        return houses[index]

    return None


def _get_point(
    index: int,
    jd: float | None,
    lat: float,
    lon: float | None,
    house_system: int | None,
    part_formula: int | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> dict:
    """Function for point() and armc_point()."""
    if index == chart.VERTEX:
        if armc is not None:
            return _get_angles_houses_vertex_armc(
                armc, lat, armc_obliquity, house_system
            )["vertex"]
        else:
            return _get_angles_houses_vertex(jd, lat, lon, house_system)["vertex"]

    if index == chart.SYZYGY:
        return _get_syzygy(jd)

    if index in (chart.PART_OF_FORTUNE, chart.PART_OF_SPIRIT, chart.PART_OF_EROS):
        return _get_part(index, jd, lat, lon, part_formula, armc, armc_obliquity)

    return _get_swisseph_point(index, jd)


@cache
def _get_swisseph_point(index: int, jd: float) -> dict:
    """Pull any remaining non-calculated points straight from pyswisseph."""
    res = swe.calc_ut(jd, _SWE[index])[0]
    lon = (
        res[0]
        if index not in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE)
        else swe.degnorm(res[0] - 180)
    )
    lat = (
        res[1]
        if index
        not in (
            chart.NORTH_NODE,
            chart.TRUE_NORTH_NODE,
            chart.SOUTH_NODE,
            chart.TRUE_SOUTH_NODE,
        )
        else 0.0
    )
    speed = res[3]
    dec = swe.cotrans((lon, lat, 0), -earth_obliquity(jd))[1]

    return {
        "index": index,
        "type": chart.POINT,
        "name": _(names.POINTS[index]),
        "lon": lon,
        "lat": lat,
        "speed": speed,
        "dec": dec,
    }


@cache
def _get_part(
    index: int,
    jd: float,
    lat: float,
    lon: float | None,
    formula: int,
    armc: float | None = None,
    armc_obliquity: float | None = None,
) -> dict:
    """Calculates Parts of Fortune, Spirit, and Eros."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    venus = get_planet(chart.VENUS, jd) if index == chart.PART_OF_EROS else None
    asc = (
        get_angle(chart.ASC, jd, lat, lon, chart.PLACIDUS)
        if armc is None
        else get_armc_angle(chart.ASC, armc, lat, armc_obliquity, chart.PLACIDUS)
    )
    lon = part_longitude(index, sun, moon, asc, venus, formula)
    dec = swe.cotrans((lon, 0, 0), -earth_obliquity(jd))[1]

    return {
        "index": index,
        "type": chart.POINT,
        "name": _(names.POINTS[index]),
        "lon": lon,
        "lat": 0.0,
        "speed": 0.0,
        "dec": dec,
    }


@cache
def _get_syzygy(jd: float) -> dict:
    """Calculate prenatal full/new moon - this can potentially
    be an expensive calculation so should be cached."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    distance = swe.difdeg2n(moon["lon"], sun["lon"])
    syzygy_jd = previous_new_moon(jd) if distance > 0 else previous_full_moon(jd)
    syzygy_moon = get_planet(chart.MOON, syzygy_jd)

    return {
        "index": chart.SYZYGY,
        "type": chart.POINT,
        "name": _(names.POINTS[chart.SYZYGY]),
        "lon": syzygy_moon["lon"],
        "lat": syzygy_moon["lat"],
        "speed": syzygy_moon["speed"],
        "dec": syzygy_moon["dec"],
    }


@cache
def _get_angles_houses_vertex(
    jd: float,
    lat: float,
    lon: float,
    house_system: int,
    first_house_lon: float | None = None,
) -> dict:
    """Returns ecliptic longitudes for the houses, main angles, and the vertex,
    along with their speeds. Defaults to Placidus for main angles & vertex if
    an PLANET_ON_FIRST house system is chosen. Based on Julian date and
    lat / lon coordinates."""
    return _get_angles_houses_vertex_from_swe(
        earth_obliquity(jd),
        *swe.houses_ex2(
            jd,
            lat,
            lon,
            _SWE[
                house_system if house_system < chart.PLANET_ON_FIRST else chart.PLACIDUS
            ],
        ),
        first_house_lon,
    )


@cache
def _get_angles_houses_vertex_armc(
    armc: float,
    lat: float,
    obliquity: float,
    house_system: int,
    first_house_lon: float | None = None,
) -> dict:
    """Returns ecliptic longitudes for the houses, main angles, and the vertex,
    along with their speeds. Defaults to Placidus for main angles & vertex if
    an PLANET_ON_FIRST house system is chosen. Based on ARMC, latitude and
    ecliptic obliquity."""
    return _get_angles_houses_vertex_from_swe(
        obliquity,
        *swe.houses_armc_ex2(
            armc,
            lat,
            obliquity,
            _SWE[
                house_system if house_system < chart.PLANET_ON_FIRST else chart.PLACIDUS
            ],
        ),
        first_house_lon,
    )


def _get_angles_houses_vertex_from_swe(
    obliquity: float,
    cusps: tuple,
    ascmc: tuple,
    cuspsspeed: tuple,
    ascmcspeed: tuple,
    first_house_lon: float | None,
) -> dict:
    """Get houses, angles & vertex direct from pyswisseph."""
    angles = {}

    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[_SWE[i]]
        speed = ascmcspeed[_SWE[i]]
        dec = swe.cotrans((lon, 0, 0), -obliquity)[1]

        angles[i] = {
            "index": i,
            "type": chart.ANGLE,
            "name": _(names.ANGLES[i]),
            "lon": lon,
            "speed": speed,
            "dec": dec,
        }

        if i in (chart.ASC, chart.MC):
            index = chart.DESC if i == chart.ASC else chart.IC

            angles[index] = {
                "index": index,
                "type": chart.ANGLE,
                "name": _(names.ANGLES[index]),
                "lon": swe.degnorm(lon - 180),
                "speed": speed,
                "dec": dec * -1,
            }

    houses = {}

    for i in range(1, 13):
        index = chart.HOUSE + i

        if first_house_lon is not None:
            lon = swe.degnorm(first_house_lon + (30 * (i - 1)))
            size = 30
            speed = 0
            dec = 0
        else:
            lon = cusps[i - 1]
            size = swe.difdeg2n(cusps[i if i < 12 else 0], lon)
            speed = cuspsspeed[i - 1]
            dec = swe.cotrans((lon, 0, 0), -obliquity)[1]

        houses[index] = {
            "index": index,
            "type": chart.HOUSE,
            "name": _(names.HOUSES[index]),
            "number": i,
            "lon": lon,
            "size": size,
            "speed": speed,
            "dec": dec,
        }

    vertex_lon = ascmc[_SWE[chart.VERTEX]]
    vertex_speed = ascmcspeed[_SWE[chart.VERTEX]]
    vertex_dec = swe.cotrans((vertex_lon, 0, 0), -obliquity)[1]

    vertex = {
        "index": chart.VERTEX,
        "type": chart.POINT,
        "name": _(names.POINTS[chart.VERTEX]),
        "lon": vertex_lon,
        "speed": vertex_speed,
        "dec": vertex_dec,
    }

    return {
        "angles": angles,
        "houses": houses,
        "vertex": vertex,
    }


def _first_house_planet_index(house_system: int) -> int:
    """Return the index of the planet that marks the first house."""
    return (house_system - chart.PLANET_ON_FIRST) + chart.PLANET


def _type(index: int) -> int:
    """Return the type index of a given object's index."""
    return round(index, -2)


"""
CALCULATIONS
--------------------------------------------------------------------------------
These functions deal with calculations based on data passed in (usually from
pyswisseph).
"""


def part_longitude(
    index: int,
    sun: dict | float,
    moon: dict | float,
    asc: dict | float,
    venus: dict | float = None,
    formula: int = calc.DAY_NIGHT_FORMULA,
) -> float:
    """Returns the longitude of the given Part - currently supports Parts of
    Fortune, Spirit and Eros."""
    sun_lon, moon_lon, asc_lon = (
        object["lon"] if isinstance(object, dict) else object
        for object in (sun, moon, asc)
    )
    night = formula == calc.NIGHT_FORMULA or (
        formula == calc.DAY_NIGHT_FORMULA and not is_daytime_from(sun_lon, asc_lon)
    )

    if index == chart.PART_OF_FORTUNE:
        lon = _part_of_fortune(sun_lon, moon_lon, asc_lon, night)
    elif index == chart.PART_OF_SPIRIT:
        lon = _part_of_spirit(sun_lon, moon_lon, asc_lon, night)
    elif index == chart.PART_OF_EROS:
        venus_lon = venus["lon"] if isinstance(venus, dict) else venus
        spirit_lon = _part_of_spirit(sun_lon, moon_lon, asc_lon, night)
        lon = _part_of_eros(venus_lon, spirit_lon, asc_lon, night)

    return swe.degnorm(lon)


def is_daytime(jd: float, lat: float, lon: float) -> bool:
    """Returns whether the sun is above the horizon line at the time and
    place specified."""
    return _is_daytime(jd=jd, lat=lat, lon=lon, armc=None, armc_obliquity=None)


def armc_is_daytime(jd: float, armc: float, lat: float, obliquity: float) -> bool:
    """Returns whether the sun is above the horizon line at the time and
    place specified, as calculated by the passed ARMC."""
    return _is_daytime(jd=jd, lat=lat, lon=None, armc=armc, armc_obliquity=obliquity)


def is_daytime_from(sun: dict | float, asc: dict | float) -> bool:
    """Returns whether the sun is above the ascendant."""
    sun_lon, asc_lon = (
        object["lon"] if isinstance(object, dict) else object for object in (sun, asc)
    )
    return swe.difdeg2n(sun_lon, asc_lon) < 0


@cache
def moon_phase(jd: float) -> int:
    """Returns the moon phase at the given Julian date."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    return moon_phase_from(sun, moon)


def moon_phase_from(sun: dict | float, moon: dict | float) -> int:
    """Returns the moon phase given the positions of the Sun and Moon."""
    sun_lon, moon_lon = (
        object["lon"] if isinstance(object, dict) else object for object in (sun, moon)
    )
    distance = swe.difdegn(moon_lon, sun_lon)

    for angle in range(45, 361, 45):
        if distance < angle:
            return angle


@cache
def earth_obliquity(jd: float, mean: bool = False) -> float:
    """Returns the earth's true or mean obliquity at the
    given Julian date."""
    ecl_nut = swe.calc_ut(jd, swe.ECL_NUT)[0]
    return ecl_nut[1] if mean else ecl_nut[0]


@cache
def deltat(jd: float, seconds: bool = False) -> float:
    """Return the Delta-T value of the passed Julian date. Optionally it
    will return this value in seconds."""
    return swe.deltat(jd) if not seconds else swe.deltat(jd) * 24 * 3600


def sidereal_time(armc: dict | float) -> float:
    """Returns sidereal time based on ARMC longitude."""
    return (armc["lon"] if isinstance(armc, dict) else armc) / 15


def object_movement(object: dict | float) -> int:
    """Returns whether a chart object is direct, stationary or retrograde."""
    speed = object["speed"] if isinstance(object, dict) else object

    if -calc.STATION_SPEED <= speed <= calc.STATION_SPEED:
        return calc.STATIONARY

    return calc.DIRECT if speed > calc.STATION_SPEED else calc.RETROGRADE


def is_object_movement_typical(object: dict) -> bool:
    """Returns whether an object's movement is typical, ie. direct for planets,
    retrograde for nodes, stationary for Parts and eclipses."""
    if object["index"] in (
        chart.PART_OF_FORTUNE,
        chart.PART_OF_SPIRIT,
        chart.PART_OF_EROS,
        chart.PRE_NATAL_SOLAR_ECLIPSE,
        chart.PRE_NATAL_LUNAR_ECLIPSE,
        chart.POST_NATAL_SOLAR_ECLIPSE,
        chart.POST_NATAL_SOLAR_ECLIPSE,
    ):
        return object["speed"] == 0.0

    movement = object_movement(object)

    is_node = object["index"] in (
        chart.NORTH_NODE,
        chart.SOUTH_NODE,
        chart.TRUE_NORTH_NODE,
        chart.TRUE_SOUTH_NODE,
    )

    return movement == calc.RETROGRADE if is_node else movement == calc.DIRECT


def is_out_of_bounds(
    object: dict | float, jd: float | None = None, obliquity: float | None = None
) -> bool:
    """Returns whether the passed object is out of bounds either on the passed
    Julian date or relative to the passed obliquity."""
    if isinstance(object, dict):
        if "dec" not in object:
            return None
        dec = object["dec"]
    else:
        dec = object

    if jd is not None:
        obliquity = earth_obliquity(jd)
    elif obliquity is None:
        return None

    return not -obliquity < dec < obliquity


def is_in_sect(object: dict, is_daytime: bool, sun: dict | float = None) -> bool:
    """Returns whether the passed planet is in sect."""
    if object["index"] in (chart.SUN, chart.JUPITER, chart.SATURN):
        return is_daytime

    if object["index"] in (chart.MOON, chart.VENUS, chart.MARS):
        return not is_daytime

    if object["index"] == chart.MERCURY:
        sun_mercury_position = relative_position(sun, object)
        return (
            sun_mercury_position == calc.ORIENTAL
            if is_daytime
            else sun_mercury_position == calc.OCCIDENTAL
        )

    return False


def relative_position(object1: dict | float, object2: dict | float) -> int:
    """Calculate which side of object1 object2 is."""
    lon1, lon2 = (
        object["lon"] if isinstance(object, dict) else object
        for object in (object1, object2)
    )

    return calc.OCCIDENTAL if swe.difdegn(lon1, lon2) > 180 else calc.ORIENTAL


def orbital_eccentricity(index: int, jd: float) -> float:
    """Returns the passed object's orbital eccentricity."""
    return _orbital_elements(index, jd)[1]


def sidereal_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's sidereal orbital period."""
    sidereal_period = _orbital_elements(index, jd)[10]
    return sidereal_period * solar_year_length(jd) if unit == DAYS else sidereal_period


def tropical_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's tropical orbital period."""
    tropical_period = _orbital_elements(index, jd)[12]
    return tropical_period * solar_year_length(jd) if unit == DAYS else tropical_period


def synodic_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns the passed object's synodic period."""
    synodic_period = _orbital_elements(index, jd)[13]
    return synodic_period if unit == DAYS else synodic_period / solar_year_length(jd)


def synodic_period_between(
    index1: int, index2: int, jd: float, type: int = SYNODIC_AVG, unit: int = DAYS
) -> float:
    """Returns the approximate synodic period between two objects."""
    sidereal_period1 = sidereal_period(index1, jd)
    sidereal_period2 = sidereal_period(index2, jd)

    synodic_period = 1 / abs(1 / sidereal_period1 - 1 / sidereal_period2)

    if type in (SYNODIC_MIN, SYNODIC_MAX):
        orbital_eccentricity1 = orbital_eccentricity(index1, jd)
        orbital_eccentricity2 = orbital_eccentricity(index2, jd)
        synodic_period *= (
            1 + ((orbital_eccentricity1 + orbital_eccentricity2) * type) / 2
        )

    return synodic_period if unit == DAYS else synodic_period / solar_year_length(jd)


def retrograde_period(index: int, jd: float, unit: int = DAYS) -> float:
    """Returns an approximate estimate of a planet's retrograde period. This is
    very approximate and should not be used for anything precise since it is
    based on Newtonian mechanics and perfect-circle orbit calculations. Formula
    borrowed from https://physics.stackexchange.com/a/476286."""
    if index in (chart.SUN, chart.MOON):
        return 0.0

    a1, *_, t1 = _orbital_elements(chart.TERRA, jd)[:11]
    a2 = _orbital_elements(index, jd)[0]

    r = a2 / a1

    num = math.acos((math.sqrt(r) + 1) / (r + (1 / math.sqrt(r))))
    den = math.pi * (1 - (1 / (r ** (3 / 2))))
    t_retro = t1 * (num / den)

    retrograde_period = abs(t_retro)

    return (
        retrograde_period * solar_year_length(jd) if unit == DAYS else retrograde_period
    )


def solar_year_length(jd: float) -> float:
    """Returns the tropical year length in days of the given Julian date.
    This is a direct copy of astro.com's calculations."""
    t = (jd - calc.J2000) / 365250
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # Arcsec per millennium
    dvel = (
        1296027711.03429
        + 2 * 109.15809 * t
        + 3 * 0.07207 * t2
        - 4 * 0.23530 * t3
        - 5 * 0.00180 * t4
        + 6 * 0.00020 * t5
    )
    # Degrees per millennium
    dvel /= 3600
    return 360 * 365250 / dvel


def _part_of_fortune(
    sun_lon: float, moon_lon: float, asc_lon: float, night: bool
) -> float:
    """Night & day calculations for Part of Fortune."""
    return asc_lon + sun_lon - moon_lon if night else asc_lon + moon_lon - sun_lon


def _part_of_spirit(
    sun_lon: float, moon_lon: float, asc_lon: float, night: bool
) -> float:
    """Night & day calculations for Part of Spirit."""
    return asc_lon + moon_lon - sun_lon if night else asc_lon + sun_lon - moon_lon


def _part_of_eros(
    venus_lon: float, spirit_lon: float, asc_lon: float, night: bool
) -> float:
    """Night & day calculations for Part of Eros."""
    return (
        asc_lon + spirit_lon - venus_lon if night else asc_lon + venus_lon - spirit_lon
    )


@cache
def _is_daytime(
    jd: float | None,
    lat: float,
    lon: float | None,
    armc: float | None,
    armc_obliquity: float | None,
) -> bool:
    """Function for is_daytime() and armc_is_daytime()."""
    sun = get_planet(chart.SUN, jd)
    asc = _get_angle(chart.ASC, jd, lat, lon, chart.PLACIDUS, armc, armc_obliquity)
    return is_daytime_from(sun, asc)


@cache
def _orbital_elements(index: int, jd: float) -> tuple:
    """Returns pyswisseph's orbital data for the passed object."""
    return swe.get_orbital_elements(jd + swe.deltat(jd), _SWE[index], swe.FLG_SWIEPH)


"""
PREDICTIVE CALCULATIONS
--------------------------------------------------------------------------------
These functions deal with predicting aspects, moon phases, eclipses, etc.
"""


def previous_aspect(index1: int, index2: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit previous
    to the passed Julian day."""
    return _search(index1, index2, jd, aspect, PREVIOUS)


def next_aspect(index1: int, index2: int, jd: float, aspect: float) -> float:
    """Returns the Julian day of the requested transit after
    the passed Julian day."""
    return _search(index1, index2, jd, aspect, NEXT)


def previous_new_moon(jd: float) -> float:
    """Fast rewind to approximate conjunction."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"])
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def previous_full_moon(jd: float) -> float:
    """Fast rewind to approximate opposition."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    distance = swe.difdegn(moon["lon"], sun["lon"] + 180)
    jd -= math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return previous_aspect(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def next_new_moon(jd: float) -> float:
    """Fast forward to approximate conjunction."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"], moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next_aspect(chart.SUN, chart.MOON, jd, calc.CONJUNCTION)


def next_full_moon(jd: float) -> float:
    """Fast forward to approximate opposition."""
    sun = get_planet(chart.SUN, jd)
    moon = get_planet(chart.MOON, jd)
    distance = swe.difdegn(sun["lon"] + 180, moon["lon"])
    jd += math.floor(distance) / math.ceil(calc.MEAN_MOTIONS[chart.MOON])
    return next_aspect(chart.SUN, chart.MOON, jd, calc.OPPOSITION)


def previous_solar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent global solar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(
        jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR, True
    )
    return _eclipse_type(res), tret[0]


def previous_lunar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the most recent lunar eclipse that occurred before the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR, True)
    return _eclipse_type(res), tret[0]


def next_solar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next global solar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR)
    return _eclipse_type(res), tret[0]


def next_lunar_eclipse(jd: float) -> tuple:
    """Returns the eclipse type and Julian date of the moment of maximum
    eclipse for the next lunar eclipse that occurred after the
    passed Julian date."""
    res, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR)
    return _eclipse_type(res), tret[0]


def _eclipse_type(swe_index: int) -> int:
    """Returns the internal index of an eclipse type based on pyswisseph's
    bit flags. This clears the ECL_CENTRAL / ECL_NONCENTRAL bits from the
    end and maintains the simple eclipse type flag."""
    return _SWE_ECLIPSES[(swe_index >> 2) << 2]


def _search(
    index1: int, index2: int, jd: float, aspect: float, direction: int
) -> float:
    """Iteratively searches for and returns the Julian date of the previous
    or next requested aspect. Useful for short dates and fast planets but too
    expensive for anything more advanced."""
    while True:
        planet1 = get_planet(index1, jd)
        planet2 = get_planet(index2, jd)
        distance = abs(swe.difdeg2n(planet1["lon"], planet2["lon"]))
        diff = abs(aspect - distance)

        if diff <= calc.MAX_ERROR:
            return jd

        add = direction
        speed = abs(
            max(planet1["speed"], planet2["speed"])
            - min(planet1["speed"], planet2["speed"])
        )

        if diff < speed:
            add *= diff / 180

        jd += add
