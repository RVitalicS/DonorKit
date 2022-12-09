#!/usr/bin/env python

"""
Camera

This module defines functions to work with a Maya camera.
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import toolkit.maya.time as time
from toolkit.maya.scene import getUnits
from typing import Union


def getCurrent () -> OpenMaya.MFnCamera:
    """Get the camera for a current viewport

    Returns:
        A camera object
    """
    MDagPath = OpenMaya.MDagPath()
    if OpenMayaUI.M3dView.numberOf3dViews() > 0:
        M3dView = OpenMayaUI.M3dView.active3dView()
        M3dView.getCamera(MDagPath)
    else:
        MSelectionList = OpenMaya.MSelectionList()
        MSelectionList.add("|persp|perspShape")
        MSelectionList.getDagPath(0, MDagPath)
    return OpenMaya.MFnCamera(MDagPath)


def getSettings (camera: OpenMaya.MFnCamera) -> dict:
    """Get focal length, clipping and aperture
    attributes for the specified camera.
    Scale attribute values for working in metric units.

    Arguments:
        camera: The camera object
    Returns:
        A settings data for the camera
    """
    factor = 1.0
    units = getUnits()
    if units in ["m", "cm", "mm"]:
        factor = 0.01           # UNIT DEPEND
    MDistance = OpenMaya.MDistance(
        camera.verticalFilmAperture(),
        OpenMaya.MDistance.kInches)
    return dict(
        focalLength = camera.focalLength(),
        clipping = [factor * camera.nearClippingPlane(),
                    factor * camera.farClippingPlane()],
        vAperture = MDistance.asMillimeters())


def getAnimation (camera: OpenMaya.MFnCamera,
                  startTime: Union[None, int, float] = None,
                  endTime: Union[None, int, float] = None) -> dict:
    """Get a position and rotation animation data.
    Scale position values for working in metric units.

    Arguments:
        camera: The camera object
        startTime: The start time code of the animation
        endTime: The end time code of the animation
    Returns:
        An animation data for the camera
    """
    factor = 1.0
    units = getUnits()
    if units in ["m", "cm", "mm"]:
        factor = 0.01           # UNIT DEPEND

    # create a node to capture transformations
    parent = camera.parent(0)
    MDagModifier = OpenMaya.MDagModifier()
    sampleObject = MDagModifier.createNode("transform", parent)
    MDagModifier.renameNode(sampleObject, "matrixSample") 
    MDagModifier.doIt()

    MFnDagNode = OpenMaya.MFnDagNode(sampleObject)
    MDagPath = OpenMaya.MDagPath()
    MFnDagNode.getPath(MDagPath)

    # define local functions to get values
    def getTranslate () -> list:
        MMatrix = MDagPath.inclusiveMatrix()
        MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)
        MVector = MTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
        return [MVector.x * factor,
                MVector.y * factor,
                MVector.z * factor]

    def getRotate () -> list:
        MMatrix = MDagPath.inclusiveMatrix()
        MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)
        MQuaternion = MTransformationMatrix.rotation()
        MVector = MQuaternion.asEulerRotation().asVector()
        return [OpenMaya.MAngle(MVector.x).asDegrees(),
                OpenMaya.MAngle(MVector.y).asDegrees(),
                OpenMaya.MAngle(MVector.z).asDegrees()]

    # get data
    translate = time.machine(getTranslate, startTime, endTime)
    rotate    = time.machine(getRotate,    startTime, endTime)
    MDagModifier.deleteNode(sampleObject)

    return dict(translate=translate, rotate=rotate)
