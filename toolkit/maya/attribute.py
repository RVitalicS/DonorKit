#!/usr/bin/env python

"""
Attribute

This module defines functions to work with Maya attributes.
"""

import maya.OpenMaya as OpenMaya
from toolkit.maya import mplug
from typing import Any


def get (node: OpenMaya.MFnDependencyNode,
         name: str) -> OpenMaya.MPlug:
    """Get an attribute of the specified node

    Arguments:
        node: The node object
        name: The attribute name
    Returns:
        An attribute object
    """
    for index in range(node.attributeCount()):
        MObject = node.attribute(index)
        attribute = OpenMaya.MFnAttribute(MObject)
        attrName = attribute.name()
        if attrName == name:
            MPlug = node.findPlug(attrName)
            return MPlug


def getValue (node: OpenMaya.MFnDependencyNode,
              name: str) -> Any:
    """Get a value of the specified node

    Arguments:
        node: The node object
        name: The attribute name
    Returns:
        A value of the attribute
    """
    attribute = get(node, name)
    attributeValue = mplug.getAs(
        attribute, asValue=True)
    return attributeValue


def assignNetworkID (node: OpenMaya.MFnDependencyNode,
                     ID: str) -> None:
    """Create 'assetID' attribute
    for the specified material and its network

    Arguments:
        node: The material node
        ID: The asset ID
    """
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


def isAnimated (node: OpenMaya.MFnDependencyNode,
                name: str) -> bool:
    """Check if an attribute is animated

    Arguments:
        node: The node object
        name: The attribute name
    Returns:
        A result of the check
    """
    attribute = get(node, name)
    MObject = attribute.node()
    return OpenMayaAnim.MAnimUtil.isAnimated(MObject)
