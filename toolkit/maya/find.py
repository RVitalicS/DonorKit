#!/usr/bin/env python

import maya.OpenMaya as OpenMaya





def nodeByPath (path):

    MSelectionList = OpenMaya.MSelectionList()
    MSelectionList.add(path)
    
    if MSelectionList.isEmpty(): return

    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)

    MObject = MDagPath.node()
    node = OpenMaya.MFnDependencyNode(MObject)
    
    return node





def nodeByName (name):

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    
    if MSelectionList.isEmpty(): return

    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)

    MObject = MDagPath.node()
    node = OpenMaya.MFnDependencyNode(MObject)
    
    return node





def shaderByName (name):

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    
    if MSelectionList.isEmpty(): return

    MPlug = OpenMaya.MPlug()
    MSelectionList.getPlug(0, MPlug)

    MObject = MPlug.node()
    shader = OpenMaya.MFnDependencyNode(MObject)
    
    return shader
