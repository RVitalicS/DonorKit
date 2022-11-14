#!/usr/bin/env python


import re
import os

from databank import pathEnvmap


import shutil

import toolkit.system.stream
from toolkit.system.ostree import SUBDIR_PREVIEWS
from toolkit.core.timing import isAnimation
import toolkit.core.geometry as geometry

import toolkit.usd.attribute
from toolkit.usd.editor import addMaterialPayload


from pxr import Sdf, Gf, Vt, Usd, UsdGeom, UsdShade, UsdLux






def recordCommand (
        usdFilePath,
        outputImagePath,
        frameSpec=None,
        camera=None,
        imageWidth=None,
        complexity=None,
        colorCorrectionMode=None,
        purposes=None,
        renderer=None, ):


    command = ["usdrecord"]

    command.append("--frames")
    if frameSpec == None:
        Stage = Usd.Stage.Open(usdFilePath)
        startTime = Stage.GetStartTimeCode()
        endTime   = Stage.GetEndTimeCode()
        frameSpec = "{}:{}".format(startTime, endTime)
    command.append(frameSpec)

    if camera != None:
        command.append("--camera")
        command.append(camera)

    if imageWidth != None:
        command.append("--imageWidth")
        command.append(str(imageWidth))

    if complexity != None:
        command.append("--complexity")
        command.append(complexity)

    if colorCorrectionMode != None:
        command.append("--colorCorrectionMode")
        command.append(colorCorrectionMode)

    if purposes != None:
        command.append("--purposes")
        command.append(purposes)

    if renderer != None:
        command.append("--renderer")
        command.append(renderer)

    command.append(usdFilePath)
    command.append(outputImagePath)


    return command






def recordAssetPreviews (
        usdpath, timedata,
        width=480, ratio=16/9 ):


    stageScene = Usd.Stage.Open(usdpath)
    startTime = stageScene.GetStartTimeCode()
    endTime   = stageScene.GetEndTimeCode()
    fps = stageScene.GetFramesPerSecond()
        
    pathAsset = os.path.dirname(usdpath)
    filenameAsset = os.path.basename(usdpath)
    nameGroup = re.sub(r"\.usd[ac]*$", "", filenameAsset)


    pathGroup = os.path.join(pathAsset, SUBDIR_PREVIEWS, nameGroup)
    if os.path.exists(pathGroup): shutil.rmtree(pathGroup)
    os.mkdir(pathGroup)


    filenameCamera = "Camera.usda"
    pathCamera = os.path.join(pathGroup, filenameCamera)
    StageCamera = Usd.Stage.CreateNew(pathCamera)
    LayerCamera = StageCamera.GetRootLayer()

    scenepathXform = "/Camera"
    XformCamera = UsdGeom.Xform.Define(StageCamera, Sdf.Path(scenepathXform))


    def setOp (operation, data):

        if isAnimation(data):
            for time, value in data.items():
                operation.Set(
                    time=float(time),
                    value=Gf.Vec3d(*value) )
        else:
            for time, value in data.items():
                operation.Set(
                    value=Gf.Vec3d(*value) )
                break

    translatedata = timedata.get("translate")
    if translatedata:
        Translate = toolkit.usd.attribute.getTranslateOp(XformCamera)
        setOp(Translate, translatedata)

    rotatedata = timedata.get("rotate")
    if rotatedata:
        RotateXYZ = toolkit.usd.attribute.getRotateXYZOp(XformCamera)
        setOp(RotateXYZ, rotatedata)


    scenepathCamera = scenepathXform + "/CameraShape"
    Camera = UsdGeom.Camera.Define(StageCamera, Sdf.Path(scenepathCamera))
    Camera.CreateClippingRangeAttr( Gf.Vec2f(*timedata.get("clipping")) )
    Camera.CreateFocalLengthAttr( timedata.get("focalLength") )

    Camera.CreateHorizontalApertureAttr( timedata.get("vAperture")*ratio )
    Camera.CreateVerticalApertureAttr( timedata.get("vAperture") )

    LayerCamera.defaultPrim = scenepathXform.replace("/", "")
    StageCamera.SetStartTimeCode(startTime)
    StageCamera.SetEndTimeCode(endTime)
    StageCamera.SetFramesPerSecond(fps)

    LayerCamera.Save()


    filenameLight = "Light.usda"
    pathLight = os.path.join(pathGroup, filenameLight)
    StageLight = Usd.Stage.CreateNew(pathLight)
    LayerLight = StageLight.GetRootLayer()

    scenepathDomeLight = "/DomeLight"
    DomeLight = UsdLux.DomeLight.Define(
        StageLight, Sdf.Path(scenepathDomeLight) )
    DomeLight.CreateTextureFileAttr(pathEnvmap)

    RotateYOp = DomeLight.AddRotateYOp()
    RotateYOp.Set(90)

    LayerLight.subLayerPaths = [
        "../../" + filenameAsset,
        "./" + filenameCamera ]

    LayerLight.defaultPrim = scenepathDomeLight.replace("/", "")
    StageLight.SetStartTimeCode(startTime)
    StageLight.SetEndTimeCode(endTime)
    StageLight.SetFramesPerSecond(fps)

    LayerLight.Save()


    filenameFrames = "Hydra.f###.png"
    pathFrames = os.path.join(pathGroup, filenameFrames)

    frameSpec = "{}:{}".format(startTime, endTime)

    command = recordCommand(
        pathLight, pathFrames,
        frameSpec=frameSpec,
        camera=scenepathCamera,
        imageWidth=width,
        complexity="high",
        colorCorrectionMode="sRGB",
        purposes="render",
        renderer="GL" )

    command += ["&&", "rm", pathLight]
    toolkit.system.stream.terminal(command)






