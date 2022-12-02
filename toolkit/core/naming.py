#!/usr/bin/env python

"""Functions to work with the asset name and its components."""

import os
import re
from toolkit.system import ostree    # FIXME: circular import
from widgets import Settings


def rule_Input (text: str) -> str:
    """Cuts the spaces and the all symbols,
    that are not the latin characters, the numbers,
    the underscore or the dash characters

    Arguments:
        text: The text to apply the rule
    Returns:
        The edited text
    """
    return re.sub(r"[^A-Za-z0-9_-]", "", text )


def rule_Material (name: str) -> str:
    """Use a regular expression from the settings
    to rename the material while exporting

    Arguments:
        name: The name of the material
    Returns:
        The edited name
    """
    with Settings.Manager(
            app="MaterialExport",
            update=False ) as settings:
        name = re.sub(
            settings["resub"][0],
            settings["resub"][1],
            str(name) )
    return name


def rule_Ignore (filename: str) -> bool:
    """A function used to skip the file names with reserved tags
    and to show ones with the 'usd' extension only

    Arguments:
        filename: The file name to apply the rule
    Returns:
        A result of conditions to skip the name
    """
    if not re.search(r"\.usd[ac]?$", filename):
        return True
    elif re.search(r"\.*(Final|Hydra|RenderMan)[.-]", filename):
        return True
    return False


def getVariantName (name: str) -> str:
    """Gets the variant name from the name of the asset's item

    Arguments:
        name: The name of the file
    Returns:
        The variant name
    """
    variantTag = re.search(r"\.*(v\d+|Final)-[A-Za-z]+\.", name)
    if variantTag:
        return re.sub(
            r"\.|(v\d+|Final)-", "", variantTag.group())
    return ""


def getVersion (name: str) -> int:
    """Gets the version number of the asset from the name of it's item

    Arguments:
        name: The name of the file
    Returns:
        The version number
    """
    versionTag = re.search(r"\.*v\d+-*[A-Za-z]*\.", name)
    if versionTag:
        versionString = re.sub(
            r"^\.*v|-*[A-Za-z]*\.*$", "", versionTag.group())
        return int(versionString)
    return int()


def getAnimationName (name: str) -> str:
    """Gets the animation name from the name of the asset's item

    Arguments:
        name: The name of the file
    Returns:
        The animation name
    """
    animationTag = re.search(r"\.[-_A-Za-z]+\.usd[ac]?$", name)
    if animationTag:
        animationName = re.sub(r"\.|usd[ac]?$", "", animationTag.group())
        if animationName not in ["Final", "Hydra", "RenderMan"]:
            return animationName
    return ""


def getAssetName (name: str) -> str:
    """Gets the name of the asset from the name of it's item

    Arguments:
        name: The name of the file
    Returns:
        The name of the asset
    """
    assetTag = re.search(r"^[-_A-Za-z]+\.", name)
    if assetTag:
        return re.sub(r"\.", "", assetTag.group())
    return ""


def getAnimationList (path: str, version: int) -> list:
    """Gets all animation names for the specified version of the asset

    Arguments:
        path: The root directory where the asset's items lie
        version: The version of the asset
    Returns:
        List of animation names for the asset version
    """
    animationList = []
    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]?$", name):
                if version != getVersion(name):
                    continue
                animation = getAnimationName(name)
                if not animation:
                    continue
                if animation in animationList:
                    continue
                animationList.append(animation)

    return sorted(animationList)


def getVariantList (path: str, version: int) -> list:
    """Gets all variant names for the specified version of the asset

    Arguments:
        path: The root directory where the asset's items lie
        version: The version of the asset
    Returns:
        List of variant names for the asset version
    """
    variantList = []
    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]?$", name):
                if version != getVersion(name):
                    continue
                variant = getVariantName(name)
                if not variant:
                    continue
                if variant in variantList:
                    continue
                variantList.append(variant)

    return sorted(variantList)


