"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Provides a Config class that can be passed to a chart class on instantiation.
If none is passed, the default config is used - DEFAULTS, a simple instance
of the Config class. Some of the aspect and orb settings are maintained in
ChainMaps and getter/setter pairs to allow for cascading behavior.

This module also allows filepath(s) to ephemeris files to be changed or added.

"""

import copy
import os
from collections import ChainMap

import swisseph as swe

from immanuel.classes.localize import Localize
from immanuel.const import calc, chart, data, dignities

_ANGLES = (
    chart.ASC,
    chart.DESC,
    chart.MC,
    chart.IC,
)

_PLANETS = (
    chart.SUN,
    chart.MOON,
    chart.MERCURY,
    chart.VENUS,
    chart.MARS,
    chart.JUPITER,
    chart.SATURN,
    chart.URANUS,
    chart.NEPTUNE,
    chart.PLUTO,
)

_POINTS = (
    chart.NORTH_NODE,
    chart.SOUTH_NODE,
    chart.TRUE_NORTH_NODE,
    chart.TRUE_SOUTH_NODE,
    chart.SYZYGY,
    chart.PART_OF_FORTUNE,
    chart.PART_OF_SPIRIT,
    chart.PART_OF_EROS,
    chart.VERTEX,
    chart.LILITH,
    chart.TRUE_LILITH,
    chart.INTERPOLATED_LILITH,
)


class Config:
    def __init__(self):
        """Data that should be included for each chart type's output."""
        self.chart_data = {
            chart.NATAL: [
                data.NATIVE,
                data.HOUSE_SYSTEM,
                data.SHAPE,
                data.DIURNAL,
                data.MOON_PHASE,
                data.OBJECTS,
                data.HOUSES,
                data.ASPECTS,
                data.WEIGHTINGS,
            ],
            chart.SOLAR_RETURN: [
                data.NATIVE,
                data.SOLAR_RETURN_YEAR,
                data.SOLAR_RETURN_DATE_TIME,
                data.HOUSE_SYSTEM,
                data.SHAPE,
                data.DIURNAL,
                data.MOON_PHASE,
                data.OBJECTS,
                data.HOUSES,
                data.ASPECTS,
                data.WEIGHTINGS,
            ],
            chart.PROGRESSED: [
                data.NATIVE,
                data.PROGRESSION_DATE_TIME,
                data.PROGRESSED_DATE_TIME,
                data.PROGRESSION_METHOD,
                data.HOUSE_SYSTEM,
                data.SHAPE,
                data.DIURNAL,
                data.MOON_PHASE,
                data.OBJECTS,
                data.HOUSES,
                data.ASPECTS,
                data.WEIGHTINGS,
            ],
            chart.COMPOSITE: [
                data.NATIVE,
                data.PARTNER,
                data.HOUSE_SYSTEM,
                data.SHAPE,
                data.DIURNAL,
                data.MOON_PHASE,
                data.OBJECTS,
                data.HOUSES,
                data.ASPECTS,
                data.WEIGHTINGS,
            ],
            chart.TRANSITS: [
                data.NATIVE,
                data.HOUSE_SYSTEM,
                data.SHAPE,
                data.DIURNAL,
                data.MOON_PHASE,
                data.OBJECTS,
                data.HOUSES,
                data.ASPECTS,
                data.WEIGHTINGS,
            ],
        }

        """Default coordinates when none are supplied. Currently points to
        the GMT prime meridian."""
        self.default_latitude = 51.4779
        self.default_longitude = -0.0015

        """Whether or not the stringified output of chart objects should
        always display the object's motion even when it is typical for
        that object."""
        self.output_typical_object_motion = False

        """Rounding for formatted angle strings."""
        self.angle_precision = calc.SECOND

        """House system as supported by pysweph."""
        self.house_system = chart.PLACIDUS

        """Which planets, points etc. to show."""
        self.objects = [
            chart.ASC,
            chart.DESC,
            chart.MC,
            chart.IC,
            chart.TRUE_NORTH_NODE,
            chart.TRUE_SOUTH_NODE,
            chart.VERTEX,
            chart.PART_OF_FORTUNE,
            chart.TRUE_LILITH,
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
            chart.URANUS,
            chart.NEPTUNE,
            chart.PLUTO,
            chart.CHIRON,
        ]

        """Which planets, points etc. to use in chart shape calculations."""
        self.chart_shape_objects = [
            chart.SUN,
            chart.MOON,
            chart.MERCURY,
            chart.VENUS,
            chart.MARS,
            chart.JUPITER,
            chart.SATURN,
            chart.URANUS,
            chart.NEPTUNE,
            chart.PLUTO,
        ]

        """Orb for calculating chart shapes."""
        self.chart_shape_orb = 5.0

        """MC progression formula for secondary progressions."""
        self.mc_progression_method = calc.NAIBOD

        """Part of Fortune / Spirit / Eros formula."""
        self.part_formula = calc.DAY_NIGHT_FORMULA

        """Dignity settings."""
        self.rulerships = dignities.MODERN_RULERSHIPS
        self.triplicities = dignities.PTOLEMAIC_TRIPLICITIES
        self.terms = dignities.EGYPTIAN_TERMS
        self.include_participatory_triplicities = False
        self.include_mutual_receptions = True
        self.dignity_scores = {
            dignities.RULER: 5,
            dignities.EXALTED: 4,
            dignities.TRIPLICITY_RULER: 3,
            dignities.TERM_RULER: 2,
            dignities.FACE_RULER: 1,
            dignities.MUTUAL_RECEPTION_RULER: 5,
            dignities.MUTUAL_RECEPTION_EXALTED: 4,
            dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER: 3,
            dignities.MUTUAL_RECEPTION_TERM_RULER: 2,
            dignities.MUTUAL_RECEPTION_FACE_RULER: 1,
            dignities.DETRIMENT: -5,
            dignities.FALL: -4,
            dignities.PEREGRINE: -5,
        }

        """Which aspects to calculate and which objects can use them."""
        self._aspects = [
            calc.CONJUNCTION,
            calc.OPPOSITION,
            calc.SQUARE,
            calc.TRINE,
            calc.SEXTILE,
            calc.QUINCUNX,
        ]
        self.default_aspect_rule = ChainMap(
            {"initiate": self._aspects, "receive": self._aspects}
        )
        self._planet_aspect_rule = ChainMap(
            {"initiate": self._aspects, "receive": self._aspects}
        )
        self._point_aspect_rule = ChainMap(
            {"initiate": [calc.CONJUNCTION], "receive": self._aspects}
        )
        self.aspect_rules = {}
        for p in _PLANETS:
            self.aspect_rules[p] = ChainMap({}, self._planet_aspect_rule)
        for p in _POINTS + _ANGLES:
            self.aspect_rules[p] = ChainMap({}, self._point_aspect_rule)

        """Orbs for chart objects and their aspects."""
        self.default_orb = 1.0
        self.exact_orb = 0.3
        self.orb_calculation = calc.MEAN
        self._planet_orbs = ChainMap(
            {
                calc.CONJUNCTION: 10.0,
                calc.OPPOSITION: 10.0,
                calc.SQUARE: 10.0,
                calc.TRINE: 10.0,
                calc.SEXTILE: 6.0,
                calc.SEPTILE: 3.0,
                calc.SEMISQUARE: 3.0,
                calc.SESQUISQUARE: 3.0,
                calc.SEMISEXTILE: 3.0,
                calc.QUINCUNX: 3.0,
                calc.QUINTILE: 2.0,
                calc.BIQUINTILE: 2.0,
            }
        )
        self._point_orbs = ChainMap(
            {
                calc.CONJUNCTION: 0.0,
                calc.OPPOSITION: 0.0,
                calc.SQUARE: 0.0,
                calc.TRINE: 0.0,
                calc.SEXTILE: 0.0,
                calc.SEPTILE: 0.0,
                calc.SEMISQUARE: 0.0,
                calc.SESQUISQUARE: 0.0,
                calc.SEMISEXTILE: 0.0,
                calc.QUINCUNX: 0.0,
                calc.QUINTILE: 0.0,
                calc.BIQUINTILE: 0.0,
            }
        )
        self.orbs = {}
        for p in _ANGLES + _PLANETS:
            self.orbs[p] = ChainMap({}, self._planet_orbs)
        for p in _POINTS:
            self.orbs[p] = ChainMap({}, self._point_orbs)

    """The following getters and setters are simple wrappers for the ChainMaps
    used to maintain our cascading settings behavior for aspects and orbs."""

    @property
    def aspects(self) -> list[float]:
        return self._aspects

    @aspects.setter
    def aspects(self, value) -> None:
        self._aspects[:] = value

    @property
    def planet_aspect_rule(self) -> ChainMap:
        return self._planet_aspect_rule

    @planet_aspect_rule.setter
    def planet_aspect_rule(self, value: dict) -> None:
        self._planet_aspect_rule.maps[0].update(value)

    @property
    def point_aspect_rule(self) -> ChainMap:
        return self._point_aspect_rule

    @point_aspect_rule.setter
    def point_aspect_rule(self, value: dict) -> None:
        self._point_aspect_rule.maps[0].update(value)

    @property
    def planet_orbs(self) -> ChainMap:
        return self._planet_orbs

    @planet_orbs.setter
    def planet_orbs(self, value: dict) -> None:
        self._planet_orbs.maps[0].update(value)

    @property
    def point_orbs(self) -> ChainMap:
        return self._point_orbs

    @point_orbs.setter
    def point_orbs(self, value: dict) -> None:
        self._point_orbs.maps[0].update(value)

    def copy(self) -> "Config":
        return copy.deepcopy(self)


