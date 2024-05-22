"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Defines flexible classes to represent data in multiple formats.
    While user-friendly names are defined in the const.names module,
    JSON keys are defined here, either explicitly or as class members.

"""

from datetime import datetime

from immanuel.const import calc, chart, dignities, names
from immanuel.reports import dignity
from immanuel.setup import settings
from immanuel.tools import calculate, convert, date, ephemeris, position
from immanuel.classes.localize import gender, _


class Angle:
    precision = {
        calc.DEGREE: convert.ROUND_DEGREE,
        calc.MINUTE: convert.ROUND_MINUTE,
        calc.SECOND: convert.ROUND_SECOND,
    }

    def __init__(self, angle: float, format: int = convert.FORMAT_DMS, round_to: int = calc.SECOND) -> None:
        self.raw = angle
        self.formatted = convert.dec_to_string(angle, format, Angle.precision[round_to])
        self.direction = None
        self.degrees = None
        self.minutes = None
        self.seconds = None
        self.__dict__.update(dict(zip(('direction', 'degrees', 'minutes', 'seconds'), convert.dec_to_dms(self.raw))))

    def __str__(self) -> str:
        return self.formatted


class Aspect:
    def __init__(self, aspect: dict, active_name: str, passive_name: str) -> None:
        self._active_name = active_name
        self._passive_name = passive_name
        self.active = aspect['active']
        self.passive = aspect['passive']
        self.type = _(names.ASPECTS[aspect['aspect']])
        self.aspect = aspect['aspect']
        self.orb = aspect['orb']
        self.distance = Angle(aspect['distance'], round_to=settings.angle_precision)
        self.difference = Angle(aspect['difference'], round_to=settings.angle_precision)
        self.movement = AspectMovement(aspect)
        self.condition = AspectCondition(aspect)

    def __str__(self) -> str:
        return _('{active} {passive} {type} within {difference} ({movement}, {condition})').format(
                active=self._active_name,
                passive=self._passive_name,
                type=self.type,
                difference = self.difference,
                movement = self.movement,
                condition = self.condition,
            )


class AspectCondition:
    def __init__(self, aspect: dict) -> None:
        self.associate = aspect['condition'] == calc.ASSOCIATE
        self.dissociate = aspect['condition'] == calc.DISSOCIATE
        self.formatted = _(names.ASPECT_CONDITIONS[aspect['condition']], gender(aspect['aspect']))

    def __str__(self) -> str:
        return self.formatted


class AspectMovement:
    def __init__(self, aspect: dict) -> None:
        self.applicative = aspect['movement'] == calc.APPLICATIVE
        self.exact = aspect['movement'] == calc.EXACT
        self.separative = aspect['movement'] == calc.SEPARATIVE
        self.formatted = _(names.ASPECT_MOVEMENTS[aspect['movement']], gender(aspect['aspect']))

    def __str__(self) -> str:
        return self.formatted


class Coordinates:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = Angle(latitude, convert.FORMAT_LAT)
        self.longitude = Angle(longitude, convert.FORMAT_LON)

    def __str__(self) -> str:
        return f'{self.latitude}, {self.longitude}'


class DateTime:
    def __init__(self, dt: datetime | float, armc: dict | float = None, latitude: float = None, longitude: float = None, time_is_dst: bool = None) -> None:
        self.datetime = date.to_datetime(dt, latitude, longitude)
        self.timezone = self.datetime.tzname()
        self.ambiguous = date.ambiguous(self.datetime) and time_is_dst is None
        self.julian = date.to_jd(dt)
        self.deltat = ephemeris.deltat(self.julian)

        if armc is not None:
            self.sidereal_time = convert.dec_to_string(calculate.sidereal_time(armc), convert.FORMAT_TIME)

    def __str__(self) -> str:
        str = f"{self.datetime.strftime('%a %b %d %Y %H:%M:%S')} {self.timezone}"

        if self.ambiguous:
            str += f" ({_('ambiguous')})"

        return str


class Decan:
    def __init__(self, number: int) -> None:
        self.number = number
        self.name = _(names.DECANS[self.number])

    def __str__(self) -> str:
        return self.name


class DignityState:
    def __init__(self, object: dict, dignity_state: dict) -> None:
        self.ruler = dignity_state[dignities.RULER]
        self.exalted = dignity_state[dignities.EXALTED]
        self.triplicity_ruler = dignity_state[dignities.TRIPLICITY_RULER]
        self.term_ruler = dignity_state[dignities.TERM_RULER]
        self.face_ruler = dignity_state[dignities.FACE_RULER]
        self.mutual_reception_ruler = dignity_state[dignities.MUTUAL_RECEPTION_RULER]
        self.mutual_reception_exalted = dignity_state[dignities.MUTUAL_RECEPTION_EXALTED]
        self.mutual_reception_triplicity_ruler = dignity_state[dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER]
        self.mutual_reception_term_ruler = dignity_state[dignities.MUTUAL_RECEPTION_TERM_RULER]
        self.mutual_reception_face_ruler = dignity_state[dignities.MUTUAL_RECEPTION_FACE_RULER]
        self.detriment = dignity_state[dignities.DETRIMENT]
        self.fall = dignity_state[dignities.FALL]
        self.peregrine = dignity_state[dignities.PEREGRINE]
        self.formatted = [_(names.DIGNITIES[dignity], gender(object['index'])) for dignity, active in dignity_state.items() if active]

    def __str__(self) -> str:
        return ', '.join(self.formatted)


class EclipseType:
    def __init__(self, eclipse_type: int) -> None:
        self.total = eclipse_type == chart.TOTAL
        self.annular = eclipse_type == chart.ANNULAR
        self.partial = eclipse_type == chart.PARTIAL
        self.annular_total = eclipse_type == chart.ANNULAR_TOTAL
        self.penumbral = eclipse_type == chart.PENUMBRAL
        self.formatted = _(names.ECLIPSE_TYPES[eclipse_type])

    def __str__(self) -> str:
        return self.formatted


class House:
    def __init__(self, house: dict) -> None:
        self.index = house['index']
        self.number = house['number']
        self.name = house['name']

    def __str__(self) -> str:
        return self.name


class MoonPhase:
    def __init__(self, moon_phase: int) -> None:
        self.new_moon = moon_phase == calc.NEW_MOON
        self.waxing_crescent = moon_phase == calc.WAXING_CRESCENT
        self.first_quarter = moon_phase == calc.FIRST_QUARTER
        self.waxing_gibbous = moon_phase == calc.WAXING_GIBBOUS
        self.full_moon = moon_phase == calc.FULL_MOON
        self.disseminating = moon_phase == calc.DISSEMINATING
        self.third_quarter = moon_phase == calc.THIRD_QUARTER
        self.balsamic = moon_phase == calc.BALSAMIC
        self.formatted = _(names.MOON_PHASES[moon_phase])

    def __str__(self) -> str:
        return self.formatted


class Object:
    def __init__(
        self,
        object: dict,
        date_time: datetime = None,
        house: int = None,
        out_of_bounds: bool = None,
        in_sect: bool = None,
        dignity_state: dict = None,
    ) -> None:
        self.index = object['index']

        if object['type'] == chart.HOUSE:
            self.number = object['number']

        self.name = object['name']
        self.type = ObjectType(object['type'])

        if 'eclipse_type' in object:
            self.eclipse_type = EclipseType(object['eclipse_type'])

        if date_time is not None:
            self.date_time = DateTime(date_time)

        if 'lat' in object:
            self.latitude = Angle(object['lat'], round_to=settings.angle_precision)

        self.longitude = Angle(object['lon'], round_to=settings.angle_precision)
        self.sign_longitude = Angle(position.sign_longitude(object), round_to=settings.angle_precision)
        self.sign = Sign(position.sign(object))
        self.decan = Decan(position.decan(object))

        if house is not None:
            self.house = House(house)

        if 'dist' in object:
            self.distance = object['dist']

        self.speed = object['speed']

        if object['type'] not in (chart.HOUSE, chart.ANGLE, chart.FIXED_STAR):
            self.movement = ObjectMovement(object)

        if 'dec' in object:
            self.declination = Angle(object['dec'], round_to=settings.angle_precision)

        if object['type'] not in (chart.HOUSE, chart.ANGLE, chart.FIXED_STAR):
            self.out_of_bounds = out_of_bounds

        if 'size' in object:
            self.size = object['size']

        if in_sect is not None:
            self.in_sect = in_sect

        if dignity_state is not None:
            self.dignities = DignityState(object=object, dignity_state=dignity_state)
            self.score = dignity.score(dignity_state)

    def __str__(self) -> str:
        formatted = _('{name} {longitude} in {sign}').format(
                name=self.name,
                longitude=self.sign_longitude,
                sign=self.sign,
            )

        if hasattr(self, 'house'):
            formatted += f', {_(self.house)}'

        if hasattr(self, 'movement') and (settings.output_typical_object_motion or not self.movement.typical):
            formatted += f', {_(self.movement)}'

        return formatted


class ObjectMovement:
    def __init__(self, object: dict) -> None:
        self._movement = calculate.object_movement(object)
        self.direct = self._movement == calc.DIRECT
        self.stationary = self._movement == calc.STATIONARY
        self.retrograde = self._movement == calc.RETROGRADE
        self.typical = calculate.is_object_movement_typical(object)
        self.formatted = _(names.OBJECT_MOVEMENTS[self._movement], gender(object['index']))

    def __str__(self) -> str:
        return self.formatted


class ObjectType:
    def __init__(self, type: int) -> None:
        self.index = type
        self.name = _(names.OBJECTS[type])

    def __str__(self) -> str:
        return self.name


class Sign:
    def __init__(self, number: int) -> None:
        self.number = number
        self.name = _(names.SIGNS[self.number])
        self.element = _(names.ELEMENTS[position.element((self.number-1) * 30)])
        self.modality = _(names.MODALITIES[position.modality((self.number-1) * 30)])

    def __str__(self) -> str:
        return self.name


class Subject:
    def __init__(self, subject: 'Subject') -> None:
        armc = ephemeris.angle(
                index=chart.ARMC,
                jd=subject.julian_date,
                lat=subject.latitude,
                lon=subject.longitude,
                house_system=settings.house_system,
            )
        self.date_time = DateTime(
                dt=subject.date_time,
                armc=armc,
                latitude=subject.latitude,
                longitude=subject.longitude,
                time_is_dst=subject.time_is_dst,
            )
        self.coordinates = Coordinates(
                latitude=subject.latitude,
                longitude=subject.longitude,
            )

    def __str__(self) -> str:
        return _('{date_time} at {lat}, {lon}').format(
                date_time=self.date_time,
                lat=self.coordinates.latitude,
                lon=self.coordinates.longitude,
            )


class Weightings:
    def __init__(self, elements: dict, modalities: dict, quadrants: dict) -> None:
        self.elements = Elements(elements)
        self.modalities = Modalities(modalities)
        self.quadrants = Quadrants(quadrants)

    def __str__(self) -> str:
        return f'{self.elements}\n{self.modalities}\n{self.quadrants}'


class Elements:
    def __init__(self, elements: dict) -> None:
        self.fire = elements[chart.FIRE]
        self.earth = elements[chart.EARTH]
        self.air = elements[chart.AIR]
        self.water = elements[chart.WATER]

    def __str__(self) -> str:
        return f"{_('Fire')}: {len(self.fire)}, {_('Earth')}: {len(self.earth)}, {_('Air')}: {len(self.air)}, {_('Water')}: {len(self.water)}"


class Modalities:
    def __init__(self, modalities: dict) -> None:
        self.cardinal = modalities[chart.CARDINAL]
        self.fixed = modalities[chart.FIXED]
        self.mutable = modalities[chart.MUTABLE]

    def __str__(self) -> str:
        return f"{_('Cardinal')}: {len(self.cardinal)}, {_('Fixed')}: {len(self.fixed)}, {_('Mutable')}: {len(self.mutable)}"


class Quadrants:
    def __init__(self, quadrants: dict) -> None:
        self.first = quadrants[1]
        self.second = quadrants[2]
        self.third = quadrants[3]
        self.fourth = quadrants[4]

    def __str__(self) -> str:
        return f"{_('First')}: {len(self.first)}, {_('Second')}: {len(self.second)}, {_('Third')}: {len(self.third)}, {_('Fourth')}: {len(self.fourth)}"
