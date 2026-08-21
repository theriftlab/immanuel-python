"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Defines flexible classes to represent data in multiple formats.
While user-friendly names are defined in the const.names module,
JSON keys are defined here, either explicitly or as class members.

"""

from __future__ import annotations

from datetime import datetime

from immanuel.classes.localize import localize as _
from immanuel.classes.subject import Subject as ChartSubject
from immanuel.const import calc, chart, contexts, dignities, names
from immanuel.reports import dignity
from immanuel.settings import DEFAULTS, Config
from immanuel.tools import condition, convert, date, ephemeris, position


class Angle:
    precision = {
        calc.DEGREE: convert.ROUND_DEGREE,
        calc.MINUTE: convert.ROUND_MINUTE,
        calc.SECOND: convert.ROUND_SECOND,
    }

    def __init__(
        self,
        angle: float,
        format: int = convert.FORMAT_DMS,
        round_to: int = calc.SECOND,
    ) -> None:
        self.raw = angle
        self.formatted = convert.dec_to_string(
            angle, format=format, round_to=Angle.precision[round_to]
        )
        self.direction, self.degrees, self.minutes, self.seconds = convert.dec_to_dms(
            angle
        )

    def __str__(self) -> str:
        return self.formatted


class Aspect:
    def __init__(
        self,
        aspect: dict,
        active_name: str,
        passive_name: str,
        config: Config = DEFAULTS,
    ) -> None:
        self._config = config
        self._active_name = _(active_name, config.locale)
        self._passive_name = _(passive_name, config.locale)
        self.active = aspect["active"]
        self.passive = aspect["passive"]
        self.type = _(names.ASPECTS[aspect["aspect"]], config.locale)
        self.aspect = aspect["aspect"]
        self.orb = aspect["orb"]
        self.distance = Angle(aspect["distance"], round_to=config.angle_precision)
        self.difference = Angle(aspect["difference"], round_to=config.angle_precision)
        self.movement = AspectMovement(aspect, config=config)
        self.condition = AspectCondition(aspect, config=config)

    def __str__(self) -> str:
        return _(
            "{active} {passive} {type} within {difference} ({movement}, {condition})",
            self._config.locale,
        ).format(
            active=self._active_name,
            passive=self._passive_name,
            type=self.type,
            difference=self.difference,
            movement=self.movement,
            condition=self.condition,
        )


class AspectCondition:
    def __init__(self, aspect: dict, config: Config = DEFAULTS) -> None:
        self.associate = aspect["condition"] == calc.ASSOCIATE
        self.dissociate = aspect["condition"] == calc.DISSOCIATE
        self.formatted = _(
            names.ASPECT_CONDITIONS[aspect["condition"]],
            config.locale,
            context=(contexts.GENDERS, aspect["aspect"]),
        )

    def __str__(self) -> str:
        return self.formatted


class AspectMovement:
    def __init__(self, aspect: dict, config: Config = DEFAULTS) -> None:
        self.applicative = aspect["movement"] == calc.APPLICATIVE
        self.exact = aspect["movement"] == calc.EXACT
        self.separative = aspect["movement"] == calc.SEPARATIVE
        self.formatted = _(
            names.ASPECT_MOVEMENTS[aspect["movement"]],
            config.locale,
            context=(contexts.GENDERS, aspect["aspect"]),
        )

    def __str__(self) -> str:
        return self.formatted


class Coordinates:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = Angle(latitude, format=convert.FORMAT_LAT)
        self.longitude = Angle(longitude, format=convert.FORMAT_LON)

    def __str__(self) -> str:
        return f"{self.latitude}, {self.longitude}"


class DateTime:
    def __init__(
        self,
        dt: datetime | float,
        armc: dict | float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        offset: float | None = None,
        timezone: str | None = None,
        time_is_dst: bool | None = None,
        config: Config = DEFAULTS,
    ) -> None:
        self._config = config
        self.datetime = date.to_datetime(dt, latitude, longitude, offset, timezone)
        self.timezone = date.timezone_name(self.datetime)
        self.ambiguous = date.ambiguous(self.datetime) and time_is_dst is None
        self.julian = date.to_jd(dt)
        self.deltat = date.deltat(self.julian)
        if armc is not None:
            self.sidereal_time = convert.dec_to_string(
                date.sidereal_time(armc["lon"] if isinstance(armc, dict) else armc),
                format=convert.FORMAT_TIME,
            )

    def __str__(self) -> str:
        formatted = _(
            "{weekday} {month} {day} {year} {time} {timezone}",  # This must match the format in immanuel.po
            self._config.locale,
        ).format(
            weekday=_(
                names.WEEKDAYS[self.datetime.weekday()],
                self._config.locale,
                context=contexts.WEEKDAY,
            ),
            month=_(
                names.MONTHS[self.datetime.month],
                self._config.locale,
                context=contexts.MONTH,
            ),
            day=f"{self.datetime.day:02d}",
            year=self.datetime.year,
            time=self.datetime.strftime("%H:%M:%S"),
            timezone=self.timezone,
        )
        if self.ambiguous:
            formatted += f" ({_('ambiguous', self._config.locale)})"
        return formatted


class Decan:
    def __init__(self, number: int, config: Config = DEFAULTS) -> None:
        self.number = number
        self.name = _(names.DECANS[self.number], config.locale)

    def __str__(self) -> str:
        return self.name


class DignityState:
    def __init__(
        self, object: dict, dignity_state: dict, config: Config = DEFAULTS
    ) -> None:
        self.ruler = dignity_state[dignities.RULER]
        self.exalted = dignity_state[dignities.EXALTED]
        self.triplicity_ruler = dignity_state[dignities.TRIPLICITY_RULER]
        self.term_ruler = dignity_state[dignities.TERM_RULER]
        self.face_ruler = dignity_state[dignities.FACE_RULER]
        self.mutual_reception_ruler = dignity_state[dignities.MUTUAL_RECEPTION_RULER]
        self.mutual_reception_exalted = dignity_state[
            dignities.MUTUAL_RECEPTION_EXALTED
        ]
        self.mutual_reception_triplicity_ruler = dignity_state[
            dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER
        ]
        self.mutual_reception_term_ruler = dignity_state[
            dignities.MUTUAL_RECEPTION_TERM_RULER
        ]
        self.mutual_reception_face_ruler = dignity_state[
            dignities.MUTUAL_RECEPTION_FACE_RULER
        ]
        self.detriment = dignity_state[dignities.DETRIMENT]
        self.fall = dignity_state[dignities.FALL]
        self.peregrine = dignity_state[dignities.PEREGRINE]
        self.formatted = [
            _(
                names.DIGNITIES[dignity],
                config.locale,
                context=(contexts.GENDERS, object["index"]),
            )
            for dignity, active in dignity_state.items()
            if active
        ]

    def __str__(self) -> str:
        return ", ".join(self.formatted)


class EclipseType:
    def __init__(self, eclipse_type: int, config: Config = DEFAULTS) -> None:
        self.total = eclipse_type == chart.TOTAL
        self.annular = eclipse_type == chart.ANNULAR
        self.partial = eclipse_type == chart.PARTIAL
        self.annular_total = eclipse_type == chart.ANNULAR_TOTAL
        self.penumbral = eclipse_type == chart.PENUMBRAL
        self.formatted = _(names.ECLIPSE_TYPES[eclipse_type], config.locale)

    def __str__(self) -> str:
        return self.formatted


class House:
    def __init__(self, house: dict, config: Config = DEFAULTS) -> None:
        self.index = house["index"]
        self.number = house["number"]
        self.name = _(house["name"], config.locale)

    def __str__(self) -> str:
        return self.name


class MoonPhase:
    def __init__(self, moon_phase: int, config: Config = DEFAULTS) -> None:
        self.new_moon = moon_phase == calc.NEW_MOON
        self.waxing_crescent = moon_phase == calc.WAXING_CRESCENT
        self.first_quarter = moon_phase == calc.FIRST_QUARTER
        self.waxing_gibbous = moon_phase == calc.WAXING_GIBBOUS
        self.full_moon = moon_phase == calc.FULL_MOON
        self.disseminating = moon_phase == calc.DISSEMINATING
        self.third_quarter = moon_phase == calc.THIRD_QUARTER
        self.balsamic = moon_phase == calc.BALSAMIC
        self.formatted = _(names.MOON_PHASES[moon_phase], config.locale)

    def __str__(self) -> str:
        return self.formatted


class Object:
    def __init__(
        self,
        object: dict,
        date_time: datetime | None = None,
        house: dict | None = None,
        out_of_bounds: bool | None = None,
        in_sect: bool | None = None,
        dignity_state: dict | None = None,
        config: Config = DEFAULTS,
    ) -> None:
        self._config = config
        self.index = object["index"]
        if object["type"] == chart.HOUSE:
            self.number = object["number"]
        self.name = _(object["name"], config.locale)
        self.type = ObjectType(object["type"], config=config)
        if "eclipse_type" in object:
            self.eclipse_type = EclipseType(object["eclipse_type"], config=config)
        if date_time is not None:
            self.date_time = DateTime(date_time, config=config)
        if "lat" in object:
            self.latitude = Angle(object["lat"], round_to=config.angle_precision)
        self.longitude = Angle(object["lon"], round_to=config.angle_precision)
        self.sign_longitude = Angle(
            position.sign_longitude(object), round_to=config.angle_precision
        )
        self.sign = Sign(position.sign(object), config=config)
        self.decan = Decan(position.decan(object), config=config)
        if house is not None:
            self.house = House(house, config=config)
        if "dist" in object:
            self.distance = object["dist"]
        self.speed = object["speed"]
        if object["type"] not in (chart.HOUSE, chart.ANGLE, chart.FIXED_STAR):
            self.movement = ObjectMovement(object, config=config)
        if "dec" in object:
            self.declination = Angle(object["dec"], round_to=config.angle_precision)
        if object["type"] not in (chart.HOUSE, chart.ANGLE, chart.FIXED_STAR):
            self.out_of_bounds = out_of_bounds
        if "size" in object:
            self.size = object["size"]
        if in_sect is not None:
            self.in_sect = in_sect
        if dignity_state is not None:
            self.dignities = DignityState(
                object, dignity_state=dignity_state, config=config
            )
            self.score = dignity.score(dignity_state, config)
        self._config = config

    def __str__(self) -> str:
        formatted = _("{name} {longitude} in {sign}", self._config.locale).format(
            name=self.name,
            longitude=self.sign_longitude,
            sign=self.sign,
        )
        if hasattr(self, "house"):
            formatted += f", {_(self.house, self._config.locale)}"
        if hasattr(self, "movement") and (
            self._config.output_typical_object_motion or not self.movement.typical
        ):
            formatted += f", {_(self.movement, self._config.locale)}"

        return formatted


class ObjectMovement:
    def __init__(self, object: dict, config: Config = DEFAULTS) -> None:
        self._movement = condition.object_motion(object)
        self.direct = self._movement == calc.DIRECT
        self.stationary = self._movement == calc.STATIONARY
        self.retrograde = self._movement == calc.RETROGRADE
        self.typical = condition.is_object_motion_typical(object)
        self.formatted = _(
            names.OBJECT_MOVEMENTS[self._movement],
            config.locale,
            context=(contexts.GENDERS, object["index"]),
        )

    def __str__(self) -> str:
        return self.formatted


class ObjectType:
    def __init__(self, type: int, config: Config = DEFAULTS) -> None:
        self.index = type
        self.name = _(names.OBJECTS[type], config.locale)

    def __str__(self) -> str:
        return self.name


class Sign:
    def __init__(self, number: int, config: Config = DEFAULTS) -> None:
        self.number = number
        self.name = _(names.SIGNS[self.number], config.locale)
        self.element = _(
            names.ELEMENTS[position.element((self.number - 1) * 30)], config.locale
        )
        self.modality = _(
            names.MODALITIES[position.modality((self.number - 1) * 30)], config.locale
        )

    def __str__(self) -> str:
        return self.name


class Subject:
    def __init__(
        self,
        subject: ChartSubject,
        config: Config = DEFAULTS,
    ) -> None:
        self._config = config
        armc = ephemeris.get_angle(
            index=chart.ARMC,
            jd=subject.julian_date,
            lat=subject.latitude,
            lon=subject.longitude,
            house_system=config.house_system,
        )
        self.date_time = DateTime(
            dt=subject.date_time,
            armc=armc,
            latitude=subject.latitude,
            longitude=subject.longitude,
            offset=subject.timezone_offset,
            timezone=subject.timezone,
            time_is_dst=subject.time_is_dst,
            config=config,
        )
        self.coordinates = Coordinates(
            latitude=subject.latitude,
            longitude=subject.longitude,
        )

    def __str__(self) -> str:
        return _("{date_time} at {lat}, {lon}", self._config.locale).format(
            date_time=self.date_time,
            lat=self.coordinates.latitude,
            lon=self.coordinates.longitude,
        )


class Weightings:
    def __init__(
        self,
        elements: dict,
        modalities: dict,
        quadrants: dict,
        config: Config = DEFAULTS,
    ) -> None:
        self.elements = Elements(elements, config=config)
        self.modalities = Modalities(modalities, config=config)
        self.quadrants = Quadrants(quadrants, config=config)

    def __str__(self) -> str:
        return f"{self.elements}\n{self.modalities}\n{self.quadrants}"


class Elements:
    def __init__(self, elements: dict, config: Config = DEFAULTS) -> None:
        self._config = config
        self.fire = elements[chart.FIRE]
        self.earth = elements[chart.EARTH]
        self.air = elements[chart.AIR]
        self.water = elements[chart.WATER]

    def __str__(self) -> str:
        return f"{_('Fire', self._config.locale)}: {len(self.fire)}, {_('Earth', self._config.locale)}: {len(self.earth)}, {_('Air', self._config.locale)}: {len(self.air)}, {_('Water', self._config.locale)}: {len(self.water)}"


class Modalities:
    def __init__(self, modalities: dict, config: Config = DEFAULTS) -> None:
        self._config = config
        self.cardinal = modalities[chart.CARDINAL]
        self.fixed = modalities[chart.FIXED]
        self.mutable = modalities[chart.MUTABLE]

    def __str__(self) -> str:
        return f"{_('Cardinal', self._config.locale)}: {len(self.cardinal)}, {_('Fixed', self._config.locale)}: {len(self.fixed)}, {_('Mutable', self._config.locale)}: {len(self.mutable)}"


class Quadrants:
    def __init__(self, quadrants: dict, config: Config = DEFAULTS) -> None:
        self._config = config
        self.first = quadrants[1]
        self.second = quadrants[2]
        self.third = quadrants[3]
        self.fourth = quadrants[4]

    def __str__(self) -> str:
        return f"{_('First', self._config.locale)}: {len(self.first)}, {_('Second', self._config.locale)}: {len(self.second)}, {_('Third', self._config.locale)}: {len(self.third)}, {_('Fourth', self._config.locale)}: {len(self.fourth)}"