def getVersionList (path: str) -> list:
    """Gets all version numbers of the asset

    Arguments:
        path: The root directory where the asset's items lie
    Returns:
        List of integers that are versions of the asset
    """
    versionList = []
    if os.path.exists(path):
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]?$", name):
                version = getVersion(name)
                if not version:
                    continue
                if version in versionList:
                    continue
                versionList.append(version)

    return sorted(versionList)


def makeFinal (name: str) -> str: 
    """Replace the version of the asset with the 'Final' tag
    and make the file format extension without varying 'a|c' suffix
    to use a formatted name for a symbolic link

    Arguments:
        name: A name or a path of the usd file
    Returns:
        A formatted name
    """
    name = re.sub(r"v\d+", "Final", name)
    name = re.sub(r"\.usd[ac]$" , ".usd", name)

    return name


def createAssetName (
        name: str = None, version: int = 1,
        variant: str = None, animation: str = None,
        final: bool = False, extension: str = "usd" ) -> str:
    """
    Creates a name for a file that describe version of the asset

    Keyword Arguments:
        name:      The name of the asset
        version:   The version of the asset
        variant:   The variant name of the asset
        animation: The animation name of the asset
        final:     A flag used to create a name for symbolic link
        extension: The varying extension suffix of the asset
    Returns:
        A created name
    """
    assetName = [name] if name else []
    version = f"v{version:02d}"
    if variant:
        version = f"{version}-{variant}"
    assetName.append(version)
    if animation:
        assetName.append(animation)
    assetName.append(extension)
    assetName = ".".join(assetName)
    if final:
        assetName = makeFinal(assetName)

    return assetName


# TODO: it's not the right module for this function
def getUsdPreviews (root: str, name: str) -> list:
    """Find the preview files for the specified item of the asset

    Arguments:
        root: The root directory where the asset's items lie
        name: The name of the file
    Returns:
        A list of the sorted preview's paths
    """
    basename = re.sub(r"\.usd[ac]?$", "", name)
    extension = r"\.png$"
    path = os.path.join(root, "previews", basename)

    previews, prman, hydra = [], [], []
    if not os.path.exists(path):
        return previews

    for item in os.listdir(path):
        if re.search(extension, item):
            frame = os.path.join(path, item)
            if re.search(r"^Prman.*", item):
                prman.append(frame)
            elif re.search(r"^Hydra.*", item):
                hydra.append(frame)

    if prman: previews = prman
    else: previews = hydra

    # rule to sort previews by frame
    def sorter (x):
        match = re.search(r"\.f\d*\.", os.path.basename(x) )
        if match:
            return float(re.sub(r"[.f]", "", match.group()))
        return float()
    previews.sort(key=sorter)

    return previews


# TODO: it's not the right module for this function
def chooseAssetItem (path: str) -> str:
    """Chooses one version of the asset's files 
    to use it for the UI item preview

    Arguments:
        path: The root directory where the asset items lie
    Returns:
        A path of a chosen file
    """
    chosenItem  = str()
    for assetItem in os.listdir(path):
        if rule_Ignore(assetItem):
            continue
        if not chosenItem:
            chosenItem = assetItem

        # get data to compare current iteration item
        # with previously chosen one
        chosenHasPreviews = getUsdPreviews(path, chosenItem)
        chosenIsFinal = ostree.isFinal(
            os.path.join(path, chosenItem))
        chosenVersion = getVersion(chosenItem)

        assetHasPreviews = getUsdPreviews(path, assetItem)
        assetIsFinal = ostree.isFinal(
            os.path.join(path, assetItem))
        assetVersion = getVersion(assetItem)

        noPreviews = not chosenHasPreviews and not assetHasPreviews
        bothHasPreviews = chosenHasPreviews and assetHasPreviews

        # first choose that one with previews
        # then that one that is final version
        # then depending on higher version
        if not chosenHasPreviews and assetHasPreviews:
            chosenItem = assetItem
        elif noPreviews or bothHasPreviews:
            if assetIsFinal:
                chosenItem = assetItem
            elif assetVersion > chosenVersion:
                if not chosenIsFinal:
                    chosenItem = assetItem

    return chosenItem
