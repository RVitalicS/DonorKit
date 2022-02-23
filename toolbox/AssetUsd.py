#!/usr/bin/env python



import re
import os
import importlib



# define libraries in env. variable
if not os.getenv("ASSETLIBS", ""):
    os.environ["ASSETLIBS"] = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)),
        "examples", "library" )

# use this font in UI
os.environ["FONT_FAMILY"] = "Cantarell"




from pxr import Usd

from Qt import QtGui, QtCore

from widgets import ExportWidget
from widgets import Metadata
from widgets import Settings
from widgets import tools


from . import ostree
from . import scene

importlib.reload(scene)


from . import material
from . import editor
from . import asset


import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMaya as OpenMaya





def UsdExport (
        file,
        exportUVs=1,
        exportSkels="none",
        exportSkin="none",
        exportBlendShapes=0,
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
        exportDisplayColor=0,
        shadingMode="none",
        exportInstances=1,
        exportVisibility=0,
        mergeTransformAndShape=0,
        stripNamespaces=1 ):

    '''
        Runs MEL command to export selected objects to "usd" file
    '''


    # create export options
    options = ';'.join([
        "exportUVs={}".format( exportUVs ),
        "exportSkels={}".format( exportSkels ),
        "exportSkin={}".format( exportSkin ),
        "exportBlendShapes={}".format( exportBlendShapes ),
        "exportColorSets={}".format( exportColorSets ),
        "defaultMeshScheme={}".format( defaultMeshScheme ),
        "defaultUSDFormat={}".format( defaultUSDFormat ),
        "animation={}".format( animation ),
        "eulerFilter={}".format( eulerFilter ),
        "staticSingleSample={}".format( staticSingleSample ),
        "startTime={}".format( startTime ),
        "endTime={}".format( endTime ),
        "frameStride={}".format( frameStride ),
        "frameSample={}".format( frameSample ),
        "parentScope={}".format( parentScope ),
        "exportDisplayColor={}".format( exportDisplayColor ),
        "shadingMode={}".format( shadingMode ),
        "exportInstances={}".format( exportInstances ),
        "exportVisibility={}".format( exportVisibility ),
        "mergeTransformAndShape={}".format( mergeTransformAndShape ),
        "stripNamespaces={}".format( stripNamespaces ) ])

    # create export command
    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format( options ),
        '-typ "USD Export"',
        '-pr',
        '-es "{}"'.format( file ) ])

    # run export command
    OpenMaya.MGlobal.executeCommand(command)





def commandQuery (command, flag):

    result = OpenMaya.MCommandResult()

    command = "{} -query -{}".format(command, flag)
    OpenMaya.MGlobal.executeCommand(command, result)

    if result.resultType() == OpenMaya.MCommandResult.kInt:
        value = OpenMaya.intPtr()
        result.getResult(value)
        return value.value()

    elif result.resultType() == OpenMaya.MCommandResult.kString:
        value = [""]
        result.getResult(value)
        return value[0]





def getDisplayPreferences ():

    command = "displayPref"
    settings = dict()

    for flag in [
        "activeObjectPivots"      ,
        "displayAffected"         ,
        "displayGradient"         ,
        "materialLoadingMode"     ,
        "maxTextureResolution"    ,
        "regionOfEffect"          ,
        "shadeTemplates"          ,
        "textureDrawPixel"        ,
        "wireframeOnShadedActive" ]:

        value = commandQuery(command, flag)

        if not value is None:
            settings[flag] = value

    return settings





def setDisplayPreferences (settings):
    
    command = ['displayPref']

    for flag, value in settings.items():

        if type(value) == str:
            argument = '-{} "{}"'
        else:
            argument = '-{} {}'

        argument = argument.format(flag, value)
        command.append(argument)

    command = " ".join(command)
    OpenMaya.MGlobal.executeCommand(command)





