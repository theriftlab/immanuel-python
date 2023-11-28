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
from immanuel.tools import calculate, convert, date, ephemeris, position


class Angle:
    def __init__(self, angle: float, format: int = convert.FORMAT_DMS) -> None:
        self.raw = angle
        self.formatted = convert.dec_to_string(angle, format)
        self.direction = None
        self.degrees = None
        self.minutes = None
        self.seconds = None
        self.__dict__.update(dict(zip(('direction', 'degrees', 'minutes', 'seconds'), convert.dec_to_dms(self.raw))))

    def __str__(self) -> str:
        return self.formatted


class Aspect:
    def __init__(self, aspect: dict, objects: dict) -> None:
        self._active_name = objects[aspect['active']]['name']
        self._passive_name = objects[aspect['passive']]['name']
        self.active = aspect['active']
        self.passive = aspect['passive']
        self.type = names.ASPECTS[aspect['aspect']]
        self.aspect = aspect['aspect']
        self.orb = aspect['orb']
        self.distance = Angle(aspect['distance'])
        self.difference = Angle(aspect['difference'])
        self.movement = AspectMovement(aspect['movement'])
        self.condition = AspectCondition(aspect['condition'])

    def __str__(self) -> str:
        return f'{self._active_name} {self._passive_name} {self.type} within {self.difference} ({self.movement}, {self.condition})'


class AspectMovement:
    def __init__(self, movement: int) -> None:
        self.applicative = movement == calc.APPLICATIVE
        self.exact = movement == calc.EXACT
        self.separative = movement == calc.SEPARATIVE
        self.formatted = names.ASPECT_MOVEMENTS[movement]

    def __str__(self) -> str:
        return self.formatted


class AspectCondition:
    def __init__(self, condition: int) -> None:
        self.associate = condition == calc.ASSOCIATE
        self.dissociate = condition == calc.DISSOCIATE
        self.formatted = names.ASPECT_CONDITIONS[condition]

    def __str__(self) -> str:
        return self.formatted


class Coordinates:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = Angle(latitude, convert.FORMAT_LAT)
        self.longitude = Angle(longitude, convert.FORMAT_LON)

    def __str__(self) -> str:
        return f'{self.latitude}, {self.longitude}'


class Date:
    def __init__(self, dt: datetime | float, armc: dict = None, lat: float = None, lon: float = None) -> None:
        self.datetime = dt if isinstance(dt, datetime) else date.from_jd(dt, lat, lon)
        self.timezone = self.datetime.tzname()
        self.julian = date.to_jd(dt) if isinstance(dt, datetime) else dt
        self.deltat = ephemeris.deltat(self.julian)

        if armc is not None:
            self.sidereal_time = convert.dec_to_string(calculate.sidereal_time(armc), convert.FORMAT_TIME)

    def __str__(self) -> str:
        return f'{self.datetime.strftime("%a %b %d %Y %I:%M:%S %p")} {self.timezone}'


class DignityState:
    def __init__(self, dignity_state: dict) -> None:
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
        self.formatted = [names.DIGNITIES[dignity] for dignity, active in dignity_state.items() if active]

    def __str__(self) -> str:
        return ', '.join(self.formatted)


class EclipseType:
    def __init__(self, eclipse_type: int) -> None:
        self.total = eclipse_type == chart.TOTAL
        self.annular = eclipse_type == chart.ANNULAR
        self.partial = eclipse_type == chart.PARTIAL
        self.annular_total = eclipse_type == chart.ANNULAR_TOTAL
        self.penumbral = eclipse_type == chart.PENUMBRAL
        self.formatted = names.ECLIPSE_TYPES[eclipse_type]

    def __str__(self) -> str:
        return self.formatted


class House:
    def __init__(self, house: dict) -> None:
        self.index = house['index']
        self.number = house['number']
        self.name = house['name']

    def __str__(self) -> str:
        return self.name


class ObjectMovement:
    def __init__(self, object: dict) -> None:
        self._movement = calculate.object_movement(object)
        self.direct = self._movement == calc.DIRECT
        self.stationary = self._movement == calc.STATIONARY
        self.retrograde = self._movement == calc.RETROGRADE
        self.formatted = names.OBJECT_MOVEMENTS[self._movement]

    def __str__(self) -> str:
        return self.formatted


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
        self.formatted = names.MOON_PHASES[moon_phase]

    def __str__(self) -> str:
        return self.formatted


class Object:
    def __init__(self, object: dict, objects: dict = None, houses: dict = None, is_daytime: bool = None, obliquity: float = None) -> None:
        self.index = object['index']
        self.name = object['name']
        self.type = ObjectType(object['type'])

        if 'eclipse_type' in object:
            self.eclipse_type = EclipseType(object['eclipse_type'])

        if 'date' in object:
            self.date = Date(object['date'])

        if 'lat' in object:
            self.latitude = Angle(object['lat'])

        self.longitude = Angle(object['lon'])
        self.sign_longitude = Angle(position.sign_longitude(object))
        self.sign = Sign(position.sign(object))

        if houses is not None:
            self.house = House(position.house(object, houses))

        if 'dist' in object:
            self.distance = object['dist']

        self.speed = object['speed']

        if object['type'] not in (chart.HOUSE, chart.FIXED_STAR, chart.ANGLE):
            self.movement = ObjectMovement(object)

        if 'dec' in object:
            self.declination = Angle(object['dec'])
            self.out_of_bounds = calculate.is_out_of_bounds(object=object, obliquity=obliquity)

        if 'size' in object:
            self.size = object['size']

        if object['type'] == chart.PLANET:
            dignity_state = dignity.all(object=object, objects=objects, is_daytime=is_daytime)
            self.dignities = DignityState(dignity_state)
            self.score = dignity.score(dignity_state)

    def __str__(self) -> str:
        str = f'{self.name} {self.sign_longitude} in {self.sign}'

        if (hasattr(self, 'house')):
            str += f', {self.house.name}'

        return str


class ObjectType:
    def __init__(self, type: int) -> None:
        self.index = type
        self.name = names.OBJECTS[type]

    def __str__(self) -> str:
        return self.name


class Sign:
    def __init__(self, number: int) -> None:
        self.number = number
        self.name = names.SIGNS[self.number]

    def __str__(self) -> str:
        return self.name


class Elements:
    def __init__(self, elements: dict) -> None:
        self.fire = elements[chart.FIRE]
        self.earth = elements[chart.EARTH]
        self.air = elements[chart.AIR]
        self.water = elements[chart.WATER]

    def __str__(self) -> str:
        return f'Fire: {len(self.fire)}, Earth: {len(self.earth)}, Air: {len(self.air)}, Water: {len(self.water)}'


class Modalities:
    def __init__(self, modalities: dict) -> None:
        self.cardinal = modalities[chart.CARDINAL]
        self.fixed = modalities[chart.FIXED]
        self.mutable = modalities[chart.MUTABLE]

    def __str__(self) -> str:
        return f'Cardinal: {len(self.cardinal)}, Fixed: {len(self.fixed)}, Mutable: {len(self.mutable)}'


class Quadrants:
    def __init__(self, quadrants: dict) -> None:
        self.first = quadrants[1]
        self.second = quadrants[2]
        self.third = quadrants[3]
        self.fourth = quadrants[4]

    def __str__(self) -> str:
        return f'First: {len(self.first)}, Second: {len(self.second)}, Third: {len(self.third)}, Fourth: {len(self.fourth)}'
