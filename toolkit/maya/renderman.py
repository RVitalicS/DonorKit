#!/usr/bin/env python


import re
import os

import maya.cmds as mayaCommand

from toolkit.system import stream
from toolkit.maya import export
from toolkit.maya import hypershade
from toolkit.maya import message

import databank


ocioConfig = os.getenv("OCIO", "")

nameExr = "Render.exr"
namePng = "Prman.f000.png"





def createShaderRIB (directory, filldisplay=True):


    # get selected shading group
    MATERIAL = hypershade.getSelectionName()
    if not MATERIAL: return


    # create service mesh
    meshname = "_RIBMESH_"
    mayaCommand.polyPlane(
        createUVs=0,
        subdivisionsX=1,
        subdivisionsY=1,
        name=meshname)

    mayaCommand.delete(meshname, constructionHistory = True)
    mayaCommand.sets(meshname, edit=True, forceElement=MATERIAL)


    # get Bxdf/Displace names
    BXDFSHADER = None
    DISPLACESHADER = None

    outPlugs = mayaCommand.listConnections(
        MATERIAL, plugs=True,
        source=True, destination=False )
    for outPlug in outPlugs:
        
        inPlugs = mayaCommand.listConnections(
            outPlug, plugs=True,
            source=False, destination=True )
        for inPlug in inPlugs:
            
            if "rman__surface" in inPlug:
                BXDFSHADER = re.sub(r"\..*", "", outPlug)
            elif "rman__displacement" in inPlug:
                DISPLACESHADER = re.sub(r"\..*", "", outPlug)

    if not BXDFSHADER: return


    # export rib file
    mayaCommand.select(meshname, replace=True)
    ribExport_path = os.path.join(directory, "export.rib")
    export.RIB(ribExport_path)
    mayaCommand.select([MATERIAL], replace=True, noExpand=True)
    mayaCommand.delete(meshname)


    # cut rib and edit displacement strenght
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

    ribShader = re.sub(
        r'\"float dispAmount\" \[.+?\]',
        '"float dispAmount" [0.01]',           # UNIT DEPEND
        ribShader)
    ribShader = re.sub(
        r'\"string name_uvSet\" \[\"[\w\s]*\"\]',
        '"string name_uvSet" [""]',
        ribShader)
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
        P  = " ".join( [str(i) for i in [
            -1.5, 0,  1.5,
             1.5, 0,  1.5,
            -1.5, 0, -1.5,
             1.5, 0, -1.5]] )
        ST = " ".join(
            [str(i) for i in [-1,-1, 2,-1, 2,2, -1,2]] )
    else:
        P  = " ".join( [str(i) for i in [
            -0.5, 0,  0.5,
             0.5, 0,  0.5,
            -0.5, 0, -0.5,
             0.5, 0, -0.5]])
        ST = " ".join(
            [str(i) for i in [0,0, 1,0, 1,1, 0,1]] )
    
    ribMesh = re.sub(r"\%P\%", P, ribMesh)
    ribMesh = re.sub(r"\%ST\%", ST, ribMesh)


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





def createShaderPreview (directory, periodic=True, echo=False):

    # render
    path_RenderRib = createShaderRIB(directory, filldisplay=periodic)
    if os.path.exists(path_RenderRib):
        message.info("Work On RenderMan Preview")

        command = ["prman", path_RenderRib]
        stream.terminal(command, echo=True)
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
            colorconfig=ocioConfig )

        OUT_Buf.write(outputPng)
        os.remove(outputExr)

    # result message
    if os.path.exists(outputPng):
        if echo: message.info(
            f'Preview Saved to Directory: "{outputPng}"' )
        return outputPng
    elif echo:
        message.warning(
            'Preview Creation Failed' )
