#!/usr/bin/env python

"""
RenderMan

Implement utility functions to talk to RenderMan.
"""

import re
import os
import maya.cmds as mayaCommand
from toolkit.system import stream
from toolkit.system import run
from toolkit.maya import hypershade
import toolkit.maya.export as exportCommand
import toolkit.maya.message as messageCommand
import databank
from typing import Union

# check OCIO usage
ocioConfig = os.getenv("OCIO", "")

# names for files
nameExr = "Render.exr"
namePng = "Prman.f000.png"


def isDefined() -> bool:
    """Check RenderMan Pro Server to be installed on your machine

    Returns:
        A result of the check
    """
    if os.getenv("RMANTREE"):
        return True
    else:
        return False


def createShaderRIB (directory: str, filldisplay: bool = True) -> Union[str, None]:
    """Create a RIB file from a selected Maya material
    to transfer this data to RenderMan and to get preview image

    Arguments:
        directory: The directory, where a RIB file will be saved
    Keyword Arguments:
        filldisplay: A flag used to create a plane geometry
                     that fills a whole camera view
    Returns:
        A path to a RIB file
    """

    # get selected shading group
    MATERIAL = hypershade.getSelectionName()
    if not MATERIAL:
        return

    # create service mesh
    meshname = "_RIBMESH_"
    mayaCommand.polyPlane(
        createUVs=0, subdivisionsX=1,
        subdivisionsY=1, name=meshname)
    mayaCommand.delete(meshname, constructionHistory = True)
    mayaCommand.sets(meshname, edit=True, forceElement=MATERIAL)

    # get Bxdf/Displace names
    BXDFSHADER = None
    DISPLACESHADER = None
    outPlugs = mayaCommand.listConnections(
        MATERIAL, plugs=True,
        source=True, destination=False)
    for outPlug in outPlugs:
        inPlugs = mayaCommand.listConnections(
            outPlug, plugs=True,
            source=False, destination=True)
        for inPlug in inPlugs:
            if "rman__surface" in inPlug:
                BXDFSHADER = re.sub(r"\..*", "", outPlug)
            elif "rman__displacement" in inPlug:
                DISPLACESHADER = re.sub(r"\..*", "", outPlug)
    if not BXDFSHADER:
        return

    # export rib file
    mayaCommand.select(meshname, replace=True)
    ribExport_path = os.path.join(directory, "export.rib")
    exportCommand.RIB(ribExport_path)
    mayaCommand.select([MATERIAL], replace=True, noExpand=True)
    mayaCommand.delete(meshname)

    # cut rib and edit values
    ribExport = stream.fileread(ribExport_path)
    ribExport = re.sub(r"\n(\t|\s)*", "\n", ribExport)
    ribExport = re.sub(r'\n\"', ' "', ribExport)
    ribExport = re.sub(r'\n', " >LINEPOINT< ", ribExport)
    ribShader = ""
    AttrScopes = re.findall(r"AttributeBegin.*?AttributeEnd", ribExport)
    for scope in AttrScopes:
        scope = re.sub(r"\s*\>LINEPOINT\<\s*", "\n", scope)
        isShader = True
        for line in scope.splitlines():
            result = re.search(r"^\w*", line)
            if result.group(0) not in [
                    "AttributeBegin",
                    "Bxdf", "Pattern", "Displace",
                    "AttributeEnd"]:
                isShader = False
        if isShader:
            ribShader = f"\n{scope}\n"
            break
    units = 0.01           # UNIT DEPEND
    subtext = []
    for line in ribShader.splitlines():
        if re.match(r'\s*Displace \"PxrDisplace\"', line):
            submap, text = list(), list()
            pattern = r'\"float dispAmount\" \[.+?\]'
            for match in re.finditer(pattern, line):
                value = re.search(r"\[.*\]", match.group())
                if value:
                    value = float(value.group()[1:-1])
                    submap.append([match, f'"float dispAmount" [{value*units}]'])
            posend = 0
            for pair in submap:
                match, edited = pair
                text.append(line[posend:match.start()])
                text.append(edited)
                posend = match.end()
            text.append(line[posend:len(line)])
            line = "".join(text)
        elif re.match(r'\s*Pattern \"PxrRoundCube\"', line):
            submap, text = list(), list()
            pattern = r'\"float frequency\" \[.+?\]'
            for match in re.finditer(pattern, line):
                value = re.search(r"\[.*\]", match.group())
                if value:
                    value = float(value.group()[1:-1])
                    submap.append([match, f'"float frequency" [{value/units}]'])
            posend = 0
            for pair in submap:
                match, edited = pair
                text.append(line[posend:match.start()])
                text.append(edited)
                posend = match.end()
            text.append(line[posend:len(line)])
            line = "".join(text)
        else:
            submap, text = list(), list()
            pattern = r'\"string name_uvSet\" \[\"[\w\s]+\"\]'
            for match in re.finditer(pattern, line):
                value = re.search(r"\[\".*\"\]", match.group())
                if value:
                    value = value.group()[2:-2]
                    if value != "world":
                        submap.append([match, '"string name_uvSet" [""]'])
            posend = 0
            for pair in submap:
                match, edited = pair
                text.append(line[posend:match.start()])
                text.append(edited)
                posend = match.end()
            text.append(line[posend:len(line)])
            line = "".join(text)
        subtext.append(line)
    ribShader = "\n".join(subtext)
    os.remove(ribExport_path)

    # display rib part
    if ocioConfig:
        ribDisplay = databank.RIB_DISPLAY_EXR
        OUTPUTPATH = os.path.join(directory, nameExr)
    else:
        ribDisplay = databank.RIB_DISPLAY_PNG
        OUTPUTPATH = os.path.join(directory, namePng)
    ribDisplay = re.sub(r"\%OUTPUTPATH\%", OUTPUTPATH, ribDisplay)

    # mesh rib part
    if DISPLACESHADER:
        ribMesh = databank.RIB_MESH_SUBD
        ribMesh = re.sub(r"\%DISPLACESHADER\%", DISPLACESHADER, ribMesh)
        ribMesh = re.sub(r"\%MATERIAL\%", MATERIAL, ribMesh)
    else:
        ribMesh = databank.RIB_MESH
    if filldisplay:
        P  = " ".join([str(i) for i in [
            -1.5, 0,  1.5,
             1.5, 0,  1.5,
            -1.5, 0, -1.5,
             1.5, 0, -1.5]])
        ST = " ".join(
            [str(i) for i in [-1,-1, 2,-1, 2,2, -1,2]])
        WORLD = ST
    else:
        P  = " ".join([str(i) for i in [
            -0.5, 0,  0.5,
             0.5, 0,  0.5,
            -0.5, 0, -0.5,
             0.5, 0, -0.5]])
        ST = " ".join(
            [str(i) for i in [0,0, 1,0, 1,1, 0,1]])
        WORLD = ST
    ribMesh = re.sub(r"\%P\%", P, ribMesh)
    ribMesh = re.sub(r"\%ST\%", ST, ribMesh)
    ribMesh = re.sub(r"\%WORLD\%", WORLD, ribMesh)

    # get all rib parts together
    ribPreview = databank.RIB_PREVIEW
    ribPreview = re.sub(r"\%BXDFSHADER\%", BXDFSHADER, ribPreview)
    ribPreview = re.sub(r"\%MATERIAL\%", MATERIAL, ribPreview)
    ribPreview = re.sub(r"\%DISPLAYRIB\%", ribDisplay, ribPreview)
    ribPreview = re.sub(r"\%SHADERRIB\%", ribShader, ribPreview)
    ribPreview = re.sub(r"\%MESHRIB\%", ribMesh, ribPreview)

    # write to file
    pathRib = os.path.join(directory, "render.rib")
    stream.filewrite(pathRib, ribPreview)
    return pathRib