def PlayBlast (
        path, name,
        minTime, maxTime ):

    '''
        Creates viewport preview with defined width and height
        and save it to file
    '''


    displayPreferences = getDisplayPreferences()
    setDisplayPreferences(
        dict(wireframeOnShadedActive="none") )

    View = OpenMayaUI.M3dView.active3dView()
    View.refresh()


    baseName = re.sub(r"\.usd[ac]*$", "", name)
    previewRoot = os.path.join(
        path,
        ostree.SUBDIR_PREVIEWS )

    for assetName in os.listdir(previewRoot):
        if baseName in assetName:

            previewRemove = os.path.join(
                previewRoot, assetName )
            os.remove(previewRemove)


    framename    = "frame"
    filename     = os.path.join(previewRoot, framename)
    framePadding = 3
    compression  = "png"

    width  = Settings.UIsettings.AssetBrowser.Icon.Preview.width
    height = Settings.UIsettings.AssetBrowser.Icon.Preview.height


    Time = OpenMayaAnim.MAnimControl().currentTime()
    timeBefore = Time.value()

    if minTime is None:
        minTime = timeBefore
    if maxTime is None:
        maxTime = timeBefore

    minTime = int(minTime)
    maxTime = int(maxTime)


    command = [
        "playblast",
        "-startTime {}".format(minTime),
        "-endTime {}".format(maxTime),
        "-format image ",
        '-filename "{}"'.format(filename),
        "-sequenceTime 0",
        "-clearCache 1",
        "-viewer 0",
        "-showOrnaments 0",
        "-framePadding {}".format(framePadding),
        "-percent 100",
        "-compression {}".format(compression),
        "-quality 100",
        "-forceOverwrite",
        "-width {}".format(width),
        "-height {}".format(height) ]
    command = " ".join(command)

    OpenMaya.MGlobal.executeCommand(command)


    for frame in range(minTime, maxTime+1):

        padding = "{}".format(framePadding)

        sourceName = "{}/{}.{:0" + padding + "d}.{}"
        sourcePath = sourceName.format(
            previewRoot,
            framename,
            frame,
            compression )
        
        previewName = "{}/{}.f{:0" + padding + "d}.{}"
        previewPath = previewName.format(
            previewRoot,
            baseName,
            frame,
            compression )

        os.rename(sourcePath, previewPath)


    Time.setValue(timeBefore)
    OpenMayaAnim.MAnimControl.setCurrentTime(Time)

    setDisplayPreferences(displayPreferences)





