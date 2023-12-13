"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class. Each chart type
    is instantiated by passing an object of type Subject.

"""

from datetime import datetime

from immanuel.classes import wrap
from immanuel.const import chart, data, names
from immanuel.reports import aspect, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import calculate, convert, date, ephemeris, forecast, midpoint


class Subject:
    def __init__(self, date_time: datetime | str, latitude: float, longitude: float, time_is_dst: bool = None):
        self.latitude, self.longitude = (convert.to_dec(v) for v in (latitude, longitude))
        self.time_is_dst = time_is_dst
        self.date_time = date.localize(
                dt=date_time if isinstance(date_time, datetime) else datetime.fromisoformat(date_time),
                lat=self.latitude,
                lon=self.longitude,
                is_dst=time_is_dst,
            )


class BaseChart:
    """ Since straightforward self-typing is not available in Python 3.10
    we cheat by creating an empty base class allowing Chart to essentially
    type-hint itself. """
    pass

class Chart(BaseChart):
    """ Base chart class. This is essentially an abstract class for the actual
    chart classes to inherit from. The constructor sets some properties common
    to all chart types. """
    def __init__(self, type: int, aspects_to: BaseChart = None) -> None:
        self.type = names.CHART_TYPES[type]

        if hasattr(self, '_native'):
            self._native_jd = date.to_jd(self._native.date_time)
            self._native_armc = ephemeris.angle(
                    index=chart.ARMC,
                    jd=self._native_jd,
                    lat=self._native.latitude,
                    lon=self._native.longitude,
                    house_system=settings.house_system,
                )
            self._native_armc_longitude = self._native_armc['lon']

        if hasattr(self, '_partner'):
            self._partner_jd = date.to_jd(self._partner.date_time)
            self._partner_armc = ephemeris.angle(
                    index=chart.ARMC,
                    jd=self._partner_jd,
                    lat=self._partner.latitude,
                    lon=self._partner.longitude,
                    house_system=settings.house_system,
                )
            self._partner_armc_longitude = self._partner_armc['lon']

        self.set_data()

        for index in settings.chart_data[type]:
            match index:
                case data.DATE_TIME:
                    self.date_time = wrap.Date(
                            dt=self._native.date_time,
                            armc=self._native_armc_longitude,
                            is_time_dst=self._native.time_is_dst,
                        )

                case data.COORDINATES:
                    self.coordinates = wrap.Coordinates(
                            latitude=self._native.latitude,
                            longitude=self._native.longitude,
                        )

                case data.PARTNER_DATE_TIME:
                    self.partner_date_time = wrap.Date(
                            dt=self._partner.date_time,
                            armc=self._partner_armc_longitude,
                            is_time_dst=self._partner.time_is_dst,
                        )

                case data.PARTNER_COORDINATES:
                    self.partner_coordinates = wrap.Coordinates(
                            latitude=self._partner.latitude,
                            longitude=self._partner.longitude,
                        )

                case data.SOLAR_RETURN_YEAR:
                    self.solar_return_year = self._solar_return_year

                case data.SOLAR_RETURN_DATE:
                    self.solar_return_date = wrap.Date(
                            dt=self._solar_return_jd,
                            armc=self._solar_return_armc,
                            latitude=self._native.latitude,
                            longitude=self._native.longitude,
                        )

                case data.PROGRESSION_DATE:
                    self.progression_date = wrap.Date(
                            dt=self._progression_date,
                            armc=self._progression_armc_longitude,
                        )

                case data.PROGRESSED_DATE:
                    self.progressed_date = wrap.Date(
                            dt=self._progressed_jd,
                            armc=self._progressed_armc_longitude,
                            latitude=self._native.latitude,
                            longitude=self._native.longitude,
                        )

                case data.PROGRESSION_METHOD:
                    self.progression_method = names.PROGRESSION_METHODS[settings.mc_progression_method]

                case data.HOUSE_SYSTEM:
                    self.house_system = names.HOUSE_SYSTEMS[settings.house_system]

                case data.SHAPE:
                    self.shape = names.CHART_SHAPES[pattern.chart_shape(self._objects)]

                case data.DIURNAL:
                    self.diurnal = self._diurnal

                case data.MOON_PHASE:
                    self.moon_phase = wrap.MoonPhase(self._moon_phase)

                case data.OBJECTS:
                    self.objects = {}
                    for index, object in self._objects.items():
                        if 'jd' in object:
                            object['date'] = date.localize(
                                    dt=date.from_jd(object['jd']),
                                    lat=self._native.latitude,
                                    lon=self._native.longitude,
                                )
                        self.objects[index] = wrap.Object(
                                object=object,
                                objects=self._objects,
                                houses=self._houses if hasattr(self, '_houses') else None,
                                is_daytime=self._diurnal if hasattr(self, '_diurnal') else None,
                                obliquity=self._obliquity if hasattr(self, '_obliquity') else None,
                            )

                case data.HOUSES:
                    self.houses = {index: wrap.Object(object=house) for index, house in self._houses.items()}

                case data.ASPECTS:
                    aspects = aspect.all(self._objects) if aspects_to is None else aspect.synastry(self._objects, aspects_to._objects)
                    self.aspects = {index: {object_index: wrap.Aspect(aspect=object_aspect, objects=self._objects) for object_index, object_aspect in aspect_list.items()} for index, aspect_list in aspects.items()}

                case data.WEIGHTINGS:
                    self.weightings = {
                        'elements': wrap.Elements(weighting.elements(self._objects)),
                        'modalities': wrap.Modalities(weighting.modalities(self._objects)),
                        'quadrants': wrap.Quadrants(weighting.quadrants(self._objects, self._houses)),
                    }

    def set_data(self) -> None:
        self._native: Subject = None
        self._partner: Subject = None
        self._obliquity: float = None
        self._solar_return_year: int = None
        self._solar_return_jd: float = None
        self._solar_return_armc: float = None
        self._progression_date: datetime | str = None
        self._progression_armc_longitude: float = None
        self._progressed_jd: float = None
        self._progressed_armc_longitude: float = None
        self._diurnal: bool = None
        self._moon_phase: int = None
        self._objects: dict = {}
        self._houses: dict = {}


class Natal(Chart):
    """ Standard natal chart generates data straight from the passed
    native information. """
    def __init__(self, native: Subject, aspects_to: Chart = None) -> None:
        self._native = native
        super().__init__(chart.NATAL, aspects_to)

    def set_data(self) -> None:
        self._obliquity = ephemeris.obliquity(self._native_jd)

        sun = ephemeris.planet(chart.SUN, self._native_jd)
        moon = ephemeris.planet(chart.MOON, self._native_jd)
        asc = ephemeris.angle(
                index=chart.ASC,
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.houses(
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )


class SolarReturn(Chart):
    """ Solar return chart for the given year. """
    def __init__(self, native: Subject, year: int, aspects_to: Chart = None) -> None:
        self._native = native
        self._solar_return_year = year
        super().__init__(chart.SOLAR_RETURN)

    def set_data(self) -> None:
        self._solar_return_jd = forecast.solar_return(self._native_jd, self._solar_return_year)
        self._obliquity = ephemeris.obliquity(self._solar_return_jd)
        self._solar_return_armc = ephemeris.angle(
                index=chart.ARMC,
                jd=self._solar_return_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )

        sun = ephemeris.planet(chart.SUN, self._solar_return_jd)
        moon = ephemeris.planet(chart.MOON, self._solar_return_jd)
        asc = ephemeris.angle(
                index=chart.ASC,
                jd=self._solar_return_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._solar_return_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.houses(
                jd=self._solar_return_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )


class Progressed(Chart):
    """ Secondary progression chart uses the MC progression method from
    settings. """
    def __init__(self, native: Subject, date_time: datetime | str, aspects_to: Chart = None) -> None:
        self._native = native
        self._date_time = date_time
        super().__init__(chart.PROGRESSED)

    def set_data(self) -> None:
        self._progression_date = date.localize(
                dt=self._date_time if isinstance(self._date_time, datetime) else datetime.fromisoformat(self._date_time),
                lat=self._native.latitude,
                lon=self._native.longitude,
            )
        progression_jd = date.to_jd(self._progression_date)
        progression_armc = ephemeris.angle(
                index=chart.ARMC,
                jd=progression_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
        self._progression_armc_longitude = progression_armc['lon']

        self._progressed_jd, self._progressed_armc_longitude = forecast.progression(
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
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
                lat=self._native.latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.armc_objects(
                object_list=settings.objects,
                jd=self._progressed_jd,
                armc=self._progressed_armc_longitude,
                lat=self._native.latitude,
                lon=self._native.longitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.armc_houses(
                armc=self._progressed_armc_longitude,
                lat=self._native.latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )


class Composite(Chart):
    """ Generates a midpoint chart based on the two passed sets of data. """
    def __init__(self, native: Subject, partner: Subject, aspects_to: Chart = None) -> None:
        self._native = native
        self._partner = partner
        super().__init__(chart.COMPOSITE)

    def set_data(self) -> None:
        self._obliquity = midpoint.obliquity(self._native_jd, self._partner_jd)

        native_objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        partner_objects = ephemeris.objects(
                object_list=settings.objects,
                jd=self._partner_jd,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._objects = midpoint.all(
                objects1=native_objects,
                objects2=partner_objects,
                obliquity=self._obliquity,
            )

        native_houses = ephemeris.houses(
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
        partner_houses = ephemeris.houses(
                jd=self._partner_jd,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
        self._houses = midpoint.all(
                objects1=native_houses,
                objects2=partner_houses,
                obliquity=self._obliquity,
            )

        native_sun = ephemeris.planet(chart.SUN, self._native_jd)
        native_moon = ephemeris.planet(chart.MOON, self._native_jd)

        partner_sun = ephemeris.planet(chart.SUN, self._partner_jd)
        partner_moon = ephemeris.planet(chart.MOON, self._partner_jd)

        sun = midpoint.composite(native_sun, partner_sun, self._obliquity)
        moon = midpoint.composite(native_moon, partner_moon, self._obliquity)
        asc = self._houses[chart.HOUSE1]

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)

        self._aspects = aspect.all(self._objects)


class Transits(Chart):
    """ A very basic chart containing the main chart objects only. If no
    coordinates are given then house-based points Vertex and Part of Fortune
    are excluded. """
    def __init__(self, latitude: float = 0.0, longitude: float = 0.0, aspects_to: Chart = None) -> None:
        self._native = Subject(datetime.now(), latitude, longitude)
        super().__init__(chart.TRANSITS, aspects_to)

    def set_data(self) -> None:
        exclude = [chart.ASC, chart.DESC, chart.MC, chart.IC]

        if self._native.latitude == 0.0 and self._native.longitude == 0.0:
            exclude += [chart.VERTEX, chart.PARS_FORTUNA]

        object_list = [object for object in settings.objects if object not in exclude]

        self._objects = ephemeris.objects(
                object_list=object_list,
                jd=self._native_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
            )