def recordMaterialPreview ( usdpath,
        periodic=True, displacement=False,
        width=480, ratio=16/9 ):


    pathMaterial = os.path.dirname(usdpath)
    filenameMaterial = os.path.basename(usdpath)
    nameGroup = re.sub(r"\.usd[ac]*$", "", filenameMaterial)
    pathGroup = os.path.join(pathMaterial, SUBDIR_PREVIEWS, nameGroup)

    pathRender = os.path.join(pathGroup, "render.usda")
    Stage = Usd.Stage.CreateNew(pathRender)
    UsdGeom.SetStageUpAxis(Stage, "Y")
    Layer = Stage.GetRootLayer()

    CameraPath = Sdf.Path("/Camera")
    Camera = UsdGeom.Camera.Define(Stage, CameraPath)
    Camera.AddXformOp(UsdGeom.XformOp.TypeTransform).Set(
        value=Gf.Matrix4d(
             0.89879, 0      ,  0.43837, 0,
             0.33466, 0.6459 , -0.68616, 0,
            -0.28314, 0.76342,  0.58053, 0,
            -0.504  , 1.323  ,  1.057  , 1) )
    Camera.CreateClippingRangeAttr(Gf.Vec2f(0.01, 100))
    vAperture = 23.999952
    Camera.CreateHorizontalApertureAttr(vAperture*ratio)
    Camera.CreateVerticalApertureAttr(vAperture)

    LightPath = Sdf.Path("/Light")
    Light = UsdLux.DomeLight.Define(Stage, LightPath)
    Light.CreateTextureFileAttr(pathEnvmap)
    RotateYOp = Light.AddRotateYOp()
    RotateYOp.Set(90)
    FormatInput = Light.CreateInput(
        "texture:format", Sdf.ValueTypeNames.Token)
    FormatInput.Set("latlong")

    MeshPath = Sdf.Path("/Plane")
    if periodic:
        scale = 3.0
    else:
        scale = 1.0
    if displacement:
        divisions = 64
        complexity = "veryhigh"
        scheme = "catmullClark"
    else:
        divisions = 0
        complexity = "low"
        scheme = "none"
    faceCounts = geometry.createPlaneFaceCounts(divisions)
    indices    = geometry.createPlaneIndices(divisions)
    points     = geometry.createPlanePoints(scale, divisions)
    normals    = geometry.createPlaneNormals(divisions)
    texCoord   = geometry.createPlaneTexCoord(scale, divisions)
    
    Mesh = UsdGeom.Mesh.Define(Stage, MeshPath)
    MeshPrim = Stage.GetPrimAtPath(MeshPath)
    Mesh.CreateDoubleSidedAttr(1)
    Mesh.CreateFaceVertexCountsAttr(Vt.IntArray(faceCounts))
    Mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(indices))
    Mesh.CreatePointsAttr(Vt.Vec3fArray(points))
    Mesh.CreateNormalsAttr(Vt.Vec3fArray(normals))
    TexCoord = MeshPrim.CreateAttribute(
        "primvars:st",
        Sdf.ValueTypeNames.TexCoord2fArray,
        custom=False)
    TexCoord.Set(value=Vt.Vec2fArray(texCoord))
    TexCoord.SetMetadata("interpolation", "faceVarying")
    Indices = MeshPrim.CreateAttribute(
        "primvars:st:indices",
        Sdf.ValueTypeNames.IntArray,
        custom=False)
    Indices.Set(value=Vt.IntArray(indices) )
    Indices.SetMetadata("interpolation", "faceVarying")
    Mesh.CreateSubdivisionSchemeAttr(scheme)

    MaterialPath = Sdf.Path("/Material")
    Material = UsdShade.Material.Define(Stage, MaterialPath)
    MaterialPrim = Stage.GetPrimAtPath(MaterialPath)
    addMaterialPayload(MaterialPrim, usdpath)
    MeshPrim.ApplyAPI(UsdShade.MaterialBindingAPI)
    UsdShade.MaterialBindingAPI(MeshPrim).Bind(Material)

    Layer.defaultPrim = MeshPath.name
    Layer.Export(pathRender, args=dict(format="usda") )


    filenameFrames = "Hydra.f###.png"
    pathFrames = os.path.join(pathGroup, filenameFrames)

    command = recordCommand(
        pathRender, pathFrames,
        camera=CameraPath.pathString,
        imageWidth=width,
        complexity=complexity,
        colorCorrectionMode="sRGB",
        purposes="render",
        renderer="GL" )

    command += ["&&", "rm", pathRender]
    toolkit.system.stream.terminal(command)
