#!/usr/bin/env python

"""
Asset Export

Define an interface to create USD Asset with version control.
"""

import re
import os
from pxr import Usd
from widgets import AssetExport
from toolkit.core import Metadata
from toolkit.core.naming import rule_Material
from toolkit.core import timing
from toolkit.system import ostree
import toolkit.maya.camera as cameraCommand
import toolkit.maya.export as exportCommand
import toolkit.maya.proxy as proxyCommand
import toolkit.maya.outliner as outlinerCommand
import toolkit.maya.message as messageCommand
from toolkit.maya import MaterialUsd
import toolkit.usd.editor as editorUSD
import toolkit.usd.asset as assetUSD
import toolkit.usd.imaging as imagingUSD
import maya.OpenMayaAnim as OpenMayaAnim
import toolkit.maya.scene as sceneCommand


def Export (options: object = None) -> None:
    """Create USD Asset from a Maya selection

    Keyword Arguments:
        options: The options of the export dialog
                 that returns DataClass object
                 with the attributes listed below

        options.modelling         : bool
        options.modellingOverride : bool
        options.surfacing         : bool
        options.surfacingOverride : bool
        options.animation         : bool
        options.animationOverride : bool
        options.animationName     : str
        options.minTime           : int
        options.maxTime           : int
        options.proxy             : bool
        options.reduceFactor      : float
        options.assetPath         : str
        options.assetName         : str
        options.version           : int
        options.variant           : str
        options.link              : bool
        options.maya              : bool
        options.info              : str
        options.comment           : str
        options.status            : str
    """
    if not options:
        selection = outlinerCommand.getSelectionName()
        if not selection:
            text = "Select Any Object"
            messageCommand.warning(text)
            messageCommand.viewport(text)
            return
        dialog = AssetExport.Dialog(initname=selection)
        dialog.exec()
        options = dialog.getOptions()
        if not options:
            return
    mayaScene = sceneCommand.Manager()
    mayaScene.applyMaterialNaming(rule_Material)
    if not mayaScene.tree:
        text = "Wrong Selection"
        messageCommand.warning(text)
        messageCommand.viewport(text)
        return

    # naming
    version = f"v{options.version:02d}"
    if options.variant:
        version += f"-{options.variant}"
    SourceModelPath = os.path.join(
        options.assetPath, ostree.SUBDIR_MODELLING, "source.geo.usd")
    ModelFileName = "{}.{}.usd".format(
        os.path.basename(mayaScene.root), version)
    ModelPath = os.path.join(
        options.assetPath, ostree.SUBDIR_MODELLING, ModelFileName)
    SourceProxyPath = os.path.join(
        options.assetPath, ostree.SUBDIR_MODELLING, "source.proxy.usd")
    ProxyFileName = "{}.{}.Proxy.usd".format(
        os.path.basename(mayaScene.root), version)
    ProxyPath = os.path.join(
        options.assetPath, ostree.SUBDIR_MODELLING, ProxyFileName)
    AnimationFileName = "{}.{}.usd".format(
        options.animationName, version)
    AnimationPath = os.path.join(
        options.assetPath, ostree.SUBDIR_ANIMATION, AnimationFileName)
    AssetPath = os.path.join(
        options.assetPath, options.assetName)
    if not os.path.exists(options.assetPath):
        os.mkdir(options.assetPath)
    os.chdir(options.assetPath)

    # export decision
    export = False
    extractModel = False
    extractAnimation = False
    units = 0.01           # UNIT DEPEND
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
        ostree.buildUsdRoot(
            options.assetPath, modelling=True)
        exportCommand.USD(
            SourceModelPath,
            defaultMeshScheme = mayaScene.defaultMeshScheme,
            animation= 1 if options.animation else 0,
            startTime=options.minTime,
            endTime=options.maxTime,
            shading=True)
        StageSource = Usd.Stage.Open(
            SourceModelPath, load=Usd.Stage.LoadNone)

    # create geometry layer
    if extractModel:
        if os.path.exists(ModelPath):
            # TODO: delete existing ones
            modelMessage = "Model Overwritten: "
        else:
            modelMessage = "Model Saved: "
        Stage = Usd.Stage.CreateNew(ModelPath)
        editorUSD.copyStage(
            StageSource, Stage,
            root=mayaScene.root, units=units,
            namingGeomSubset=rule_Material)
        editorUSD.addMayaAttributes(Stage, mayaScene.tree)
        Stage.GetRootLayer().Export(
            ModelPath, args=dict(format="usdc"))
        messageCommand.info(modelMessage + ModelFileName)

        if options.proxy:
            if os.path.exists(ProxyPath):
                proxyMessage = "Proxy Overwritten: "
            else:
                proxyMessage = "Proxy Saved: "
            proxyCommand.generate(
                SourceProxyPath, threshold=options.reduceFactor)
            StageProxy = Usd.Stage.Open(
                SourceProxyPath, load=Usd.Stage.LoadNone)
            Stage = Usd.Stage.CreateNew(ProxyPath)
            editorUSD.copyStage(
                StageProxy, Stage, proxy=True,
                root=mayaScene.root, units=units)
            Stage.GetRootLayer().Export(
                ProxyPath, args=dict(format="usdc"))
            messageCommand.info(proxyMessage + ProxyFileName)

    # create animation layer
    if extractAnimation:
        ostree.buildUsdRoot(
            options.assetPath, animation=True)
        if os.path.exists(AnimationPath):
            animationMessage = "Animation Overwritten: "
        else:
            animationMessage = "Animation Saved: "
        Stage = Usd.Stage.CreateNew(AnimationPath)
        editorUSD.copyAnimation(
            StageSource, Stage, root=mayaScene.root,
            reference=ModelPath, units=units)
        Stage.GetRootLayer().Export(
            AnimationPath, args=dict(format="usdc"))
        messageCommand.info(animationMessage + AnimationFileName)

    if os.path.exists(SourceModelPath):
        os.remove(SourceModelPath)
    if os.path.exists(SourceProxyPath):
        os.remove(SourceProxyPath)

    # create material layers
    if options.surfacing and mayaScene.shaders:
        ostree.buildUsdRoot(
            options.assetPath, surfacing=True)
        MaterialPath = os.path.join(
            options.assetPath,
            ostree.SUBDIR_SURFACING)

        class DataClass: pass
        for MaterialName, data in mayaScene.shaders.items():
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
            MaterialUsd.Export(options=uishadow, data=data)

    # create asset
    ReferencePath = AnimationPath if options.animation else ModelPath
    if os.path.exists(ReferencePath):
        if os.path.exists(AssetPath):
            assetMessage = "Asset Overwritten: "
        else:
            assetMessage = "Asset Saved: "
        assetUSD.make(
            AssetPath, ReferencePath, ProxyPath,
            mayaScene.tree, mayaScene.root)

        # create/update a symbolic link
        if options.link:
            ostree.linkUpdate(
                options.assetPath,
                options.assetName)

        # create/update .metadata.json
        with Metadata.MetadataManager(
                options.assetPath,
                metatype="usdasset") as data:
            data["info"] = options.info
            data["status"] = options.status
            data["items"][options.assetName] = dict(
                published = timing.getTimeCode(),
                comment   = options.comment)

        # create a preview image
        if os.path.exists(AssetPath):
            ostree.buildUsdRoot(
                options.assetPath, previews=True)
            minTime = OpenMayaAnim.MAnimControl().currentTime().value()
            maxTime = minTime
            if options.animation:
                minTime = options.minTime
                maxTime = options.maxTime
            camera = cameraCommand.getCurrent()
            animation = cameraCommand.getAnimation(
                camera, minTime, maxTime)
            timedata = cameraCommand.getSettings(camera)
            timedata.update(animation)
            imagingUSD.recordAssetPreviews(AssetPath, timedata)

        # export selected as a Maya file
        if options.maya:
            ostree.buildUsdRoot(
                options.assetPath, sources=True)
            MayaFileName = re.sub(r"usd[ac]?$", "mb", options.assetName)
            MayaPath = os.path.join(
                options.assetPath,
                ostree.SUBDIR_SOURCES,
                MayaFileName)
            if os.path.exists(MayaPath):
                mayaMessage = "Source Overwritten: "
            else:
                mayaMessage = "Source Saved: "
            exportCommand.Maya(MayaPath)
            messageCommand.info(mayaMessage + MayaFileName)

        # a summary message
        messageCommand.info(assetMessage + options.assetName)
