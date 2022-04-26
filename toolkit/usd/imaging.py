#!/usr/bin/env python


import re
import os

thisDir = os.path.dirname(__file__)
toolDir = os.path.dirname(thisDir)
rootDir = os.path.dirname(toolDir)


import shutil

import toolkit.system.stream
from toolkit.system.ostree import SUBDIR_PREVIEWS
from toolkit.core.timing import isAnimation

from pxr import Sdf, Gf, Usd, UsdGeom, UsdLux






def recordCommand (
        usdFilePath,
        outputImagePath,
        frameSpec=None,
        camera=None,
        imageWidth=None,
        complexity=None,
        colorCorrectionMode=None,
        renderer=None ):


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

    if renderer != None:
        command.append("--renderer")
        command.append(renderer)

    command.append(usdFilePath)
    command.append(outputImagePath)


    return command






def recordAssetPreviews (usdpath, timedata, width=480, ratio=16/9):


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
        Translate = XformCamera.AddTranslateOp()
        setOp(Translate, translatedata)

    rotatedata = timedata.get("rotate")
    if rotatedata:
        RotateXYZ = XformCamera.AddRotateXYZOp()
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

    pathTexture = os.path.join(rootDir, "databank", "envmap.exr")
    DomeLight.CreateTextureFileAttr(pathTexture)

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

    command = recordCommand (
        pathLight, pathFrames,
        frameSpec=frameSpec,
        camera=scenepathCamera,
        imageWidth=width,
        complexity="high",
        colorCorrectionMode="sRGB",
        renderer="GL" )

    command += ["&&", "rm", pathLight]
    toolkit.system.stream.terminal(command)
