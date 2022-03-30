#!/usr/bin/env python



import time, datetime






def getTimeCode ():

    return time.strftime(
        "%d.%m.%Y %H.%M" ,
        time.localtime() )






def getTimeDifference (timeString):

    timeSplit = timeString.split(" ")

    datePart = timeSplit[0]
    timePart = timeSplit[1]

    dateList = datePart.split(".")
    timeList = timePart.split(".")

    timeSplit = dateList + timeList
    timeSplit = [int(i) for i in timeSplit]


    dayPublished   = timeSplit[0]
    monthPublished = timeSplit[1]
    yearPublished  = timeSplit[2]
    hourPublished   = timeSplit[3]
    minutePublished = timeSplit[4]

    dayCurrent    = time.strftime("%d", time.localtime() )
    monthCurrent  = time.strftime("%m", time.localtime() )
    yearCurrent   = time.strftime("%Y", time.localtime() )
    hourCurrent   = time.strftime("%H", time.localtime() )
    minuteCurrent = time.strftime("%M", time.localtime() )


    timeCurrent = datetime.datetime(
        int(yearCurrent), 
        int(monthCurrent),
        int(dayCurrent),
        hour=int(hourCurrent),
        minute=int(minuteCurrent))

    timePublished = datetime.datetime(
        yearPublished,
        monthPublished,
        dayPublished,
        hour=hourPublished,
        minute=minutePublished)


    timeDelta = timeCurrent-timePublished

    days    = timeDelta.days
    seconds = timeDelta.seconds

    years  = int( days/365 )
    months = int( days/30 )

    hours   = int( seconds/3600 )
    minutes = int( seconds/60 )


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