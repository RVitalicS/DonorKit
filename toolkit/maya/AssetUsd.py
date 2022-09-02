#!/usr/bin/env python



import re
import os
import importlib


from pxr import Usd

from widgets import AssetExport

from toolkit.core import Metadata
from toolkit.core.naming import rule_Material

import toolkit.core.timing
import toolkit.system.ostree

import toolkit.maya.camera
import toolkit.maya.export
import toolkit.maya.outliner
import toolkit.maya.message
import toolkit.maya.MaterialUsd

import toolkit.maya.scene
importlib.reload(toolkit.maya.scene)

import toolkit.usd.material
import toolkit.usd.editor
import toolkit.usd.asset
import toolkit.usd.imaging

import maya.OpenMayaAnim as OpenMayaAnim




def Export (options=None):


    """
        options.modelling = True
        options.modellingOverride = True

        options.surfacing = True
        options.surfacingOverride = True

        options.animation = True
        options.animationOverride = True

        options.animationName = ""

        options.minTime = 0
        options.maxTime = 0

        options.assetPath = ""
        options.assetName = ""

        options.version = 1
        options.variant = ""
        options.link = True

        options.maya = True

        options.info = ""
        options.comment = ""
        options.status = "WIP"
    """


    if not options:
        selection = toolkit.maya.outliner.getSelectionName()
        if not selection:
            text = "Select Any Object"
            toolkit.maya.message.warning(text)
            toolkit.maya.message.viewport(text)
            return
        
        dialog = AssetExport.Dialog(initname=selection)
        dialog.exec()

        options = dialog.getOptions()
        if not options: return



    version = "v{:02d}".format(options.version)
    if options.variant:
        version += "-{}".format(options.variant)
    
    units = 0.01           # UNIT DEPEND



    mayaScene = toolkit.maya.scene.Manager(
        getshaders=options.surfacing)
    mayaScene.applyMaterialNaming(rule_Material)

    if not mayaScene.tree:
        text = "Wrong Selection"
        toolkit.maya.message.warning(text)
        toolkit.maya.message.viewport(text)
        return



    if not os.path.exists(options.assetPath):
        os.mkdir(options.assetPath)
    os.chdir(options.assetPath)



    SourceModelPath = os.path.join(
        options.assetPath,
        toolkit.system.ostree.SUBDIR_MODELLING,
        "source.geo.usd" )

    ModelFileName = "{}.{}.usdc".format(
        os.path.basename(mayaScene.root), version )

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
    extractAnimation = False

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
            extractAnimation = True
        elif options.animationOverride:
            export = True
            extractAnimation = True



    if export:
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, modelling=True)
        toolkit.maya.export.USD(
            SourceModelPath,
            defaultMeshScheme = mayaScene.defaultMeshScheme,
            animation= 1 if options.animation else 0,
            startTime=options.minTime,
            endTime=options.maxTime,
            shading=options.surfacing )
        StageSource = Usd.Stage.Open(SourceModelPath)



    if extractModel:
        if os.path.exists(ModelPath):
            modelMessage = "Model Overwritten: "
        else:
            modelMessage = "Model Saved: "

        Stage = Usd.Stage.CreateNew(ModelPath)
        toolkit.usd.editor.copyStage(
            StageSource,
            Stage,
            root=mayaScene.root, units=units,
            namingGeomSubset=rule_Material)

        toolkit.usd.editor.addMayaAttributes(Stage, mayaScene.tree)
        Stage.GetRootLayer().Export(
            ModelPath, args=dict(format="usdc") )

        toolkit.maya.message.info(modelMessage + ModelFileName)



    if extractAnimation:
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, animation=True)

        if os.path.exists(AnimationPath):
            animationMessage = "Animation Overwritten: "
        else:
            animationMessage = "Animation Saved: "

        Stage = Usd.Stage.CreateNew(AnimationPath)
        toolkit.usd.editor.copyAnimation(
            StageSource,
            Stage,
            root=mayaScene.root, reference=ModelPath, units=units )

        Stage.GetRootLayer().Export(
            AnimationPath, args=dict(format="usdc") )

        toolkit.maya.message.info(animationMessage + AnimationFileName)


    if os.path.exists(SourceModelPath):
        os.remove(SourceModelPath)



    if options.surfacing and mayaScene.shaders:
        toolkit.system.ostree.buildUsdRoot(
            options.assetPath, surfacing=True)

        MaterialPath = os.path.join(
            options.assetPath,
            toolkit.system.ostree.SUBDIR_SURFACING )

        for MaterialName, data in mayaScene.shaders.items():

            class DataClass: pass
            uishadow = DataClass()

            uishadow.library      = None
            uishadow.materialPath = MaterialPath
            uishadow.materialName = MaterialName
            uishadow.version      = options.version
            uishadow.variant      = options.variant
            uishadow.link         = False
            uishadow.maya         = False
            uishadow.info         = ""
            uishadow.comment      = ""
            uishadow.status       = options.status
            uishadow.prman        = False
            uishadow.hydra        = False

            toolkit.maya.MaterialUsd.Export(options=uishadow, data=data)



    ReferencePath = AnimationPath if options.animation else ModelPath
    if os.path.exists(ReferencePath):

        AssetPath = os.path.join(
            options.assetPath,
            options.assetName )

        if os.path.exists(AssetPath):
            assetMessage = "Asset Overwritten: "
        else:
            assetMessage = "Asset Saved: "

        toolkit.usd.asset.make (
            ReferencePath,
            AssetPath,
            mayaScene.tree,
            mayaScene.root )


        # Create/Update Symbolic Link
        if options.link:
            toolkit.system.ostree.linkUpdate(
                options.assetPath,
                options.assetName )


        # Create/Update .metadata.json
        with Metadata.MetadataManager(
                options.assetPath,
                metatype="usdasset") as data:

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

            camera = toolkit.maya.camera.getCurrent()
            animation = toolkit.maya.camera.getAnimation(
                camera, minTime, maxTime)
            timedata = toolkit.maya.camera.getSettings(camera)
            timedata.update(animation)

            toolkit.usd.imaging.recordAssetPreviews(AssetPath, timedata)


        # Export Selected as Maya File
        if options.maya:
            toolkit.system.ostree.buildUsdRoot(
                options.assetPath, sources=True)

            MayaFileName = re.sub(r"usd[ac]{0,1}$", "mb", options.assetName)
            MayaPath = os.path.join(
                options.assetPath,
                toolkit.system.ostree.SUBDIR_SOURCES,
                MayaFileName )

            if os.path.exists(MayaPath):
                mayaMessage = "Source Overwritten: "
            else:
                mayaMessage = "Source Saved: "

            toolkit.maya.export.Maya(MayaPath)

            toolkit.maya.message.info(mayaMessage + MayaFileName)


        toolkit.maya.message.info(assetMessage + options.assetName)
