

# Naming Convention
#    
#    Name.VariantName-v01.usdc
#    Name.AnimationName.v01.usd
#    Name.v01.final.usda
#    
#    name
#        "AssetName."
#    tag
#        ".Proxy." [ reserved ]
#        ".RenderMan." [ reserved ]
#        ".AnimationName-01."
#    variant & version
#        ".v01."
#        ".VariantName-v01."
#    final tag option
#        ".final." [ reserved ]
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
#         ModelName.v01.usdc
#         ModelName.Proxy.v01.usdc
# 
#     [animation]
#         AnimationName.v01.usdc
# 
#     [surfacing]
#         [textures]
#             ...
# 
#         SurfaceName.RenderMan.v01.usda
#         SurfaceName.v01.usda
# 
#     AssetName.AnimationName.VariantName-v01.final.usda
#     .metadata.json





import os
import re


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

        textures = os.path.join(surfacing, SUBDIR_TEXTURES)
        if not os.path.exists(textures):
            os.mkdir(textures)
