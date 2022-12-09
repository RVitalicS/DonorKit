#!/usr/bin/env python

"""
Maya Actions

Functions to load assets to Maya.
"""

import mayaUsd
import ufe
import os
import maya.cmds as mayaCommand
import maya.mel as mayaMEL
from pxr import UsdGeom
import toolkit.maya.find as findCommand
import toolkit.maya.outliner as outlinerCommand
import toolkit.maya.attribute as attributeCommand
import toolkit.maya.stage as stageCommand
import toolkit.maya.message as mayaMessage
from toolkit.core import naming
from toolkit.core import message
from toolkit.core import Metadata
import toolkit.usd.read as readUSD


def loadUsdFile (path: str) -> None:
    """Creates a reference to the USD Asset as {mayaUsdProxyShape}

    Arguments:
        path: The path of the USD file
    """

    # get asset name
    fileName = os.path.basename(path)
    assetName = naming.getAssetName(fileName)

    # get scene stage
    mayaStagePath = ("|world" + stageCommand.getPathAnyway())
    Stage = mayaUsd.ufe.getStage(mayaStagePath)
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
    outlinerCommand.refresh()


def loadMaterial (path: str) -> None:
    """Creates a maya material network from the USD file

    Arguments:
        path: The path of the USD file
    """
    units = 0.01           # UNIT DEPEND

    # get selected meshes
    selection = mayaCommand.ls(selection=True)
    meshes = findCommand.selectionMeshes()

    # get asset data
    path = os.path.realpath(path)
    filename  = os.path.basename(path)
    directory = os.path.dirname(path)

    ID = Metadata.getID(directory, filename)
    data = readUSD.asMayaBuildScheme(path)
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
        name=materialName)
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
            mayaCommand.shadingNode(nodeType, asShader=True, name=nodeName)
        elif mayatype == "texture":
            mayaCommand.shadingNode(nodeType, asTexture=True, name=nodeName)
        else:
            mayaCommand.shadingNode(nodeType, asUtility=True, name=nodeName)

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
                mayaCommand.setAttr(attrName, value, type=spec.get("type"))
            else:
                mayaCommand.setAttr(attrName, *value, type=spec.get("type"))

        if nodeType == "PxrDisplace":
            mayaCommand.setAttr(
                f"{nodeName}.dispAmount",
                inputs.get("dispAmount").get("value") / units)
        elif nodeType == "PxrRoundCube":
            value = inputs.get("frequency").get("value") * units
            if round(value, 3) <= 0.001: value += 0.000001
            mayaCommand.setAttr(f"{nodeName}.frequency", value)

    # connect shaders to network
    for pair in connections:
        mayaCommand.connectAttr(*pair)

    # add ID attribute
    MFnDependencyNode = findCommand.shaderByName(shadingGroup)
    attributeCommand.assignNetworkID(MFnDependencyNode, ID)

    # restore selection
    mayaCommand.select(selection, replace=True)


def loadColor (data: list) -> None:
    """The placeholder function.
    Need definition to act on input argument

    Arguments:
        data: The list of RGB color channels
    """

    # TODO: erase this and make you happy
    message.defaultDefinition(
        "loadColor", __file__, mode="maya")
