#!/usr/bin/env python



import os
import re

import toolkit.system.ostree
from widgets import Settings

import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim





def commandQuery (command, flag):

    result = OpenMaya.MCommandResult()

    command = "{} -query -{}".format(command, flag)
    OpenMaya.MGlobal.executeCommand(command, result)

    if result.resultType() == OpenMaya.MCommandResult.kInt:
        value = OpenMaya.intPtr()
        result.getResult(value)
        return value.value()

    elif result.resultType() == OpenMaya.MCommandResult.kString:
        value = [""]
        result.getResult(value)
        return value[0]





def UsdExport (
        file,
        exportUVs=1,
        exportSkels="none",
        exportSkin="none",
        exportBlendShapes=0,
        exportColorSets=1,
        defaultMeshScheme="none",
        defaultUSDFormat="usdc",
        animation=0,
        eulerFilter=0,
        staticSingleSample=0,
        startTime=1,
        endTime=1,
        frameStride=1,
        frameSample=0.0,
        parentScope="",
        exportDisplayColor=0,
        shadingMode="none",
        exportInstances=1,
        exportVisibility=0,
        mergeTransformAndShape=0,
        stripNamespaces=1 ):

    """
        Runs MEL command to export selected objects to "usd" file
    """


    # create export options
    options = ';'.join([
        "exportUVs={}".format( exportUVs ),
        "exportSkels={}".format( exportSkels ),
        "exportSkin={}".format( exportSkin ),
        "exportBlendShapes={}".format( exportBlendShapes ),
        "exportColorSets={}".format( exportColorSets ),
        "defaultMeshScheme={}".format( defaultMeshScheme ),
        "defaultUSDFormat={}".format( defaultUSDFormat ),
        "animation={}".format( animation ),
        "eulerFilter={}".format( eulerFilter ),
        "staticSingleSample={}".format( staticSingleSample ),
        "startTime={}".format( startTime ),
        "endTime={}".format( endTime ),
        "frameStride={}".format( frameStride ),
        "frameSample={}".format( frameSample ),
        "parentScope={}".format( parentScope ),
        "exportDisplayColor={}".format( exportDisplayColor ),
        "shadingMode={}".format( shadingMode ),
        "exportInstances={}".format( exportInstances ),
        "exportVisibility={}".format( exportVisibility ),
        "mergeTransformAndShape={}".format( mergeTransformAndShape ),
        "stripNamespaces={}".format( stripNamespaces ) ])

    # create export command
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format( options ),
        '-typ "USD Export"',
        '-pr',
        '-es "{}"'.format( file ) ])

    # run export command
    OpenMaya.MGlobal.executeCommand(command)





def viewportMessage (text):

    command = ' '.join([
        'inViewMessage',
        '-fade',
        '-position "botCenter"',
        '-assistMessage "{}"'.format(text) ])

    OpenMaya.MGlobal.executeCommand(command)





def getDisplayPreferences ():

    command = "displayPref"
    settings = dict()

    for flag in [
        "activeObjectPivots"      ,
        "displayAffected"         ,
        "displayGradient"         ,
        "materialLoadingMode"     ,
        "maxTextureResolution"    ,
        "regionOfEffect"          ,
        "shadeTemplates"          ,
        "textureDrawPixel"        ,
        "wireframeOnShadedActive" ]:

        value = commandQuery(command, flag)

        if not value is None:
            settings[flag] = value

    return settings





def setDisplayPreferences (settings):
    
    command = ['displayPref']

    for flag, value in settings.items():

        if type(value) == str:
            argument = '-{} "{}"'
        else:
            argument = '-{} {}'

        argument = argument.format(flag, value)
        command.append(argument)

    command = " ".join(command)
    OpenMaya.MGlobal.executeCommand(command)





