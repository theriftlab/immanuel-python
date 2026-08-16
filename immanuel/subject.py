"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


The subject of a chart - essentially a time and a place,
standardized into the coordinates, datetime, and Julian date
the rest of the package's tools work with.

"""

from datetime import datetime

from immanuel.tools import convert, date


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
