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
from immanuel.tools import calculate, convert, date, eph, position


class Angle:
    def __init__(self, angle: float) -> None:
        self.raw = angle
        self.formatted = convert.dec_to_string(angle)
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
        self.movement = names.ASPECT_MOVEMENTS[aspect['movement']]
        self.condition = names.ASPECT_CONDITIONS[aspect['condition']]

    def __str__(self) -> str:
        return f'{self._active_name} {self._passive_name} {self.type} within {self.difference} ({self.movement}, {self.condition})'


class Coords:
    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon
        self.lat_formatted = convert.dec_to_string(self.lat, convert.FORMAT_LAT)
        self.lon_formatted = convert.dec_to_string(self.lon, convert.FORMAT_LON)

    def __str__(self) -> str:
        return f'{self.lat_formatted}, {self.lon_formatted}'


class Date:
    def __init__(self, dt: datetime, armc_lon: float = None) -> None:
        self.datetime = dt
        self.timezone = dt.tzname()
        self.julian = date.to_jd(dt)
        self.deltat = eph.deltat(self.julian)

        if armc_lon is not None:
            self.sidereal_time = convert.dec_to_string(calculate.sidereal_time(armc_lon), convert.FORMAT_TIME)

    def __str__(self) -> str:
        return f'{self.datetime.strftime("%a %b %d %Y %I:%M:%S %p")} {self.timezone}'


class DignityState:
    def __init__(self, dignity_state: dict) -> None:
        self.ruler = dignity_state[dignities.RULER] if dignities.RULER in dignity_state else None
        self.exalted = dignity_state[dignities.EXALTED] if dignities.EXALTED in dignity_state else None
        self.detriment = dignity_state[dignities.DETRIMENT] if dignities.DETRIMENT in dignity_state else None
        self.fall = dignity_state[dignities.FALL] if dignities.FALL in dignity_state else None
        self.mutual_reception_rulership = dignity_state[dignities.MUTUAL_RECEPTION_RULERSHIP] if dignities.MUTUAL_RECEPTION_RULERSHIP in dignity_state else None
        self.mutual_reception_exaltation = dignity_state[dignities.MUTUAL_RECEPTION_EXALTATION] if dignities.MUTUAL_RECEPTION_EXALTATION in dignity_state else None
        self.mutual_reception_house = dignity_state[dignities.MUTUAL_RECEPTION_HOUSE] if dignities.MUTUAL_RECEPTION_HOUSE in dignity_state else None
        self.triplicity_ruler_day = dignity_state[dignities.TRIPLICITY_RULER_DAY] if dignities.TRIPLICITY_RULER_DAY in dignity_state else None
        self.triplicity_ruler_night = dignity_state[dignities.TRIPLICITY_RULER_NIGHT] if dignities.TRIPLICITY_RULER_NIGHT in dignity_state else None
        self.triplicity_ruler_participatory = dignity_state[dignities.TRIPLICITY_RULER_PARTICIPATORY] if dignities.TRIPLICITY_RULER_PARTICIPATORY in dignity_state else None
        self.term_ruler  = dignity_state[dignities.TERM_RULER ] if dignities.TERM_RULER  in dignity_state else None
        self.face_ruler  = dignity_state[dignities.FACE_RULER ] if dignities.FACE_RULER  in dignity_state else None
        self.peregrine  = dignity_state[dignities.PEREGRINE ] if dignities.PEREGRINE  in dignity_state else None
        self.formatted = [names.DIGNITIES[dignity] for dignity, active in dignity_state.items() if active]

    def __str__(self) -> str:
        return ', '.join(self.formatted)


class House:
    def __init__(self, house: dict) -> None:
        self.number = house['number']
        self.name = house['name']

    def __str__(self) -> str:
        return self.name


class Movement:
    def __init__(self, object: dict) -> None:
        self._movement = calculate.object_movement(object)
        self.direct = self._movement == calc.DIRECT
        self.stationary = self._movement == calc.STATIONARY
        self.retrograde = self._movement == calc.RETROGRADE
        self.formatted = names.OBJECT_MOVEMENTS[self._movement]

    def __str__(self) -> str:
        return self.formatted


class Object:
    def __init__(self, object: dict, objects: dict = None, houses: dict = None, is_daytime: bool = None, obliquity: float = None) -> None:
        self.index = object['index']
        self.name = object['name']
        self.type = ObjectType(object['type'])

        if 'date' in object:
            self.date = Date(object['date'])

        if 'lat' in object:
            self.latitude = Angle(object['lat'])

        self.longitude = Angle(object['lon'])
        signlon = position.signlon(object['lon'])
        self.sign_longitude = Angle(signlon[position.LON])
        self.sign = Sign(signlon[position.SIGN])

        if houses is not None:
            self.house = House(position.house(object['lon'], houses))

        if 'dist' in object:
            self.distance = object['dist']

        self.speed = object['speed']

        if object['type'] not in (chart.HOUSE, chart.FIXED_STAR, chart.ANGLE):
            self.movement = Movement(object)

        if 'dec' in object:
            self.declination = Angle(object['dec'])
            self.out_of_bounds = calculate.is_out_of_bounds(object=object, obliquity=obliquity)

        if 'size' in object:
            self.size = object['size']

        if object['type'] == chart.PLANET:
            dignities = dignity.all(object, objects=objects, houses=houses, is_daytime=is_daytime)
            self.dignities = DignityState(dignities)
            self.score = dignity.score(object, dignities=dignities)

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
