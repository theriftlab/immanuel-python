"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)

This module provides a thin cache wrapper around the real
TimezoneFinder class. Its instantiation can be heavy, so we keep a
single cached instance on hand in here for lookups.

"""


class TimezoneFinder:
    """This class is simply a cache for a TimezoneFinder instance, with
    an additional timezone_at() wrapper, since that is all Immanuel needs."""

    _timezone_finder = None

    @classmethod
    def get(cls):
        if cls._timezone_finder is None:
            from timezonefinder import TimezoneFinder as TF

            cls._timezone_finder = TF()
        return cls._timezone_finder

    @classmethod
    def timezone_at(cls, lat: float, lon: float) -> str:
        return cls.get().timezone_at(lat=lat, lng=lon)
