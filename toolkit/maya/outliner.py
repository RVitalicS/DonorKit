#!/usr/bin/env python

import maya.OpenMaya as OpenMaya





def refresh ():
    
    command = """
        melOptions -duplicateVariableWarnings false;

        string $intersector = `stringArrayIntersector`;
        stringArrayIntersector -edit -intersect `getPanel -visiblePanels` $intersector;
        stringArrayIntersector -edit -intersect `getPanel -type outlinerPanel` $intersector;
        string $outliners[] = `stringArrayIntersector -query $intersector`;

        for ($i = 0; $i < `size $outliners`; $i++) {
            outlinerEditor -edit -refresh $outliners[$i];
        }"""

    OpenMaya.MGlobal.executeCommand(command)





def getSelectionName ():

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

    if MSelectionList.isEmpty(): return

    MDagPath = OpenMaya.MDagPath()
    MSelectionList.getDagPath(0, MDagPath)

    return MDagPath.partialPathName()