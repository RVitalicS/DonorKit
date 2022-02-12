#!/usr/bin/env python



# Naming Convention
#    
#    Name.v01-VariantName.usdc
#    Name.v01.AnimationName.usd
#    Name.Final.usda [ symbolic link ]
#    
#    name
#        "AssetName."
#    variant & version (Final)
#        ".v01."
#        ".v01-VariantName."
#        ".Final."
#        ".Final-VariantName."
#    tag & animation
#        ".Proxy."            [ reserved ]
#        ".RenderMan."        [ reserved ]
#        ".AnimationName-01."
#    extension 
#        ".usd"



# Asset Structure
#
# [AssetName]
# 
#     [previews]
#         AssetName.v01.png
#         AssetName.v01.mp4
# 
#     [sources]
#         AssetName.v01.mb
# 
#     [vfx]
#         Hair.v01.usd
#         Cloth.v01.usd
#         Fire.v01.usd
# 
#     [modelling]
#         ModelName.v01.Proxy.usdc
#         ModelName.v01.usdc
# 
#     [animation]
#         AnimationName.v01.usdc
# 
#     [surfacing]
#         [textures]
#             ...
# 
#         SurfaceName.v01.RenderMan.usda
#         SurfaceName.v01.usda
# 
#     AssetName.Final.AnimationName.usda [AssetName.v01-VariantName.AnimationName.usda]
#     AssetName.v01-VariantName.AnimationName.usda
#     .metadata.json





import os
import re


# define names of directories
SUBDIR_PREVIEWS  = "previews"
SUBDIR_SOURCES   = "sources"
SUBDIR_VFX       = "vfx"
SUBDIR_MODELLING = "modelling"
SUBDIR_ANIMATION = "animation"
SUBDIR_SURFACING = "surfacing"
SUBDIR_TEXTURES  = "textures"





def build ( root,
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
