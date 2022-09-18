#!/usr/bin/env python

import maya.OpenMaya as OpenMaya





def isValidCompound (MPlug):

    apiType = MPlug.attribute().apiType()
    if apiType != OpenMaya.MFn.kCompoundAttribute:
        return True
    
    if MPlug.isNetworked():
        return True

    return False





def getAs ( MPlug,
        asValue = False ,
        asType  = False ,
        echo    = False ):


    MObject = MPlug.attribute()

    attribute = OpenMaya.MFnAttribute(MObject)
    attrName  = attribute.name()

    apiType = MObject.apiType()
    if echo: print( "[API Type] {}: {}".format(
        attrName, MObject.apiTypeStr()) )


    if MPlug.isChild():
        if not isValidCompound(MPlug.parent()):
            return


    if apiType == OpenMaya.MFn.kNumericAttribute:

        MFnNumericAttribute = OpenMaya.MFnNumericAttribute(MObject)
        unitType = MFnNumericAttribute.unitType()

        if unitType == OpenMaya.MFnNumericData.kBoolean:
            if echo: print( "{}: bool".format(attrName) )
            if asType: return "bool"
            if asValue: return MPlug.asBool()
            
        elif unitType in [ 
                OpenMaya.MFnNumericData.kInt,
                OpenMaya.MFnNumericData.kByte,
                OpenMaya.MFnNumericData.kShort,
                OpenMaya.MFnNumericData.kLong ]:

            if echo: print( "{}: int".format(attrName) )
            if asType: return "int"
            if asValue: return MPlug.asInt()
            
        elif unitType == OpenMaya.MFnNumericData.kFloat:
            if echo: print( "{}: float".format(attrName) )
            if asType: return "float"
            if asValue: return MPlug.asFloat()
            
        elif unitType == OpenMaya.MFnNumericData.kDouble:
            if echo: print( "{}: double".format(attrName) )
            if asType: return "double"
            if asValue: return MPlug.asDouble()


    elif apiType == OpenMaya.MFn.kDoubleLinearAttribute:

        if echo: print( "{}: double".format(attrName) )
        if asType: return "double"
        if asValue: return MPlug.asDouble()


    elif apiType == OpenMaya.MFn.kDoubleAngleAttribute:

        value = MPlug.asFloat()
        MAngle = OpenMaya.MAngle(value)

        if echo: print( "{}: float".format(attrName) )
        if asType: return "float"
        if asValue: return MAngle.asDegrees()


    elif apiType == OpenMaya.MFn.kEnumAttribute:

        if echo: print( "{}: int".format(attrName) )
        if asType: return "int"
        if asValue: return MPlug.asInt()


    elif apiType == OpenMaya.MFn.kTypedAttribute:

        MFnTypedAttribute = OpenMaya.MFnTypedAttribute(MObject)
        attrType = MFnTypedAttribute.attrType()

        if attrType == OpenMaya.MFnData.kString:
            if echo: print( "{}: string".format(attrName) )
            if asType: return "string"
            if asValue: return MPlug.asString()

        elif attrType == OpenMaya.MFnData.kMatrix:
            MFnMatrixData = OpenMaya.MFnMatrixData( MPlug.asMObject() )

            if echo: print( "{}: matrix".format(attrName) )
            if asType: return "matrix"
            if asValue: return MFnMatrixData.matrix()


    elif apiType in [ 
            OpenMaya.MFn.kAttribute2Float,
            OpenMaya.MFn.kAttribute2Double ]:

        result = []
        for index in range( MPlug.numChildren() ):
            value = getAs( MPlug.child(index),
                   asValue=True, echo=echo )
            result.append( value )

        if echo: print( "{}: float2".format(attrName) )
        if asType: return "float2"
        if asValue: return tuple(result)


    elif apiType in [ 
            OpenMaya.MFn.kAttribute3Float,
            OpenMaya.MFn.kAttribute3Double,
            OpenMaya.MFn.kCompoundAttribute ]:

        if not isValidCompound(MPlug):
            return

        result = []
        for index in range( MPlug.numChildren() ):
            value = getAs( MPlug.child(index),
                   asValue=True, echo=echo )
            result.append( value )
        
        typeString = "float3"
        if attribute.isUsedAsColor():
            typeString = "color3f"

        if echo: print( "{}: {}".format(attrName, typeString) )
        if asType: return typeString
        if asValue: return tuple(result)
