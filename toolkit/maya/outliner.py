#!/usr/bin/env python

import maya.cmds as mayaCommand
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

    selection = mayaCommand.ls(selection=True)
    if not selection: return

    node = selection[0]
    if mayaCommand.nodeType(node) in ["transform", "mesh"]:
        return node
