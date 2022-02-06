#!/bin/python


import os, re
import sys, json
import time, datetime







def dataread (path):

    with open(path, "r") as file:
        return json.load(file)


def datawrite (path, data):

    with open(path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)






def keydata (dictionary, keyname):

    for key, value in dictionary.items():
        
        if key == keyname:
            return value






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

    years  = int(round( days/365 ))
    months = int(round( days/30 ))

    hours   = int(round( seconds/3600 ))
    minutes = int(round( seconds/60 ))


    if years == 1:
        return "1 year ago"
    elif years > 1:
        return "{} years ago".format(years)

    if months == 1:
        return "1 month ago"
    elif months > 1:
        return "{} months ago".format(months)

    if days == 1:
        return "1 day ago"
    elif days > 1:
        return "{} days ago".format(days)

    if hours == 1:
        return "1 hour ago"
    elif hours > 1:
        return "{} hours ago".format(hours)

    if minutes == 1:
        return "1 minute ago"
    elif minutes > 1:
        return "{} minutes ago".format(minutes)

    return "a moment ago"






def isFinalVersion (path, name):

    for item in os.listdir(path):
        if re.search(r"\.final\.", item):

            itempath = os.path.join(path, item)
            realpath = os.path.realpath(itempath)
            linkedname = os.path.basename(realpath)

            if name == linkedname:
                return True






def getVariantName (name):

    variantTag = re.search(r"\.v\d+-*[A-Za-z]*\.", name)
    if variantTag:
        variantTag = variantTag.group()

        variantCut = re.search(r"-[A-Za-z]*\.", variantTag)
        if variantCut:
            variantName = variantCut.group()
            variantName = re.sub(r"-", "", variantName)
            variantName = re.sub(r"\.", "", variantName)

            return variantName

    return ""






def getVersion (name):

    versionTag = re.search(r"\.v\d+-*[A-Za-z]*\.", name)
    if versionTag:
        versionTag = versionTag.group()

        versionCut = re.search(r"\.v\d+-*", versionTag)
        if versionCut:
            versionString = versionCut.group()
            versionString = re.sub(r"\.", "", versionString)
            versionString = re.sub(r"v", "", versionString)
            versionString = re.sub(r"-", "", versionString)

            return int(versionString)

    return int()






def getAnimationName (name):

    animationTag = re.search(r"\.[A-Z_a-z]+\.usd", name)
    if animationTag:
        animationName = animationTag.group()

        animationName = re.sub(r"\.usd", "", animationName)
        animationName = re.sub(r"\.", "", animationName)

        if animationName != "final":
            return animationName

    return ""






def getAssetName (name):

    assetTag = re.search(r"^[A-Z_a-z]+\.", name)
    if assetTag:
        assetName = assetTag.group()

        assetName = re.sub(r"\.", "", assetName)
        return assetName

    return ""






def getUsdPreview (root, name):

    basename = re.sub( r"\.usd[ac]*$", "", name)

    path = os.path.join(root, "previews")
    for item in os.listdir(path):
        if re.search(r"^"+basename, item):

            return os.path.join(path, basename)

    return str()






def getUsdLeadItem (path):

    assetItem  = str()
    maxVersion = int()

    for item in os.listdir(path):
        if re.search(r"\.final\.", item):
            continue
        if re.search(r"\.usd[ac]*$", item):

            animation = getAnimationName(item)
            if not animation:

                if isFinalVersion(path, item):
                    assetItem = item
                    break

                itemVersion = getVersion(item)
                if maxVersion < itemVersion:
                    maxVersion = itemVersion
                    assetItem  = item

    return assetItem






def getItemsCount (path):

    count = int()

    for item in os.listdir(path):
        if re.match(r"^\..+", item):
            continue
        count += 1

    return count
