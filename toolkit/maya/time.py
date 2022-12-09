#!/usr/bin/env python

"""
Time

Define functions to manipulate an animation data.
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
from typing import Union
from typing import Callable


def machine (function: Callable,
             startTime: Union[None, int, float] = None,
             endTime: Union[None, int, float] = None) -> dict:
    """Collect a result of the given function execution
    for the specified time range of an animation
    
    Arguments:
        function: The function to get a data for a current frame
    Keyword Arguments:
        startTime: The start time code of the animation
        endTime: The end time code of the animation
    Returns:
        A varying animation data
    """
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


def getTimeNode () -> OpenMaya.MFnDependencyNode:
    """Get the global frame time node
    
    Returns:
        A dependency graph node
    """
    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName("*", MSelectionList)
    for index in range(MSelectionList.length()):
        MObject = OpenMaya.MObject()
        MSelectionList.getDependNode(index, MObject)
        if MObject.apiType() == OpenMaya.MFn.kTime:
            return OpenMaya.MFnDependencyNode(MObject)
