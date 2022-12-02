#!/usr/bin/env python

"""Functions to manage the library items."""

import os
import re
from toolkit.core import naming
from toolkit.core.Metadata import METAFILE

# define names of directories
SUBDIR_PREVIEWS  = "previews"
SUBDIR_SOURCES   = "sources"
SUBDIR_VFX       = "vfx"
SUBDIR_MODELLING = "modelling"
SUBDIR_ANIMATION = "animation"
SUBDIR_SURFACING = "surfacing"
SUBDIR_TEXTURES  = "textures"

# TODO: another reserved tags (Hydra, Prman, Final)
# define tags
RESERVED_TAGS = [
    "Render",
    "Proxy",
    "RenderMan" ]


def buildUsdRoot (
        root: str, previews: bool  = False, sources: bool = False,
        vfx: bool = False, modelling: bool = False,
        animation: bool = False, surfacing: bool = False ) -> None:
    """Creates required folders to store different parts of the asset

    Arguments:
        root:  The root directory of the asset that would be created
    Keyword Arguments:
        previews:  Create the folder to hold previews
        sources:   Create the folder to hold working files of DCC app
        vfx:       Create the folder to hold hairs, smokes, particles
        modelling: Create the folder to hold mesh data
        animation: Create the folder to hold animation data
        surfacing: Create the folder to hold shaders and textures
    """
    if not os.path.exists(root):
        os.mkdir(root)
    if previews:
        previews = os.path.join(root, SUBDIR_PREVIEWS)
        if not os.path.exists(previews):
            os.mkdir(previews)
    if sources:
        sources = os.path.join(root, SUBDIR_SOURCES)
        if not os.path.exists(sources):
            os.mkdir(sources)
    if vfx:
        vfx = os.path.join(root, SUBDIR_VFX)
        if not os.path.exists(vfx):
            os.mkdir(vfx)
    if modelling:
        modelling = os.path.join(root, SUBDIR_MODELLING)
        if not os.path.exists(modelling):
            os.mkdir(modelling)
    if animation:
        animation = os.path.join(root, SUBDIR_ANIMATION)
        if not os.path.exists(animation):
            os.mkdir(animation)
    if surfacing:
        surfacing = os.path.join(root, SUBDIR_SURFACING)
        if not os.path.exists(surfacing):
            os.mkdir(surfacing)
        # textures = os.path.join(surfacing, SUBDIR_TEXTURES)
        # if not os.path.exists(textures):
        #     os.mkdir(textures)


def getItemCount (path: str) -> int:
    """Count folders the directory contain

    Arguments:
        path: The directory where it should be done
    Returns:
        The number of folders
    """
    count = int()
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if not os.path.isdir(itempath):
            continue
        count += 1
    return count


def getGroupCount (path: str) -> int:
    """Count color groups the directory contain

    Arguments:
        path: The directory where it should be done
    Returns:
        The number of color groups
    """
    count = int()
    for item in os.listdir(path):
        if item == METAFILE:
            continue
        if not re.search(r"\.json$", item):
            continue
        count += 1
    return count


def getPathUSD (path: str, name: str, final: bool = False) -> str:
    """Find the item of the asset with the varying file extension

    Arguments:
        path: The root directory where the asset's items lie
        name: The name of the file
    Keyword Arguments:
        final: A flag used to find a symbolic link that point to the file
    Returns:
        A path of a found file or {None} if it doesn't exist
    """
    if final:
        name = naming.makeFinal(name)
    name = os.path.splitext(name)[0]
    for extension in ["usd", "usdc", "usda"]:
        pathUSD = os.path.join(
            path, f"{name}.{extension}" )
        if os.path.exists(pathUSD):
            return pathUSD


def isFinal (path: str) -> bool:
    """Check that the given file is the final version of the asset

    Arguments:
        path: The path of the usd file
    Returns:
        A result of the check
    """
    result = False
    root = os.path.dirname(path)
    name = os.path.basename(path)
    pathfinal = getPathUSD(root, name, final=True)
    if pathfinal:
        pathlink = os.path.realpath(pathfinal)
        link = os.path.basename(pathlink)
        if name == link:
            result = True

    return result


def linkUpdate (path: str, name: str, create: bool = True) -> None:
    """Remove the symbolic link that point to the file
    that is the final version of the asset, then optionally create a new one

    Arguments:
        path: The root directory where the asset's items lie
        name: The name of the file
    Keyword Arguments:
        create: A flag used to create a symbolic link
    """
    os.chdir(path)
    finalpath = getPathUSD(path, name, final=True)
    if finalpath:
        os.remove(finalpath)
    if create:
        finalname = naming.makeFinal(name)
        os.symlink(name, finalname)
