#!/usr/bin/env python


import maya.api.OpenMaya as OpenMayaAPI





def USD (
        file,
        exportUVs=1,
        exportSkels="none",
        exportSkin="none",
        exportBlendShapes=0,
        exportDisplayColor=0,
        exportColorSets=1,
        defaultMeshScheme="none",
        defaultUSDFormat="usdc",
        animation=0,
        eulerFilter=0,
        staticSingleSample=0,
        startTime=1,
        endTime=1,
        frameStride=1,
        frameSample=0.0,
        parentScope="",
        shading=False,
        exportInstances=1,
        exportVisibility=0,
        mergeTransformAndShape=0,
        stripNamespaces=1 ):

    """
        Runs MEL command to export
        selected objects to "USD" file
    """


    if shading:
        shadingOptions = (
            "shadingMode=useRegistry;" +
            "convertMaterialsTo=[" +
                "UsdPreviewSurface," +
                "rendermanForMaya]")
    else:
        shadingOptions = ("shadingMode=none")


    # create export options
    options = ';'.join([
        'exportUVs={}'.format( exportUVs ),
        'exportSkels={}'.format( exportSkels ),
        'exportSkin={}'.format( exportSkin ),
        'exportBlendShapes={}'.format( exportBlendShapes ),
        'exportDisplayColor={}'.format( exportDisplayColor ),
        'exportColorSets={}'.format( exportColorSets ),
        'defaultMeshScheme={}'.format( defaultMeshScheme ),
        'defaultUSDFormat={}'.format( defaultUSDFormat ),
        'animation={}'.format( animation ),
        'eulerFilter={}'.format( eulerFilter ),
        'staticSingleSample={}'.format( staticSingleSample ),
        'startTime={}'.format( startTime ),
        'endTime={}'.format( endTime ),
        'frameStride={}'.format( frameStride ),
        'frameSample={}'.format( frameSample ),
        'parentScope={}'.format( parentScope ),
        shadingOptions,
        'exportInstances={}'.format( exportInstances ),
        'exportVisibility={}'.format( exportVisibility ),
        'mergeTransformAndShape={}'.format( mergeTransformAndShape ),
        'stripNamespaces={}'.format( stripNamespaces ) ])

    # create export command
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format(options),
        '-type "USD Export"',
        '-preserveReferences',
        '-exportSelected',
        '"{}"'.format(file) ])

    # run export command
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)





def Maya (file, binary=True):

    """
        Runs MEL command to export
        selected objects to "Maya" file
    """


    # create export command
    command = ' '.join([
        'file',
        '-force',
        '-options "v=1;"',
        '-type "{}"'.format(
            'mayaBinary' if binary else 'mayaAscii'),
        '-preserveReferences',
        '-exportUnloadedReferences',
        '-exportSelected',
        '"{}"'.format(file) ])

    # run export command
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)





def RIB (file):

    """
        Runs MEL command to export
        selected objects to "RIB" file
    """


    # create export options
    options = ';'.join([
        'rmanExportRIBFormat=0' ,
        'rmanExportMultipleFrames=0' ,
        'rmanExportByFrame=1' ,
        'rmanExportRIBArchive=0' ])

    # create export command
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format(options),
        '-type "RIB"',
        '-preserveReferences',
        '-exportUnloadedReferences',
        '-exportSelected',
        '"{}"'.format(file) ])

    # run export command
    OpenMayaAPI.MGlobal.executeCommandStringResult(command)