def createShaderPreview (
        directory: str, periodic: bool = True,
        echo: bool = False) -> Union[str, None]:
    """Create a preview image for a selected Maya material using RenderMan renderer

    Arguments:
        directory: The directory, where an image will be saved
    Keyword Arguments:
        periodic: A flag used to tell that a material has texture repetition
                  and to generate an image that fills a whole camera view
        echo: A flag used to print a summary message
    Returns:
        A path to an image
    """

    # render
    path_RenderRib = createShaderRIB(directory, filldisplay=periodic)
    if os.path.exists(path_RenderRib):
        messageCommand.info("Work On RenderMan Preview")
        command = ["prman", path_RenderRib]
        run.terminal(command, echo=True)
        os.remove(path_RenderRib)
    outputPng = os.path.join(directory, namePng)
    outputExr = os.path.join(directory, nameExr)

    # color correction
    if ocioConfig and os.path.exists(outputExr):
        import OpenImageIO as OIIO
        ImageBuf = OIIO.ImageBuf(outputExr)
        # ["sRGB", "Rec.709"]
        OUT_Buf = OIIO.ImageBufAlgo.ociodisplay(
            ImageBuf, "ACES", "Rec.709",
            fromspace="acescg",
            colorconfig=ocioConfig)
        OUT_Buf.write(outputPng)
        os.remove(outputExr)

    # result message
    if os.path.exists(outputPng):
        if echo: messageCommand.info(
            f'Preview Saved to Directory: "{outputPng}"')
        return outputPng
    elif echo:
        messageCommand.warning(
            'Preview Creation Failed')
