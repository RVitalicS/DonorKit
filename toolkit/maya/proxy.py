#!/usr/bin/env python

"""
Proxy

The module to manage a geometry for a preview purpose.
"""

import re
import maya.cmds as mayaCommand
from toolkit.maya import export


def generate (path: str, threshold: float = 0.8) -> None:
    """Create a USD file from simplified polygonal objects
    by reducing geometry while preserving the overall shape of the mesh

    Arguments:
        path: The path to save a USD file
    Keyword Arguments:
        threshold: The value that specifies how many vertices
                   to remove during reduction
                   as a unit interval of the original mesh
    """

    # get selection
    sourceDagPath = mayaCommand.ls(selection=True, long=True)[0]
    sourceName = mayaCommand.ls(selection=True, long=False)[0]
    copyDagPath = re.sub(
        f"{sourceName}$", f":proxy:{sourceName}", sourceDagPath)

    # duplicate mesh and create namespace
    if not mayaCommand.namespace(exists=":proxy"):
        mayaCommand.namespace(addNamespace=":proxy")
        mayaCommand.namespace(setNamespace=":proxy")
    mayaCommand.duplicate(name=copyDagPath)

    # remesh and sharp edges
    mayaCommand.select(copyDagPath, hierarchy=True)
    for shape in mayaCommand.ls(
            exactType="mesh", selection=True, long=True):
        mayaCommand.select(shape)
        if threshold < 1.0:
            mayaCommand.polyReduce(
                version=1,
                termination=0,
                sharpness=0.0,
                keepMapBorder=False,
                keepColorBorder=False,
                keepFaceGroupBorder=False,
                keepHardEdge=False,
                keepCreaseEdge=False,
                keepBorder=True,
                keepBorderWeight=1.0,
                useVirtualSymmetry=0,
                preserveTopology=True,
                keepQuadsWeight=1.0,
                cachingReduce=True,
                constructionHistory=True,
                percentage=(1-threshold)*100,
                replaceOriginal=True)
        mayaCommand.polySoftEdge(
            angle=0.0, constructionHistory=True)
        mayaCommand.delete(constructionHistory=True)

    # export
    mayaCommand.select(copyDagPath, hierarchy=False)
    export.USD(path, exportUVs=0, exportColorSets=0,
               defaultMeshScheme="none", animation=0, shading=False)

    # remove mesh and namespace
    mayaCommand.delete(copyDagPath)
    mayaCommand.namespace(setNamespace=":")
    mayaCommand.namespace(removeNamespace=":proxy", force=True)

    # select source mesh
    mayaCommand.select(sourceDagPath)
