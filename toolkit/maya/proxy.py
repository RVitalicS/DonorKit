#!/usr/bin/env python

import re

import maya.cmds as mayaCommand
from toolkit.maya import export




def generate (path, threshold=0.8):
        
    # get selection
    sourceDagPath = mayaCommand.ls(selection=True, long=True)[0]
    sourceName = mayaCommand.ls(selection=True, long=False)[0]

    copyDagPath = re.sub( f"{sourceName}$",
        f":proxy:{sourceName}", sourceDagPath )

    # create namespace
    if not mayaCommand.namespace(exists=":proxy"):
        mayaCommand.namespace(addNamespace=":proxy")
        mayaCommand.namespace(setNamespace=":proxy")

    # duplicate
    mayaCommand.duplicate(name=copyDagPath)

    # remesh & sharp edges
    mayaCommand.select(copyDagPath, hierarchy=True)
    for shape in mayaCommand.ls(
            exactType="mesh", selection=True, long=True):

        mayaCommand.select(shape)
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
            angle=0.0, constructionHistory=True )
        mayaCommand.delete(constructionHistory=True)

    # export
    mayaCommand.select(copyDagPath, hierarchy=False)
    export.USD(path,
        defaultUSDFormat="usda",
        exportUVs=0, exportColorSets=0,
        defaultMeshScheme="none",
        animation=0, shading=False )

    # remove mesh
    mayaCommand.delete(copyDagPath)

    # remove namespace
    mayaCommand.namespace(setNamespace=":")
    mayaCommand.namespace(removeNamespace=":proxy", force=True)

    # select source mesh
    mayaCommand.select(sourceDagPath)
