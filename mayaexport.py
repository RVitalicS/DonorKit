

import re
import os

encModel = "utf8"
os.environ["PYTHONIOENCODING"] = encModel


from pxr import Usd, Sdf

from PySide2 import QtWidgets

import ostree
import mayatree

import usdmaterial
import usdeditor
import usdbind
import usdasset


# import pymel.core as PyMELcore
from pymel.core import inViewMessage as PyMelMessage
from pymel.core import selected as PyMelSelected
from pymel.core.system import exportSelected as PyMelExportSelected






def mayaEcho (message, mode=0):

    PyMelMessage(
        assistMessage = message,
        position      = "botCenter",
        fade          = True)

    messageStatus = "Info"
    if mode > 0:
        messageStatus = "Warning"

    print( "{}: {}".format(messageStatus, message) )






def pxrUsdExport (
    file,
    shadingMode="none",
    materialsScopeName="",
    exportDisplayColor=0,
    exportRefsAsInstanceable=0,
    exportUVs=1,
    exportMaterialCollections=0,
    materialCollectionsPath="",
    exportCollectionBasedBindings=0,
    exportColorSets=0,
    exportReferenceObjects=0,
    renderableOnly=0,
    filterTypes="",
    defaultCameras=0,
    renderLayerMode="defaultLayer",
    mergeTransformAndShape=0,
    exportInstances=0,
    defaultMeshScheme="none",
    exportSkels="none",
    exportSkin="none",
    exportBlendShapes=0,
    exportVisibility=0,
    stripNamespaces=0,
    animation=0,
    eulerFilter=0,
    staticSingleSample=0,
    startTime=1,
    endTime=1,
    frameStride=1,
    parentScope="",
    compatibility="none" ):


    PyMelExportSelected(
        file,
        force=True,
        type="pxrpxrUsdExport",
        options=';'.join([
            "shadingMode={}".format( shadingMode ),
            "materialsScopeName={}".format( materialsScopeName ),
            "exportDisplayColor={}".format( exportDisplayColor ),
            "exportRefsAsInstanceable={}".format( exportRefsAsInstanceable ),
            "exportUVs={}".format( exportUVs ),
            "exportMaterialCollections={}".format( exportMaterialCollections ),
            "materialCollectionsPath=".format( materialCollectionsPath ),
            "exportCollectionBasedBindings={}".format( exportCollectionBasedBindings ),
            "exportColorSets={}".format( exportColorSets ),
            "exportReferenceObjects={}".format( exportReferenceObjects ),
            "renderableOnly={}".format( renderableOnly ),
            "filterTypes=".format( filterTypes ),
            "defaultCameras={}".format( defaultCameras ),
            "renderLayerMode={}".format( renderLayerMode ),
            "mergeTransformAndShape={}".format( mergeTransformAndShape ),
            "exportInstances={}".format( exportInstances ),
            "defaultMeshScheme={}".format( defaultMeshScheme ),
            "exportSkels={}".format( exportSkels ),
            "exportSkin={}".format( exportSkin ),
            "exportBlendShapes={}".format( exportBlendShapes ),
            "exportVisibility={}".format( exportVisibility ),
            "stripNamespaces={}".format( stripNamespaces ),
            "animation={}".format( animation ),
            "eulerFilter={}".format( eulerFilter ),
            "staticSingleSample={}".format( staticSingleSample ),
            "startTime={}".format( startTime ),
            "endTime={}".format( endTime ),
            "frameStride={}".format( frameStride ),
            "parentScope=".format( parentScope ),
            "compatibility={}".format( compatibility ) ]) )






def askUsdExport (
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

    
    PyMelExportSelected(
        file,
        force=True,
        type="USD Export",
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
            "stripNamespaces={}".format( stripNamespaces ) ]) )






def main ():
    if PyMelSelected():

        scene = mayatree.get()

        treedata  = scene["data"]
        shaders = scene["shaders"]
        root    = scene["root"]



        class FileDialog (QtWidgets.QFileDialog):

            def __init__ (self):
                super(FileDialog, self).__init__()

        widget = FileDialog()
        path = widget.getExistingDirectory().encode(encModel)



        if path:
            AssetName = os.path.basename(path)
            AssetName = re.sub(r"\..*$", "", AssetName)

            AssetDirectory = os.path.dirname(path)
            ostree.build(AssetDirectory, AssetName)


            ModelName = os.path.basename(path)
            SourceModelName = "{}.Source.usd".format(ModelName)

            SourceModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                SourceModelName )

            askUsdExport(SourceModelPath)



            RenderModelName = "{}.usd".format(
                os.path.basename(root))

            RenderModelPath = os.path.join(
                AssetDirectory,
                AssetName,
                ostree.SUBDIR_MODELLING,
                RenderModelName )

            OldStage = Usd.Stage.Open(SourceModelPath)
            NewStage = Usd.Stage.CreateNew(RenderModelPath)
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
                        ShaderPath = os.path.join(
                            AssetDirectory,
                            AssetName,
                            ostree.SUBDIR_SURFACING,
                            ShaderName )

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






            RenderBindName = "{}.Render.usda".format(AssetName)

            RenderBindPath = os.path.join(
                AssetDirectory,
                AssetName,
                RenderBindName )


            ModelStage = Usd.Stage.Open(RenderModelPath)
            BindStage  = Usd.Stage.CreateNew(RenderBindPath)

            usdbind.wrap(
                ModelStage,
                BindStage,
                treedata,
                scope=None )

            BindLayer = BindStage.GetRootLayer()

            RelativeModelPath = re.sub(
                os.path.dirname(RenderBindPath), ".",
                RenderModelPath)
            BindLayer.subLayerPaths = [ RelativeModelPath ]

            BindLayer.Save(force=True)





            ProxyBindName = "{}.Proxy.usda".format(AssetName)

            ProxyBindPath = os.path.join(
                AssetDirectory,
                AssetName,
                ProxyBindName )

            if not os.path.exists(ProxyBindPath):

                import shutil
                shutil.copyfile(RenderBindPath, ProxyBindPath)




            AssetPath = os.path.join(
                AssetDirectory,
                AssetName,
                "{}.usda".format(AssetName) )

            usdasset.make (
                    AssetPath,
                    render   = RenderBindPath,
                    proxy    = ProxyBindPath,
                    name     = AssetName,
                    root     = ModelName,
                    instance = False )


            mayaEcho( "Asset Saved", mode=0 )


    else:
        mayaEcho( "Select Any Object", mode=1 )


