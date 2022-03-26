#!/usr/bin/env python


import os
import re

import toolbox.core.naming


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

        textures = os.path.join(surfacing, SUBDIR_TEXTURES)
        if not os.path.exists(textures):
            os.mkdir(textures)






def getItemsCount (path):

    count = int()

    for item in os.listdir(path):

        itempath = os.path.join(path, item)
        if not os.path.isdir(itempath):
            continue
        count += 1

    return count






def linkUpdate (path, name, create=True):

    os.chdir(path)

    finalname = toolbox.core.naming.makeFinal(name)
    finalpath = os.path.join(path, finalname)

    if os.path.exists(finalpath):
        os.remove(finalpath)

    if create:
        os.symlink(name, finalname)
