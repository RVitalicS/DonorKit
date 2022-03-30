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
    image="DonorManager",
    command="""
# define libraries to manage assets
# os.environ["ASSETLIBS"]=/server/library

from toolkit.maya import DonorManager
DonorManager.show()
"""))


buttons.append(dict(label="Separator"))


buttons.append(dict(
    label="UsdExport",
    annotation="Export selected to USD asset",
    enableBackground=False,
    style="iconOnly",
    sourceType="python",
    image="UsdExport",
    command="""
# define libraries to export assets
# os.environ["ASSETLIBS"]=/server/library

from toolkit.maya import AssetUsd
AssetUsd.Export()

import importlib
importlib.reload(AssetUsd)
"""))




def createButton ():

    # get top shelf
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")

    # get top shelf names
    shelves = cmds.tabLayout(gShelfTopLevel, query=1, ca=1)

    # create shelf if not exists
    shelfName = "DonorKit"
    firstRun = False
    if shelfName not in shelves:
        firstRun = True
        cmds.shelfLayout(shelfName, parent=gShelfTopLevel)


    # get existing members
    names = cmds.shelfLayout(shelfName, query=True, childArray=True) or []
    labels = [cmds.shelfButton(n, query=True, label=True) for n in names]


    # add buttons if not exist
    for button in buttons:
        buttonName = button.get("label")

        if buttonName == "Separator":
            if firstRun: addSeparator(shelfName)
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
