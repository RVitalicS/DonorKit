#!/usr/bin/env python



import time
import re
import os
import ctypes



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
from . import mayatree

from . import usdmaterial
from . import usdeditor
from . import usdasset


import maya.OpenMayaUI as OpenMayaUI
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





def ViewportShot (path, width, height):

    '''
        Creates viewport preview with defined width and height
        and save it to file
    '''
    
    
    view = OpenMayaUI.M3dView.active3dView()
    view.refresh()

    viewWidth = view.portWidth()
    viewHeight = view.portHeight()

    buffer = OpenMaya.MImage()
    view.readColorBuffer(buffer, False)


    pointer = ctypes.cast( int(buffer.pixels()), ctypes.POINTER(ctypes.c_char) )
    pointerAsString = ctypes.string_at(pointer, viewWidth * viewHeight * 4)

    image = QtGui.QImage(
        pointerAsString,
        viewWidth, viewHeight,
        QtGui.QImage.Format_RGB32 )

    image = image.mirrored(horizontal=False, vertical=True)


    if image.width() > width:
        scaledImage = image.scaledToHeight(
            height, QtCore.Qt.SmoothTransformation)

        x = int((scaledImage.width() - width)/2)
        scaledImage = scaledImage.copy(x, 0, width, height)
        scaledImage.save(path)


    elif image.height() > height:
        scaledImage = image.scaledToWidth(
            width, QtCore.Qt.SmoothTransformation)

        y = int((scaledImage.height() - height)/2)
        scaledImage = scaledImage.copy(0, y, width, height)
        scaledImage.save(path)





def Export ():


    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

    if not MSelectionList.isEmpty():



        widget = ExportWidget.ExportWidget()

        # CAN CAUSE FATAL ERROR ON SECOND RUN
        widget.exec()

        options = widget.getOptions()
        widget = None


        if options:

            version = "v{:02d}".format(options.version)
            units = 0.01 * options.unitsMultiplier



            # ALARM ALARM ALARM
            start = time.time()
            scene = mayatree.get(getshaders=options.surfacing)
            end = time.time()
            print("\nGot Scene Data for {} sec.\n".format(end - start) )

            treedata  = scene["data"]
            shaders = scene["shaders"]
            root    = scene["root"]

            if not treedata:
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
                    startTime=options.startFrame,
                    endTime=options.endFrame )



            if extractModel:
                if os.path.exists(ModelPath):
                    message = "Model Overwritten: "
                else:
                    message = "Model Saved: "

                OldStage = Usd.Stage.Open(SourceModelPath)
                NewStage = Usd.Stage.CreateNew(ModelPath)
                usdeditor.copyStage(
                    OldStage,
                    NewStage,
                    root=root, units=units)

                usdeditor.addMayaAttributes(NewStage, treedata)
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
                usdeditor.copyAnimation(
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
                            ShaderFileName = "{}.RenderMan.{}.usda".format(
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
                            usdmaterial.make(
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

                usdasset.make (
                    ReferencePath,
                    AssetPath,
                    treedata )


                # Create/Update Symbolic Link
                if options.final:

                    if os.path.exists(options.assetFinal):
                        os.remove(options.assetFinal)

                    os.symlink(
                        options.assetName,
                        options.assetFinal )


                # Create Preview Image
                if os.path.exists(AssetPath):

                    command = 'displayPref -wsa "none";'
                    OpenMaya.MGlobal.executeCommand(command)

                    ostree.build(options.assetPath, previews=True)

                    PreviewPath = os.path.join(
                        options.assetPath,
                        ostree.SUBDIR_PREVIEWS,
                        options.assetPreview )

                    ViewportShot(PreviewPath,
                        Settings.UIsettings.AssetBrowser.Icon.Asset.max.width,
                        Settings.UIsettings.AssetBrowser.Icon.Asset.max.height )

                    command = 'displayPref -wsa "full";'
                    OpenMaya.MGlobal.executeCommand(command)


                # Create/Update .metadata.json
                with Metadata.MetadataManager(options.assetPath, "usdasset") as data:
                    data["published"] = tools.getTimeCode()



                OpenMaya.MGlobal.displayInfo(message + options.assetName)



    else:
            OpenMaya.MGlobal.displayWarning(
                "Select Any Object")
