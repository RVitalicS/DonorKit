#!/usr/bin/env python

import maya.OpenMaya as OpenMaya

from toolkit.maya import mplug





def get (node, name):
    
    for index in range(node.attributeCount()):

        MObject = node.attribute(index)
        attribute = OpenMaya.MFnAttribute(MObject)

        attrName = attribute.name()
        if attrName == name:
            MPlug = node.findPlug(attrName)

            return MPlug





def getValue (node, name):

    attribute = get(node, name)
    attributeValue = mplug.getAs(
        attribute, asValue=True )
    
    return attributeValue





def assignNetworkID (node, ID):

    typeName = node.typeName()
    if typeName in ["expression"]:
        return

    isMaterial = typeName == "shadingEngine"

    attrName = "assetID"
    hasID = node.hasAttribute(attrName)

    if not isMaterial:
        if not hasID:
            attribute = OpenMaya.MFnTypedAttribute()
            MObject = attribute.create(
                attrName, attrName,
                OpenMaya.MFnData.kString)
            attribute.setHidden(True)
            node.addAttribute(MObject)

        MPlug = node.findPlug(attrName)
        MPlug.setString(ID)


    for index in range(node.attributeCount()):
        MObject = node.attribute(index)
        MPlug = node.findPlug(MObject)

        source = MPlug.source()
        if source.isNull(): continue

        nodeSource = OpenMaya.MFnDependencyNode(source.node())
        assignNetworkID(nodeSource, ID)





def isAnimated (node, name):

    attribute = get(node, name)
    MObject = attribute.node()
    
    return OpenMayaAnim.MAnimUtil.isAnimated(MObject)