def PlayBlast (
        path, name,
        minTime, maxTime ):

    """
        Creates viewport preview with defined width and height
        and save it to file
    """


    baseName = re.sub(r"\.usd[ac]*$", "", name)
    previewRoot = os.path.join(
        path,
        toolkit.system.ostree.SUBDIR_PREVIEWS )

    for assetName in os.listdir(previewRoot):
        if baseName in assetName:

            previewRemove = os.path.join(
                previewRoot, assetName )
            os.remove(previewRemove)


    framename    = "frame"
    filename     = os.path.join(previewRoot, framename)
    framePadding = 3
    compression  = "png"

    width  = Settings.UIGlobals.AssetBrowser.Icon.Preview.width
    height = Settings.UIGlobals.AssetBrowser.Icon.Preview.height


    Time = OpenMayaAnim.MAnimControl().currentTime()
    timeBefore = Time.value()

    if minTime is None:
        minTime = timeBefore
    if maxTime is None:
        maxTime = timeBefore

    minTime = int(minTime)
    maxTime = int(maxTime)


    displayPreferences = getDisplayPreferences()
    setDisplayPreferences(
        dict(wireframeOnShadedActive="none") )

    View = OpenMayaUI.M3dView.active3dView()
    View.refresh()

    command = [
        "playblast",
        "-startTime {}".format(minTime),
        "-endTime {}".format(maxTime),
        "-format image ",
        '-filename "{}"'.format(filename),
        "-sequenceTime 0",
        "-clearCache 1",
        "-viewer 0",
        "-showOrnaments 0",
        "-framePadding {}".format(framePadding),
        "-percent 100",
        "-compression {}".format(compression),
        "-quality 100",
        "-forceOverwrite",
        "-width {}".format(width),
        "-height {}".format(height) ]
    command = " ".join(command)

    OpenMaya.MGlobal.executeCommand(command)

    setDisplayPreferences(displayPreferences)
    View.refresh()


    for frame in range(minTime, maxTime+1):

        padding = "{}".format(framePadding)

        sourceName = "{}/{}.{:0" + padding + "d}.{}"
        sourcePath = sourceName.format(
            previewRoot,
            framename,
            frame,
            compression )
        
        previewName = "{}/{}.f{:0" + padding + "d}.{}"
        previewPath = previewName.format(
            previewRoot,
            baseName,
            frame,
            compression )

        os.rename(sourcePath, previewPath)


    Time.setValue(timeBefore)
    OpenMayaAnim.MAnimControl.setCurrentTime(Time)





def getNodeByName (name):

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    
    if MSelectionList.isEmpty(): return

    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)

    MObject = MDagPath.node()
    node = OpenMaya.MFnDependencyNode(MObject)
    
    return node





def getShaderByName (name):

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(
        name, MSelectionList)
    
    if MSelectionList.isEmpty(): return

    MPlug = OpenMaya.MPlug()
    MSelectionList.getPlug(0, MPlug)

    MObject = MPlug.node()
    shader = OpenMaya.MFnDependencyNode(MObject)
    
    return shader





def getNodeAttribute (node, name):
    
    for index in range(node.attributeCount()):

        MObject = node.attribute(index)
        attribute = OpenMaya.MFnAttribute(MObject)

        attrName = attribute.name()
        if attrName == name:
            MPlug = node.findPlug(attrName)

            return MPlug





def getNodeAttributeValue (node, name):

    attribute = getNodeAttribute(node, name)
    attributeValue = getMPlugAs(attribute, asValue=True)
    
    return attributeValue





def isAttributeAnimated (node, name):

    attribute = getNodeAttribute(node, name)
    MObject = attribute.node()
    
    return OpenMayaAnim.MAnimUtil.isAnimated(MObject)





