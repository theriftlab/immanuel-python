"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class. Each chart type
    is instantiated by passing an instance of Subject.

    Instead of a dedicated synastry chart, the optional aspects_to parameter
    in each chart type's constructor takes another Chart instance and forms its
    aspects to the planets in that chart rather than its own.

"""

from datetime import datetime
from typing import Any

from immanuel.classes import wrap
from immanuel.const import chart, names
from immanuel.reports import aspect, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import calculate, convert, date, ephemeris, forecast, midpoint


class Subject:
    """ Simple class to model a chart subject - essentially just
    a time and place. """
    def __init__(self, date_time: datetime | str, latitude: Any, longitude: Any, time_is_dst: bool = None) -> None:
        self._lat, self._lon = (convert.to_dec(v) for v in (latitude, longitude))
        self._dt = date.localize(
                dt=date_time if isinstance(date_time, datetime) else datetime.fromisoformat(date_time),
                lat=self._lat,
                lon=self._lon,
                is_dst=time_is_dst,
            )
        self._jd = date.to_jd(self._dt)
        armc = ephemeris.angle(
                index=chart.ARMC,
                jd=self._jd,
                lat=self._lat,
                lon=self._lon,
                house_system=settings.house_system,
            )
        self.date_time = wrap.DateTime(
                dt=self._dt,
                armc=armc,
                latitude=self._lat,
                longitude=self._lon,
                is_time_dst=time_is_dst,
            )
        self.coordinates = wrap.Coordinates(
                latitude=self._lat,
                longitude=self._lon,
            )


class BaseChart:
    """ Since straightforward self-typing is not available in Python 3.10
    we cheat by creating a base class allowing Chart's constructor to
    type-hint itself. """
    pass


class Chart(BaseChart):
    """ Base chart class. This acts as an abstract class for the actual chart
    classes to inherit from. """
    def __init__(self, type: int, aspects_to: BaseChart = None) -> None:
        self.type: str = names.CHART_TYPES[type]
        self._type = type
        self._aspects_to = aspects_to
        self.generate()
        self.wrap()

    def generate(self) -> None:
        """ Generating the raw data is each descendant class's responsibility.
        Placeholders for properties common to all charts are set here. """
        self._native: Subject = None
        self._obliquity: float = None
        self._diurnal: bool = None
        self._moon_phase: int = None
        self._objects: dict = {}
        self._houses: dict = {}

    def wrap(self) -> None:
        """ Loop through the required data and wrap each one with a custom
        function. """
        for index in settings.chart_data[self._type]:
            method = f'set_wrapped_{index}'
            if hasattr(self, method):
                getattr(self, method)()

    # Base class provides wrappers for properties common to all classes.
    def set_wrapped_date_time(self) -> None:
        self.date_time = self._native.date_time

    def set_wrapped_coordinates(self) -> None:
        self.coordinates = self._native.coordinates

    def set_wrapped_house_system(self) -> None:
        self.house_system = names.HOUSE_SYSTEMS[settings.house_system]

    def set_wrapped_shape(self) -> None:
        self.shape = names.CHART_SHAPES[pattern.chart_shape(self._objects)]

    def set_wrapped_diurnal(self) -> None:
        self.diurnal = self._diurnal

    def set_wrapped_moon_phase(self) -> None:
        self.moon_phase = wrap.MoonPhase(self._moon_phase)

    def set_wrapped_objects(self) -> None:
        self.objects = {}
        for index, object in self._objects.items():
            if 'jd' in object:
                object['date'] = date.localize(
                        dt=date.from_jd(object['jd']),
                        lat=self._native._lat,
                        lon=self._native._lon,
                    )
            self.objects[index] = wrap.Object(
                    object=object,
                    objects=self._objects,
                    houses=self._houses,
                    is_daytime=self._diurnal,
                    obliquity=self._obliquity,
                )

    def set_wrapped_houses(self) -> None:
        self.houses = {index: wrap.Object(object=house) for index, house in self._houses.items()}

    def set_wrapped_aspects(self) -> None:
        aspects = aspect.all(self._objects) if self._aspects_to is None else aspect.synastry(self._objects, self._aspects_to._objects)
        self.aspects = {index: {object_index: wrap.Aspect(aspect=object_aspect, objects=self._objects) for object_index, object_aspect in aspect_list.items()} for index, aspect_list in aspects.items()}

    def set_wrapped_weightings(self) -> None:
        self.weightings = {
            'elements': wrap.Elements(weighting.elements(self._objects)),
            'modalities': wrap.Modalities(weighting.modalities(self._objects)),
            'quadrants': wrap.Quadrants(weighting.quadrants(self._objects, self._houses)),
        }


class Natal(Chart):
    """ Standard natal chart generates data straight from the passed
    native information. """
    def __init__(self, native: Subject, aspects_to: Chart = None) -> None:
        self._native = native
        super().__init__(chart.NATAL, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.obliquity(self._native._jd)

        sun = ephemeris.planet(chart.SUN, self._native._jd)
        moon = ephemeris.planet(chart.MOON, self._native._jd)
        asc = ephemeris.angle(
                index=chart.ASC,
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.houses(
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )


class SolarReturn(Chart):
    """ Solar return chart for the given year. """
    def __init__(self, native: Subject, year: int, aspects_to: Chart = None) -> None:
        self._native = native
        self._solar_return_year = year
        super().__init__(chart.SOLAR_RETURN, aspects_to)

    def generate(self) -> None:
        self._solar_return_jd = forecast.solar_return(self._native._jd, self._solar_return_year)
        self._obliquity = ephemeris.obliquity(self._solar_return_jd)
        self._solar_return_armc = ephemeris.angle(
                index=chart.ARMC,
                jd=self._solar_return_jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )

        sun = ephemeris.planet(chart.SUN, self._solar_return_jd)
        moon = ephemeris.planet(chart.MOON, self._solar_return_jd)
        asc = ephemeris.angle(
                index=chart.ASC,
                jd=self._solar_return_jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._solar_return_jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.houses(
                jd=self._solar_return_jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )

    def set_wrapped_solar_return_year(self) -> None:
        self.solar_return_year = self._solar_return_year

    def set_wrapped_solar_return_date_time(self) -> None:
        self.solar_return_date_time = wrap.DateTime(
                dt=self._solar_return_jd,
                armc=self._solar_return_armc,
                latitude=self._native._lat,
                longitude=self._native._lon,
            )


class Progressed(Chart):
    """ Secondary progression chart uses the MC progression method from
    settings. """
    def __init__(self, native: Subject, date_time: datetime | str, aspects_to: Chart = None) -> None:
        self._native = native
        self._date_time = date_time
        super().__init__(chart.PROGRESSED, aspects_to)

    def generate(self) -> None:
        self._progression_date_time = date.localize(
                dt=self._date_time if isinstance(self._date_time, datetime) else datetime.fromisoformat(self._date_time),
                lat=self._native._lat,
                lon=self._native._lon,
            )
        progression_jd = date.to_jd(self._progression_date_time)
        progression_armc = ephemeris.angle(
                index=chart.ARMC,
                jd=progression_jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )
        self._progression_armc_longitude = progression_armc['lon']

        self._progressed_jd, self._progressed_armc_longitude = forecast.progression(
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                pjd=progression_jd,
                house_system=settings.house_system,
                method=settings.mc_progression_method,
            )
        self._obliquity = ephemeris.obliquity(self._progressed_jd)

        sun = ephemeris.planet(chart.SUN, self._progressed_jd)
        moon = ephemeris.planet(chart.MOON, self._progressed_jd)
        asc = ephemeris.armc_angle(
            index=chart.ASC,
                armc=self._progressed_armc_longitude,
                lat=self._native._lat,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.armc_objects(
                object_list=settings.objects,
                jd=self._progressed_jd,
                armc=self._progressed_armc_longitude,
                lat=self._native._lat,
                lon=self._native._lon,
                obliquity=self._obliquity,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.armc_houses(
                armc=self._progressed_armc_longitude,
                lat=self._native._lat,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )

    def set_wrapped_progression_date_time(self) -> None:
        self.progression_date_time = wrap.DateTime(
                dt=self._progression_date_time,
                armc=self._progression_armc_longitude,
            )

    def set_wrapped_progressed_date_time(self) -> None:
        self.progressed_date_time = wrap.DateTime(
                dt=self._progressed_jd,
                armc=self._progressed_armc_longitude,
                latitude=self._native._lat,
                longitude=self._native._lon,
            )

    def set_wrapped_progression_method(self) -> None:
        self.progression_method = names.PROGRESSION_METHODS[settings.mc_progression_method]


class Composite(Chart):
    """ Generates a midpoint chart based on the two passed sets of data. """
    def __init__(self, native: Subject, partner: Subject, aspects_to: Chart = None) -> None:
        self._native = native
        self._partner = partner
        super().__init__(chart.COMPOSITE, aspects_to)

    def generate(self) -> None:
        self._obliquity = midpoint.obliquity(self._native._jd, self._partner._jd)

        native_objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        partner_objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._partner._jd,
                lat=self._partner._lat,
                lon=self._partner._lon,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._objects = midpoint.all(
                objects1=native_objects,
                objects2=partner_objects,
                obliquity=self._obliquity,
            )

        native_houses = ephemeris.houses(
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )
        partner_houses = ephemeris.houses(
                jd=self._partner._jd,
                lat=self._partner._lat,
                lon=self._partner._lon,
                house_system=settings.house_system,
            )
        self._houses = midpoint.all(
                objects1=native_houses,
                objects2=partner_houses,
                obliquity=self._obliquity,
            )

        native_sun = ephemeris.planet(chart.SUN, self._native._jd)
        native_moon = ephemeris.planet(chart.MOON, self._native._jd)

        partner_sun = ephemeris.planet(chart.SUN, self._partner._jd)
        partner_moon = ephemeris.planet(chart.MOON, self._partner._jd)

        sun = midpoint.composite(native_sun, partner_sun, self._obliquity)
        moon = midpoint.composite(native_moon, partner_moon, self._obliquity)
        asc = self._houses[chart.HOUSE1]

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)

    def set_wrapped_partner_date_time(self):
        self.partner_date_time = self._partner.date_time

    def set_wrapped_partner_coordinates(self):
        self.partner_coordinates = wrap.Coordinates(
                latitude=self._partner._lat,
                longitude=self._partner._lon,
            )


class Transits(Chart):
    """ Chart of the moment for the given coordinates. Structurally identical
    to the natal chart. """
    def __init__(self, latitude: Any, longitude: Any, aspects_to: Chart = None) -> None:
        self._native = Subject(datetime.now(), latitude, longitude)
        super().__init__(chart.TRANSITS, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.obliquity(self._native._jd)

        sun = ephemeris.planet(chart.SUN, self._native._jd)
        moon = ephemeris.planet(chart.MOON, self._native._jd)
        asc = ephemeris.angle(
                index=chart.ASC,
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.houses(
                jd=self._native._jd,
                lat=self._native._lat,
                lon=self._native._lon,
                house_system=settings.house_system,
            )
