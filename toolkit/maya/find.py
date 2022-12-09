#!/usr/bin/env python

"""
Find

This module defines functions to find node objects in a Maya scene.
"""

import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya
from typing import Union


def nodeByPath (path: str) -> Union[OpenMaya.MFnDependencyNode, None]:
    """Get a node at the specified path

    Arguments:
        path: The DAG path to a node
    Returns:
        A node object
    """
    MSelectionList = OpenMaya.MSelectionList()
    MSelectionList.add(path)
    if MSelectionList.isEmpty():
        return
    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)
    MObject = MDagPath.node()
    return OpenMaya.MFnDependencyNode(MObject)


def nodeByName (name: str) -> Union[OpenMaya.MFnDependencyNode, None]:
    """Get a node with the specified name

    Arguments:
        name: The name of a node
    Returns:
        A node object
    """
    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    if MSelectionList.isEmpty():
        return
    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)
    MObject = MDagPath.node()
    return OpenMaya.MFnDependencyNode(MObject)


def shaderByName (name: str) -> Union[OpenMaya.MFnDependencyNode, None]:
    """Get a shader node with the specified name

    Arguments:
        name: The name of a shader node
    Returns:
        A shader node object
    """
    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    if MSelectionList.isEmpty():
        return
    MPlug = OpenMaya.MPlug()
    MSelectionList.getPlug(0, MPlug)
    MObject = MPlug.node()
    return OpenMaya.MFnDependencyNode(MObject)


def selectionMeshes (selection: Union[None, list] = None) -> list:
    """Get list of DAG paths for selected objects

    Keyword Arguments:
        selection: The exchange data for the iterations
    Returns:
        A list of DAG paths
    """
    meshes = []
    if selection is None:
        selection = mayaCommand.ls(
            selection=True, long=True,
            noIntermediate=True)
    for dagPath in selection:
        if mayaCommand.nodeType(dagPath) == "mesh":
            meshes.append(dagPath)
        elif mayaCommand.nodeType(dagPath) == "transform":
            listRelatives = mayaCommand.listRelatives(
                dagPath, children=True, fullPath=True) or []
            meshes += selectionMeshes(selection=listRelatives)
    return meshes
