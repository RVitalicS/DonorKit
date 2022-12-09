#!/usr/bin/env python

"""
Timing

This module hold utilities to work with time dependent data.
"""

import time
import datetime


def getTimeCode () -> str:
    """Create timestamp as formatted string

    Returns:
        Human-readable timestamp
    """
    return time.strftime(
        "%d.%m.%Y %H.%M" ,
        time.localtime())


def getTimeDelta (timeString: str) -> datetime.timedelta:
    """Get the difference between two dates or times

    Arguments:
        timeString: The timestamp string
    Returns:
        A duration expressing to microsecond resolution
    """
    timeSplit = timeString.split(" ")
    datePart = timeSplit[0]
    timePart = timeSplit[1]
    dateList = datePart.split(".")
    timeList = timePart.split(".")

    timeSplit = dateList + timeList
    dayPublished   = timeSplit[0]
    monthPublished = timeSplit[1]
    yearPublished  = timeSplit[2]
    hourPublished   = timeSplit[3]
    minutePublished = timeSplit[4]

    dayCurrent    = time.strftime("%d", time.localtime())
    monthCurrent  = time.strftime("%m", time.localtime())
    yearCurrent   = time.strftime("%Y", time.localtime())
    hourCurrent   = time.strftime("%H", time.localtime())
    minuteCurrent = time.strftime("%M", time.localtime())

    timeCurrent = datetime.datetime(
        int(yearCurrent), 
        int(monthCurrent),
        int(dayCurrent),
        hour=int(hourCurrent),
        minute=int(minuteCurrent))
    timePublished = datetime.datetime(
        int(yearPublished),
        int(monthPublished),
        int(dayPublished),
        hour=int(hourPublished),
        minute=int(minutePublished))
    return timeCurrent-timePublished


def getTimeDifference (timeString: str) -> str:
    """Get the difference between two dates or times

    Arguments:
        timeString: The timestamp string
    Returns:
        A duration expressing to formatted string
    """
    timeDelta = getTimeDelta(timeString)
    days    = timeDelta.days
    seconds = timeDelta.seconds
    years  = int(days/365)
    months = int(days/30)
    hours   = int(seconds/3600)
    minutes = int(seconds/60)

    if years == 1:
        return "1 year ago"
    elif years > 1:
        return "{} years ago".format(years)
    if 12 > months > 0:
        return "{} mon. ago".format(months)
    if days == 1:
        return "1 day ago"
    elif 30 > days > 1:
        return "{} days ago".format(days)
    if hours == 1:
        return "1 hour ago"
    elif 24 > hours > 1:
        return "{} hours ago".format(hours)
    if 60 > minutes > 0:
        return "{} min. ago".format(minutes)
    return "a sec. ago"


def isDayAgo (timeString: str) -> bool:
    """Check if duration between the timestamp
    and current time is longer than 24 hours

    Arguments:
        timeString: The timestamp string
    Returns:
        A result of the check
    """
    timeDelta = getTimeDelta(timeString)
    if timeDelta.days > 0:
        return True
    else:
        return False


def isAnimation (data: dict) -> bool:
    """To say the data is animated,
    check if values in the array are varying,
    otherwise it is static description

    Arguments:
        data: The array to annalise
    Returns:
        A result of the check
    """
    last = None
    for key, value in data.items():
        if value == last:
            continue
        elif last is None:
            last = value
            continue
        return True
    return False
