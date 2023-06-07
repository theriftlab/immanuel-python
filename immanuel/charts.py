"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class.

"""

from datetime import datetime

from immanuel.const import chart, names
from immanuel.data import aspect, pattern, report
from immanuel.setup import settings
from immanuel.tools import calculate, convert, date, eph, forecast
from immanuel.classes import wrap


class Chart:
    """ Base chart class. This is essentially an abstract class for the actual
     chart classes to inherit from. """
    def __init__(self, dob: str, lat: float, lon: float, type: int) -> None:
        self.type = names.CHART_TYPES[type]

        self._dob = dob
        self._lat = lat
        self._lon = lon

        self._dt = self.get_dt()
        self._jd = self.get_jd()

        sun = eph.planet(chart.SUN, self._jd)
        moon = eph.planet(chart.MOON, self._jd)
        asc = eph.angle(chart.ASC, self._jd, lat, lon, settings.house_system)
        armc_lon = self.get_armc_lon()

        self._objects = self.get_objects()
        self._houses = self.get_houses()

        self.house_system = names.HOUSE_SYSTEMS[settings.house_system]
        self.shape = names.CHART_SHAPES[pattern.chart_shape(self._objects)]
        self.diurnal = calculate.is_daytime(sun['lon'], asc['lon'])
        self.moon_phase = names.MOON_PHASES[calculate.moon_phase(sun['lon'], moon['lon'])]
        self.sidereal_time = convert.dec_to_string(calculate.sidereal_time(armc_lon), convert.FORMAT_TIME)
        self.date = wrap.Date(self._dt)
        self.coords = wrap.Coords(self._lat, self._lon)
        # self.objects = {index: wrap.Object(obj, self._objects, self._houses, self.diurnal, self._jd) for index, obj in self._objects.items()}
        # self.houses = {index: wrap.Object(house) for index, house in self._houses.items()}

        # self.aspects = {}
        # aspects = self.get_aspects()

        # for index, aspect_list in aspects.items():
        #     self.aspects[index] = {object_index: wrap.Aspect(object_aspect, self._objects) for object_index, object_aspect in aspect_list.items()}

        # self.weightings = {
        #     'elements': dict(zip(('fire', 'earth', 'air', 'water'), report.elements(self._objects).values())),
        #     'modalities': dict(zip(('cardinal', 'fixed', 'mutable'), report.modalities(self._objects).values())),
        #     'quadrants': report.quadrants(self._objects, self._houses),
        # }

    def get_dt(self) -> datetime:
        pass

    def get_jd(self) -> float:
        pass

    def get_armc_lon(self) -> float:
        pass

    def get_objects(self) -> dict:
        pass

    def get_houses(self) -> dict:
        pass

    def get_aspects(self) -> dict:
        pass


class Natal(Chart):
    """ Standard natal chart generates data straight from the passed date and
    coordinates. """
    def __init__(self, dob: str, lat: float, lon: float) -> None:
        super().__init__(dob, lat, lon, chart.NATAL)

    def get_dt(self) -> datetime:
        return date.localize(datetime.fromisoformat(self._dob), self._lat, self._lon)

    def get_jd(self) -> float:
        return date.to_jd(self._dt)

    def get_armc_lon(self) -> float:
        return eph.angle(chart.ARMC, self._jd, self._lat, self._lon, settings.house_system)['lon']

    def get_objects(self) -> dict:
        return eph.objects(settings.objects, self._jd, self._lat, self._lon, settings.house_system)

    def get_houses(self) -> dict:
        return eph.houses(self._jd, self._lat, self._lon, settings.house_system)

    def get_aspects(self) -> dict:
        return aspect.all(self._objects)


class Progressed(Chart):
    """ Secondary progression chart uses the MC progression method from
    settings. """
    def __init__(self, dob: str, lat: float, lon: float, pdt: str) -> None:
        natal_dt = date.localize(datetime.fromisoformat(dob), lat, lon)
        natal_jd = date.to_jd(natal_dt)
        progression_dt = date.localize(datetime.fromisoformat(pdt), lat, lon)
        progression_jd = date.to_jd(progression_dt)
        self._progressed_jd, self._progressed_armc = forecast.progression(natal_jd, lat, lon, progression_jd, settings.house_system, settings.mc_progression)
        self._progressed_dt = date.from_jd(self._progressed_jd)
        super().__init__(None, lat, lon, chart.PROGRESSED)      # TODO: tidy this up

    def get_dt(self) -> datetime:
        return self._progressed_dt

    def get_jd(self) -> float:
        return self._progressed_jd

    def get_armc_lon(self) -> float:
        return self._progressed_armc

    def get_objects(self) -> dict:
        return eph.objects(settings.objects, self._jd, self._lat, self._lon, settings.house_system)

    def get_houses(self) -> dict:
        return eph.armc_houses(self._jd, self._lat, self._progressed_armc, settings.house_system)

    def get_aspects(self) -> dict:
        return aspect.all(self._objects)
