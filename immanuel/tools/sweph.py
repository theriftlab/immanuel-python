"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


This module provides easy access to relatively consistently standardized
pysweph data for all of the supported angles, houses, points and planets
relevant to creating charts. Many of the functions here, including angle
and house functions, accept either a Julian date or ARMC values as input.

"""

import swisseph as swe

from immanuel.const import chart, names

ALL = -1

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


def planet(index: int, jd: float) -> dict:
    """Returns a planet by Julian date. Can be used to return the six
    major asteroids supported by pysweph without using a separate file."""
    ec_res = swe.calc_ut(jd, _SWE[index])[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -true_earth_obliquity(jd))
    asteroid = type_of(index) == chart.ASTEROID
    return {
        "index": index,
        "type": chart.ASTEROID if asteroid else chart.PLANET,
        "name": names.ASTEROIDS[index] if asteroid else names.PLANETS[index],
        "lon": ec_res[0],
        "lat": ec_res[1],
        "dist": ec_res[2],
        "speed": ec_res[3],
        "dec": eq_res[1],
    }


def asteroid(index: int, jd: float) -> dict:
    """Returns an asteroid by Julian date and Swiss Ephemeris
    index from an external asteroid's file as specified
    in the settings module."""
    swe_index = index + swe.AST_OFFSET
    name = swe.get_planet_name(swe_index)
    ec_res = swe.calc_ut(jd, swe_index)[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -true_earth_obliquity(jd))
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


def fixed_star(name: str, jd: float) -> dict:
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


def pre_post_natal_eclipse(
    index: int, jd: float, eclipse_type: int, eclipse_jd: float
) -> dict:
    """Returns a calculated object based on the Moon's or Sun's position
    during a pre or post-natal lunar or solar eclipse. The declination
    value is based on the natal date."""
    eclipse_object = {
        chart.PRE_NATAL_SOLAR_ECLIPSE: swe.SUN,
        chart.PRE_NATAL_LUNAR_ECLIPSE: swe.MOON,
        chart.POST_NATAL_SOLAR_ECLIPSE: swe.SUN,
        chart.POST_NATAL_LUNAR_ECLIPSE: swe.MOON,
    }[index]
    ec_res = swe.calc_ut(eclipse_jd, eclipse_object)[0]
    eq_res = swe.cotrans((ec_res[0], ec_res[1], ec_res[2]), -true_earth_obliquity(jd))
    return {
        "index": index,
        "type": chart.ECLIPSE,
        "name": names.ECLIPSES[index],
        "eclipse_type": eclipse_type,
        "jd": eclipse_jd,
        "lon": ec_res[0],
        "lat": ec_res[1],
        "dist": ec_res[2],
        "speed": 0.0,
        "dec": eq_res[1],
    }


def syzygy(jd: float) -> dict:
    """Returns the Moon on the given Julian date as a syzygy point."""
    syzygy_moon = planet(chart.MOON, jd)
    return {
        "index": chart.SYZYGY,
        "type": chart.POINT,
        "name": names.POINTS[chart.SYZYGY],
        "lon": syzygy_moon["lon"],
        "lat": syzygy_moon["lat"],
        "speed": syzygy_moon["speed"],
        "dec": syzygy_moon["dec"],
    }


def part(index: int, jd: float, lon: float) -> dict:
    """Returns one of the Parts of Fortune, Spirit, or Eros from its
    ecliptic longitude as calculated by the part module."""
    dec = swe.cotrans((lon, 0, 0), -true_earth_obliquity(jd))[1]
    return {
        "index": index,
        "type": chart.POINT,
        "name": names.POINTS[index],
        "lon": lon,
        "lat": 0.0,
        "speed": 0.0,
        "dec": dec,
    }


def point(index: int, jd: float) -> dict:
    """Pull any remaining non-calculated points straight from pysweph."""
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
    dec = swe.cotrans((lon, lat, 0), -true_earth_obliquity(jd))[1]
    return {
        "index": index,
        "type": chart.POINT,
        "name": names.POINTS[index],
        "lon": lon,
        "lat": lat,
        "speed": speed,
        "dec": dec,
    }


def angle(
    index: int,
    jd: float | None = None,
    lat: float | None = None,
    lon: float | None = None,
    house_system: int | None = None,
    armc: float | None = None,
    armc_obliquity: float | None = None,
) -> dict:
    """Returns the specified angle (or all angles if index is ALL) based
    on either Julian date or ARMC."""
    if armc is not None:
        if lat is None or house_system is None or armc_obliquity is None:
            raise TypeError(
                "lat, house_system, and armc_obliquity must be provided when "
                "armc is used."
            )
        angles = angles_houses_vertex(
            lat=lat, house_system=house_system, armc=armc, armc_obliquity=armc_obliquity
        )["angles"]
    elif jd is not None:
        if lat is None or lon is None or house_system is None:
            raise TypeError(
                "lat, lon, and house_system must be provided when jd is used."
            )
        angles = angles_houses_vertex(
            jd=jd, lat=lat, lon=lon, house_system=house_system
        )["angles"]
    else:
        raise TypeError("Either jd or armc and armc_obliquity must be provided.")
    if index == ALL:
        return angles
    return angles[index]


def angles_houses_vertex(
    lat: float,
    house_system: int,
    first_house_lon: float | None = None,
    jd: float | None = None,
    lon: float | None = None,
    armc: float | None = None,
    armc_obliquity: float | None = None,
) -> dict:
    """Returns ecliptic longitudes for the houses, main angles, and the vertex,
    along with their speeds. Defaults to Placidus for main angles & vertex if
    a PLANET_ON_FIRST house system is chosen. Based on Julian date and
    lat / lon coordinates."""
    if armc is not None:
        if lat is None or armc_obliquity is None:
            raise TypeError(
                "lat and armc_obliquity must be provided when armc is used."
            )
        cusps, ascmc, cuspsspeed, ascmcspeed = swe.houses_armc_ex2(
            armc,
            lat,
            armc_obliquity,
            _SWE[
                house_system if house_system < chart.PLANET_ON_FIRST else chart.PLACIDUS
            ],
        )
        return _angles_houses_vertex_from_sweph(
            armc_obliquity,
            cusps,
            ascmc,
            cuspsspeed,
            ascmcspeed,
            first_house_lon,
        )
    if jd is not None:
        if lat is None or lon is None:
            raise TypeError("lat and lon must be provided when jd is used.")
        cusps, ascmc, cuspsspeed, ascmcspeed = swe.houses_ex2(
            jd,
            lat,
            lon,
            _SWE[
                house_system if house_system < chart.PLANET_ON_FIRST else chart.PLACIDUS
            ],
        )
        return _angles_houses_vertex_from_sweph(
            true_earth_obliquity(jd),
            cusps,
            ascmc,
            cuspsspeed,
            ascmcspeed,
            first_house_lon,
        )
    raise TypeError("Either jd or armc and armc_obliquity must be provided.")


def _angles_houses_vertex_from_sweph(
    obliquity: float,
    cusps: tuple,
    ascmc: tuple,
    cuspsspeed: tuple,
    ascmcspeed: tuple,
    first_house_lon: float | None,
) -> dict:
    """Get houses, angles & vertex direct from pysweph."""
    angles = {}
    for i in (chart.ASC, chart.MC, chart.ARMC):
        lon = ascmc[_SWE[i]]
        speed = ascmcspeed[_SWE[i]]
        dec = swe.cotrans((lon, 0, 0), -obliquity)[1]
        angles[i] = {
            "index": i,
            "type": chart.ANGLE,
            "name": names.ANGLES[i],
            "lon": lon,
            "speed": speed,
            "dec": dec,
        }
        if i in (chart.ASC, chart.MC):
            index = chart.DESC if i == chart.ASC else chart.IC
            angles[index] = {
                "index": index,
                "type": chart.ANGLE,
                "name": names.ANGLES[index],
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
            lon = cusps[i]
            size = swe.difdeg2n(cusps[i + 1 if i < 12 else 1], lon)
            speed = cuspsspeed[i]
            dec = swe.cotrans((lon, 0, 0), -obliquity)[1]
        houses[index] = {
            "index": index,
            "type": chart.HOUSE,
            "name": names.HOUSES[index],
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
        "name": names.POINTS[chart.VERTEX],
        "lon": vertex_lon,
        "speed": vertex_speed,
        "dec": vertex_dec,
    }
    return {
        "angles": angles,
        "houses": houses,
        "vertex": vertex,
    }


def true_earth_obliquity(jd: float) -> float:
    """Returns the true obliquity of the ecliptic for the given Julian date."""
    return swe.calc_ut(jd, swe.ECL_NUT)[0][0]


def mean_earth_obliquity(jd: float) -> float:
    """Returns the mean obliquity of the ecliptic for the given Julian date."""
    return swe.calc_ut(jd, swe.ECL_NUT)[0][1]


def orbital_elements(index: int, jd: float) -> dict:
    """Returns pysweph's orbital data for the passed object on the
    given Julian date."""
    elements = swe.get_orbital_elements(
        jd + swe.deltat(jd), _SWE[index], swe.FLG_SWIEPH | swe.FLG_J2000
    )
    return {
        "semimajor_axis": elements[0],
        "eccentricity": elements[1],
        "inclination": elements[2],
        "longitude_of_ascending_node": elements[3],
        "argument_of_periapsis": elements[4],
        "longitude_of_periapsis": elements[5],
        "mean_anomaly_at_epoch": elements[6],
        "true_anomaly_at_epoch": elements[7],
        "eccentric_anomaly_at_epoch": elements[8],
        "mean_longitude_at_epoch": elements[9],
        "sidereal_orbital_period": elements[10],
        "mean_daily_motion": elements[11],
        "tropical_period": elements[12],
        "synodic_period": elements[13],
        "time_of_perihelion_passage": elements[14],
        "perihelion_distance": elements[15],
        "aphelion_distance": elements[16],
    }


def type_of(index: int | str) -> int:
    """Returns the type index of any supported chart object index. This is
    either an internal object index, an official asteroid number, or a
    fixed star's name."""
    if isinstance(index, str):
        return chart.FIXED_STAR
    if index < chart.TYPE_MULTIPLIER:
        return chart.ASTEROID
    return index // chart.TYPE_MULTIPLIER * chart.TYPE_MULTIPLIER


def is_external(index: int | str) -> bool:
    """Returns whether a chart object must be read from a user-supplied
    ephemeris file rather than from those bundled with Immanuel."""
    return isinstance(index, int) and index < chart.TYPE_MULTIPLIER
