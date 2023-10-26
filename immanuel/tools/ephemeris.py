"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides easy access to fairly standardised pyswisseph data.

    Relevant data on the main angles, houses, points and planets are
    available using the module's functions, many of which are cached.

    Many of the functions here, including angle, house and vertex functions,
    have an "armc_"-prefixed alternative if they are required to calculate
    from an ARMC.

"""

from functools import cache

import swisseph as swe

from immanuel.const import chart, names
from immanuel.tools import calculate, find


ALL = -1

_SWE = {
    chart.ALCABITUS: b'B',
    chart.AZIMUTHAL: b'H',
    chart.CAMPANUS: b'C',
    chart.EQUAL: b'A',
    chart.KOCH: b'K',
    chart.MERIDIAN: b'X',
    chart.MORINUS: b'M',
    chart.PLACIDUS: b'P',
    chart.POLICH_PAGE: b'T',
    chart.PORPHYRIUS: b'O',
    chart.REGIOMONTANUS: b'R',
    chart.VEHLOW_EQUAL: b'V',
    chart.WHOLE_SIGN: b'W',

    chart.ASC: swe.ASC,
    chart.DESC: swe.ASC,
    chart.MC: swe.MC,
    chart.IC: swe.MC,
    chart.ARMC: swe.ARMC,

    chart.SUN: swe.SUN,
    chart.MOON: swe.MOON,
    chart.MERCURY: swe.MERCURY,
    chart.VENUS: swe.VENUS,
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
    chart.SYZYGY: chart.SYZYGY,
    chart.PARS_FORTUNA: chart.PARS_FORTUNA,
}


def objects(object_list: tuple, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function returns a dict of all passed chart objects. """
    return _objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=None,
        armc_obliquity=None
    )


def armc_objects(object_list: tuple, jd: float, armc: float, lat: float = None, lon: float = None, obliquity: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function returns a dict of all passed chart objects
    with houses & angles calculated from the passed ARMC. """
    return _objects(
        object_list=object_list,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=armc,
        armc_obliquity=obliquity
    )


def get(index: int | str, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star. """
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=None,
        armc_obliquity=None
    )


