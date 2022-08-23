#!/usr/bin/env python


import mayaUsd
import ufe
import os

from pxr import UsdGeom

import toolkit.maya.stage
import toolkit.maya.outliner

from toolkit.core import naming
from toolkit.core import message





def loadUsdFile (path):
    
    """
        Creates reference to usd asset
        inside mayaUsdProxyShape

        :type  path: str
        :param path: path to usd file
    """

    
    # get asset name
    fileName = os.path.basename(path)
    assetName = naming.getAssetName(fileName)


    # get scene stage
    mayaStagePath = ( "|world"
        + toolkit.maya.stage.getPathAnyway() )
    Stage = mayaUsd.ufe.getStage(mayaStagePath)

    stageRoot = ""
    stagePath = ""
    for SceneItem in list(ufe.GlobalSelection.get()):
        
        ufePath = SceneItem.path()
        ufeSplit = str(ufePath).split("/")

        stageRoot = ufeSplit[0]
        if len(ufeSplit) == 2:
            if mayaStagePath == stageRoot:
                stagePath = "/" +  ufeSplit[1]
        break


    # create reference
    if stagePath == "":
        refStagePath = "/" + assetName
        RefXform = UsdGeom.Xform.Define(Stage, refStagePath)
        RefPrim = RefXform.GetPrim()

    else:
        refStagePath = mayaStagePath + "," + stagePath
        RefPrim = mayaUsd.ufe.ufePathToPrim(refStagePath)

    RefPrim.GetReferences().AddReference(path)


    # update maya outliner "shape display"
    toolkit.maya.outliner.refresh()





def loadMaterial (path):
    
    """
        Placeholder function
        Need definition to act on input argument

        :type  path: str
        :param path: path to usd file
    """


    # erase this
    message.defaultDefinition(
        "loadMaterial", __file__, mode="maya")





def loadColor (data):
    
    """
        Placeholder function
        Need definition to act on input argument

        :type  data: list
        :param data: RGB color channels
    """


    # erase this
    message.defaultDefinition(
        "loadColor", __file__, mode="maya")
