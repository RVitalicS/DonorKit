

# (AssetName)
#     (modelling)
#         RootName.usd
#         RootName.Proxy.usd
#     (surfacing)
#         (textures)
#         ShadingGroupName.RenderMan.usda
#         ShadingGroupName.usda
#     AssetName.usda


import os
import re





SUBDIR_MODELLING = "modelling"
SUBDIR_SURFACING = "surfacing"
SUBDIR_TEXTURES  = "textures"





def build (path, name):

    root = os.path.join(path, name)
    if not os.path.exists(root):
        os.mkdir(root)

    modelling = os.path.join(root, SUBDIR_MODELLING)
    if not os.path.exists(modelling):
        os.mkdir(modelling)

    surfacing = os.path.join(root, SUBDIR_SURFACING)
    if not os.path.exists(surfacing):
        os.mkdir(surfacing)

    textures = os.path.join(surfacing, SUBDIR_TEXTURES)
    if not os.path.exists(textures):
        os.mkdir(textures)
