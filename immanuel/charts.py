"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    The actual user-facing chart classes are contained in this module. Each
    chart class is easily serializable using the ToJSON class. Each chart type
    is instantiated by passing an instance of Subject, apart from Transits.
    This assumes the current moment and optionally takes a pair of coordinates
    for house calculations, although these will default to those specified in
    the settings if they are not required.

    Instead of a dedicated synastry chart, the optional aspects_to parameter
    in each chart type's constructor takes another Chart instance and forms its
    aspects to the planets in that chart rather than its own. An additional
    houses_for_aspected boolean is available on the Transits chart to use the
    houses of the passed aspects_to chart.

"""

import json
from datetime import datetime
from typing import TypeVar

from immanuel.classes import wrap
from immanuel.classes.localize import localize as _
from immanuel.classes.serialize import ToJSON
from immanuel.classes.transit_events import TransitPeriod
from immanuel.const import calc, chart, names, transits
from immanuel.reports import aspect, dignity, pattern, weighting
from immanuel.setup import settings
from immanuel.tools import (
    convert,
    date,
    ephemeris,
    forecast,
    midpoint,
    position,
    transit,
)


ChartType = TypeVar("ChartType", bound="Chart")


class Subject:
    """Simple class to model a chart subject - essentially just
    a time and place."""

    def __init__(
        self,
        date_time: str | float | datetime,
        latitude: float | list | tuple | str,
        longitude: float | list | tuple | str,
        timezone_offset: float | None = None,
        timezone: str | None = None,
        time_is_dst: bool | None = None,
    ) -> None:
        self.latitude, self.longitude = convert.coordinates(latitude, longitude)
        self.timezone_offset = timezone_offset
        self.timezone = timezone
        self.time_is_dst = time_is_dst
        self.date_time = date.to_datetime(
            dt=date_time,
            lat=self.latitude,
            lon=self.longitude,
            offset=timezone_offset,
            time_zone=timezone,
            is_dst=time_is_dst,
        )
        self.date_time_ambiguous = (
            date.ambiguous(self.date_time) and time_is_dst is None
        )
        self.julian_date = date.to_jd(self.date_time)


class Chart:
    """Base chart class. This acts as an abstract class for the actual chart
    classes to inherit from."""

    def __init__(self, type: int, aspects_to: ChartType | None = None) -> None:
        self.type = _(names.CHART_TYPES[type])
        self._type = type
        self._aspects_to = aspects_to

        self._native: Subject
        self._obliquity: float
        self._diurnal: bool
        self._moon_phase: int
        self._triad: dict = {
            chart.SUN: None,
            chart.MOON: None,
            chart.ASC: None,
        }
        self._objects: dict
        self._houses: dict

        self.generate()
        self.wrap()

    def house_for(self, object: wrap.Object) -> int:
        """Returns the index of the house where any passed arbitrary object
        would appear in the current chart. Useful for synastries and
        transit charts."""
        return position.house(object.longitude.raw, self._houses)["index"]

    def generate(self) -> None:
        """Generating the raw data is each descendant class's
        responsibility."""
        pass

    def wrap(self) -> None:
        """Loop through the required data and wrap each one with a custom
        function."""
        for index in settings.chart_data[self._type]:
            method = f"set_wrapped_{index}"
            if hasattr(self, method):
                getattr(self, method)()

    # Base class provides wrappers for properties common to all classes.
    def set_wrapped_native(self) -> None:
        self.native = wrap.Subject(self._native)

    def set_wrapped_house_system(self) -> None:
        self.house_system = _(names.HOUSE_SYSTEMS[settings.house_system])

    def set_wrapped_shape(self) -> None:
        self.shape = _(names.CHART_SHAPES[pattern.chart_shape(self._objects)])

    def set_wrapped_diurnal(self) -> None:
        self.diurnal = self._diurnal

    def set_wrapped_moon_phase(self) -> None:
        self.moon_phase = wrap.MoonPhase(self._moon_phase)

    def set_wrapped_objects(self) -> None:
        self.objects = {}

        for index, object in self._objects.items():
            house = position.house(
                object=object,
                houses=self._houses,
            )
            out_of_bounds = ephemeris.is_out_of_bounds(
                object=object,
                obliquity=self._obliquity,
            )
            in_sect = (
                ephemeris.is_in_sect(
                    object=object,
                    is_daytime=self._diurnal,
                    sun=self._triad[chart.SUN],
                )
                if object["index"]
                in (
                    chart.SUN,
                    chart.MOON,
                    chart.MERCURY,
                    chart.VENUS,
                    chart.MARS,
                    chart.JUPITER,
                    chart.SATURN,
                )
                else None
            )
            dignity_state = (
                dignity.all(
                    object=object,
                    objects=self._objects,
                    is_daytime=self._diurnal,
                )
                if object["type"] == chart.PLANET
                and calc.PLANETS.issubset(self._objects)
                else None
            )
            date_time = (
                date.to_datetime(
                    dt=object["jd"],
                    lat=self._native.latitude,
                    lon=self._native.longitude,
                    offset=self._native.timezone_offset,
                    time_zone=self._native.timezone,
                )
                if "jd" in object
                else None
            )

            self.objects[index] = wrap.Object(
                object=object,
                date_time=date_time,
                house=house,
                out_of_bounds=out_of_bounds,
                in_sect=in_sect,
                dignity_state=dignity_state,
            )

    def set_wrapped_houses(self) -> None:
        self.houses = {
            index: wrap.Object(object=house) for index, house in self._houses.items()
        }

    def set_wrapped_aspects(self) -> None:
        aspects = (
            aspect.all(self._objects)
            if self._aspects_to is None
            else aspect.synastry(self._objects, self._aspects_to._objects)
        )
        self.aspects = {
            index: {
                object_index: wrap.Aspect(
                    aspect=object_aspect,
                    active_name=self._objects[object_aspect["active"]]["name"]
                    if object_aspect["active"] in self._objects
                    else self._aspects_to._objects[object_aspect["active"]]["name"],
                    passive_name=self._objects[object_aspect["passive"]]["name"]
                    if object_aspect["passive"] in self._objects
                    else self._aspects_to._objects[object_aspect["passive"]]["name"],
                )
                for object_index, object_aspect in aspect_list.items()
            }
            for index, aspect_list in aspects.items()
        }

    def set_wrapped_weightings(self) -> None:
        self.weightings = wrap.Weightings(
            elements=weighting.elements(self._objects),
            modalities=weighting.modalities(self._objects),
            quadrants=weighting.quadrants(self._objects, self._houses),
        )

    def to_json(self, **kwargs) -> str:
        return json.dumps(self, cls=ToJSON, **kwargs)


class Natal(Chart):
    """Standard natal chart generates data straight from the passed
    native information."""

    def __init__(self, native: Subject, aspects_to: Chart | None = None) -> None:
        self._native = native
        super().__init__(chart.NATAL, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.earth_obliquity(self._native.julian_date)

        self._triad[chart.SUN] = ephemeris.get_planet(
            chart.SUN, self._native.julian_date
        )
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._native.julian_date
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_houses(
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )


class SolarReturn(Chart):
    """Solar return chart for the given year."""

    def __init__(
        self, native: Subject, year: int, aspects_to: Chart | None = None
    ) -> None:
        self._native = native
        self._solar_return_year = year
        super().__init__(chart.SOLAR_RETURN, aspects_to)

    def generate(self) -> None:
        self._solar_return_jd = forecast.solar_return(
            self._native.julian_date, self._solar_return_year
        )
        self._obliquity = ephemeris.earth_obliquity(self._solar_return_jd)
        self._solar_return_armc = ephemeris.get_angle(
            index=chart.ARMC,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._triad[chart.SUN] = ephemeris.get_planet(chart.SUN, self._solar_return_jd)
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._solar_return_jd
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_houses(
            jd=self._solar_return_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

    def set_wrapped_solar_return_year(self) -> None:
        self.solar_return_year = self._solar_return_year

    def set_wrapped_solar_return_date_time(self) -> None:
        self.solar_return_date_time = wrap.DateTime(
            dt=self._solar_return_jd,
            armc=self._solar_return_armc,
            latitude=self._native.latitude,
            longitude=self._native.longitude,
            offset=self._native.timezone_offset,
            timezone=self._native.timezone,
        )


class Progressed(Chart):
    """Secondary progression chart uses the MC progression method from
    settings."""

    def __init__(
        self,
        native: Subject,
        date_time: datetime | str,
        aspects_to: Chart | None = None,
    ) -> None:
        self._native = native
        self._date_time = date_time
        super().__init__(chart.PROGRESSED, aspects_to)

    def generate(self) -> None:
        self._progression_date_time = date.to_datetime(
            dt=self._date_time,
            lat=self._native.latitude,
            lon=self._native.longitude,
            offset=self._native.timezone_offset,
            time_zone=self._native.timezone,
        )
        progression_jd = date.to_jd(self._progression_date_time)
        progression_armc = ephemeris.get_angle(
            index=chart.ARMC,
            jd=progression_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )
        self._progression_armc_longitude = progression_armc["lon"]

        self._progressed_jd, self._progressed_armc_longitude = forecast.progression(
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            pjd=progression_jd,
            house_system=settings.house_system,
            method=settings.mc_progression_method,
        )
        self._obliquity = ephemeris.earth_obliquity(self._progressed_jd)

        self._triad[chart.SUN] = ephemeris.get_planet(chart.SUN, self._progressed_jd)
        self._triad[chart.MOON] = ephemeris.get_planet(chart.MOON, self._progressed_jd)
        self._triad[chart.ASC] = ephemeris.get_armc_angle(
            index=chart.ASC,
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
            obliquity=self._obliquity,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_armc_objects(
            object_list=settings.objects,
            jd=self._progressed_jd,
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
            lon=self._native.longitude,
            obliquity=self._obliquity,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_armc_houses(
            armc=self._progressed_armc_longitude,
            lat=self._native.latitude,
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
            latitude=self._native.latitude,
            longitude=self._native.longitude,
            offset=self._native.timezone_offset,
            timezone=self._native.timezone,
        )

    def set_wrapped_progression_method(self) -> None:
        self.progression_method = _(
            names.PROGRESSION_METHODS[settings.mc_progression_method]
        )


class Composite(Chart):
    """Generates a midpoint chart based on the two passed sets of data."""

    def __init__(
        self, native: Subject, partner: Subject, aspects_to: Chart | None = None
    ) -> None:
        self._native = native
        self._partner = partner
        super().__init__(chart.COMPOSITE, aspects_to)

    def generate(self) -> None:
        self._obliquity = midpoint.obliquity(
            self._native.julian_date, self._partner.julian_date
        )

        native_objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        partner_objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._partner.julian_date,
            lat=self._partner.latitude,
            lon=self._partner.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._objects = midpoint.all(
            objects1=native_objects,
            objects2=partner_objects,
            obliquity=self._obliquity,
        )

        if settings.house_system == chart.WHOLE_SIGN:
            native_armc = ephemeris.get_angle(
                index=chart.ARMC,
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_armc = ephemeris.get_angle(
                index=chart.ARMC,
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            armc = midpoint.composite(native_armc, partner_armc, self._obliquity)["lon"]
            latitude = (self._native.latitude + self._partner.latitude) / 2

            self._houses = ephemeris.get_armc_houses(
                armc=armc,
                lat=latitude,
                obliquity=self._obliquity,
                house_system=settings.house_system,
            )
        else:
            native_houses = ephemeris.get_houses(
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_houses = ephemeris.get_houses(
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            self._houses = midpoint.all(
                objects1=native_houses,
                objects2=partner_houses,
                obliquity=self._obliquity,
            )

        if chart.ASC in self._objects:
            self._triad[chart.ASC] = self._objects[chart.ASC]
        else:
            native_asc = ephemeris.get_angle(
                index=chart.ASC,
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            partner_asc = ephemeris.get_angle(
                index=chart.ASC,
                jd=self._partner.julian_date,
                lat=self._partner.latitude,
                lon=self._partner.longitude,
                house_system=settings.house_system,
            )
            self._triad[chart.ASC] = midpoint.composite(
                native_asc, partner_asc, self._obliquity
            )

        if chart.SUN in self._objects:
            self._triad[chart.SUN] = self._objects[chart.SUN]
        else:
            native_sun = ephemeris.get_planet(chart.SUN, self._native.julian_date)
            partner_sun = ephemeris.get_planet(chart.SUN, self._partner.julian_date)
            self._triad[chart.SUN] = midpoint.composite(
                native_sun, partner_sun, self._obliquity
            )

        if chart.MOON in self._objects:
            self._triad[chart.MOON] = self._objects[chart.MOON]
        else:
            native_moon = ephemeris.get_planet(chart.MOON, self._native.julian_date)
            partner_moon = ephemeris.get_planet(chart.MOON, self._partner.julian_date)
            self._triad[chart.MOON] = midpoint.composite(
                native_moon, partner_moon, self._obliquity
            )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )

    def set_wrapped_partner(self):
        self.partner = wrap.Subject(self._partner)


class Transits(Chart):
    """Chart of the moment for the given coordinates. Structurally identical
    to the natal chart. Coordinates default to those specified in settings."""

    def __init__(
        self,
        latitude: float | list | tuple | str = settings.default_latitude,
        longitude: float | list | tuple | str = settings.default_longitude,
        offset: float | None = None,
        timezone: str | None = None,
        aspects_to: Chart | None = None,
        houses_for_aspected: bool = False,
    ) -> None:
        lat, lon = convert.coordinates(latitude, longitude)
        date_time = date.localize(datetime.now(), lat, lon, offset, timezone)
        self._native = Subject(date_time, lat, lon, offset, timezone)
        self._houses_for_aspected = houses_for_aspected
        super().__init__(chart.TRANSITS, aspects_to)

    def generate(self) -> None:
        self._obliquity = ephemeris.earth_obliquity(self._native.julian_date)

        self._triad[chart.SUN] = ephemeris.get_planet(
            chart.SUN, self._native.julian_date
        )
        self._triad[chart.MOON] = ephemeris.get_planet(
            chart.MOON, self._native.julian_date
        )
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=self._native.julian_date,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = (
            ephemeris.get_houses(
                jd=self._native.julian_date,
                lat=self._native.latitude,
                lon=self._native.longitude,
                house_system=settings.house_system,
            )
            if self._aspects_to is None or self._houses_for_aspected is False
            else self._aspects_to._houses
        )


class MundaneTransits(Chart):
    """Calculates transits for a fixed geographic location over a time period.
    Provides planetary positions and movements at regular intervals."""

    def __init__(
        self,
        start_date: str | datetime,
        end_date: str | datetime,
        latitude: float | list | tuple | str = settings.default_latitude,
        longitude: float | list | tuple | str = settings.default_longitude,
        interval: transits.IntervalType = settings.transit_default_interval,
        timezone_offset: float | None = None,
        timezone: str | None = None,
        aspects_to: Chart | None = None,
    ) -> None:
        # Convert coordinates
        lat, lon = convert.coordinates(latitude, longitude)

        # Store parameters for calculation
        self._start_date = date.to_datetime(
            dt=start_date,
            lat=lat,
            lon=lon,
            offset=timezone_offset,
            time_zone=timezone,
        ) if isinstance(start_date, str) else start_date

        self._end_date = date.to_datetime(
            dt=end_date,
            lat=lat,
            lon=lon,
            offset=timezone_offset,
            time_zone=timezone,
        ) if isinstance(end_date, str) else end_date

        self._interval = interval
        self._latitude = lat
        self._longitude = lon
        self._timezone_offset = timezone_offset
        self._timezone = timezone

        # Create a Subject for the location (using start date)
        self._native = Subject(
            self._start_date, lat, lon, timezone_offset, timezone
        )

        # Initialize transit calculator
        self._calculator = transit.TransitCalculator(
            precision=settings.transit_precision
        )

        super().__init__(chart.MUNDANE_TRANSITS, aspects_to)

    def generate(self) -> None:
        """Generate transit timeline for the specified period."""
        # Calculate transit timeline
        self._transit_period = self._calculator.calculate_transit_timeline(
            objects=settings.objects,
            start_date=self._start_date,
            end_date=self._end_date,
            interval=self._interval,
            latitude=self._latitude,
            longitude=self._longitude
        )

        # For consistency with other chart types, we need these values
        # Use the midpoint of the period for calculations
        mid_date = self._start_date + (self._end_date - self._start_date) / 2
        mid_jd = date.to_jd(mid_date)

        self._obliquity = ephemeris.earth_obliquity(mid_jd)

        # Get Sun, Moon, and ASC for the midpoint
        self._triad[chart.SUN] = ephemeris.get_planet(chart.SUN, mid_jd)
        self._triad[chart.MOON] = ephemeris.get_planet(chart.MOON, mid_jd)
        self._triad[chart.ASC] = ephemeris.get_angle(
            index=chart.ASC,
            jd=mid_jd,
            lat=self._latitude,
            lon=self._longitude,
            house_system=settings.house_system,
        )

        self._diurnal = ephemeris.is_daytime_from(
            self._triad[chart.SUN], self._triad[chart.ASC]
        )
        self._moon_phase = ephemeris.moon_phase_from(
            self._triad[chart.SUN], self._triad[chart.MOON]
        )

        # Get objects and houses for the midpoint
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=mid_jd,
            lat=self._latitude,
            lon=self._longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )
        self._houses = ephemeris.get_houses(
            jd=mid_jd,
            lat=self._latitude,
            lon=self._longitude,
            house_system=settings.house_system,
        )

    def set_wrapped_transit_period(self) -> None:
        """Wrap the transit period data."""
        self.transit_period = wrap.TransitPeriodWrapper(self._transit_period)

    def set_wrapped_transit_events(self) -> None:
        """Wrap the transit events data."""
        self.transit_events = [
            wrap.TransitEventWrapper(event)
            for event in self._transit_period.events
        ]

    def set_wrapped_transit_statistics(self) -> None:
        """Wrap the transit statistics."""
        self.transit_statistics = wrap.TransitStatisticsWrapper(
            self._transit_period.statistics
        )


class NatalTransits(Chart):
    """Calculates transits to a natal chart over a time period.
    Shows aspects between transiting planets and natal positions."""

    def __init__(
        self,
        natal_chart: Chart,
        start_date: str | datetime,
        end_date: str | datetime,
        interval: transits.IntervalType = settings.transit_default_interval,
        aspects_to_calculate: list = None,
        aspects_to: Chart | None = None,
    ) -> None:
        self._natal_chart = natal_chart
        self._start_date = date.to_datetime(
            dt=start_date,
            lat=natal_chart._native.latitude,
            lon=natal_chart._native.longitude,
            offset=natal_chart._native.timezone_offset,
            time_zone=natal_chart._native.timezone,
        ) if isinstance(start_date, str) else start_date

        self._end_date = date.to_datetime(
            dt=end_date,
            lat=natal_chart._native.latitude,
            lon=natal_chart._native.longitude,
            offset=natal_chart._native.timezone_offset,
            time_zone=natal_chart._native.timezone,
        ) if isinstance(end_date, str) else end_date

        self._interval = interval
        self._aspects_to_calculate = aspects_to_calculate or settings.aspects

        # Use natal chart's location
        self._native = natal_chart._native

        # Initialize transit calculator
        self._calculator = transit.TransitCalculator(
            precision=settings.transit_precision
        )

        super().__init__(chart.NATAL_TRANSITS, aspects_to or natal_chart)

    def generate(self) -> None:
        """Generate transit timeline and calculate aspects to natal chart."""
        # Calculate transit timeline
        self._transit_period = self._calculator.calculate_transit_timeline(
            objects=settings.objects,
            start_date=self._start_date,
            end_date=self._end_date,
            interval=self._interval,
            latitude=self._native.latitude,
            longitude=self._native.longitude
        )

        # Use midpoint for chart consistency calculations
        mid_date = self._start_date + (self._end_date - self._start_date) / 2
        mid_jd = date.to_jd(mid_date)

        self._obliquity = ephemeris.earth_obliquity(mid_jd)

        # Use natal chart's triad
        self._triad = self._natal_chart._triad.copy()

        self._diurnal = self._natal_chart._diurnal
        self._moon_phase = self._natal_chart._moon_phase

        # Get current transiting objects
        self._objects = ephemeris.get_objects(
            object_list=settings.objects,
            jd=mid_jd,
            lat=self._native.latitude,
            lon=self._native.longitude,
            house_system=settings.house_system,
            part_formula=settings.part_formula,
        )

        # Use natal houses
        self._houses = self._natal_chart._houses

    def set_wrapped_transit_period(self) -> None:
        """Wrap the transit period data."""
        self.transit_period = wrap.TransitPeriodWrapper(self._transit_period)

    def set_wrapped_transit_events(self) -> None:
        """Wrap the transit events data."""
        self.transit_events = [
            wrap.TransitEventWrapper(event)
            for event in self._transit_period.events
        ]

    def set_wrapped_transit_statistics(self) -> None:
        """Wrap the transit statistics."""
        self.transit_statistics = wrap.TransitStatisticsWrapper(
            self._transit_period.statistics
        )


class AstrocartographyChart(Chart):
    """Astrocartography chart generates planetary lines, zenith points,
    and optional advanced features like parans, local space lines, and aspect lines."""

    def __init__(
        self,
        subject: Subject,
        planets: list = None,
        line_types: list = None,
        sampling_resolution: float = None,
        calculation_method: str = None,
        orb_influence_km: float = None,
        include_parans: bool = False,
        include_local_space: bool = False,
        aspect_lines_config: dict = None,
        aspects_to: Chart | None = None
    ) -> None:
        # Validate subject
        if subject is None:
            raise ValueError("Subject cannot be None")

        # Store parameters
        self._subject = subject
        self._planets = planets or [chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS, chart.JUPITER, chart.SATURN]
        self._include_parans = include_parans
        self._include_local_space = include_local_space
        self._aspect_lines_config = aspect_lines_config

        # Import constants here to avoid circular imports
        from immanuel.const import astrocartography

        self._line_types = line_types or [astrocartography.LINE_MC, astrocartography.LINE_IC, astrocartography.LINE_ASCENDANT, astrocartography.LINE_DESCENDANT]
        self._sampling_resolution = sampling_resolution or astrocartography.DEFAULT_SAMPLING_RESOLUTION
        self._calculation_method = calculation_method or astrocartography.METHOD_ZODIACAL
        self._orb_influence_km = orb_influence_km or astrocartography.DEFAULT_ORB_INFLUENCE_KM

        # Store as native for compatibility with base class
        self._native = subject

        super().__init__(chart.ASTROCARTOGRAPHY, aspects_to)

    def generate(self) -> None:
        """Generate astrocartography data including planetary lines and zenith points."""
        # Import here to avoid circular imports
        from immanuel.tools.astrocartography import AstrocartographyCalculator

        # Initialize calculator
        self._calculator = AstrocartographyCalculator(
            julian_date=self._subject.julian_date,
            sampling_resolution=self._sampling_resolution,
            calculation_method=self._calculation_method
        )

        # Generate planetary lines
        self._planetary_lines = {}
        for planet_id in self._planets:
            planet_lines = {}

            # Calculate MC/IC lines if requested
            if any(lt in self._line_types for lt in ['MC', 'IC']):
                try:
                    mc_coords, ic_coords = self._calculator.calculate_mc_ic_lines(planet_id)

                    if 'MC' in self._line_types:
                        planet_lines['MC'] = {
                            'coordinates': mc_coords,
                            'planet_id': planet_id,
                            'line_type': 'MC'
                        }

                    if 'IC' in self._line_types:
                        planet_lines['IC'] = {
                            'coordinates': ic_coords,
                            'planet_id': planet_id,
                            'line_type': 'IC'
                        }
                except Exception:
                    # Skip failed calculations
                    pass

            # Calculate ASC/DESC lines if requested
            if any(lt in self._line_types for lt in ['ASC', 'DESC']):
                try:
                    asc_coords, desc_coords = self._calculator.calculate_ascendant_descendant_lines(planet_id)

                    if 'ASC' in self._line_types:
                        planet_lines['ASC'] = {
                            'coordinates': asc_coords,
                            'planet_id': planet_id,
                            'line_type': 'ASC'
                        }

                    if 'DESC' in self._line_types:
                        planet_lines['DESC'] = {
                            'coordinates': desc_coords,
                            'planet_id': planet_id,
                            'line_type': 'DESC'
                        }
                except Exception:
                    # Skip failed calculations
                    pass

            self._planetary_lines[planet_id] = planet_lines

        # Generate zenith points
        self._zenith_points = {}
        for planet_id in self._planets:
            try:
                zenith_lon, zenith_lat = self._calculator.calculate_zenith_point(planet_id)
                self._zenith_points[planet_id] = {
                    'longitude': zenith_lon,
                    'latitude': zenith_lat,
                    'planet_id': planet_id
                }
            except Exception:
                # Skip failed calculations
                pass

        # Initialize optional features
        self._paran_lines = []
        self._local_space_lines = {}
        self._aspect_lines = []

        # Set basic chart properties for compatibility
        self._obliquity = ephemeris.earth_obliquity(self._subject.julian_date)
        self._diurnal = True  # Placeholder
        self._moon_phase = 1  # Placeholder
        self._objects = {}  # Not used for astrocartography
        self._houses = {}   # Not used for astrocartography

    # Chart interface methods

    def get_lines_for_planet(self, planet_id: int) -> dict:
        """Get all line types for a specific planet."""
        if planet_id not in self._planetary_lines:
            raise ValueError(f"Planet {planet_id} not found in chart")
        return self._planetary_lines[planet_id]

    def get_lines_by_type(self, line_type: str) -> dict:
        """Get all planets for a specific line type."""
        valid_types = ['MC', 'IC', 'ASC', 'DESC']
        if line_type not in valid_types:
            raise ValueError(f"Invalid line_type: {line_type}")

        lines_by_type = {}
        for planet_id, planet_lines in self._planetary_lines.items():
            if line_type in planet_lines:
                lines_by_type[planet_id] = planet_lines[line_type]

        return lines_by_type

    def get_influences_at_location(self, longitude: float, latitude: float) -> dict:
        """Analyze planetary influences at a specific location."""
        import math

        # Validate coordinates
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}")

        influences = {
            'active_lines': [],
            'nearby_lines': [],
            'zenith_distances': {}
        }

        # Check for active lines (within orb)
        orb_degrees = self._orb_influence_km / 111.0  # Rough km to degrees conversion

        for planet_id, planet_lines in self._planetary_lines.items():
            for line_type, line_data in planet_lines.items():
                if 'coordinates' in line_data and line_data['coordinates']:
                    # Find closest point on line
                    min_distance = float('inf')
                    for line_lon, line_lat in line_data['coordinates']:
                        distance = math.sqrt((longitude - line_lon)**2 + (latitude - line_lat)**2)
                        min_distance = min(min_distance, distance)

                    # Check if within orb
                    if min_distance <= orb_degrees:
                        influences['active_lines'].append({
                            'planet_id': planet_id,
                            'line_type': line_type,
                            'distance_degrees': min_distance
                        })
                    elif min_distance <= orb_degrees * 3:  # Nearby threshold
                        influences['nearby_lines'].append({
                            'planet_id': planet_id,
                            'line_type': line_type,
                            'distance_degrees': min_distance
                        })

        # Calculate zenith distances
        for planet_id, zenith_data in self._zenith_points.items():
            zenith_distance = math.sqrt(
                (longitude - zenith_data['longitude'])**2 +
                (latitude - zenith_data['latitude'])**2
            )
            influences['zenith_distances'][planet_id] = zenith_distance

        return influences

    def calculate_travel_recommendations(self, target_influences: list, max_distance_km: float = 5000) -> list:
        """Calculate travel recommendations based on desired planetary influences."""
        # Simplified implementation
        return []

    def export_coordinates(self, format: str = 'geojson') -> str | dict:
        """Export coordinates in various formats."""
        if format.lower() == 'geojson':
            return self._export_geojson()
        elif format.lower() == 'kml':
            return self._export_kml()
        elif format.lower() == 'csv':
            return self._export_csv()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_geojson(self) -> dict:
        """Export coordinates as GeoJSON."""
        features = []

        for planet_id, planet_lines in self._planetary_lines.items():
            for line_type, line_data in planet_lines.items():
                if 'coordinates' in line_data and line_data['coordinates']:
                    # Convert to GeoJSON LineString
                    coordinates = [[lon, lat] for lon, lat in line_data['coordinates']]

                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': coordinates
                        },
                        'properties': {
                            'planet_id': planet_id,
                            'line_type': line_type
                        }
                    }
                    features.append(feature)

        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def _export_kml(self) -> str:
        """Export coordinates as KML."""
        kml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        kml_lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml_lines.append('<Document>')

        for planet_id, planet_lines in self._planetary_lines.items():
            for line_type, line_data in planet_lines.items():
                if 'coordinates' in line_data and line_data['coordinates']:
                    kml_lines.append('<Placemark>')
                    kml_lines.append(f'<name>Planet {planet_id} {line_type}</name>')
                    kml_lines.append('<LineString>')
                    kml_lines.append('<coordinates>')

                    coord_str = ' '.join([f'{lon},{lat},0' for lon, lat in line_data['coordinates']])
                    kml_lines.append(coord_str)

                    kml_lines.append('</coordinates>')
                    kml_lines.append('</LineString>')
                    kml_lines.append('</Placemark>')

        kml_lines.append('</Document>')
        kml_lines.append('</kml>')

        return '\n'.join(kml_lines)

    def _export_csv(self) -> str:
        """Export coordinates as CSV."""
        csv_lines = ['planet_id,line_type,longitude,latitude']

        for planet_id, planet_lines in self._planetary_lines.items():
            for line_type, line_data in planet_lines.items():
                if 'coordinates' in line_data and line_data['coordinates']:
                    for lon, lat in line_data['coordinates']:
                        csv_lines.append(f'{planet_id},{line_type},{lon},{lat}')

        return '\n'.join(csv_lines)

    def __json__(self) -> dict:
        """JSON serialization method for ToJSON encoder."""
        return {
            'type': 'AstrocartographyChart',
            'subject': {
                'date_time': self._subject.date_time.isoformat(),
                'latitude': self._subject.latitude,
                'longitude': self._subject.longitude,
                'julian_date': self._subject.julian_date
            },
            'planetary_lines': self._planetary_lines,
            'zenith_points': self._zenith_points,
            'paran_lines': self._paran_lines,
            'local_space_lines': self._local_space_lines,
            'aspect_lines': self._aspect_lines,
            'calculation_metadata': {
                'planets': self._planets,
                'line_types': self._line_types,
                'sampling_resolution': self._sampling_resolution,
                'calculation_method': self._calculation_method,
                'orb_influence_km': self._orb_influence_km
            }
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        planet_count = len(self._planets)
        line_count = sum(len(lines) for lines in self._planetary_lines.values())
        return f"AstrocartographyChart({planet_count} planets, {line_count} lines, method={self._calculation_method})"

    # Wrapper methods for base class compatibility

    def set_wrapped_planetary_lines(self) -> None:
        """Wrap planetary lines data."""
        self.planetary_lines = self._planetary_lines

    def set_wrapped_zenith_points(self) -> None:
        """Wrap zenith points data."""
        self.zenith_points = self._zenith_points

    def set_wrapped_paran_lines(self) -> None:
        """Wrap paran lines data."""
        self.paran_lines = self._paran_lines

    def set_wrapped_local_space_lines(self) -> None:
        """Wrap local space lines data."""
        self.local_space_lines = self._local_space_lines

    def set_wrapped_aspect_lines(self) -> None:
        """Wrap aspect lines data."""
        self.aspect_lines = self._aspect_lines

    def set_wrapped_subject(self) -> None:
        """Wrap subject data."""
        self.subject = self._subject
