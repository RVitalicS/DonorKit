#!/usr/bin/env python

import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

import toolkit.maya.time
from toolkit.maya.scene import getUnits





def getCurrent ():

    M3dView = OpenMayaUI.M3dView.active3dView()
    MDagPath = OpenMaya.MDagPath()
    M3dView.getCamera(MDagPath)

    return OpenMaya.MFnCamera(MDagPath)





def getSettings (camera):

    factor = 1.0
    units = getUnits()
    if units in ["m", "cm", "mm"]:
        factor = 0.01           # UNIT DEPEND


    MDistance = OpenMaya.MDistance(
        camera.verticalFilmAperture(),
        OpenMaya.MDistance.kInches )

    return dict(
        focalLength = camera.focalLength(),
        clipping = [
            factor * camera.nearClippingPlane(),
            factor * camera.farClippingPlane() ],
        vAperture = MDistance.asMillimeters() )





def getAnimation (camera, startTime=None, endTime=None):

    factor = 1.0
    units = getUnits()
    if units in ["m", "cm", "mm"]:
        factor = 0.01           # UNIT DEPEND


    parent = camera.parent(0)

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


    translate = toolkit.maya.time.machine(getTranslate, startTime, endTime)
    rotate    = toolkit.maya.time.machine(getRotate,    startTime, endTime)

    MDagModifier.deleteNode(sampleObject)


    return dict( translate=translate, rotate=rotate )