def armc_get(index: int | str, jd: float, armc: float, lat: float = None, lon: float = None, obliquity: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Helper function to retrieve an angle, house, planet, point,
    asteroid, or fixed star with houses & angles calculated from the
    passed ARMC. """
    return _get(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=armc,
        armc_obliquity=obliquity
    )


def angles(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns all four main chart angles & ARMC. """
    return _angle(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None
    )


def armc_angles(jd: float, armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns all four main chart angles calculated from the
    passed ARMC. """
    return _angle(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity
    )


def angle(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns one of the four main chart angles & its speed. Also stores
    the ARMC for further calculations. Returns all if index == ALL. """
    return _angle(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None
    )


def armc_angle(index: int, jd: float, armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns one of the four main chart angles & its speed, calculated from
    the passed ARMC. Returns all if index == ALL. """
    return _angle(
        index=index,
        jd=jd,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity
    )


def houses(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns all houses. """
    return _house(
        index=ALL,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None
    )


def armc_houses(armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns all houses calculated from the passed ARMC. """
    return _house(
        index=ALL,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity
    )


def house(index: int, jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL. """
    return _house(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        armc=None,
        armc_obliquity=None
    )


def armc_house(index: int, armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns a house cusp & its speed, or all houses if index == ALL,
    calculated from passed ARMC. """
    return _house(
        index=index,
        jd=None,
        lat=lat,
        lon=None,
        house_system=house_system,
        armc=armc,
        armc_obliquity=obliquity
    )


def point(index: int, jd: float, lat: float = None, lon: float = None, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Returns a calculated point by Julian date, and additionally by lat / lon
    coordinates. """
    return _point(
        index=index,
        jd=jd,
        lat=lat,
        lon=lon,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=None,
        armc_obliquity=None
    )


def armc_point(index: int, jd: float, armc: float, lat: float, obliquity: float, house_system: int = None, pars_fortuna_formula: int = None) -> dict:
    """ Returns a calculated point by Julian date, and additionally by the
    passed ARMC. """
    return _point(
        index=index,
        jd=jd,
        lat=lat,
        lon=None,
        house_system=house_system,
        pars_fortuna_formula=pars_fortuna_formula,
        armc=armc,
        armc_obliquity=obliquity
    )


def _objects(object_list: tuple, jd: float, lat: float, lon: float, house_system: int, pars_fortuna_formula: int, armc: float, armc_obliquity: float) -> dict:
    """ Function for items() and armc_items(). """
    objects = {}

    for index in object_list:
        objects[index] = _get(index, jd, lat, lon, house_system, pars_fortuna_formula, armc, armc_obliquity)

    return objects


def _get(index: int | str, jd: float, lat: float, lon: float, house_system: int, pars_fortuna_formula: int, armc: float, armc_obliquity: float) -> dict:
    """ Function for get() and armc_get(). """
    if armc is not None and armc_obliquity is None:
        armc_obliquity = obliquity(jd)

    if isinstance(index, int):
        if index < chart.TYPE_MULTIPLIER:
            return asteroid(index, jd)

        if index == chart.ANGLE:
            return _angle(ALL, jd, lat, lon, house_system, armc, armc_obliquity)

        if index == chart.HOUSE:
            return _house(ALL, jd, lat, lon, house_system, armc, armc_obliquity)

        match _type(index):
            case chart.ANGLE:
                return _angle(index, jd, lat, lon, house_system, armc, armc_obliquity)
            case chart.HOUSE:
                return _house(index, jd, lat, lon, house_system, armc, armc_obliquity)
            case chart.POINT:
                return _point(index, jd, lat, lon, house_system, pars_fortuna_formula, armc, armc_obliquity)
            case chart.ECLIPSE:
                return eclipse(index, jd)
            case (chart.ASTEROID|chart.PLANET):
                return planet(index, jd)
    else:
        return fixed_star(index, jd)


def _angle(index: int, jd: float, lat: float, lon: float, house_system: int, armc: float, armc_obliquity: float) -> dict:
    """ Function for angle() and armc_angle(). """
    if armc is not None:
        angles = _angles_houses_vertex_armc(armc, lat, armc_obliquity, house_system)['angles']
    else:
        angles = _angles_houses_vertex(jd, lat, lon, house_system)['angles']

    if index == ALL:
        return angles

    if index in angles:
        return angles[index]

    return None


def _house(index: int, jd: float, lat: float, lon: float, house_system: int, armc: float, armc_obliquity: float) -> dict:
    """ Function for house() and armc_house(). """
    if armc is not None:
        houses = _angles_houses_vertex_armc(armc, lat, armc_obliquity, house_system)['houses']
    else:
        houses = _angles_houses_vertex(jd, lat, lon, house_system)['houses']

    if index == ALL:
        return houses

    if index in houses:
        return houses[index]

    return None


def _point(index: int, jd: float, lat: float, lon: float, house_system: int, pars_fortuna_formula: int, armc: float, armc_obliquity: float) -> dict:
    """ Function for point() and armc_point(). """
    if index == chart.VERTEX:
        if armc is not None:
            return _angles_houses_vertex_armc(armc, lat, armc_obliquity, house_system)['vertex']
        else:
            return _angles_houses_vertex(jd, lat, lon, house_system)['vertex']

    if index == chart.SYZYGY:
        return _syzygy(jd)

    if index == chart.PARS_FORTUNA:
        return _pars_fortuna(jd, lat, lon, pars_fortuna_formula, armc, armc_obliquity)

    return _swisseph_point(index, jd)


@cache
def planet(index: int, jd: float) -> dict:
    """ Returns a pyswisseph object by Julian date. Can be used to
    return the six major asteroids supported by pyswisseph without using
    a separate ephemeris file. """
    ec_res = swe.calc_ut(jd, _SWE[index])[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -obliquity(jd))
    asteroid = _type(index) == chart.ASTEROID

    return {
        'index': index,
        'type': chart.ASTEROID if asteroid else chart.PLANET,
        'name': names.ASTEROIDS[index] if asteroid else names.PLANETS[index],
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def asteroid(index: int, jd: float) -> dict:
    """ Returns an asteroid by Julian date and pyswisseph index
    from an external asteroid's ephmeris file as specified
    in the setup module. """
    if _type(index) == chart.ASTEROID:
        return planet(index, jd)

    swe_index = index + swe.AST_OFFSET
    name = swe.get_planet_name(swe_index)

    ec_res = swe.calc_ut(jd, swe_index)[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -obliquity(jd))

    return {
        'index': index,
        'type': chart.ASTEROID,
        'name': name,
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': ec_res[3],
        'dec': eq_res[1],
    }


@cache
def fixed_star(name: str, jd: float) -> dict:
    """ Returns a fixed star by Julian date and name. """
    res, stnam = swe.fixstar2_ut(name, jd)[:2]
    name = stnam.partition(',')[0]

    return {
        'index': name,
        'type': chart.FIXED_STAR,
        'name': name,
        'lon': res[0],
        'lat': res[1],
        'dist': res[2],
        'speed': res[3],
    }


@cache
def eclipse(index: int, jd: float) -> dict:
    """ Returns a calculated object based on the moon's or sun's position
    during a pre or post-natal lunar or solar eclipse. The declination
    value is based on the natal date. """
    match index:
        case chart.PRE_NATAL_SOLAR_ECLIPSE:
            eclipse_type, eclipse_jd = find.previous_solar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.SUN)[0]
        case chart.PRE_NATAL_LUNAR_ECLIPSE:
            eclipse_type, eclipse_jd = find.previous_lunar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.MOON)[0]
        case chart.POST_NATAL_SOLAR_ECLIPSE:
            eclipse_type, eclipse_jd = find.next_solar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.SUN)[0]
        case chart.POST_NATAL_LUNAR_ECLIPSE:
            eclipse_type, eclipse_jd = find.next_lunar_eclipse(jd)
            ec_res = swe.calc_ut(eclipse_jd, swe.MOON)[0]

    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -obliquity(jd))

    return {
        'index': index,
        'type': chart.ECLIPSE,
        'name': names.ECLIPSES[index],
        'eclipse_type': eclipse_type,
        'jd': eclipse_jd,
        'lon': ec_res[0],
        'lat': ec_res[1],
        'dist': ec_res[2],
        'speed': 0.0,
        'dec': eq_res[1],
    }


@cache
def moon_phase(jd: float) -> int:
    """ Returns the moon phase at the given Julian date. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    return calculate.moon_phase(sun, moon)


@cache
def obliquity(jd: float, mean: bool = False) -> float:
    """ Returns the earth's true or mean obliquity at the
    given Julian date. """
    ecl_nut = swe.calc_ut(jd, swe.ECL_NUT)[0]
    return ecl_nut[1] if mean else ecl_nut[0]


def deltat(jd: float, seconds: bool = False) -> float:
    """ Return the Delta-T value of the passed Julian date. Optionally it
    will return this value in seconds. """
    return swe.deltat(jd) if not seconds else swe.deltat(jd) * 24 * 3600


def is_daytime(jd: float, lat: float, lon: float) -> bool:
    """ Returns whether the sun is above the horizon line at the time and
    place specified. """
    return _is_daytime(
        jd=jd,
        lat=lat,
        lon=lon,
        armc=None,
        armc_obliquity=None
    )


def armc_is_daytime(jd: float, armc: float, lat: float, obliquity: float) -> bool:
    """ Returns whether the sun is above the horizon line at the time and
    place specified, as calculated by the passed ARMC. """
    return _is_daytime(
        jd=jd,
        lat=lat,
        lon=None,
        armc=armc,
        armc_obliquity=obliquity
    )


@cache
def _is_daytime(jd: float, lat: float, lon: float, armc: float, armc_obliquity: float) -> bool:
    """ Function for is_daytime() and armc_is_daytime(). """
    sun = planet(chart.SUN, jd)
    asc = _angle(chart.ASC, jd, lat, lon, chart.PLACIDUS, armc, armc_obliquity)
    return calculate.is_daytime(sun, asc)


@cache
def _angles_houses_vertex(jd: float, lat: float, lon: float, house_system: int) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles,
    and the vertex, along with their speeds. Based on Julian
    date and lat / lon coordinates. """
    return _angles_houses_vertex_from_swe(*swe.houses_ex2(jd, lat, lon, _SWE[house_system]))


@cache
def _angles_houses_vertex_armc(armc: float, lat: float, obliquity: float, house_system: int) -> dict:
    """ Returns ecliptic longitudes for the houses, main angles,
    and the vertex, along with their speeds. Based on ARMC, latitude
    and ecliptic obliquity. """
    return _angles_houses_vertex_from_swe(*swe.houses_armc_ex2(armc, lat, obliquity, _SWE[house_system]))


def _angles_houses_vertex_from_swe(cusps: tuple, ascmc: tuple, cuspsspeed: tuple, ascmcspeed: tuple) -> dict:
    """ Get houses, angles & vertex direct from pyswisseph. """
    angles = {}

    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[_SWE[i]]

        angles[i] = {
            'index': i,
            'type': chart.ANGLE,
            'name': names.ANGLES[i],
            'lon': lon,
            'speed': ascmcspeed[_SWE[i]],
        }

        if i in (chart.ASC, chart.MC):
            index = chart.DESC if i == chart.ASC else chart.IC

            angles[index] = {
                'index': index,
                'type': chart.ANGLE,
                'name': names.ANGLES[index],
                'lon': swe.degnorm(lon - 180),
                'speed': ascmcspeed[_SWE[i]],
            }

    houses = {}

    for i, lon in enumerate(cusps, start=1):
        index = chart.HOUSE + i
        size = swe.difdeg2n(cusps[i if i < 12 else 0], lon)

        houses[index] = {
            'index': index,
            'type': chart.HOUSE,
            'name': names.HOUSES[index],
            'number': i,
            'lon': lon,
            'size': size,
            'speed': cuspsspeed[i-1],
        }

    vertex = {
        'index': chart.VERTEX,
        'type': chart.POINT,
        'name': names.POINTS[chart.VERTEX],
        'lon': ascmc[_SWE[chart.VERTEX]],
        'speed': ascmcspeed[_SWE[chart.VERTEX]],
    }

    return {
        'angles': angles,
        'houses': houses,
        'vertex': vertex,
    }


@cache
def _syzygy(jd: float) -> dict:
    """ Calculate prenatal full/new moon - this can potentially
    be an expensive calculation so should be cached. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    distance = swe.difdeg2n(moon['lon'], sun['lon'])
    syzygy_jd = find.previous_new_moon(jd) if distance > 0 else find.previous_full_moon(jd)
    syzygy_moon = planet(chart.MOON, syzygy_jd)

    return {
        'index': chart.SYZYGY,
        'type': chart.POINT,
        'name': names.POINTS[chart.SYZYGY],
        'lon': syzygy_moon['lon'],
        'speed': syzygy_moon['speed'],
    }


@cache
def _pars_fortuna(jd: float, lat: float, lon: float, formula: int, armc: float = None, armc_obliquity: float = None) -> dict:
    """ Calculate Part of Fortune - this relies on the ascendant which will be
    consistent across all supported systems, so it is safe to pass Placidus as
    the default. """
    sun = planet(chart.SUN, jd)
    moon = planet(chart.MOON, jd)
    asc = angle(chart.ASC, jd, lat, lon, chart.PLACIDUS) if armc is None else armc_angle(chart.ASC, jd, armc, lat, armc_obliquity, chart.PLACIDUS)
    lon = calculate.pars_fortuna_longitude(sun, moon, asc, formula)

    return {
        'index': chart.PARS_FORTUNA,
        'type': chart.POINT,
        'name': names.POINTS[chart.PARS_FORTUNA],
        'lon': lon,
        'speed': 0.0,
    }


@cache
def _swisseph_point(index: int, jd: float) -> dict:
    """ Pull any remaining non-calculated points straight from pyswisseph. """
    res = swe.calc_ut(jd, _SWE[index])[0]

    return {
        'index': index,
        'type': chart.POINT,
        'name': names.POINTS[index],
        'lon': res[0] if index not in (chart.SOUTH_NODE, chart.TRUE_SOUTH_NODE) else swe.degnorm(res[0] - 180),
        'speed': res[3],
    }


def _type(index: int) -> int:
    """ Return the type index of a given object's index. """
    return round(index, -2)
