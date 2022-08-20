#!/usr/bin/env python

import maya.OpenMaya as OpenMaya

import toolkit.maya.mplug





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
    attributeValue = toolkit.maya.mplug.getAs(
        attribute, asValue=True )
    
    return attributeValue





def isAnimated (node, name):

    attribute = get(node, name)
    MObject = attribute.node()
    
    return OpenMayaAnim.MAnimUtil.isAnimated(MObject)
