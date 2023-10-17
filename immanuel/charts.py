"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class.

"""

from datetime import datetime

from immanuel.classes import wrap
from immanuel.const import calc, chart, data, names
from immanuel.reports import aspect, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import calculate, date, ephemeris, forecast, midpoint


class Chart:
    """ Base chart class. This is essentially an abstract class for the actual
     chart classes to inherit from. """
    def __init__(self, type: int) -> None:
        self.type = names.CHART_TYPES[type]
        self.set_data()

        for index in settings.chart_data[type]:
            match index:
                case data.NATAL_DATE:
                    self.natal_date = wrap.Date(self._natal_date, self._natal_armc_lon)
                case data.NATAL_COORDS:
                    self.coords = wrap.Coords(self._lat, self._lon)
                case data.PARTNER_DATE:
                    self.partner_date = wrap.Date(self._partner_date, self._partner_armc_lon)
                case data.PARTNER_COORDS:
                    self.partner_coords = wrap.Coords(self._partner_lat, self._partner_lon)
                case data.SOLAR_RETURN_YEAR:
                    self.solar_return_year = self._solar_return_year
                case data.SOLAR_RETURN_DATE:
                    self.solar_return_date = wrap.Date(self._solar_return_date, self._solar_return_armc_lon)
                case data.PROGRESSION_DATE:
                    self.progression_date = wrap.Date(self._progression_date, self._progression_armc_lon)
                case data.PROGRESSED_DATE:
                    self.progressed_date = wrap.Date(self._progressed_date, self._progressed_armc_lon)
                case data.HOUSE_SYSTEM:
                    self.house_system = names.HOUSE_SYSTEMS[settings.house_system]
                case data.SHAPE:
                    self.shape = names.CHART_SHAPES[pattern.chart_shape(self._objects)]
                case data.PARTNER_SHAPE:
                    self.partner_shape = names.CHART_SHAPES[pattern.chart_shape(self._partner_objects)]
                case data.DIURNAL:
                    self.diurnal = self._diurnal
                case data.PARTNER_DIURNAL:
                    self.partner_diurnal = self._partner_diurnal
                case data.MOON_PHASE:
                    self.moon_phase = self._moon_phase
                case data.PARTNER_MOON_PHASE:
                    self.partner_moon_phase = self._partner_moon_phase
                case data.OBJECTS:
                    self.objects = {}
                    for index, object in self._objects.items():
                        if 'jd' in object:
                            object['date'] = date.localize(date.from_jd(object['jd']), self._lat, self._lon)
                        self.objects[index] = wrap.Object(object, self._objects, self._houses, self._diurnal, self._obliquity)
                case data.PARTNER_OBJECTS:
                    self.partner_objects = {}
                    for index, object in self._partner_objects.items():
                        if 'jd' in object:
                            object['date'] = date.localize(date.from_jd(object['jd']), self._partner_lat, self._partner_lon)
                        self.partner_objects['index'] = wrap.Object(object, self._partner_objects, self._partner_houses, self._partner_diurnal, self._partner_obliquity)
                case data.HOUSES:
                    self.houses = {index: wrap.Object(house) for index, house in self._houses.items()}
                case data.PARTNER_HOUSES:
                    self.partner_houses = {index: wrap.Object(house) for index, house in self._partner_houses.items()}
                case data.ASPECTS:
                    self.aspects = {index: {object_index: wrap.Aspect(object_aspect, self._objects) for object_index, object_aspect in aspect_list.items()} for index, aspect_list in self._aspects.items()}
                case data.WEIGHTINGS:
                    self.weightings = {
                        'elements': wrap.Elements(weighting.elements(self._objects)),
                        'modalities': wrap.Modalities(weighting.modalities(self._objects)),
                        'quadrants': wrap.Quadrants(weighting.quadrants(self._objects, self._houses)),
                    }
                case data.PARTNER_WEIGHTINGS:
                    self.partner_weightings = {
                        'elements': wrap.Elements(weighting.elements(self._partner_objects)),
                        'modalities': wrap.Modalities(weighting.modalities(self._partner_objects)),
                        'quadrants': wrap.Quadrants(weighting.quadrants(self._partner_objects, self._partner_houses)),
                    }

    def set_data(self) -> None:
        self._obliquity = None
        self._partner_obliquity = None
        self._natal_date = None
        self._partner_date = None
        self._natal_armc_lon = None
        self._partner_armc_lon = None
        self._solar_return_year = None
        self._solar_return_date = None
        self._solar_return_armc_lon = None
        self._progression_date = None
        self._progression_armc_lon = None
        self._progressed_date = None
        self._progressed_armc_lon = None
        self._lat = None
        self._partner_lat = None
        self._lon = None
        self._partner_lon = None
        self._diurnal = None
        self._partner_diurnal = None
        self._moon_phase = None
        self._partner_moon_phase = None
        self._objects = {}
        self._partner_objects = {}
        self._houses = {}
        self._partner_houses = {}
        self._aspects = {}


class Natal(Chart):
    """ Standard natal chart generates data straight from the passed date and
    coordinates. """
    def __init__(self, dob: str, lat: float, lon: float) -> None:
        self._dob = dob
        self._lat = lat
        self._lon = lon
        super().__init__(chart.NATAL)

    def set_data(self) -> None:
        self._natal_date = date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)
        natal_jd = date.to_jd(self._natal_date)
        self._obliquity = ephemeris.obliquity(natal_jd)
        self._natal_armc_lon = ephemeris.angle(chart.ARMC, natal_jd, self._lat, self._lon, settings.house_system)['lon']
        sun = ephemeris.planet(chart.SUN, natal_jd)
        moon = ephemeris.planet(chart.MOON, natal_jd)
        asc = ephemeris.angle(chart.ASC, natal_jd, self._lat, self._lon, settings.house_system)
        self._diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self._moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
        self._objects = ephemeris.objects(settings.objects, natal_jd, self._lat, self._lon, settings.house_system)
        self._houses = ephemeris.houses(natal_jd, self._lat, self._lon, settings.house_system)
        self._aspects = aspect.all(self._objects)


class SolarReturn(Chart):
    """ Solar return chart for the given year. """
    def __init__(self, dob: str, lat: float, lon: float, year: int) -> None:
        self._dob = dob
        self._lat = lat
        self._lon = lon
        self._solar_return_year = year
        super().__init__(chart.SOLAR_RETURN)

    def set_data(self) -> None:
        self._natal_date = date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)
        natal_jd = date.to_jd(self._natal_date)
        solar_return_jd = forecast.solar_return(natal_jd, self._solar_return_year)
        self._obliquity = ephemeris.obliquity(solar_return_jd)
        self._solar_return_date = date.from_jd(solar_return_jd)
        self._natal_armc_lon = ephemeris.angle(chart.ARMC, natal_jd, self._lat, self._lon, settings.house_system)['lon']
        self._solar_return_armc_lon = ephemeris.angle(chart.ARMC, solar_return_jd, self._lat, self._lon, settings.house_system)['lon']
        sun = ephemeris.planet(chart.SUN, solar_return_jd)
        moon = ephemeris.planet(chart.MOON, solar_return_jd)
        asc = ephemeris.angle(chart.ASC, solar_return_jd, self._lat, self._lon, settings.house_system)
        self._diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self._moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
        self._objects = ephemeris.objects(settings.objects, solar_return_jd, self._lat, self._lon, settings.house_system)
        self._houses = ephemeris.houses(solar_return_jd, self._lat, self._lon, settings.house_system)
        self._aspects = aspect.all(self._objects)


class Progressed(Chart):
    """ Secondary progression chart uses the MC progression method from
    settings. """
    def __init__(self, dob: str, lat: float, lon: float, pdt: str) -> None:
        self._dob = dob
        self._lat = lat
        self._lon = lon
        self._pdt = pdt
        super().__init__(chart.PROGRESSED)

    def set_data(self) -> None:
        self._natal_date = date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)
        natal_jd = date.to_jd(self._natal_date)
        self._natal_armc_lon = ephemeris.angle(chart.ARMC, natal_jd, self._lat, self._lon, settings.house_system)['lon']

        self._progression_date = date.localize(datetime.fromisoformat(self._pdt), self._lat, self._lon)
        progression_jd = date.to_jd(self._progression_date)
        self._progression_armc_lon = ephemeris.angle(chart.ARMC, progression_jd, self._lat, self._lon, settings.house_system)['lon']

        progressed_jd, self._progressed_armc_lon = forecast.progression(natal_jd, self._lat, self._lon, progression_jd, settings.house_system, settings.mc_progression)
        self._progressed_date = date.from_jd(progressed_jd)
        self._obliquity = ephemeris.obliquity(progressed_jd)

        sun = ephemeris.planet(chart.SUN, progressed_jd)
        moon = ephemeris.planet(chart.MOON, progressed_jd)
        asc = ephemeris.angle(chart.ASC, progressed_jd, self._lat, self._lon, settings.house_system)

        self._diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self._moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
        self._objects = ephemeris.objects(settings.objects, progressed_jd, self._lat, self._lon, settings.house_system)
        self._houses = ephemeris.houses(progressed_jd, self._lat, self._lon, settings.house_system)
        self._aspects = aspect.all(self._objects)


class Synastry(Chart):
    """ Synastry chart is a special case - there are two sets of objects
    and houses, with aspects between them. """
    def __init__(self, dob: str, lat: float, lon: float, partner_dob: str, partner_lat: float, partner_lon: float) -> None:
        self._dob = dob
        self._lat = lat
        self._lon = lon
        self._partner_dob = partner_dob
        self._partner_lat = partner_lat
        self._partner_lon = partner_lon
        super().__init__(chart.SYNASTRY)

    def set_data(self) -> None:
        self._natal_date = date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)
        natal_jd = date.to_jd(self._natal_date)
        self._obliquity = ephemeris.obliquity(natal_jd)
        self._natal_armc_lon = ephemeris.angle(chart.ARMC, natal_jd, self._lat, self._lon, settings.house_system)['lon']

        sun = ephemeris.planet(chart.SUN, natal_jd)
        moon = ephemeris.planet(chart.MOON, natal_jd)
        asc = ephemeris.angle(chart.ASC, natal_jd, self._lat, self._lon, settings.house_system)

        self._diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self._moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
        self._objects = ephemeris.objects(settings.objects, natal_jd, self._lat, self._lon, settings.house_system)
        self._houses = ephemeris.houses(natal_jd, self._lat, self._lon, settings.house_system)

        self._partner_date = date.localize(datetime.fromisoformat(self._partner_dob), self._partner_lat, self._partner_lon)
        partner_jd = date.to_jd(self._partner_date)
        self._partner_obliquity = ephemeris.obliquity(partner_jd)
        self._partner_armc_lon = ephemeris.angle(chart.ARMC, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)['lon']

        partner_sun = ephemeris.planet(chart.SUN, partner_jd)
        partner_moon = ephemeris.planet(chart.MOON, partner_jd)
        partner_asc = ephemeris.angle(chart.ASC, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)

        self._partner_diurnal = calculate.is_daytime(partner_sun['lon'], partner_asc['lon'])
        self._partner_moon_phase = names.MOON_PHASES[calculate.moon_phase(partner_sun['lon'], partner_moon['lon'])]
        self._partner_objects = ephemeris.objects(settings.objects, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)
        self._partner_houses = ephemeris.houses(partner_jd, self._partner_lat, self._partner_lon, settings.house_system)

        self._aspects = aspect.synastry(self._objects, self._partner_objects)


class Composite(Chart):
    """ Generates a midpoint chart based on the two passed sets of data. """
    def __init__(self, dob: str, lat: float, lon: float, partner_dob: str, partner_lat: float, partner_lon: float) -> None:
        self._dob = dob
        self._lat = lat
        self._lon = lon
        self._partner_dob = partner_dob
        self._partner_lat = partner_lat
        self._partner_lon = partner_lon
        super().__init__(chart.COMPOSITE)

    def set_data(self) -> None:
        self._natal_date = date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)
        natal_jd = date.to_jd(self._natal_date)
        natal_armc = ephemeris.angle(chart.ARMC, natal_jd, self._lat, self._lon, settings.house_system)
        self._natal_armc_lon = natal_armc['lon']

        natal_sun = ephemeris.planet(chart.SUN, natal_jd)
        natal_moon = ephemeris.planet(chart.MOON, natal_jd)
        natal_asc = ephemeris.angle(chart.ASC, natal_jd, self._lat, self._lon, settings.house_system)

        self._partner_date = date.localize(datetime.fromisoformat(self._partner_dob), self._partner_lat, self._partner_lon)
        partner_jd = date.to_jd(self._partner_date)
        partner_armc = ephemeris.angle(chart.ARMC, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)
        self._partner_armc_lon = partner_armc['lon']

        partner_sun = ephemeris.planet(chart.SUN, partner_jd)
        partner_moon = ephemeris.planet(chart.MOON, partner_jd)
        partner_asc = ephemeris.angle(chart.ASC, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)

        objects = ephemeris.objects(settings.objects, natal_jd, self._lat, self._lon, settings.house_system)
        partner_objects = ephemeris.objects(settings.objects, partner_jd, self._partner_lat, self._partner_lon, settings.house_system)

        houses = ephemeris.houses(natal_jd, self._lat, self._lon, settings.house_system)
        partner_houses = ephemeris.houses(partner_jd, self._partner_lat, self._partner_lon, settings.house_system)

        self._obliquity = midpoint.obliquity(natal_jd, partner_jd)

        if settings.composite_houses == calc.MIDPOINT:
            self._houses = midpoint.all(houses, partner_houses, self._obliquity, settings.composite_pars_fortuna, settings.pars_fortuna)
        else:
            armc_lon = midpoint.composite(natal_armc, partner_armc, self._obliquity)['lon']
            self._houses = ephemeris.armc_houses(armc_lon, self._lat, self._obliquity, settings.house_system)

        self._objects = midpoint.all(objects, partner_objects, settings.composite_pars_fortuna, settings.pars_fortuna)
        self._aspects = aspect.all(self._objects)

        sun = midpoint.composite(natal_sun, partner_sun, self._obliquity)
        moon = midpoint.composite(natal_moon, partner_moon, self._obliquity)
        asc = midpoint.composite(natal_asc, partner_asc, self._obliquity)

        self._diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self._moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
