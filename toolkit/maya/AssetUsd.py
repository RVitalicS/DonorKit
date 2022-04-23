#!/usr/bin/env python



import re
import os
import importlib


from pxr import Usd

from widgets import (
    UsdExport,
    Metadata)


import toolkit.core.timing
import toolkit.system.ostree
import toolkit.maya.scene
import toolkit.maya.misc

importlib.reload(toolkit.maya.scene)

import toolkit.usd.material
import toolkit.usd.editor
import toolkit.usd.asset
import toolkit.usd.imaging


import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim





def Export ():


    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

    if MSelectionList.isEmpty():
        text = "Select Any Object"
        OpenMaya.MGlobal.displayWarning(text)
        toolkit.maya.misc.viewportMessage(text)
        return


    dialog = UsdExport.Dialog()
    dialog.exec()

    options = dialog.getOptions()
    if not options:
        return



    version = "v{:02d}".format(options.version)
    if options.variant:
        version += "-{}".format(options.variant)
    
    units = 0.01



    mayaScene = toolkit.maya.scene.Manager()
    sceneData = mayaScene.get(getshaders=options.surfacing)

    mayatree = sceneData["tree"]
    shaders  = sceneData["shaders"]
    root     = sceneData["root"]

    if not mayatree:
        text = "Wrong Selection"
        OpenMaya.MGlobal.displayWarning(text)
        toolkit.maya.misc.viewportMessage(text)
        return



    if not os.path.exists(options.assetPath):
        os.mkdir(options.assetPath)
    os.chdir(options.assetPath)



    SourceModelPath = os.path.join(
        options.assetPath,
        toolkit.system.ostree.SUBDIR_MODELLING,
        "source.geo.usd" )

    ModelFileName = "{}.{}.usdc".format(
        os.path.basename(root), version )

    ModelPath = os.path.join(
        options.assetPath,
        toolkit.system.ostree.SUBDIR_MODELLING,
        ModelFileName )

    AnimationFileName = "{}.{}.usdc".format(
        options.animationName, version)

    AnimationPath = os.path.join(
        options.assetPath,
        toolkit.system.ostree.SUBDIR_ANIMATION,
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
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, modelling=True)
        toolkit.maya.misc.UsdExport(
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
        toolkit.usd.editor.copyStage(
            OldStage,
            NewStage,
            root=root, units=units)

        toolkit.usd.editor.addMayaAttributes(NewStage, mayatree)
        NewStage.GetRootLayer().Export(
            ModelPath, args=dict(format="usdc") )

        OpenMaya.MGlobal.displayInfo(message + ModelFileName)



    if extractAnimatioin:
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, animation=True)

        if os.path.exists(AnimationPath):
            message = "Animation Overwritten: "
        else:
            message = "Animation Saved: "

        OldStage = Usd.Stage.Open(SourceModelPath)
        NewStage = Usd.Stage.CreateNew(AnimationPath)
        toolkit.usd.editor.copyAnimation(
            OldStage,
            NewStage,
            root=root, reference=ModelPath, units=units )

        NewStage.GetRootLayer().Export(
            AnimationPath, args=dict(format="usdc") )

        OpenMaya.MGlobal.displayInfo(message + AnimationFileName)


    if os.path.exists(SourceModelPath):
        os.remove(SourceModelPath)



    if options.surfacing and shaders:
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, surfacing=True)

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
                    toolkit.system.ostree.SUBDIR_SURFACING,
                    ShaderFileName )

                if os.path.exists(ShaderPath):
                    message = "Shader Overwritten: "
                else:
                    message = "Shader Saved: "

                if ShaderData.get("shaders"):
                    ShaderData["name"] = name
                    toolkit.usd.material.make(
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

        toolkit.usd.asset.make (
            ReferencePath,
            AssetPath,
            mayatree )


        # Create/Update Symbolic Link
        if options.link:
            toolkit.system.ostree.linkUpdate(
                options.assetPath,
                options.assetName )


        # Create/Update .metadata.json
        with Metadata.MetadataManager(
                options.assetPath, "usdasset") as data:

            data["info"] = options.info
            data["status"] = options.status
            data["items"][options.assetName] = dict(
                published = toolkit.core.timing.getTimeCode(),
                comment   = options.comment )


        # Create Preview Image
        if os.path.exists(AssetPath):
            toolkit.system.ostree.buildUsdRoot(
                options.assetPath, previews=True)

            minTime = OpenMayaAnim.MAnimControl().currentTime().value()
            maxTime = minTime
            if options.animation:
                minTime = options.minTime
                maxTime = options.maxTime

            animation = toolkit.maya.misc.getCurrentCameraAnimation(
                minTime, maxTime)
            timedata = toolkit.maya.misc.getCurrentCameraSettings()
            timedata.update(animation)

            toolkit.usd.imaging.recordAssetPreviews(AssetPath, timedata)


        OpenMaya.MGlobal.displayInfo(message + options.assetName)
