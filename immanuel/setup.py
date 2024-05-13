"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Provides a simple set of default settings that can be overridden.
    Also allows filepath(s) to ephemeris files to be changed or added.

"""

import os
from typing import Any

import swisseph as swe

from immanuel.classes.localize import Localize
from immanuel.const import calc, chart, data, dignities


class BaseSettings:
    def __init__(self) -> None:
        """ Set locale. """
        self._locale = None

        """ Default ephemeris file path. """
        self._file_path = f'{os.path.dirname(__file__)}{os.sep}resources{os.sep}ephemeris'

        """ Data that should be included for each chart type's output. """
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

        """ Default coordinates when none are supplied. Currently points to
        the GMT prime meridian. """
        self.default_latitude = 51.4779

        self.default_longitude = -0.0015

        """ Whether or not the stringified output of chart objects should
        always display the object's motion even when it is typical for
        that object. """
        self.output_typical_object_motion = False

        """ Rounding for formatted angle strings. """
        self.angle_precision = calc.SECOND

        """ House system as supported by pyswisseph. """
        self.house_system = chart.PLACIDUS

        """ Which planets, points etc. to show. """
        self.objects = [
            chart.ASC, chart.DESC, chart.MC, chart.IC,
            chart.TRUE_NORTH_NODE, chart.TRUE_SOUTH_NODE,
            chart.VERTEX, chart.PART_OF_FORTUNE,
            chart.TRUE_LILITH,
            chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
            chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
            chart.CHIRON,
        ]

        """ Which planets, points etc. to use in chart shape calculations. """
        self.chart_shape_objects = [
            chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
            chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
        ]

        """ Which aspects to calculate. """
        self.aspects = [
            calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
            calc.QUINCUNX,
        ]

        """ Orbs for chart objects and their aspects. """
        self.default_orb = 1.0

        self.exact_orb = 0.3

        self.orb_calculation = calc.MEAN

        self.planet_orbs = {
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

        self.point_orbs = {
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

        """ Orb for calculating chart shapes. """
        self.chart_shape_orb = 5.0

        """ MC progression formula for secondary progressions. """
        self.mc_progression_method = calc.NAIBOD

        """ Part of Fortune / Spirit / Eros formula. """
        self.part_formula = calc.DAY_NIGHT_FORMULA

        """ Dignity settings. """
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

        """ Set up empty dicts for cascading settings. """
        self._default_aspect_rule = {}
        self._planet_aspect_rule = {}
        self._point_aspect_rule = {}
        self._aspect_rules = {}
        self._orbs = {}

    @property
    def locale(self) -> str:
        return self._locale

    @locale.setter
    def locale(self, lcid: str) -> None:
        self._locale = lcid
        Localize.set_locale(lcid)

    @property
    def default_aspect_rule(self) -> dict:
        """ Cascading setting - default aspects allowed for objects. """
        return  {
            'initiate': self.aspects,
            'receive': self.aspects,
        } | self._default_aspect_rule

    @default_aspect_rule.setter
    def default_aspect_rule(self, value: dict) -> None:
        self._default_aspect_rule = value

    @property
    def planet_aspect_rule(self) -> dict:
        """ Cascading setting - default aspects allowed for planets. """
        return  {
            'initiate': self.aspects,
            'receive': self.aspects,
        } | self._planet_aspect_rule

    @planet_aspect_rule.setter
    def planet_aspect_rule(self, value: dict) -> None:
        self._planet_aspect_rule = value

    @property
    def point_aspect_rule(self) -> dict:
        """ Cascading setting - default aspects allowed for points. """
        return  {
            'initiate': [calc.CONJUNCTION,],
            'receive': self.aspects,
        } | self._point_aspect_rule

    @point_aspect_rule.setter
    def point_aspect_rule(self, value: dict) -> None:
        self._point_aspect_rule = value

    @property
    def aspect_rules(self) -> dict:
        """ Cascading setting - explicit aspects allowed per object. """
        return {
            chart.ASC: self.point_aspect_rule,
            chart.DESC: self.point_aspect_rule,
            chart.MC: self.point_aspect_rule,
            chart.IC: self.point_aspect_rule,

            chart.SUN: self.planet_aspect_rule,
            chart.MOON: self.planet_aspect_rule,
            chart.MERCURY: self.planet_aspect_rule,
            chart.VENUS: self.planet_aspect_rule,
            chart.MARS: self.planet_aspect_rule,
            chart.JUPITER: self.planet_aspect_rule,
            chart.SATURN: self.planet_aspect_rule,
            chart.URANUS: self.planet_aspect_rule,
            chart.NEPTUNE: self.planet_aspect_rule,
            chart.PLUTO: self.planet_aspect_rule,

            chart.NORTH_NODE: self.point_aspect_rule,
            chart.SOUTH_NODE: self.point_aspect_rule,
            chart.TRUE_NORTH_NODE: self.point_aspect_rule,
            chart.TRUE_SOUTH_NODE: self.point_aspect_rule,
            chart.SYZYGY: self.point_aspect_rule,
            chart.PART_OF_FORTUNE: self.point_aspect_rule,
            chart.PART_OF_SPIRIT: self.point_aspect_rule,
            chart.PART_OF_EROS: self.point_aspect_rule,
            chart.VERTEX: self.point_aspect_rule,
            chart.LILITH: self.point_aspect_rule,
            chart.TRUE_LILITH: self.point_aspect_rule,
            chart.INTERPOLATED_LILITH: self.point_aspect_rule,
        } | self._aspect_rules

    @aspect_rules.setter
    def aspect_rules(self, value: dict) -> None:
        self._aspect_rules = value

    @property
    def orbs(self) -> dict:
        """ Cascading setting - explicit orbs allowed per object. """
        return {
            chart.ASC: self.planet_orbs,
            chart.DESC: self.planet_orbs,
            chart.MC: self.planet_orbs,
            chart.IC: self.planet_orbs,

            chart.SUN: self.planet_orbs,
            chart.MOON: self.planet_orbs,
            chart.MERCURY: self.planet_orbs,
            chart.VENUS: self.planet_orbs,
            chart.MARS: self.planet_orbs,
            chart.JUPITER: self.planet_orbs,
            chart.SATURN: self.planet_orbs,
            chart.URANUS: self.planet_orbs,
            chart.NEPTUNE: self.planet_orbs,
            chart.PLUTO: self.planet_orbs,

            chart.NORTH_NODE: self.point_orbs,
            chart.SOUTH_NODE: self.point_orbs,
            chart.TRUE_NORTH_NODE: self.point_orbs,
            chart.TRUE_SOUTH_NODE: self.point_orbs,
            chart.SYZYGY: self.point_orbs,
            chart.PART_OF_FORTUNE: self.point_orbs,
            chart.PART_OF_SPIRIT: self.point_orbs,
            chart.PART_OF_EROS: self.point_orbs,
            chart.VERTEX: self.point_orbs,
            chart.LILITH: self.point_orbs,
            chart.TRUE_LILITH: self.point_orbs,
            chart.INTERPOLATED_LILITH: self.point_orbs,
        } | self._orbs

    @orbs.setter
    def orbs(self, value: dict) -> None:
        self._orbs = value

    def add_filepath(self, path: str, default: bool = False) -> None:
        """ Add an ephemeris file path. """
        if default:
            self._file_path = path
        else:
            extra_path = f'{os.pathsep}{path}'

            if self._file_path.endswith(extra_path):
                return

            self._file_path += extra_path

        self.set_swe_filepath()

    def set_swe_filepath(self) -> None:
        """ Pass defined path(s) to swisseph. """
        swe.set_ephe_path(self._file_path)


class StaticSingleton(type):
    """ Metaclass to ensure singleton behavior & route everything to
    our BaseSettings instance to emulate static behavior. """
    _instance = BaseSettings()

    def reset(cls) -> None:
        """ Reset all settings to default. """
        StaticSingleton._instance = BaseSettings()
        StaticSingleton._instance.set_swe_filepath()
        Localize.reset()

    def set(cls, values: dict) -> None:
        """ Helper mass-set method. """
        for key, value in values.items():
            setattr(StaticSingleton._instance, key, value)

    def __getattr__(cls, name: str) -> Any:
        return getattr(StaticSingleton._instance, name)

    def __setattr__(cls, name: str, value: Any) -> None:
        return setattr(StaticSingleton._instance, name, value)


class settings(metaclass=StaticSingleton):
    """ Expose actual class for import. """
    pass