def Export ():


    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

    if not MSelectionList.isEmpty():



        widget = ExportWidget.ExportWidget()
        widget.exec()

        options = widget.getOptions()


        if options:

            version = "v{:02d}".format(options.version)
            units = 0.01



            mayaScene = scene.Manager()
            sceneData = mayaScene.get(getshaders=options.surfacing)

            mayatree = sceneData["tree"]
            shaders  = sceneData["shaders"]
            root     = sceneData["root"]

            if not mayatree:
                OpenMaya.MGlobal.displayWarning(
                    "Wrong Selection")
                return



            if not os.path.exists(options.assetPath):
                os.mkdir(options.assetPath)
            os.chdir(options.assetPath)



            SourceModelPath = os.path.join(
                options.assetPath,
                ostree.SUBDIR_MODELLING,
                "source.geo.usd" )

            ModelFileName = "{}.{}.usdc".format(
                os.path.basename(root), version )

            ModelPath = os.path.join(
                options.assetPath,
                ostree.SUBDIR_MODELLING,
                ModelFileName )

            AnimationFileName = "{}.{}.usdc".format(
                options.animationName, version)

            AnimationPath = os.path.join(
                options.assetPath,
                ostree.SUBDIR_ANIMATION,
                AnimationFileName )



            export = False
            extractModel = False
            extractAnimatioin = False

            if options.modelling:
                if not os.path.exists(ModelPath):
                    export = True
                    extractModel = True
                elif options.modellingOverride:
                    export = True
                    extractModel = True

            if options.animation:
                if not os.path.exists(AnimationPath):
                    export = True
                    extractAnimatioin = True
                elif options.animationOverride:
                    export = True
                    extractAnimatioin = True



            if export:
                ostree.build(options.assetPath, modelling=True)
                UsdExport(
                    SourceModelPath,
                    animation= 1 if options.animation else 0,
                    startTime=options.minTime,
                    endTime=options.maxTime )



            if extractModel:
                if os.path.exists(ModelPath):
                    message = "Model Overwritten: "
                else:
                    message = "Model Saved: "

                OldStage = Usd.Stage.Open(SourceModelPath)
                NewStage = Usd.Stage.CreateNew(ModelPath)
                editor.copyStage(
                    OldStage,
                    NewStage,
                    root=root, units=units)

                editor.addMayaAttributes(NewStage, mayatree)
                NewStage.GetRootLayer().Export(
                    ModelPath, args=dict(format="usdc") )

                OpenMaya.MGlobal.displayInfo(message + ModelFileName)



            if extractAnimatioin:
                ostree.build(options.assetPath, animation=True)

                if os.path.exists(AnimationPath):
                    message = "Animation Overwritten: "
                else:
                    message = "Animation Saved: "

                OldStage = Usd.Stage.Open(SourceModelPath)
                NewStage = Usd.Stage.CreateNew(AnimationPath)
                editor.copyAnimation(
                    OldStage,
                    NewStage,
                    root=root, reference=ModelPath, units=units )

                NewStage.GetRootLayer().Export(
                    AnimationPath, args=dict(format="usdc") )

                OpenMaya.MGlobal.displayInfo(message + AnimationFileName)


            if os.path.exists(SourceModelPath):
                os.remove(SourceModelPath)



            if options.surfacing and shaders:
                ostree.build(options.assetPath, surfacing=True)

                for name, data in shaders.items():
                    for key in ["render", "preview"]:

                        ShaderData = data[key]

                        if key == "render":
                            prman=True
                            ShaderFileName = "{}.{}.RenderMan.usda".format(
                                name, version )

                        else:
                            prman=False
                            ShaderFileName = "{}.{}.usda".format(
                                name, version )

                        ShaderPath = os.path.join(
                            options.assetPath,
                            ostree.SUBDIR_SURFACING,
                            ShaderFileName )

                        if os.path.exists(ShaderPath):
                            message = "Shader Overwritten: "
                        else:
                            message = "Shader Saved: "

                        if ShaderData:
                            ShaderData["name"] = name
                            material.make(
                                ShaderPath,
                                ShaderData,
                                prman=prman)

                            OpenMaya.MGlobal.displayInfo(message + ShaderFileName)



            ReferencePath = AnimationPath if options.animation else ModelPath
            if os.path.exists(ReferencePath):

                AssetPath = os.path.join(
                    options.assetPath,
                    options.assetName )

                if os.path.exists(AssetPath):
                    message = "Asset Overwritten: "
                else:
                    message = "Asset Saved: "

                asset.make (
                    ReferencePath,
                    AssetPath,
                    mayatree )


                # Create/Update Symbolic Link
                if options.final:

                    if os.path.exists(options.assetFinal):
                        os.remove(options.assetFinal)

                    os.symlink(
                        options.assetName,
                        options.assetFinal )


                # Create/Update .metadata.json
                with Metadata.MetadataManager(options.assetPath, "usdasset") as data:
                    data["published"] = tools.getTimeCode()


                # Create Preview Image
                if os.path.exists(AssetPath):
                    ostree.build(options.assetPath, previews=True)

                    minTime = None
                    maxTime = None
                    if options.animation:
                        minTime = options.minTime
                        maxTime = options.maxTime

                    PlayBlast(
                        options.assetPath,
                        options.assetName,
                        minTime, maxTime )



                OpenMaya.MGlobal.displayInfo(message + options.assetName)



    else:
        OpenMaya.MGlobal.displayWarning(
            "Select Any Object")
