"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides conversions between D:M:S and decimal.

    These functions perform simple conversions between the base-12 data used
    by astrology (ie. angles, coordinates, and time) in string/list format,
    and decimal numbers in float format.

"""

import math
import re

import swisseph as swe


FORMAT_TIME = 0
FORMAT_TIME_OFFSET = 1
FORMAT_DMS = 2
FORMAT_LAT = 3
FORMAT_LON = 4

ROUND_DEGREE = (1, swe.SPLIT_DEG_ROUND_DEG)
ROUND_MINUTE = (2, swe.SPLIT_DEG_ROUND_MIN)
ROUND_SECOND = (3, swe.SPLIT_DEG_ROUND_SEC)


def dms_to_dec(dms: list | tuple) -> float:
    """ Returns the decimal conversion of a D:M:S list. """
    dec = sum([float(abs(v)) / 60**k for k, v in enumerate(dms[1:])])
    return dec if dms[0] == '+' else -dec


def dec_to_dms(dec: float, round_to: tuple = ROUND_SECOND, pad_rounded = False) -> tuple:
    """ Returns the rounded D:M:S conversion of a decimal float. """
    dms = ('-' if dec < 0 else '+', *swe.split_deg(dec, round_to[1])[:round_to[0]])
    return dms + (0,) * (3-round_to[0]) if pad_rounded else dms


def dms_to_string(dms: list | tuple, format: int = FORMAT_DMS, round_to: tuple = ROUND_SECOND, pad_rounded = None) -> str:
    """ Returns a D:M:S list as either a D:M:S, D°M'S" or
    lat/lon coordinate string. """
    pad_rounded = True if format in (FORMAT_LAT, FORMAT_LON) or (pad_rounded is None and format != FORMAT_DMS) else pad_rounded
    dms = dec_to_dms(dms_to_dec(dms), round_to, pad_rounded)

    if format == FORMAT_DMS:
        return _dms_to_string_format_dms(dms)
    if format == FORMAT_TIME:
        return _dms_to_string_format_time(dms)
    if format == FORMAT_TIME_OFFSET:
        return _dms_to_string_format_time_offset(dms)
    if format == FORMAT_LAT:
        return _dms_to_string_format_lat(dms)
    if format == FORMAT_LON:
        return _dms_to_string_format_lon(dms)

    return ''


def string_to_dms(string: str, round_to: tuple = ROUND_SECOND, pad_rounded = False) -> tuple:
    """ Takes any string supported by string_to_dec() and returns a
    DMS tuple. """
    return dec_to_dms(string_to_dec(string), round_to, pad_rounded)


def dec_to_string(dec: float, format: int = FORMAT_DMS, round_to: tuple = ROUND_SECOND, pad_rounded = None) -> str:
    """ Returns a decimal float as either a D:M:S or a D°M'S" string. """
    return dms_to_string(dec_to_dms(dec, round_to), format, round_to, pad_rounded)


def string_to_dec(string: str) -> float:
    """ Takes any string format output by dms_to_string() and returns
    a decimal float. """
    digits = re.findall(r'[0-9\.-]+', string)
    char = string[len(digits[0])].upper()
    floats = [float(v) for v in digits]
    return dms_to_dec(['-' if char in 'SW' or floats[0] < 0 else '+', *floats])


def to_dec(value: float | list | tuple | str) -> float:
    """ If the input type is unknown, this will guess and convert. """
    if isinstance(value, float):
        return value
    if isinstance(value, (list, tuple)):
        return dms_to_dec(value)
    if isinstance(value, str):
        if _is_numeric(value):
            return float(value)
        else:
            return string_to_dec(value)
    return None


def to_dms(value: float | list | tuple | str, round_to: tuple = ROUND_SECOND, pad_rounded = False) -> tuple:
    """ If the input type is unknown, this will guess and convert. """
    if isinstance(value, float):
        return dec_to_dms(value, round_to, pad_rounded)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    if isinstance(value, str):
        if _is_numeric(value):
            return dec_to_dms(float(value), round_to, pad_rounded)
        else:
            return string_to_dms(value, round_to, pad_rounded)
    return None


def to_string(value: float | list | tuple | str, format: int = FORMAT_DMS, round_to: tuple = ROUND_SECOND, pad_rounded = None) -> str:
    """ If the input type is unknown, this will guess and convert. """
    if isinstance(value, float):
        return dec_to_string(value, format, round_to, pad_rounded)
    if isinstance(value, (list, tuple)):
        return dms_to_string(value, format, round_to, pad_rounded)
    if isinstance(value, str):
        if _is_numeric(value):
            return dec_to_string(float(value), format, round_to, pad_rounded)
        else:
            return dec_to_string(string_to_dec(value), format, round_to, pad_rounded)
    return None


def _dms_to_string_format_dms(dms: list | tuple) -> str:
    """ Returns DMS in degree/minute/second format. """
    symbols = (u'\N{DEGREE SIGN}', "'", '"')
    string = ''.join([f'{v:02d}' + symbols[k] for k, v in enumerate(dms[1:])])
    return '-' + string if dms[0] == '-' else string


def _dms_to_string_format_time(dms: list | tuple) -> str:
    """ Returns DMS in hour:minute:second format. """
    string = ':'.join([f'{v:02d}' for v in dms[1:]])
    return '-' + string if dms[0] == '-' else string


def _dms_to_string_format_time_offset(dms: list | tuple) -> str:
    """ Returns DMS in signed hour:minute:second format. """
    return dms[0] + ':'.join([f'{v:02d}' for v in dms[1:]])


def _dms_to_string_format_lat(dms: list | tuple) -> str:
    """ Returns DMS in degree/direction/minute format. """
    dir = 'S' if dms[0] == '-' else 'N'
    return _dms_to_string_format_lat_lon(dms, dir)


def _dms_to_string_format_lon(dms: list | tuple) -> str:
    """ Returns DMS in degree/direction/minute format. """
    dir = 'W' if dms[0] == '-' else 'E'
    return _dms_to_string_format_lat_lon(dms, dir)


def _dms_to_string_format_lat_lon(dms: list | tuple, dir: str) -> str:
    """ Returns DMS in degree/direction/minute format. """
    minutes = dms[2] + math.ceil(((dms[3]/60)*100))/100
    return f'{dms[1]}{dir}{minutes}'


def _is_numeric(value: str) -> bool:
    """ Determine whether a string is numeric. """
    return re.match(r'^-?\d+(?:\.\d+)?$', value)
