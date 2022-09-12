#!/usr/bin/env python


import maya.cmds as cmds
import maya.mel as mel




def addSeparator (shelfName):
    for itemUI in cmds.lsUI(controlLayouts=True):

        if itemUI == shelfName:
            cmds.separator(
                parent = shelfName,
                horizontal = False,
                style = "single")

            break




buttons = []

buttons.append(dict(
    label="DonorManager",
    annotation="Manage and Load Asset",
    enableBackground=False,
    style="iconOnly",
    sourceType="python",
    image="store.svg",
    command="""
# define libraries to manage assets
# os.environ["ASSETLIBS"]=/server/library

from toolkit.maya import DonorManager
DonorManager.show()
"""))


buttons.append(dict(label="Separator"))


buttons.append(dict(
    label="UsdMaterialExport",
    annotation="Export selected as USD material",
    enableBackground=False,
    style="iconOnly",
    sourceType="python",
    image="face.svg",
    command="""
# define libraries to export assets
# os.environ["ASSETLIBS"]=/server/library

import importlib
from toolkit.maya import MaterialUsd

importlib.reload(MaterialUsd)
MaterialUsd.Export()
"""))


buttons.append(dict(
    label="UsdExport",
    annotation="Export selected to USD asset",
    enableBackground=False,
    style="iconOnly",
    sourceType="python",
    image="wing.svg",
    command="""
# define libraries to export assets
# os.environ["ASSETLIBS"]=/server/library

import importlib
from toolkit.maya import AssetUsd

importlib.reload(AssetUsd)
AssetUsd.Export()
"""))




def createButton ():

    # get top shelf
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")

    # get top shelf names
    shelves = cmds.tabLayout(gShelfTopLevel, query=1, ca=1)

    # create shelf if not exists
    shelfName = "DonorKit"
    if shelfName not in shelves:
        cmds.shelfLayout(shelfName, parent=gShelfTopLevel)
    else: return


    # get existing members
    names = cmds.shelfLayout(shelfName, query=True, childArray=True) or []
    labels = [cmds.shelfButton(n, query=True, label=True) for n in names]


    # add buttons
    for button in buttons:
        buttonName = button.get("label")

        if buttonName == "Separator":
            addSeparator(shelfName)
            continue

        if buttonName not in labels:
            cmds.shelfButton(
                label=buttonName,
                annotation=button.get("annotation"),
                enableBackground=button.get("enableBackground"),
                style=button.get("style"),
                sourceType=button.get("sourceType"),
                parent=shelfName,
                image=button.get("image"),
                command=button.get("command"))




# Runs this code automatically at the start of Maya
cmds.evalDeferred( "createButton()" )
