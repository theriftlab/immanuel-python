"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Strings for datetime format translations, so that we can avoid
OS-level locale dependencies.

"""

WEEKDAY_CONTEXT = "weekday"
MONTH_CONTEXT = "month"

WEEKDAYS = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

MONTHS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

DATE_TIME_FORMAT = "{weekday} {month} {day} {year} {time} {timezone}"
