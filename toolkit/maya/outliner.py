#!/usr/bin/env python

"""
Outliner

This module defines functions to work with a Maya outliner.
"""

import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya
from typing import Union


def refresh () -> None:
    """Cause an outliner to refresh itself"""
    command = """
        melOptions -duplicateVariableWarnings false;
        string $intersector = `stringArrayIntersector`;
        stringArrayIntersector -edit -intersect `getPanel -visiblePanels` $intersector;
        stringArrayIntersector -edit -intersect `getPanel -type outlinerPanel` $intersector;
        string $outliners[] = `stringArrayIntersector -query $intersector`;
        for ($i = 0; $i < `size $outliners`; $i++) {
            outlinerEditor -edit -refresh $outliners[$i]; }"""
    OpenMaya.MGlobal.executeCommand(command)


def getSelectionName () -> Union[str, None]:
    """Get a name of a current selected object

    Returns:
        An object name
    """
    selection = mayaCommand.ls(selection=True)
    if not selection:
        return
    node = selection[0]
    if mayaCommand.nodeType(node) in ["transform", "mesh"]:
        return node
