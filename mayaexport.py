

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

        scene = mayatree.get()

        treedata  = scene["data"]
        shaders = scene["shaders"]
        root    = scene["root"]


        if not treedata:
            OpenMaya.MGlobal.displayWarning(
                "Wrong Selection")
            return


        widget = QFileDialog()
        path = widget.getExistingDirectory(
            widget,
            "Save Asset", "",
            QFileDialog.ShowDirsOnly ).encode(encModel)


        if path:
            AssetName = os.path.basename(path)
            AssetName = re.sub(r"\..*$", "", AssetName)

            AssetDirectory = os.path.dirname(path)
            ostree.build(AssetDirectory, AssetName)


            SourceModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                "source.geo.usd" )

            UsdExport(SourceModelPath)



            ModelName = "{}.usd".format(
                os.path.basename(root))

            ModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                ModelName )

            OldStage = Usd.Stage.Open(SourceModelPath)
            NewStage = Usd.Stage.CreateNew(ModelPath)
            usdeditor.copyStage(
                OldStage,
                NewStage, root=root)

            usdeditor.addMayaAttributes(NewStage, treedata)
            NewStage.GetRootLayer().Save(force=True)

            os.remove(SourceModelPath)



            for name, data in shaders.items():
                for key in ["render", "preview"]:

                    ShaderData = mayatree.keydata(data, key)

                    if key == "render":
                        prman=True
                        ShaderName = "{}.RenderMan.usda".format(name)

                    else:
                        prman=False
                        ShaderName = "{}.usda".format(name)

                    ShaderPath = os.path.join(
                        AssetDirectory,
                        AssetName,
                        ostree.SUBDIR_SURFACING,
                        ShaderName )


                    if ShaderData:
                        ShaderData["name"] = name
                        usdmaterial.make(
                            ShaderPath,
                            ShaderData,
                            prman=prman)



            AssetPath = os.path.join(
                AssetDirectory,
                AssetName,
                "{}.usda".format(AssetName) )

            usdasset.make (
                ModelPath,
                AssetPath,
                treedata )


            OpenMaya.MGlobal.displayInfo(
                "Asset Saved: {}".format(AssetName) )



    else:
            OpenMaya.MGlobal.displayWarning(
                "Select Any Object")