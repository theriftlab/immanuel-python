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
    dec = sum([float(v) / 60**k for k, v in enumerate(dms[1:])])
    return dec if dms[0] == '+' else -dec


def dec_to_dms(dec: float, round_to: tuple = ROUND_SECOND) -> tuple:
    """ Returns the rounded D:M:S conversion of a decimal float. """
    return ('-' if dec < 0 else '+', *swe.split_deg(dec, round_to[1])[:round_to[0]])


def dms_to_string(dms: list | tuple, format: int = FORMAT_DMS) -> str:
    """ Returns a D:M:S list as either a D:M:S, D°M'S" or
    coordinate string. """
    if format == FORMAT_DMS or format == FORMAT_TIME:
        if format == FORMAT_DMS:
            symbols = (u'\N{DEGREE SIGN}', "'", '"')
            string = ''.join([f'{v:02d}' + symbols[k] for k, v in enumerate(dms[1:])])
        elif format == FORMAT_TIME:
            string = ':'.join([f'{v:02d}' for v in dms[1:]])
        if dms[0] == '-':
            string = '-' + string
    elif format == FORMAT_TIME_OFFSET:
        string = dms[0] + ':'.join([f'{v:02d}' for v in dms[1:]])
    elif format == FORMAT_LAT or format == FORMAT_LON:
        if format == FORMAT_LAT:
            dir = 'S' if dms[0] == '-' else 'N'
        elif format == FORMAT_LON:
            dir = 'W' if dms[0] == '-' else 'E'
        minutes = dms[2] + math.ceil(((dms[3]/60)*100))/100
        string = f'{dms[1]}{dir}{minutes}'
    else:
        string = ''

    return string


def string_to_dms(string: str) -> tuple:
    """ Takes either a 12w34.56-type string, or a 12°34'56.78" / 12:34:56.78
    type string, and returns a DMS tuple. """
    digits = re.findall(r'[0-9\.-]+', string)
    floats = [float(v) for v in digits]
    char = string[len(digits[0])].upper()

    if char in 'NESW':
        return ('-' if char in 'SW' else '+', *floats)
    else:
        return ('-' if floats[0] < 0 else '+', abs(floats[0]), *floats[1:])


def dec_to_string(dec: float, format: int = FORMAT_DMS, round_to: tuple = ROUND_SECOND) -> str:
    """ Returns a decimal float as either a D:M:S or a D°M'S" string. """
    return dms_to_string(dec_to_dms(dec, round_to), format)


def string_to_dec(string: str) -> float:
    """ Takes any string supported by string_to_dms() and returns a
    decimal float. """
    try:
        return float(string)
    except ValueError:
        return dms_to_dec(string_to_dms(string))
