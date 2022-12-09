#!/usr/bin/env python

"""
Maya USD Stage

This module defines functions to work with a Maya USD stage.
"""

import maya.OpenMaya as OpenMaya
import toolkit.maya.find as findCommand
import toolkit.maya.attribute as attributeCommand
import toolkit.maya.time as timeCommand
from typing import Union


def create (name: str = "UsdStage") -> str:
    """Create a new proxyShape node (USD stage)
    that appears in the Outliner

    Keyword Arguments:
        name: The name for a new node
    Returns:
        A path to the newly created proxyShape
    """

    # create Usd Stage
    MDagModifier = OpenMaya.MDagModifier()
    MObjectXform = MDagModifier.createNode("mayaUsdProxyShape")
    MDagModifier.renameNode(MObjectXform, name)
    MDagModifier.doIt()
    MFnDagNode = OpenMaya.MFnDagNode(MObjectXform)
    MObjectShape = MFnDagNode.child(0)
    MDagModifier.renameNode(MObjectShape, f"{name}Shape")
    MDagModifier.doIt()

    # link time slider
    timeNode = timeCommand.getTimeNode()
    sceneTimeAttr = attributeCommand.get(timeNode, "outTime")
    stageShapePath = f"|{name}|{name}Shape"
    stageNode = findCommand.nodeByPath(stageShapePath)
    stageTimeAttr = attributeCommand.get(stageNode, "time")
    MDGModifier = OpenMaya.MDGModifier()
    MDGModifier.connect(sceneTimeAttr, stageTimeAttr)
    MDGModifier.doIt()

    # set scale
    stageXformPath = f"|{name}"
    xformNode = findCommand.nodeByPath(stageXformPath)
    scaleX = attributeCommand.get(xformNode, "scaleX")
    scaleY = attributeCommand.get(xformNode, "scaleY")
    scaleZ = attributeCommand.get(xformNode, "scaleZ")
    value = 100.0
    scaleX.setDouble(value)
    scaleY.setDouble(value)
    scaleZ.setDouble(value)

    return stageShapePath


def getAnyPath () -> Union[str, None]:
    """Find any USD stage that exists in a current Maya scene

    Returns:
        A path to a proxyShape node
    """
    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName("*", MSelectionList)
    MItSelectionList = OpenMaya.MItSelectionList(
        MSelectionList, OpenMaya.MFn.kPluginShape)
    while not MItSelectionList.isDone():
        MObject = OpenMaya.MObject()
        MItSelectionList.getDependNode(MObject)
        node = OpenMaya.MFnDependencyNode(MObject)
        if node.typeName() == "mayaUsdProxyShape":
            MDagPath = OpenMaya.MDagPath()
            MItSelectionList.getDagPath(
                MDagPath, OpenMaya.MObject())
            return MDagPath.fullPathName()
        MItSelectionList.next()


def getSelectedPath () -> Union[str, None]:
    """Get a path of the currently selected Usd stage

    Returns:
        A path to a selected proxyShape node
    """
    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)
    MItSelectionList = OpenMaya.MItSelectionList(
        MSelectionList, OpenMaya.MFn.kPluginShape)
    while not MItSelectionList.isDone():
        MObject = OpenMaya.MObject()
        MItSelectionList.getDependNode(MObject)
        node = OpenMaya.MFnDependencyNode(MObject)
        if node.typeName() == "mayaUsdProxyShape":
            MDagPath = OpenMaya.MDagPath()
            MItSelectionList.getDagPath(
                MDagPath, OpenMaya.MObject())
            return MDagPath.fullPathName()
        MItSelectionList.next()


def getPathAnyway () -> str:
    """Get a path of a Maya Usd stage in this order:
    a selected stage, any existing one, a newly created one

    Returns:
        A path to a proxyShape node
    """
    path = getSelectedPath()
    if path:
        return path
    path = getAnyPath()
    if path:
        return path
    path = create()
    if path:
        return path
