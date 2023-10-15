"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    DMS / decimal tests ran against figures from:
    https://www.rapidtables.com/convert/number/degrees-minutes-seconds-to-degrees.html

"""

from immanuel.tools import convert


""" dms_to_dec() """
def test_dms_to_dec():
    assert convert.dms_to_dec(('+', 12, 30, 45)) == 12.5125
    assert convert.dms_to_dec(('+', 12, 30.75)) == 12.5125
    assert convert.dms_to_dec(('-', 12, 30, 45)) == -12.5125
    assert convert.dms_to_dec(('-', 12, 30.75)) == -12.5125


""" dec_to_dms() """
def test_dec_to_dms_round_degree():
    assert convert.dec_to_dms(12.5125, convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.dec_to_dms(12.5125, convert.ROUND_DEGREE, False) == ('+', 13)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_DEGREE, False) == ('-', 13)


def test_dec_to_dms_round_minute():
    assert convert.dec_to_dms(12.5125, convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.dec_to_dms(12.5125, convert.ROUND_MINUTE, False) == ('+', 12, 31)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_MINUTE, True) == ('-', 12, 31, 0)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_MINUTE, False) == ('-', 12, 31)


def test_dec_to_dms_round_second():
    assert convert.dec_to_dms(12.5125, convert.ROUND_SECOND, True) == ('+', 12, 30, 45)
    assert convert.dec_to_dms(12.5125, convert.ROUND_SECOND, False) == ('+', 12, 30, 45)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_SECOND, True) == ('-', 12, 30, 45)
    assert convert.dec_to_dms(-12.5125, convert.ROUND_SECOND, False) == ('-', 12, 30, 45)


""" dms_to_string() """
def test_dms_to_string_time_round_degree():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME, convert.ROUND_DEGREE) == '13:00:00'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME, convert.ROUND_DEGREE) == '13:00:00'


def test_dms_to_string_time_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME, convert.ROUND_MINUTE) == '12:31:00'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME, convert.ROUND_MINUTE) == '12:31:00'


def test_dms_to_string_time_round_second():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME, convert.ROUND_SECOND) == '12:30:45'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME, convert.ROUND_SECOND) == '12:30:45'


def test_dms_to_string_time_offset_round_degree():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '+13:00:00'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '+13:00:00'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '-13:00:00'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '-13:00:00'


def test_dms_to_string_time_offset_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '+12:31:00'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '+12:31:00'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '-12:31:00'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '-12:31:00'


def test_dms_to_string_time_offset_round_second():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '+12:30:45'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '+12:30:45'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '-12:30:45'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '-12:30:45'


def test_dms_to_string_dms_round_degree():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_DEGREE) == '13°'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_DEGREE) == '13°'
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '13°00\'00"'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '13°00\'00"'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_DEGREE) == '-13°'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_DEGREE) == '-13°'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '-13°00\'00"'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '-13°00\'00"'


def test_dms_to_string_dms_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_MINUTE) == '12°31\''
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_MINUTE) == '12°31\''
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '12°31\'00"'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '12°31\'00"'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_MINUTE) == '-12°31\''
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_MINUTE) == '-12°31\''
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '-12°31\'00"'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '-12°31\'00"'


def test_dms_to_string_dms_round_second():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_SECOND) == '12°30\'45"'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_SECOND) == '12°30\'45"'
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '12°30\'45"'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '12°30\'45"'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_SECOND) == '-12°30\'45"'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_SECOND) == '-12°30\'45"'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '-12°30\'45"'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '-12°30\'45"'


def test_dms_to_string_lat_round_degree():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13N0.0'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13N0.0'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13S0.0'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13S0.0'


def test_dms_to_string_lat_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12N31.0'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12N31.0'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12S31.0'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12S31.0'


def test_dms_to_string_lat_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_SECOND) == '12N30.75'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_SECOND) == '12N30.75'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LAT, convert.ROUND_SECOND) == '12S30.75'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LAT, convert.ROUND_SECOND) == '12S30.75'


def test_dms_to_string_lon_round_degree():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_DEGREE) == '13E0.0'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LON, convert.ROUND_DEGREE) == '13E0.0'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_DEGREE) == '13W0.0'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LON, convert.ROUND_DEGREE) == '13W0.0'


def test_dms_to_string_lon_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_MINUTE) == '12E31.0'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LON, convert.ROUND_MINUTE) == '12E31.0'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_MINUTE) == '12W31.0'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LON, convert.ROUND_MINUTE) == '12W31.0'


def test_dms_to_string_lon_round_minute():
    assert convert.dms_to_string(('+', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_SECOND) == '12E30.75'
    assert convert.dms_to_string(('+', 12, 30.75), convert.FORMAT_LON, convert.ROUND_SECOND) == '12E30.75'
    assert convert.dms_to_string(('-', 12, 30, 45), convert.FORMAT_LON, convert.ROUND_SECOND) == '12W30.75'
    assert convert.dms_to_string(('-', 12, 30.75), convert.FORMAT_LON, convert.ROUND_SECOND) == '12W30.75'


""" string_to_dms() """
def test_string_to_dms_time_rounded_degree():
    assert convert.string_to_dms('12:30:45', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12:30', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12:30:45', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12:30', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)


def test_string_to_dms_time_rounded_minute():
    assert convert.string_to_dms('12:30:45', convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.string_to_dms('12:30', convert.ROUND_MINUTE) == ('+', 12, 30)
    assert convert.string_to_dms('12:30:45', convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.string_to_dms('12:30', convert.ROUND_MINUTE, True) == ('+', 12, 30, 0)


def test_string_to_dms_time_rounded_second():
    assert convert.string_to_dms('12:30:45', convert.ROUND_SECOND) == ('+', 12, 30, 45)
    assert convert.string_to_dms('12:30:45', convert.ROUND_SECOND, True) == ('+', 12, 30, 45)


def test_string_to_dms_time_offset_rounded_degree():
    assert convert.string_to_dms('+12:30:45', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('+12:30:45', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('+12:30', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('+12:30', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)
    assert convert.string_to_dms('-12:30', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('-12:30', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)


def test_string_to_dms_time_offset_rounded_minute():
    assert convert.string_to_dms('+12:30:45', convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.string_to_dms('+12:30:45', convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.string_to_dms('+12:30', convert.ROUND_MINUTE) == ('+', 12, 30)
    assert convert.string_to_dms('+12:30', convert.ROUND_MINUTE, True) == ('+', 12, 30, 0)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_MINUTE) == ('-', 12, 31)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_MINUTE, True) == ('-', 12, 31, 0)
    assert convert.string_to_dms('-12:30', convert.ROUND_MINUTE) == ('-', 12, 30)
    assert convert.string_to_dms('-12:30', convert.ROUND_MINUTE, True) == ('-', 12, 30, 0)


def test_string_to_dms_time_offset_rounded_second():
    assert convert.string_to_dms('+12:30:45', convert.ROUND_SECOND) == ('+', 12, 30, 45)
    assert convert.string_to_dms('+12:30:45', convert.ROUND_SECOND, True) == ('+', 12, 30, 45)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_SECOND) == ('-', 12, 30, 45)
    assert convert.string_to_dms('-12:30:45', convert.ROUND_SECOND, True) == ('-', 12, 30, 45)


def test_string_to_dms_dms_rounded_degree():
    assert convert.string_to_dms('12°30\'45"', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12°30\'45"', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12°30\'', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12°30\'', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)
    assert convert.string_to_dms('-12°30\'', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('-12°30\'', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)


def test_string_to_dms_dms_rounded_minute():
    assert convert.string_to_dms('12°30\'45"', convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.string_to_dms('12°30\'45"', convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.string_to_dms('12°30\'', convert.ROUND_MINUTE) == ('+', 12, 30)
    assert convert.string_to_dms('12°30\'', convert.ROUND_MINUTE, True) == ('+', 12, 30, 0)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_MINUTE) == ('-', 12, 31)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_MINUTE, True) == ('-', 12, 31, 0)
    assert convert.string_to_dms('-12°30\'', convert.ROUND_MINUTE) == ('-', 12, 30)
    assert convert.string_to_dms('-12°30\'', convert.ROUND_MINUTE, True) == ('-', 12, 30, 0)


def test_string_to_dms_dms_rounded_second():
    assert convert.string_to_dms('+12°30\'45"', convert.ROUND_SECOND) == ('+', 12, 30, 45)
    assert convert.string_to_dms('+12°30\'45"', convert.ROUND_SECOND, True) == ('+', 12, 30, 45)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_SECOND) == ('-', 12, 30, 45)
    assert convert.string_to_dms('-12°30\'45"', convert.ROUND_SECOND, True) == ('-', 12, 30, 45)


def test_string_to_dms_lat_rounded_degree():
    assert convert.string_to_dms('12N30.75', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12N30.75', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12N30', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12N30', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12S30.75', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('12S30.75', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)
    assert convert.string_to_dms('12S30', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('12S30', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)


def test_string_to_dms_lat_rounded_minute():
    assert convert.string_to_dms('12N30.75', convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.string_to_dms('12N30.75', convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.string_to_dms('12N30', convert.ROUND_MINUTE) == ('+', 12, 30)
    assert convert.string_to_dms('12N30', convert.ROUND_MINUTE, True) == ('+', 12, 30, 0)
    assert convert.string_to_dms('12S30.75', convert.ROUND_MINUTE) == ('-', 12, 31)
    assert convert.string_to_dms('12S30.75', convert.ROUND_MINUTE, True) == ('-', 12, 31, 0)
    assert convert.string_to_dms('12S30', convert.ROUND_MINUTE) == ('-', 12, 30)
    assert convert.string_to_dms('12S30', convert.ROUND_MINUTE, True) == ('-', 12, 30, 0)


def test_string_to_dms_lat_rounded_second():
    assert convert.string_to_dms('12N30.75', convert.ROUND_SECOND) == ('+', 12, 30, 45)
    assert convert.string_to_dms('12N30.75', convert.ROUND_SECOND, True) == ('+', 12, 30, 45)
    assert convert.string_to_dms('12S30.75', convert.ROUND_SECOND) == ('-', 12, 30, 45)
    assert convert.string_to_dms('12S30.75', convert.ROUND_SECOND, True) == ('-', 12, 30, 45)


def test_string_to_dms_lon_rounded_degree():
    assert convert.string_to_dms('12E30.75', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12E30.75', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12E30', convert.ROUND_DEGREE) == ('+', 13)
    assert convert.string_to_dms('12E30', convert.ROUND_DEGREE, True) == ('+', 13, 0, 0)
    assert convert.string_to_dms('12W30.75', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('12W30.75', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)
    assert convert.string_to_dms('12W30', convert.ROUND_DEGREE) == ('-', 13)
    assert convert.string_to_dms('12W30', convert.ROUND_DEGREE, True) == ('-', 13, 0, 0)


def test_string_to_dms_lon_rounded_minute():
    assert convert.string_to_dms('12E30.75', convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.string_to_dms('12E30.75', convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)
    assert convert.string_to_dms('12E30', convert.ROUND_MINUTE) == ('+', 12, 30)
    assert convert.string_to_dms('12E30', convert.ROUND_MINUTE, True) == ('+', 12, 30, 0)
    assert convert.string_to_dms('12W30.75', convert.ROUND_MINUTE) == ('-', 12, 31)
    assert convert.string_to_dms('12W30.75', convert.ROUND_MINUTE, True) == ('-', 12, 31, 0)
    assert convert.string_to_dms('12W30', convert.ROUND_MINUTE) == ('-', 12, 30)
    assert convert.string_to_dms('12W30', convert.ROUND_MINUTE, True) == ('-', 12, 30, 0)


def test_string_to_dms_lon_rounded_second():
    assert convert.string_to_dms('12E30.75', convert.ROUND_SECOND) == ('+', 12, 30, 45)
    assert convert.string_to_dms('12E30.75', convert.ROUND_SECOND, True) == ('+', 12, 30, 45)
    assert convert.string_to_dms('12W30.75', convert.ROUND_SECOND) == ('-', 12, 30, 45)
    assert convert.string_to_dms('12W30.75', convert.ROUND_SECOND, True) == ('-', 12, 30, 45)


""" dec_to_string() """
def test_dec_to_string_time_round_degree():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME, convert.ROUND_DEGREE) == '13:00:00'
    assert convert.dec_to_string(12.5, convert.FORMAT_TIME, convert.ROUND_DEGREE) == '13:00:00'
    assert convert.dec_to_string(12, convert.FORMAT_TIME, convert.ROUND_DEGREE) == '12:00:00'


def test_dec_to_string_time_round_minute():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME, convert.ROUND_MINUTE) == '12:31:00'
    assert convert.dec_to_string(12.5, convert.FORMAT_TIME, convert.ROUND_MINUTE) == '12:30:00'
    assert convert.dec_to_string(12, convert.FORMAT_TIME, convert.ROUND_MINUTE) == '12:00:00'


def test_dec_to_string_time_round_second():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME, convert.ROUND_SECOND) == '12:30:45'
    assert convert.dec_to_string(12.5, convert.FORMAT_TIME, convert.ROUND_SECOND) == '12:30:00'
    assert convert.dec_to_string(12, convert.FORMAT_TIME, convert.ROUND_SECOND) == '12:00:00'


def test_dec_to_string_time_offset_round_degree():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '+13:00:00'
    assert convert.dec_to_string(12.5, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '+13:00:00'
    assert convert.dec_to_string(12, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '+12:00:00'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '-13:00:00'
    assert convert.dec_to_string(-12.5, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '-13:00:00'
    assert convert.dec_to_string(-12, convert.FORMAT_TIME_OFFSET, convert.ROUND_DEGREE) == '-12:00:00'


def test_dec_to_string_time_offset_round_minute():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '+12:31:00'
    assert convert.dec_to_string(12.5, convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '+12:30:00'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '-12:31:00'
    assert convert.dec_to_string(-12.5, convert.FORMAT_TIME_OFFSET, convert.ROUND_MINUTE) == '-12:30:00'


def test_dec_to_string_time_offset_round_second():
    assert convert.dec_to_string(12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '+12:30:45'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_TIME_OFFSET, convert.ROUND_SECOND) == '-12:30:45'


def test_dec_to_string_dms_round_degree():
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '13°'
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '13°'
    assert convert.dec_to_string(12, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '12°'
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '13°00\'00"'
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '13°00\'00"'
    assert convert.dec_to_string(12, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '12°00\'00"'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '-13°'
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '-13°'
    assert convert.dec_to_string(-12, convert.FORMAT_DMS, convert.ROUND_DEGREE) == '-12°'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '-13°00\'00"'
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '-13°00\'00"'
    assert convert.dec_to_string(-12, convert.FORMAT_DMS, convert.ROUND_DEGREE, True) == '-12°00\'00"'


def test_dec_to_string_dms_round_minute():
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE) == '12°31\''
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_MINUTE) == '12°30\''
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '12°31\'00"'
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '12°30\'00"'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE) == '-12°31\''
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_MINUTE) == '-12°30\''
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '-12°31\'00"'
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '-12°30\'00"'


def test_dec_to_string_dms_round_second():
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_SECOND) == '12°30\'45"'
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_SECOND) == '12°30\'00"'
    assert convert.dec_to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '12°30\'45"'
    assert convert.dec_to_string(12.5, convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '12°30\'00"'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_SECOND) == '-12°30\'45"'
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_SECOND) == '-12°30\'00"'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '-12°30\'45"'
    assert convert.dec_to_string(-12.5, convert.FORMAT_DMS, convert.ROUND_SECOND, True) == '-12°30\'00"'


def test_dec_to_string_lat_round_degree():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13N0.0'
    assert convert.dec_to_string(12.5, convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13N0.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13S0.0'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LAT, convert.ROUND_DEGREE) == '13S0.0'


def test_dec_to_string_lat_round_minute():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12N31.0'
    assert convert.dec_to_string(12.5, convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12N30.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12S31.0'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LAT, convert.ROUND_MINUTE) == '12S30.0'


def test_dec_to_string_lat_round_second():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LAT, convert.ROUND_SECOND) == '12N30.75'
    assert convert.dec_to_string(12.5, convert.FORMAT_LAT, convert.ROUND_SECOND) == '12N30.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LAT, convert.ROUND_SECOND) == '12S30.75'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LAT, convert.ROUND_SECOND) == '12S30.0'


def test_dec_to_string_lon_round_degree():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LON, convert.ROUND_DEGREE) == '13E0.0'
    assert convert.dec_to_string(12.5, convert.FORMAT_LON, convert.ROUND_DEGREE) == '13E0.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LON, convert.ROUND_DEGREE) == '13W0.0'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LON, convert.ROUND_DEGREE) == '13W0.0'


def test_dec_to_string_lon_round_minute():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LON, convert.ROUND_MINUTE) == '12E31.0'
    assert convert.dec_to_string(12.5, convert.FORMAT_LON, convert.ROUND_MINUTE) == '12E30.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LON, convert.ROUND_MINUTE) == '12W31.0'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LON, convert.ROUND_MINUTE) == '12W30.0'


def test_dec_to_string_lon_round_second():
    assert convert.dec_to_string(12.5125, convert.FORMAT_LON, convert.ROUND_SECOND) == '12E30.75'
    assert convert.dec_to_string(12.5, convert.FORMAT_LON, convert.ROUND_SECOND) == '12E30.0'
    assert convert.dec_to_string(-12.5125, convert.FORMAT_LON, convert.ROUND_SECOND) == '12W30.75'
    assert convert.dec_to_string(-12.5, convert.FORMAT_LON, convert.ROUND_SECOND) == '12W30.0'


""" string_to_dec() """
def test_string_to_dec_time():
    assert convert.string_to_dec('12:30:45') == 12.5125


def test_string_to_dec_time_offset():
    assert convert.string_to_dec('+12:30:45') == 12.5125
    assert convert.string_to_dec('-12:30:45') == -12.5125


def test_string_to_dec_dms():
    assert convert.string_to_dec('12°30\'45"') == 12.5125
    assert convert.string_to_dec('-12°30\'45"') == -12.5125


def test_string_to_dec_lat():
    assert convert.string_to_dec('12N30.75') == 12.5125
    assert convert.string_to_dec('12S30.75') == -12.5125


def test_string_to_dec_lon():
    assert convert.string_to_dec('12E30.75') == 12.5125
    assert convert.string_to_dec('12W30.75') == -12.5125


""" To save another few hundred tests the to_() functions are tested
to ensure they parse the input correctly and the accuracy of their
outputs is assumed to have already been covered by the above tests. """

def test_to_dec():
    assert convert.to_dec(12.5125) == 12.5125
    assert convert.to_dec(('+', 12, 30, 45)) == 12.5125
    assert convert.to_dec(['+', 12, 30, 45]) == 12.5125
    assert convert.to_dec('12.5125') == 12.5125
    assert convert.to_dec('12E30.75') == 12.5125

def test_to_dms():
    assert convert.to_dms(12.5125) == ('+', 12, 30, 45)
    assert convert.to_dms(('+', 12, 30, 45)) == ('+', 12, 30, 45)
    assert convert.to_dms(['+', 12, 30, 45]) == ('+', 12, 30, 45)
    assert convert.to_dms('12.5125') == ('+', 12, 30, 45)
    assert convert.to_dms('12E30.75') == ('+', 12, 30, 45)
    # Quick tests to ensure it respects args
    assert convert.to_dms(12.5125, convert.ROUND_MINUTE) == ('+', 12, 31)
    assert convert.to_dms(12.5125, convert.ROUND_MINUTE, True) == ('+', 12, 31, 0)

def test_to_string():
    assert convert.to_string(12.5125) == '12°30\'45"'
    assert convert.to_string(('+', 12, 30, 45)) == '12°30\'45"'
    assert convert.to_string(['+', 12, 30, 45]) == '12°30\'45"'
    assert convert.to_string('12.5125') == '12°30\'45"'
    assert convert.to_string('12E30.75') == '12°30\'45"'
    # Quick tests to ensure it respects args
    assert convert.to_string(12.5125, convert.FORMAT_LAT) == '12N30.75'
    assert convert.to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE) == '12°31\''
    assert convert.to_string(12.5125, convert.FORMAT_DMS, convert.ROUND_MINUTE, True) == '12°31\'00"'
