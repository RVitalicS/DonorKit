#!/usr/bin/env python

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim





def machine (function, startTime=None, endTime=None):

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





def getTimeNode ():

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName("*", MSelectionList)

    for index in range( MSelectionList.length() ):
        MObject = OpenMaya.MObject()
        MSelectionList.getDependNode(index, MObject)
        
        if MObject.apiType() == OpenMaya.MFn.kTime:
            return OpenMaya.MFnDependencyNode(MObject)
