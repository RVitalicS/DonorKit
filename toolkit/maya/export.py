#!/usr/bin/env python

"""
Export

This module defines functions to export objects from a Maya scene.
"""

import maya.api.OpenMaya as OpenMayaAPI


def USD (file: str, exportUVs: int = 1,
         exportSkels: str = "none",
         exportSkin: str = "none",
         exportBlendShapes: int = 0,
         exportDisplayColor: int = 0,
         exportColorSets: int = 1,
         defaultMeshScheme: str = "none",
         defaultUSDFormat: str = "usdc",
         animation: int = 0,
         eulerFilter: int = 0,
         staticSingleSample: int = 0,
         startTime: int = 1,
         endTime: int = 1,
         frameStride: int = 1,
         frameSample: float = 0.0,
         parentScope: str = "",
         shading: bool = False,
         exportInstances: int = 1,
         exportVisibility: int = 0,
         mergeTransformAndShape: int = 0,
         stripNamespaces: int = 1) -> None:
    """Run MEL command to export selected objects to USD file

    Arguments:
        file: The path to save a USD file
    Keyword Arguments:
        **kwargs: The optional export arguments
    """
    if shading:
        shadingOptions = (
            "shadingMode=useRegistry;"
          + "convertMaterialsTo=["
              + "UsdPreviewSurface,rendermanForMaya]")
    else:
        shadingOptions = ("shadingMode=none")
    options = ';'.join([
        'exportUVs={}'.format(exportUVs),
        'exportSkels={}'.format(exportSkels),
        'exportSkin={}'.format(exportSkin),
        'exportBlendShapes={}'.format(exportBlendShapes),
        'exportDisplayColor={}'.format(exportDisplayColor),
        'exportColorSets={}'.format(exportColorSets),
        'defaultMeshScheme={}'.format(defaultMeshScheme),
        'defaultUSDFormat={}'.format(defaultUSDFormat),
        'animation={}'.format(animation),
        'eulerFilter={}'.format(eulerFilter),
        'staticSingleSample={}'.format(staticSingleSample),
        'startTime={}'.format(startTime),
        'endTime={}'.format(endTime),
        'frameStride={}'.format(frameStride),
        'frameSample={}'.format(frameSample),
        'parentScope={}'.format(parentScope),
        shadingOptions,
        'exportInstances={}'.format(exportInstances),
        'exportVisibility={}'.format(exportVisibility),
        'mergeTransformAndShape={}'.format(mergeTransformAndShape),
        'stripNamespaces={}'.format(stripNamespaces) ])
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format(options),
        '-type "USD Export"',
        '-preserveReferences',
        '-exportSelected',
        '"{}"'.format(file) ])
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)


def Maya (file: str, binary: bool = True) -> None:
    """Runs MEL command to export selected objects to a Maya file

    Arguments:
        file: The path to save a Maya file 
    Keyword Arguments:
        binary: The type of Maya file
    """
    command = ' '.join([
        'file',
        '-force',
        '-options "v=1;"',
        '-type "{}"'.format(
            'mayaBinary' if binary else 'mayaAscii'),
        '-preserveReferences',
        '-exportUnloadedReferences',
        '-exportSelected',
        '"{}"'.format(file)])
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)


def RIB (file: str) -> None:
    """Runs MEL command to export selected objects to a RIB file

    Arguments:
        file: The path to save a RIB file 
    """
    options = ';'.join([
        'rmanExportRIBFormat=0' ,
        'rmanExportMultipleFrames=0' ,
        'rmanExportByFrame=1' ,
        'rmanExportRIBArchive=0' ])
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format(options),
        '-type "RIB"',
        '-preserveReferences',
        '-exportUnloadedReferences',
        '-exportSelected',
        '"{}"'.format(file) ])
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)
