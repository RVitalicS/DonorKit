#!/usr/bin/env python

"""
Image generation

Tools to create preview images for USD Assets.
"""

import re
import os
from databank import pathEnvmap
import shutil
from toolkit.system import run
from toolkit.system.ostree import SUBDIR_PREVIEWS
from toolkit.core.timing import isAnimation
import toolkit.core.geometry as geometry
import toolkit.usd.attribute as attributeCommand
from toolkit.usd.editor import addMaterialPayload
from pxr import Sdf
from pxr import Gf
from pxr import Vt
from pxr import Usd
from pxr import UsdGeom
from pxr import UsdShade
from pxr import UsdLux
from typing import Union


def recordCommand (
        usdFilePath: str, outputImagePath: str,
        frameSpec: Union[None, str] = None,
        camera: Union[None, str] = None,
        imageWidth: Union[None, int] = None,
        complexity: Union[None, str] = None,
        colorCorrectionMode: Union[None, str] = None,
        purposes: Union[None, str] = None,
        renderer: Union[None, str] = None) -> list:
    """Create command to generate images from the USD file

    Arguments:
        usdFilePath:         The path to the USD file
        outputImagePath:     The output image path with the placeholder
                             for frame ranges ("###" or "###.###")
    Keyword Arguments:
        frameSpec:           The expression that is up to three floating point values
        camera:              Which camera to use (may be given as just the prim name)
        imageWidth:          The width of the output image
        complexity:          The level of refinement to use
                             (low,medium,high,veryhigh)
        colorCorrectionMode: The color correction mode to use
                             (disabled,sRGB,openColorIO)
        purposes:            Specify which UsdGeomImageable purposes
                             should be included in the renders
        renderer:            The renderer plugin to use when generating images
    Returns:
        The command for 'usdrecord'
    """
    command = ["usdrecord"]
    command.append("--frames")
    if frameSpec is None:
        Stage = Usd.Stage.Open(
            usdFilePath, load=Usd.Stage.LoadNone)
        startTime = Stage.GetStartTimeCode()
        endTime   = Stage.GetEndTimeCode()
        frameSpec = f"{startTime}:{endTime}"
    command.append(frameSpec)

    if camera is not None:
        command.append("--camera")
        command.append(camera)
    if imageWidth is not None:
        command.append("--imageWidth")
        command.append(str(imageWidth))
    if complexity is not None:
        command.append("--complexity")
        command.append(complexity)
    if colorCorrectionMode is not None:
        command.append("--colorCorrectionMode")
        command.append(colorCorrectionMode)
    if purposes is not None:
        command.append("--purposes")
        command.append(purposes)
    if renderer is not None:
        command.append("--renderer")
        command.append(renderer)

    command.append(usdFilePath)
    command.append(outputImagePath)

    return command


def recordAssetPreviews (usdpath: str, timedata: dict,
                         width: int = 480, ratio: float = 16/9) -> None:
    """Generate or override preview files for the specified USD file
    and save to a special directory of the current USD Asset

    Arguments:
        usdpath: The path to the USD file
        timedata: The animation data for a camera
    Keyword Arguments:
        width: The width of the output images
        ratio: The horizontal aperture value for a camera
    """
    stageScene = Usd.Stage.Open(
        usdpath, load=Usd.Stage.LoadNone)
    startTime = stageScene.GetStartTimeCode()
    endTime   = stageScene.GetEndTimeCode()
    fps = stageScene.GetFramesPerSecond()
        
    pathAsset = os.path.dirname(usdpath)
    filenameAsset = os.path.basename(usdpath)
    nameGroup = re.sub(r"\.usd[ac]*$", "", filenameAsset)

    pathGroup = os.path.join(pathAsset, SUBDIR_PREVIEWS, nameGroup)
    if os.path.exists(pathGroup):
        shutil.rmtree(pathGroup)
    os.mkdir(pathGroup)

    # create camera and apply animation
    filenameCamera = "Camera.usda"
    pathCamera = os.path.join(pathGroup, filenameCamera)
    StageCamera = Usd.Stage.CreateNew(pathCamera)
    LayerCamera = StageCamera.GetRootLayer()

    scenepathXform = "/Camera"
    XformCamera = UsdGeom.Xform.Define(
        StageCamera, Sdf.Path(scenepathXform))

    def setOp (operation: UsdGeom.XformOp, data: dict) -> None:
        if isAnimation(data):
            for time, value in data.items():
                operation.Set(time=float(time), value=Gf.Vec3d(*value) )
        else:
            for time, value in data.items():
                operation.Set(value=Gf.Vec3d(*value) )
                break

    translatedata = timedata.get("translate")
    if translatedata:
        Translate = attributeCommand.getTranslateOp(XformCamera.GetPrim())
        setOp(Translate, translatedata)
    rotatedata = timedata.get("rotate")
    if rotatedata:
        RotateXYZ = attributeCommand.getRotateXYZOp(XformCamera.GetPrim())
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

    # create light
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

    # create previews
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
    run.terminal(command)


def recordMaterialPreview (usdpath: str, periodic: bool = True,
        displacement: bool = False, width: int = 480, ratio: float = 16/9) -> None:
    """Generate or override preview files for the specified USD file
    and save to a special directory of the current USD Material Asset

    Arguments:
        usdpath: The path to the USD file
    Keyword Arguments:
        periodic: Is the material has texture repetition
        displacement: Is the material has displacement
        width: The width of the output images
        ratio: The horizontal aperture value for a camera
    """
    pathMaterial = os.path.dirname(usdpath)
    filenameMaterial = os.path.basename(usdpath)
    nameGroup = re.sub(r"\.usd[ac]*$", "", filenameMaterial)
    pathGroup = os.path.join(pathMaterial, SUBDIR_PREVIEWS, nameGroup)

    pathRender = os.path.join(pathGroup, "render.usda")
    Stage = Usd.Stage.CreateNew(pathRender)
    UsdGeom.SetStageUpAxis(Stage, "Y")
    Layer = Stage.GetRootLayer()

    # create camera
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

    # create light
    LightPath = Sdf.Path("/Light")
    Light = UsdLux.DomeLight.Define(Stage, LightPath)
    Light.CreateTextureFileAttr(pathEnvmap)
    RotateYOp = Light.AddRotateYOp()
    RotateYOp.Set(90)
    FormatInput = Light.CreateInput(
        "texture:format", Sdf.ValueTypeNames.Token)
    FormatInput.Set("latlong")

    # create plane geometry
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

    # create material and add reference
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

    # create previews
    command = recordCommand(
        pathRender, pathFrames,
        camera=CameraPath.pathString,
        imageWidth=width,
        complexity=complexity,
        colorCorrectionMode="sRGB",
        purposes="render",
        renderer="GL" )
    command += ["&&", "rm", pathRender]
    run.terminal(command)
