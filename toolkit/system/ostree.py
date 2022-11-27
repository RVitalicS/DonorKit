#!/usr/bin/env python


import os
import re

import toolkit.core.naming
from toolkit.core.Metadata import METAFILE


# define names of directories
SUBDIR_PREVIEWS  = "previews"
SUBDIR_SOURCES   = "sources"
SUBDIR_VFX       = "vfx"
SUBDIR_MODELLING = "modelling"
SUBDIR_ANIMATION = "animation"
SUBDIR_SURFACING = "surfacing"
SUBDIR_TEXTURES  = "textures"


# define tags
RESERVED_TAGS = [
    "Render",
    "Proxy",
    "RenderMan" ]





def buildUsdRoot ( root,
            previews  = False,
            sources   = False,
            vfx       = False,
            modelling = False,
            animation = False,
            surfacing = False ):
    
    '''
        Creates required folders to store different parts of asset
        depending on its complexity
    '''

            
    # create folder to be interpreted as asset root
    if not os.path.exists(root):
        os.mkdir(root)

    # create folder to store previews
    if previews:
        previews = os.path.join(root, SUBDIR_PREVIEWS)
        if not os.path.exists(previews):
            os.mkdir(previews)
    
    # create folder to store working files of maya or another DCC
    if sources:
        sources = os.path.join(root, SUBDIR_SOURCES)
        if not os.path.exists(sources):
            os.mkdir(sources)

    #  create folder to hairs, smokes, particles and etc.
    if vfx:
        vfx = os.path.join(root, SUBDIR_VFX)
        if not os.path.exists(vfx):
            os.mkdir(vfx)

    # create folder to store mesh data
    if modelling:
        modelling = os.path.join(root, SUBDIR_MODELLING)
        if not os.path.exists(modelling):
            os.mkdir(modelling)
            
    # create folder to store animation data
    if animation:
        animation = os.path.join(root, SUBDIR_ANIMATION)
        if not os.path.exists(animation):
            os.mkdir(animation)

    # create folder to store shaders and textures
    if surfacing:
        surfacing = os.path.join(root, SUBDIR_SURFACING)
        if not os.path.exists(surfacing):
            os.mkdir(surfacing)

        # textures = os.path.join(surfacing, SUBDIR_TEXTURES)
        # if not os.path.exists(textures):
        #     os.mkdir(textures)






def getItemCount (path):

    count = int()

    for item in os.listdir(path):

        itempath = os.path.join(path, item)
        if not os.path.isdir(itempath):
            continue
        count += 1

    return count






def getGroupCount (path):

    count = int()

    for item in os.listdir(path):

        if item == METAFILE:
            continue

        if not re.search(r"\.json$", item):
            continue

        count += 1

    return count






def getPathUSD (path, name, final=False):

    if final:
        name = toolkit.core.naming.makeFinal(name)
    name = os.path.splitext(name)[0]

    for extension in ["usd", "usdc", "usda"]:
        pathUSD = os.path.join(
            path, f"{name}.{extension}" )
        if os.path.exists(pathUSD):
            return pathUSD






def isFinal (path):

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






def linkUpdate (path, name, create=True):

    os.chdir(path)

    finalpath = getPathUSD(path, name, final=True)
    if finalpath:
        os.remove(finalpath)

    if create:
        finalname = toolkit.core.naming.makeFinal(name)
        os.symlink(name, finalname)
