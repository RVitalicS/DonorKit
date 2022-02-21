#!/usr/bin/env python



import os, re
import sys, json
import time, datetime

from Qt import QtGui



RESERVED_TAGS = [
    "Proxy",
    "RenderMan" ]







def dataread (path):

    with open(path, "r") as file:
        return json.load(file)


def datawrite (path, data):

    with open(path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def validJSON (path):

    try: 
        data = dataread(path)
        if not data:
            return False
    except:
        return False
    
    return True






def getStringWidth (string, font):

    '''
        Calculates  string width in pixels
        for the specific font

        :type  string: str
        :param string: name to find out width

        :type    font: QFont
        :param   font: font for calculation

        :rtype : int
        :return: width in pixels
    '''


    # scale font for accuracy
    scale = 1000
    font = QtGui.QFont(font)
    font.setPointSize(
        font.pointSize() * scale )

    metrics = QtGui.QFontMetrics(font)

    # get width and scale back
    width = metrics.horizontalAdvance(string)
    width = int(round(width/scale))

    return width






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






def isFinalVersion (path, name):

    for item in os.listdir(path):
        if re.search(r"\.Final", item):

            itempath = os.path.join(path, item)
            realpath = os.path.realpath(itempath)
            linkedname = os.path.basename(realpath)

            if name == linkedname:
                return True






def getVariantName (name):

    variantTag = re.search(r"\.v\d+-*[A-Za-z]*\.", name)
    if not variantTag:
        variantTag = re.search(r"\.Final-*[A-Za-z]*\.", name)

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

        if animationName != "Final":
            return animationName

    return ""






def getAssetName (name):

    assetTag = re.search(r"^[A-Z_a-z]+\.", name)
    if assetTag:
        assetName = assetTag.group()

        if assetName not in RESERVED_TAGS:

            assetName = re.sub(r"\.", "", assetName)
            return assetName

    return ""






def getAnimationList (path, version=None):

    animationList = []

    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]*$", name):

                if version:
                    if version != getVersion(name):
                        continue

                animation = getAnimationName(name)
                if not animation:
                    continue

                if animation in animationList:
                    continue
                
                animationList.append(animation)

    return animationList






def getVariantList (path, version=None):

    variantList = []

    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]*$", name):

                if version:
                    if version != getVersion(name):
                        continue

                variant = getVariantName(name)
                if not variant:
                    continue

                if variant in variantList:
                    continue
                
                variantList.append(variant)

    return variantList






def getVersionList (path):

    versionList = []

    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]*$", name):

                version = getVersion(name)
                if not version:
                    continue

                if version in versionList:
                    continue
                
                versionList.append(version)

    return versionList






def getUsdPreviews (root, name):

    previews = []
    basename = re.sub(r"\.usd[ac]*$", "", name)

    path = os.path.join(root, "previews")
    if not os.path.exists(path):
        return previews

    for item in os.listdir(path):
        if re.search(r"^"+basename, item):

            if re.search(r"\.png$", item):
                previews.append(
                    os.path.join(path, item) )


    def sorter (path):

        match = re.search( r"\.f\d*\.", 
            os.path.basename(path) )

        if match:
            tag = re.sub(r"\.", "", match.group())
            return float(re.sub(r"f", "", tag))

        return float()


    previews.sort(key=sorter)
    return previews






def chooseAssetItem (path):

    '''
        Chooses one version of asset items
        to use it for preview
    '''


    chosenItem  = str()


    # iterate over versioned "usd" files only
    for assetItem in os.listdir(path):

        if re.search(r"\.Final\.", assetItem):
            continue
        if re.search(r"\.usd[ac]*$", assetItem):

            if not chosenItem:
                chosenItem  = assetItem


            # get data to compare current iteration item
            # with previously chosen one
            chosenHasPreivews = getUsdPreviews(path, chosenItem)
            chosenIsFinal  = isFinalVersion(path, chosenItem)
            chosenVersion  = getVersion(chosenItem)

            assetHasPreivews = getUsdPreviews(path, assetItem)
            assetIsFinal  = isFinalVersion(path, assetItem)
            assetVersion  = getVersion(assetItem)

            noPreivews = not chosenHasPreivews and not assetHasPreivews
            bothHasPreivews = chosenHasPreivews and assetHasPreivews


            # first of all choose that one with previews
            if not chosenHasPreivews and assetHasPreivews:
                chosenItem = assetItem
            
            # then that one that is final version
            elif noPreivews or bothHasPreivews:
                if assetIsFinal:
                    chosenItem = assetItem

                # then depending on higher version
                elif assetVersion > chosenVersion:
                    if not chosenIsFinal:
                        chosenItem = assetItem


    return chosenItem






def getItemsCount (path):

    count = int()

    for item in os.listdir(path):
        if re.match(r"^\..+", item):
            continue
        count += 1

    return count






def createAssetName (
        name, version,
        variant=None,
        animation=None,
        final=False,
        extension="usda" ):
    

    assetName = [name]

    version = "v{:02d}".format(version)
    if final:
        version = "Final"
    if variant:
        version = "{}-{}".format(version, variant)
    assetName.append(version)

    if animation:
        assetName.append(animation)

    assetName.append(extension)


    return ".".join(assetName)
