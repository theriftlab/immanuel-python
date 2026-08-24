"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Provides a ChartConfig class that can be passed to a chart class on
instantiation. If none is passed, the default config is used - DEFAULTS,
a simple instance of the ChartConfig class. Some of the aspect and orb
settings are maintained in ChainMaps and getter/setter pairs to allow for
cascading behavior.

This module also allows the filepath(s) to the ephemeris files to be changed
or appended.

"""

import copy
import os
from collections import ChainMap
from types import MappingProxyType
from typing import Any

import swisseph as swe

from immanuel.const import calc, chart, data, dignities


class ChartConfig:
    def __init__(self):
        """Locale ID string. Defaults to None, which is treated as en_US."""
        self.locale: str | None = None

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
        self.rulerships = dignities.MODERN_RULERSHIPS.copy()
        self.triplicities = dignities.PTOLEMAIC_TRIPLICITIES.copy()
        self.terms = dignities.EGYPTIAN_TERMS.copy()
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
        self._default_aspect_rule = ChainMap(
            {"initiate": self._aspects, "receive": self._aspects}
        )
        self._planet_aspect_rule = ChainMap(
            {"initiate": self._aspects, "receive": self._aspects}
        )
        self._point_aspect_rule = ChainMap(
            {"initiate": [calc.CONJUNCTION], "receive": self._aspects}
        )
        self._aspect_rules = ChainMap()
        for index in chart.PLANETS:
            self._aspect_rules[index] = ChainMap({}, self._planet_aspect_rule)
        for index in chart.POINTS + chart.ANGLES:
            self._aspect_rules[index] = ChainMap({}, self._point_aspect_rule)

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
        self._orbs = ChainMap()
        for index in chart.ANGLES + chart.PLANETS:
            self._orbs[index] = ChainMap({}, self._planet_orbs)
        for index in chart.POINTS:
            self._orbs[index] = ChainMap({}, self._point_orbs)

    """The following getters and setters are simple wrappers for the ChainMaps
    used to maintain our cascading settings behavior for aspects and orbs."""

    @property
    def aspects(self) -> list[float]:
        return self._aspects

    @aspects.setter
    def aspects(self, value) -> None:
        self._aspects[:] = value

    @property
    def default_aspect_rule(self) -> ChainMap:
        return self._default_aspect_rule

    @default_aspect_rule.setter
    def default_aspect_rule(self, value: dict) -> None:
        self._default_aspect_rule.maps[0].update(value)

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
    def aspect_rules(self) -> ChainMap:
        return self._aspect_rules

    @aspect_rules.setter
    def aspect_rules(self, value: dict) -> None:
        self._aspect_rules.maps[0].update(value)

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

    @property
    def orbs(self) -> ChainMap:
        return self._orbs

    @orbs.setter
    def orbs(self, value: dict) -> None:
        self._orbs.maps[0].update(value)

    def copy(self) -> "ChartConfig":
        return copy.deepcopy(self)


class FrozenChartConfig(ChartConfig):
    """This creates an immutable snapshot of a ChartConfig instance. For read-only
    purposes, this is much more efficient to read from and copy."""

    _CHAINMAPS = {
        "_aspect_rules",
        "_default_aspect_rule",
        "_orbs",
        "_planet_aspect_rule",
        "_planet_orbs",
        "_point_aspect_rule",
        "_point_orbs",
    }

    def __init__(self, config: ChartConfig) -> None:
        for key, value in config.__dict__.items():
            self.__dict__[key] = (
                _freeze(value) if key in self._CHAINMAPS else copy.deepcopy(value)
            )

    def __setattr__(self, name, value):
        raise AttributeError("Cannot set attribute on an immutable instance.")

    def copy(self) -> "FrozenChartConfig":
        return self


def _freeze(value: Any) -> Any:
    """Recursively freeze ChartConfig's ChainMaps and lists
    into immutable types."""
    if isinstance(value, (ChainMap, dict)):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(value)
    return value


DEFAULTS = FrozenChartConfig(ChartConfig())


"""
Everything below is global / per-process rather than per-chart.
"""

_DEFAULT_SWE_FILE_PATH = (
    f"{os.path.dirname(__file__)}{os.sep}resources{os.sep}ephemeris"
)
_swe_file_path = _DEFAULT_SWE_FILE_PATH


def set_swe_filepath() -> None:
    """Pass defined path(s) to swisseph."""
    swe.set_ephe_path(_swe_file_path)


def add_swe_filepath(path: str, default: bool = False) -> None:
    """Add an ephemeris file path, or replace the default one."""
    global _swe_file_path
    if default:
        _swe_file_path = path
    else:
        extra_path = f"{os.pathsep}{path}"
        if _swe_file_path.endswith(extra_path):
            return
        _swe_file_path += extra_path
    set_swe_filepath()


def reset_swe_filepath() -> None:
    """Reset the global settings file paths."""
    global _swe_file_path
    _swe_file_path = _DEFAULT_SWE_FILE_PATH
    set_swe_filepath()