"""Anything that requires config as an argument should fall back to this
as a default. It should never be modified but should be copied for each chart
class instance."""
DEFAULTS = Config()


"""
Everything below is global rather than per-chart.
"""

_DEFAULT_FILE_PATH = f"{os.path.dirname(__file__)}{os.sep}resources{os.sep}ephemeris"
_file_path = _DEFAULT_FILE_PATH


def add_filepath(path: str, default: bool = False) -> None:
    """Add an ephemeris file path, or replace the default one."""
    global _file_path
    if default:
        _file_path = path
    else:
        extra_path = f"{os.pathsep}{path}"
        if _file_path.endswith(extra_path):
            return
        _file_path += extra_path
    set_swe_filepath()


def set_swe_filepath() -> None:
    """Pass defined path(s) to swisseph."""
    swe.set_ephe_path(_file_path)


def set_locale(lcid: str | None) -> None:
    """Set the locale for all translated output, or pass None to return to
    untranslated English."""
    if lcid is None:
        Localize.reset()
    else:
        Localize.set_locale(lcid)


def locale() -> str | None:
    """Returns the currently active locale, or None if untranslated."""
    return Localize.lcid


def reset() -> None:
    """Reset the global settings state - in practice this is the locale
    and the ephemeris file paths."""
    global _file_path
    _file_path = _DEFAULT_FILE_PATH
    set_swe_filepath()
    Localize.reset()


set_swe_filepath()
