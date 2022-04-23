#!/usr/bin/env python



import os
import re






def nameFilter (text):

    text = re.sub(
        r"[^A-Za-z0-9_-]",
        "", text )

    return text






def isFinalVersion (path, name):

    for item in os.listdir(path):
        if re.search(r"\.Final[-\.]{1}", item):

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

    animationTag = re.search(r"\.[-_A-Za-z]+\.usd", name)
    if animationTag:
        animationName = animationTag.group()

        animationName = re.sub(r"\.usd", "", animationName)
        animationName = re.sub(r"\.", "", animationName)

        if animationName != "Final":
            return animationName

    return ""






def getAssetName (name):

    assetTag = re.search(r"^[-_A-Za-z]+\.", name)
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
    prman = []
    hydra = []

    basename = re.sub(r"\.usd[ac]*$", "", name)

    extension = r"\.png$"

    path = os.path.join(root, "previews", basename)
    if not os.path.exists(path):
        return previews

    for item in os.listdir(path):
        if re.search(extension, item):
            frame = os.path.join(path, item)

            if re.search(r"^Prman.*", item):
                prman.append(frame)

            elif re.search(r"^Hydra.*", item):
                hydra.append(frame)
    
    if prman:
        previews = prman
    else:
        previews = hydra


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

    """
        Chooses one version of asset items
        to use it for preview
    """


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
            chosenHasPreviews = getUsdPreviews(path, chosenItem)
            chosenIsFinal  = isFinalVersion(path, chosenItem)
            chosenVersion  = getVersion(chosenItem)

            assetHasPreviews = getUsdPreviews(path, assetItem)
            assetIsFinal  = isFinalVersion(path, assetItem)
            assetVersion  = getVersion(assetItem)

            noPreviews = not chosenHasPreviews and not assetHasPreviews
            bothHasPreviews = chosenHasPreviews and assetHasPreviews


            # first choose that one with previews
            if not chosenHasPreviews and assetHasPreviews:
                chosenItem = assetItem
            
            # then that one that is final version
            elif noPreviews or bothHasPreviews:
                if assetIsFinal:
                    chosenItem = assetItem

                # then depending on higher version
                elif assetVersion > chosenVersion:
                    if not chosenIsFinal:
                        chosenItem = assetItem


    return chosenItem






def createAssetName (
        name, version,
        variant=None,
        animation=None,
        final=False,
        extension="usda" ):
    

    assetName = [name]

    version = "v{:02d}".format(version)
    if variant:
        version = "{}-{}".format(version, variant)
    assetName.append(version)

    if animation:
        assetName.append(animation)

    assetName.append(extension)

    assetName = ".".join(assetName)

    if final:
        assetName = makeFinal(assetName)

    return assetName









def makeFinal (name):

    name = re.sub(r"\.v\d+\.", ".Final.", name)
    name = re.sub(r"\.v\d+-" , ".Final-", name)

    return name
