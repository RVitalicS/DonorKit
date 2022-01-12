
import time
import re
import os

encModel = "utf8"
os.environ["PYTHONIOENCODING"] = encModel


from pxr import Usd

from PySide2.QtWidgets import QFileDialog


import ostree
import mayatree

import usdmaterial
import usdeditor
import usdasset


import maya.OpenMaya as OpenMaya





def UsdExport (
    file,
    exportUVs=1,
    exportSkels="none",
    exportSkin="none",
    exportBlendShapes=0,
    exportColorSets=1,
    defaultMeshScheme="catmullClark",
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

    options=';'.join([
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

    command = ' '.join([
        'file',
        '-force',
        '-options "{}"'.format( options ),
        '-typ "USD Export"',
        '-pr',
        '-es "{}"'.format( file ) ])

    OpenMaya.MGlobal.executeCommand(command)





def main ():

    MSelectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

    if not MSelectionList.isEmpty():


        # Export Widget
        widget = QFileDialog()
        ExportPath = widget.getExistingDirectory(
            widget,
            "Save Asset", "",
            QFileDialog.ShowDirsOnly ).encode(encModel)
        

        version = 1                     # combobox
        version = "v{:02d}".format(version)

        variant = None                  # combobox
        final = False                   # checkbox


        modelling = True                # checkbox
        modellingOverride = False       # checkbox

        animation = True                # checkbox
        animationOverride = True        # checkbox

        timeRange  = False              # checkbox
        startFrame = 1                  # spinbox
        endFrame   = 150                # spinbox
        fps        = 30                 # combobox

        AnimationName = "Animation"     # combobox

        surfacing = False               # checkbox

        unitsMultiplier = 1.0           # combobox
        units = 0.01 * unitsMultiplier



        if ExportPath:


            start = time.time()
            scene = mayatree.get(getshaders=surfacing)
            end = time.time()
            print("\nGot Scene Data for {} sec.\n".format(end - start) )

            treedata  = scene["data"]
            shaders = scene["shaders"]
            root    = scene["root"]


            if not treedata:
                OpenMaya.MGlobal.displayWarning(
                    "Wrong Selection")
                return


            AssetName = os.path.basename(ExportPath)
            AssetName = re.sub(r"\..*$", "", AssetName)
            AssetDirectory = os.path.dirname(ExportPath)



            SourceModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                "source.geo.usd" )

            ModelFileName = "{}.{}.usd".format(
                os.path.basename(root), version )

            ModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                ModelFileName )

            AnimationFileName = "{}.{}.usd".format(
                AnimationName, version)

            AnimationPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_ANIMATION,
                AnimationFileName )



            export = False
            extractModel = False
            extractAnimatioin = False

            if modelling:
                if not os.path.exists(ModelPath):
                    export = True
                    extractModel = True
                elif modellingOverride:
                    export = True
                    extractModel = True

            if animation:
                if not os.path.exists(AnimationPath):
                    export = True
                    extractAnimatioin = True
                elif animationOverride:
                    export = True
                    extractAnimatioin = True



            if export:
                ostree.build(ExportPath, modelling=True)
                UsdExport(
                    SourceModelPath,
                    animation= 1 if animation else 0,
                    startTime=startFrame,
                    endTime=endFrame )



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
                NewStage.GetRootLayer().Save(force=True)

                OpenMaya.MGlobal.displayInfo(message + ModelFileName)



            if extractAnimatioin:
                ostree.build(ExportPath, animation=True)

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

                NewStage.GetRootLayer().Save(force=True)

                OpenMaya.MGlobal.displayInfo(message + AnimationFileName)


            if os.path.exists(SourceModelPath):
                os.remove(SourceModelPath)



            if surfacing and shaders:
                ostree.build(ExportPath, surfacing=True)

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
                            AssetDirectory,
                            AssetName,
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



            ReferencePath = AnimationPath if animation else ModelPath
            if os.path.exists(ReferencePath):

                if variant:
                    version = "{}-{}".format(variant, version)
                if final:
                    version = "{}.final".format(version)

                AssetFileName = "{}{}.{}.usda".format(
                        AssetName,
                        "." + AnimationName if animation else "",
                        version)

                AssetPath = os.path.join(
                    AssetDirectory,
                    AssetName,
                    AssetFileName )

                if os.path.exists(AssetPath):
                    message = "Asset Overwritten: "
                else:
                    message = "Asset Saved: "

                usdasset.make (
                    ReferencePath,
                    AssetPath,
                    treedata )

                OpenMaya.MGlobal.displayInfo(message + AssetFileName)



    else:
            OpenMaya.MGlobal.displayWarning(
                "Select Any Object")