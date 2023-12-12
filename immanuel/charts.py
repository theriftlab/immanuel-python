"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class. Each chart type
    is instantiated by passing an object of type Native.

"""

from datetime import datetime

from immanuel.classes import wrap
from immanuel.const import calc, chart, data, names
from immanuel.reports import aspect, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import calculate, convert, date, ephemeris, forecast, midpoint


class Native:
    def __init__(self, date_time: datetime | str, latitude: float, longitude: float, time_is_dst: bool = None):
        self.time_is_dst = time_is_dst
        self.latitude, self.longitude = (convert.to_dec(v) for v in (latitude, longitude))
        self.date_time = date.localize(
                dt=date_time if isinstance(date_time, datetime) else datetime.fromisoformat(date_time),
                lat=self.latitude,
                lon=self.longitude,
                is_dst=time_is_dst,
            )


class Chart:
    """ Base chart class. This is essentially an abstract class for the actual
    chart classes to inherit from. The constructor sets some properties common
    to all chart types. """
    def __init__(self, type: int) -> None:
        """ Set chart type name. """
        self.type = names.CHART_TYPES[type]

        if hasattr(self, '_native'):
            """ Add Julian DOB & ARMC for native. """
            self._native_jd = date.to_jd(self._native.date_time)
            self._native_armc = ephemeris.angle(
                    index=chart.ARMC,
                    jd=self._native_jd,
                    lat=self._native.latitude,
                    lon=self._native.longitude,
                    house_system=settings.house_system,
                )
            self._native_armc_lon = self._native_armc['lon']

        if hasattr(self, '_partner'):
            """ Add Julian DOB & ARMC for partner. """
            self._partner_jd = date.to_jd(self._partner.date_time)
            self._partner_armc = ephemeris.angle(
                    index=chart.ARMC,
                    jd=self._partner_jd,
                    lat=self._partner.latitude,
                    lon=self._partner.longitude,
                    house_system=settings.house_system,
                )
            self._partner_armc_lon = self._partner_armc['lon']

        """ Set chart data specific to each type. """
        self.set_data()

        """ Add formatted data per the settings for this chart type. """
        for index in settings.chart_data[type]:
            match index:
                case data.DATE_TIME:
                    self.date_time = wrap.Date(
                            dt=self._native.date_time,
                            armc=self._native_armc_lon,
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
                            armc=self._partner_armc_lon,
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

                # case data.PROGRESSION_DATE:
                #     self.progression_date = wrap.Date(self._progression_date, self._progression_armc)

                # case data.PROGRESSED_DATE:
                #     self.progressed_date = wrap.Date(self._progressed_jd, self._progressed_armc_lon, self._latitude, self._longitude)

                # case data.PROGRESSION_METHOD:
                #     self.progression_method = names.PROGRESSION_METHODS[settings.mc_progression_method]

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
                                houses=self._houses,
                                is_daytime=self._diurnal,
                                obliquity=self._obliquity,
                            )

                case data.HOUSES:
                    self.houses = {index: wrap.Object(object=house) for index, house in self._houses.items()}

                case data.ASPECTS:
                    self.aspects = {index: {object_index: wrap.Aspect(aspect=object_aspect, objects=self._objects) for object_index, object_aspect in aspect_list.items()} for index, aspect_list in self._aspects.items()}

                case data.WEIGHTINGS:
                    self.weightings = {
                        'elements': wrap.Elements(weighting.elements(self._objects)),
                        'modalities': wrap.Modalities(weighting.modalities(self._objects)),
                        'quadrants': wrap.Quadrants(weighting.quadrants(self._objects, self._houses)),
                    }

    def set_data(self) -> None:
        self._native: Native = None
        self._partner: Native = None
        self._obliquity: float = None
        self._solar_return_year: int = None
        self._solar_return_jd: float = None
        self._solar_return_armc: float = None
        self._progression_date: datetime | str = None
        self._progression_armc: float = None
        self._progressed_jd: float = None
        self._progressed_armc_lon: float = None
        self._diurnal: bool = None
        self._moon_phase: int = None
        self._objects: dict = {}
        self._houses: dict = {}
        self._aspects: dict = {}


class Natal(Chart):
    """ Standard natal chart generates data straight from the passed
    native information. """
    def __init__(self, native: Native) -> None:
        self._native = native
        super().__init__(chart.NATAL)

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
        self._aspects = aspect.all(self._objects)


class SolarReturn(Chart):
    """ Solar return chart for the given year. """
    def __init__(self, native: Native, year: int) -> None:
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
        self._aspects = aspect.all(self._objects)


class Progressed(Chart):
    """ Secondary progression chart uses the MC progression method from
    settings. """
    def __init__(self, native: Native, date_time: datetime | str) -> None:
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
        self._progression_armc = ephemeris.angle(
                index=chart.ARMC,
                jd=progression_jd,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )

        self._progressed_jd, self._progressed_armc_lon = forecast.progression(
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
                armc=self._progressed_armc_lon,
                lat=self._native.latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )

        self._diurnal = calculate.is_daytime(sun, asc)
        self._moon_phase = calculate.moon_phase(sun, moon)
        self._objects = ephemeris.armc_objects(
                object_list=settings.objects,
                jd=self._progressed_jd,
                armc=self._progressed_armc_lon,
                lat=self._native.latitude,
                lon=self._native.longitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )
        self._houses = ephemeris.armc_houses(
                armc=self._progressed_armc_lon,
                lat=self._native.latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )
        self._aspects = aspect.all(self._objects)


# class Synastry(Chart):
#     """ Synastry chart is a special case - there are two sets of objects
#     and houses, with aspects between them. """
#     def __init__(self, dob: str, lat: float, lon: float, partner_dob: str, partner_lat: float = None, partner_lon: float = None, is_dst: bool = None, partner_is_dst: bool = None) -> None:
#         self._dob = dob
#         self._lat = lat
#         self._lon = lon
#         self._partner_dob = partner_dob
#         self._partner_lat = partner_lat if partner_lat is not None else lat
#         self._partner_lon = partner_lon if partner_lon is not None else lon
#         self._is_dst = is_dst
#         self._partner_is_dst = partner_is_dst
#         super().__init__(chart.SYNASTRY)