def getMPlugAs ( MPlug,
        asValue = False ,
        asType  = False ,
        echo    = False ):


    MObject = MPlug.attribute()

    attribute = OpenMaya.MFnAttribute(MObject)
    attrName  = attribute.name()

    apiType = MObject.apiType()
    if echo: print( "[API Type] {}: {}".format(attrName, apiType) )

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

            value = getMPlugAs( MPlug.child(index),
                   asValue=True, echo=echo )
            result.append( value )

        if echo: print( "{}: float2".format(attrName) )
        if asType: return "float2"
        if asValue: return tuple(result)


    elif apiType in [ 
        OpenMaya.MFn.kAttribute3Float,
        OpenMaya.MFn.kAttribute3Double,
        OpenMaya.MFn.kCompoundAttribute ]:

        result = []
        for index in range( MPlug.numChildren() ):

            value = getMPlugAs( MPlug.child(index),
                   asValue=True, echo=echo )
            result.append( value )
        

        typeString = "float3"
        if attribute.isUsedAsColor():
            typeString = "color3f"

        if echo: print( "{}: {}".format(attrName, typeString) )
        if asType: return typeString
        if asValue: return tuple(result)





def timeMachine (function, startTime=None, endTime=None):

    collector = dict()


    Time = OpenMayaAnim.MAnimControl().currentTime()
    timeBefore = Time.value()

    if startTime is None:
        startTime = timeBefore
    if endTime is None:
        endTime = timeBefore

    startTime = int(startTime)
    endTime = int(endTime)

    for frame in range(startTime, endTime+1):
        Time.setValue(frame)
        OpenMayaAnim.MAnimControl.setCurrentTime(Time)

        collector[frame] = function()

    Time.setValue(timeBefore)
    OpenMayaAnim.MAnimControl.setCurrentTime(Time)


    return collector





def getCurrentCamera ():

    M3dView = OpenMayaUI.M3dView.active3dView()
    MDagPath = OpenMaya.MDagPath()
    M3dView.getCamera(MDagPath)

    return OpenMaya.MFnCamera(MDagPath)





def getCurrentCameraSettings ():

    factor = 1.0
    units = commandQuery("currentUnit", "linear")
    if units == "m":
        factor = 0.01


    camera = getCurrentCamera()

    MDistance = OpenMaya.MDistance(
        camera.verticalFilmAperture(),
        OpenMaya.MDistance.kInches )

    return dict(
        focalLength = camera.focalLength(),
        clipping = [
            factor * camera.nearClippingPlane(),
            factor * camera.farClippingPlane() ],
        vAperture = MDistance.asMillimeters() )





def getCurrentCameraAnimation (startTime=None, endTime=None):

    factor = 1.0
    units = commandQuery("currentUnit", "linear")
    if units == "m":
        factor = 0.01


    parent = getCurrentCamera().parent(0)

    MDagModifier = OpenMaya.MDagModifier()
    sampleObject = MDagModifier.createNode("transform", parent)
    MDagModifier.renameNode( sampleObject, "matrixSample" ) 
    MDagModifier.doIt()


    MFnDagNode = OpenMaya.MFnDagNode(sampleObject)
    MDagPath = OpenMaya.MDagPath()
    MFnDagNode.getPath(MDagPath)


    def getTranslate ():

        MMatrix = MDagPath.inclusiveMatrix()
        MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)

        MVector = MTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
        return [
            MVector.x * factor ,
            MVector.y * factor ,
            MVector.z * factor ]

    def getRotate ():

        MMatrix = MDagPath.inclusiveMatrix()
        MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)

        MQuaternion = MTransformationMatrix.rotation()
        MVector = MQuaternion.asEulerRotation().asVector()

        return [
            OpenMaya.MAngle(MVector.x).asDegrees(),
            OpenMaya.MAngle(MVector.y).asDegrees(),
            OpenMaya.MAngle(MVector.z).asDegrees()]


    translate = timeMachine(getTranslate, startTime, endTime)
    rotate    = timeMachine(getRotate,    startTime, endTime)

    MDagModifier.deleteNode(sampleObject)


    return dict( translate=translate, rotate=rotate )
