#!/usr/bin/env python


import maya.OpenMaya as OpenMaya

import toolkit.maya.find
import toolkit.maya.attribute
import toolkit.maya.time





def create (name="UsdStage"):


    # create Usd Stage
    MDagModifier = OpenMaya.MDagModifier()
    MObjectXform = MDagModifier.createNode("mayaUsdProxyShape")
    MDagModifier.renameNode(MObjectXform, name)
    MDagModifier.doIt()

    MFnDagNode = OpenMaya.MFnDagNode(MObjectXform)
    MObjectShape = MFnDagNode.child(0)
    MDagModifier.renameNode(MObjectShape, name + "Shape")
    MDagModifier.doIt()


    # link time slider
    timeNode = toolkit.maya.time.getTimeNode()
    sceneTimeAttr = toolkit.maya.attribute.get(timeNode, "outTime")

    stageShapePath = "|{0}|{0}Shape".format(name)
    stageNode = toolkit.maya.find.nodeByPath(stageShapePath)
    stageTimeAttr = toolkit.maya.attribute.get(stageNode, "time")

    MDGModifier = OpenMaya.MDGModifier()
    MDGModifier.connect( sceneTimeAttr, stageTimeAttr )
    MDGModifier.doIt()


    # set scale
    stageXformPath = "|{0}".format(name)
    xformNode = toolkit.maya.find.nodeByPath(stageXformPath)
    
    scaleX = toolkit.maya.attribute.get(xformNode, "scaleX")
    scaleY = toolkit.maya.attribute.get(xformNode, "scaleY")
    scaleZ = toolkit.maya.attribute.get(xformNode, "scaleZ")
    
    value = 100.0
    scaleX.setDouble(value)
    scaleY.setDouble(value)
    scaleZ.setDouble(value)


    return stageShapePath





def getAnyPath ():

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





def getSelectedPath ():

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





def getPathAnyway ():

    path = getSelectedPath()
    if path: return path
    
    path = getAnyPath()
    if path: return path

    path = create()
    if path: return path
