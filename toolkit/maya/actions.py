#!/usr/bin/env python


import mayaUsd
import ufe
import os

import maya.cmds as mayaCommand
import maya.mel as mayaMEL

from pxr import UsdGeom

from toolkit.maya import find
from toolkit.maya import outliner
from toolkit.maya import attribute
from toolkit.maya import stage as outlinerStage
import toolkit.maya.message as mayaMessage

from toolkit.core import naming
from toolkit.core import message
from toolkit.core import Metadata

from toolkit.usd import read





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
        + outlinerStage.getPathAnyway() )
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
    outliner.refresh()





def loadMaterial (path):
    
    """
        Creates maya material network from usd file

        :type  path: str
        :param path: path to usd file
    """


    # get selected meshes
    selection = mayaCommand.ls(selection=True)
    meshes = find.selectionMeshes()


    # get asset data
    path = os.path.realpath(path)
    filename  = os.path.basename(path)
    directory = os.path.dirname(path)

    ID = Metadata.getID(directory, filename)
    data = read.asMayaBuildScheme(path)

    material = data.get("material")
    materialName = material.get("name")

    if mayaCommand.objExists(materialName):
        text = "Material Name Conflict"
        mayaMessage.viewport(text)
        mayaMessage.warning(text)
        return


    # create new set
    mayaCommand.select(clear=True)
    shadingGroup = mayaCommand.sets(
        renderable=True,
        noSurfaceShader=True,
        name=materialName )

    for mesh in meshes:
        mayaCommand.select(mesh, replace=True)
        mayaMEL.eval(f"sets -e -forceElement {shadingGroup}")


    # get together all connections
    # create shaders and set values
    connections = []
    inputs = material.get("inputs")
    for inplug, outplug in inputs.items():
        outplug = ".".join(outplug)
        inplug = f"{materialName}.{inplug}"
        connections.append([outplug, inplug])

    shaders = data.get("shaders")
    for nodeName, nodeSpec in shaders.items():

        nodeType = nodeSpec.get("id")
        mayatype = nodeSpec.get("mayatype")
        if mayatype == "shader":
            mayaCommand.shadingNode(nodeType,
                asShader=True, name=nodeName)
        elif mayatype == "texture":
            mayaCommand.shadingNode(nodeType,
                asTexture=True, name=nodeName)
        else:
            mayaCommand.shadingNode(nodeType,
                asUtility=True, name=nodeName)

        inputs = nodeSpec.get("inputs")
        for attr, spec in inputs.items():
            attrName = f"{nodeName}.{attr}"
            value = spec.get("value")

            if attr == "colorSpace":
                mayaCommand.setAttr(
                    f"{nodeName}.ignoreColorSpaceFileRules", 1)

            if spec.get("connection"):
                outplug = ".".join(value)
                inplug = attrName
                connections.append([outplug, inplug])

            elif spec.get("type") in ["float", "int"]:
                mayaCommand.setAttr(attrName, value)

            elif spec.get("type") == "string":
                mayaCommand.setAttr(attrName, value,
                    type=spec.get("type"))
            else:
                mayaCommand.setAttr(attrName, *value,
                    type=spec.get("type"))


    # connect shaders to network
    for pair in connections:
        mayaCommand.connectAttr(*pair)


    # add ID attribute
    MFnDependencyNode = find.shaderByName(shadingGroup)
    attribute.assignNetworkID(MFnDependencyNode, ID)

    # restore selection
    mayaCommand.select(selection, replace=True)





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