#     def set_data(self) -> None:
#         self._latitude, self._longitude = (convert.to_dec(v) for v in (self._lat, self._lon))
#         self._date_time = date.localize(datetime.fromisoformat(self._dob), self._latitude, self._longitude, self._is_dst)
#         native_jd = date.to_jd(self._date_time)
#         self._obliquity = ephemeris.obliquity(native_jd)
#         self._native_armc = ephemeris.angle(chart.ARMC, native_jd, self._latitude, self._longitude, settings.house_system)['lon']

#         sun = ephemeris.planet(chart.SUN, native_jd)
#         moon = ephemeris.planet(chart.MOON, native_jd)
#         asc = ephemeris.angle(chart.ASC, native_jd, self._latitude, self._longitude, settings.house_system)

#         self._diurnal = calculate.is_daytime(sun, asc)
#         self._moon_phase = calculate.moon_phase(sun, moon)
#         self._objects = ephemeris.objects(settings.objects, native_jd, self._latitude, self._longitude, settings.house_system, settings.pars_fortuna_formula)
#         self._houses = ephemeris.houses(native_jd, self._latitude, self._longitude, settings.house_system)

#         self._partner_latitude, self._partner_longitude = (convert.to_dec(v) for v in (self._partner_lat, self._partner_lon))
#         self._partner_date_time = date.localize(datetime.fromisoformat(self._partner_dob), self._partner_latitude, self._partner_longitude, self._partner_is_dst)
#         partner_jd = date.to_jd(self._partner_date_time)
#         self._partner_obliquity = ephemeris.obliquity(partner_jd)
#         self._partner_armc = ephemeris.angle(chart.ARMC, partner_jd, self._partner_latitude, self._partner_longitude, settings.house_system)

#         partner_sun = ephemeris.planet(chart.SUN, partner_jd)
#         partner_moon = ephemeris.planet(chart.MOON, partner_jd)
#         partner_asc = ephemeris.angle(chart.ASC, partner_jd, self._partner_latitude, self._partner_longitude, settings.house_system)

#         self._partner_diurnal = calculate.is_daytime(partner_sun, partner_asc)
#         self._partner_moon_phase = calculate.moon_phase(partner_sun, partner_moon)
#         self._partner_objects = ephemeris.objects(settings.objects, partner_jd, self._partner_latitude, self._partner_longitude, settings.house_system, settings.pars_fortuna_formula)
#         self._partner_houses = ephemeris.houses(partner_jd, self._partner_latitude, self._partner_longitude, settings.house_system)

#         self._aspects = aspect.synastry(self._objects, self._partner_objects)
#         self._partner_aspects = aspect.synastry(self._partner_objects, self._objects)


class Composite(Chart):
    """ Generates a midpoint chart based on the two passed sets of data. """
    def __init__(self, native: Native, partner: Native) -> None:
        self._native = native
        self._partner = partner
        super().__init__(chart.COMPOSITE)

    def set_data(self) -> None:
        self._obliquity = midpoint.obliquity(self._native_jd, self._partner_jd)

        objects = ephemeris.objects(
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
                objects1=objects,
                objects2=partner_objects,
                obliquity=self._obliquity,
                pars_fortuna=settings.composite_pars_fortuna,
                pars_fortuna_formula=settings.pars_fortuna_formula,
            )

        houses = ephemeris.houses(
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
        if settings.composite_houses == calc.MIDPOINT:
            self._houses = midpoint.all(
                    objects1=houses,
                    objects2=partner_houses,
                    obliquity=self._obliquity,
                    pars_fortuna=settings.composite_pars_fortuna,
                    pars_fortuna_formula=settings.pars_fortuna_formula,
                )
        else:
            armc_lon = midpoint.composite(
                    object1=self._native_armc,
                    object2=self._partner_armc,
                    obliquity=self._obliquity,
                )['lon']
            self._houses = ephemeris.armc_houses(
                    armc=armc_lon,
                    lat=self._native.latitude,      # TODO: should this be mean latitude?
                    obliquity=self._obliquity,
                    house_system=settings.house_system,
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
