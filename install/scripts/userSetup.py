#!/usr/bin/env python

"""
Startup Script

Create the new Maya shelf.
"""

import maya.cmds as mayaCommand
import maya.mel as mayaMEL


def addSeparator (shelfName: str) -> None:
    """Create a separator widget in the specified shelf

    Arguments:
        shelfName: The name of a shelf
    """
    for itemUI in mayaCommand.lsUI(controlLayouts=True):
        if itemUI == shelfName:
            mayaCommand.separator(
                parent = shelfName,
                horizontal = False,
                style = "single")
            break


# shelf item collector
buttons = []

# add the launcher for the Asset Manager widget
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

# add separator
buttons.append(dict(label="Separator"))

# add the launcher for the Material Export dialog
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

from toolkit.maya import MaterialUsd
MaterialUsd.Export()
"""))

# add the launcher for the Asset Export dialog
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

from toolkit.maya import AssetUsd
AssetUsd.Export()
"""))


def createButton () -> None:
    """Create the new Maya shelf"""

    # get shelves
    gShelfTopLevel = mayaMEL.eval("$tmpVar=$gShelfTopLevel")
    shelves = mayaCommand.tabLayout(gShelfTopLevel, query=1, ca=1)

    # create new shelf
    shelfName = "DonorKit"
    if shelfName not in shelves:
        mayaCommand.shelfLayout(shelfName, parent=gShelfTopLevel)
    else:
        return

    # add buttons
    names = mayaCommand.shelfLayout(shelfName, query=True, childArray=True) or []
    labels = [mayaCommand.shelfButton(n, query=True, label=True) for n in names]
    for button in buttons:
        buttonName = button.get("label")
        if buttonName not in labels:
            if buttonName == "Separator":
                addSeparator(shelfName)
                continue
            mayaCommand.shelfButton(
                label=buttonName,
                annotation=button.get("annotation"),
                enableBackground=button.get("enableBackground"),
                style=button.get("style"),
                sourceType=button.get("sourceType"),
                parent=shelfName,
                image=button.get("image"),
                command=button.get("command"))


# runs this code automatically at the start of Maya
mayaCommand.evalDeferred("createButton()")
