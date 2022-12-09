#!/usr/bin/env python

"""
Node Plug

This module defines functions to work with Maya dependency node plugs.
"""

import maya.OpenMaya as OpenMaya
from typing import Any


def isValidCompound (MPlug: OpenMaya.MPlug) -> True:
    """Check if the value of the specified plug
    could be converted to a python type

    Arguments:
        MPlug: The plug object
    Returns:
        A result of the check
    """
    apiType = MPlug.attribute().apiType()
    if apiType != OpenMaya.MFn.kCompoundAttribute:
        return True
    if MPlug.isNetworked():
        return True
    return False


def getAs (MPlug: OpenMaya.MPlug, asType: bool = False,
           asValue: bool = False, echo: bool = False) -> Any:
    """Read a value or type of the specified plug
    and converted it to a python type

    Arguments:
        MPlug: The plug object
    Keyword Arguments:
        asType: A flag used to get type name
        asValue: A flag used to get value
        echo: A flag used to print a plug type
    Returns:
        A value or type of the plug
    """
    MObject = MPlug.attribute()
    attribute = OpenMaya.MFnAttribute(MObject)
    attrName  = attribute.name()
    apiType = MObject.apiType()

    if echo:
        print(f"[API Type] {attrName}: {MObject.apiTypeStr()}")
    if MPlug.isChild():
        if not isValidCompound(MPlug.parent()):
            return

    # bool int float double
    if apiType == OpenMaya.MFn.kNumericAttribute:
        MFnNumericAttribute = OpenMaya.MFnNumericAttribute(MObject)
        unitType = MFnNumericAttribute.unitType()

        if unitType == OpenMaya.MFnNumericData.kBoolean:
            if echo: print(f"{attrName}: bool")
            if asType: return "bool"
            if asValue: return MPlug.asBool()
        elif unitType in [
                OpenMaya.MFnNumericData.kInt,
                OpenMaya.MFnNumericData.kByte,
                OpenMaya.MFnNumericData.kShort,
                OpenMaya.MFnNumericData.kLong ]:
            if echo: print(f"{attrName}: int")
            if asType: return "int"
            if asValue: return MPlug.asInt()
        elif unitType == OpenMaya.MFnNumericData.kFloat:
            if echo: print(f"{attrName}: float")
            if asType: return "float"
            if asValue: return MPlug.asFloat()
        elif unitType == OpenMaya.MFnNumericData.kDouble:
            if echo: print(f"{attrName}: double")
            if asType: return "double"
            if asValue: return MPlug.asDouble()

    # double
    elif apiType == OpenMaya.MFn.kDoubleLinearAttribute:
        if echo: print(f"{attrName}: double")
        if asType: return "double"
        if asValue: return MPlug.asDouble()

    # float
    elif apiType == OpenMaya.MFn.kDoubleAngleAttribute:
        value = MPlug.asFloat()
        MAngle = OpenMaya.MAngle(value)
        if echo: print(f"{attrName}: float")
        if asType: return "float"
        if asValue: return MAngle.asDegrees()

    # int
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        if echo: print(f"{attrName}: int")
        if asType: return "int"
        if asValue: return MPlug.asInt()

    # string matrix
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        MFnTypedAttribute = OpenMaya.MFnTypedAttribute(MObject)
        attrType = MFnTypedAttribute.attrType()

        if attrType == OpenMaya.MFnData.kString:
            if echo: print(f"{attrName}: string")
            if asType: return "string"
            if asValue: return MPlug.asString()
        elif attrType == OpenMaya.MFnData.kMatrix:
            MFnMatrixData = OpenMaya.MFnMatrixData(MPlug.asMObject())
            if echo: print(f"{attrName}: matrix")
            if asType: return "matrix"
            if asValue: return MFnMatrixData.matrix()

    # tuple
    elif apiType in [
            OpenMaya.MFn.kAttribute2Float,
            OpenMaya.MFn.kAttribute2Double]:
        result = []
        for index in range(MPlug.numChildren()):
            value = getAs(MPlug.child(index), asValue=True, echo=echo)
            result.append(value)
        if echo: print(f"{attrName}: float2")
        if asType: return "float2"
        if asValue: return tuple(result)

    # tuple
    elif apiType in [
            OpenMaya.MFn.kAttribute3Float,
            OpenMaya.MFn.kAttribute3Double,
            OpenMaya.MFn.kCompoundAttribute]:
        if not isValidCompound(MPlug):
            return
        result = []
        for index in range(MPlug.numChildren()):
            value = getAs(MPlug.child(index), asValue=True, echo=echo)
            result.append(value)
        typeString = "float3"
        if attribute.isUsedAsColor():
            typeString = "color3f"
        if echo: print(f"{attrName}: {typeString}")
        if asType: return typeString
        if asValue: return tuple(result)
