#!/usr/bin/env python


import re
import os

import maya.cmds as mayaCommand

import toolkit.system.stream
import toolkit.maya.export


ocioConfig = os.getenv("OCIO", "")

nameExr = "Render.exr"
namePng = "Prman.f000.png"

thisDir = os.path.dirname(__file__)
toolDir = os.path.dirname(thisDir)
rootDir = os.path.dirname(toolDir)





def createShaderRIB (directory, filldisplay=True):


    # get selected shading group
    MATERIAL = None
    selection = mayaCommand.ls( selection=True )
    if selection:
        node = selection[0]
        if mayaCommand.nodeType(node) == "shadingEngine":
            MATERIAL = node

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
    path_ExportRib = os.path.join(directory, "export.rib")
    toolkit.maya.export.RIB(path_ExportRib)
    mayaCommand.select(selection, replace=True, noExpand=True)
    mayaCommand.delete(meshname)


    # cut rib and edit displacement strenght
    data_ExportRib = toolkit.system.stream.fileread(path_ExportRib)
    data_ExportRib = re.sub(r"\n(\t|\s)*", "\n", data_ExportRib)
    data_ExportRib = re.sub(r'\n\"', ' "', data_ExportRib)
    data_ExportRib = re.sub(r'\n', " >LINEPOINT< ", data_ExportRib)

    data_ShaderRib = ""
    AttrScopes = re.findall(r"AttributeBegin.*?AttributeEnd", data_ExportRib)
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
            data_ShaderRib = "\n{}\n".format(scope)
            break

    data_ShaderRib = re.sub(
        r'\"float dispAmount\" \[.+?\]',
        '"float dispAmount" [0.01]',           # UNIT DEPEND
        data_ShaderRib)
    os.remove(path_ExportRib)


    # display rib part
    databank = os.path.join(rootDir, "databank")
    if ocioConfig:
        path_DisplayRib = os.path.join(databank, "display-exr.rib")
        OUTPUTPATH = os.path.join(directory, nameExr)
    else:
        path_DisplayRib = os.path.join(databank, "display-png.rib")
        OUTPUTPATH = os.path.join(directory, namePng)

    data_DisplayRib = toolkit.system.stream.fileread(path_DisplayRib)
    data_DisplayRib = re.sub(r"\%OUTPUTPATH\%", OUTPUTPATH, data_DisplayRib)


    # mesh rib part
    if DISPLACESHADER:
        path_MeshRib = os.path.join(databank, "mesh-subdivision.rib")
        data_MeshRib = toolkit.system.stream.fileread(path_MeshRib)
        data_MeshRib = re.sub(r"\%DISPLACESHADER\%", DISPLACESHADER, data_MeshRib)
        data_MeshRib = re.sub(r"\%MATERIAL\%", MATERIAL, data_MeshRib)
    else:
        path_MeshRib = os.path.join(databank, "mesh.rib")
        data_MeshRib = toolkit.system.stream.fileread(path_MeshRib)

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
    
    data_MeshRib = re.sub(r"\%P\%", P, data_MeshRib)
    data_MeshRib = re.sub(r"\%ST\%", ST, data_MeshRib)


    # get all rib parts together
    path_PreviewRib = os.path.join(databank, "preview-shader.rib")
    data_PreviewRib = toolkit.system.stream.fileread(path_PreviewRib)

    data_PreviewRib = re.sub(r"\%BXDFSHADER\%", BXDFSHADER, data_PreviewRib)
    data_PreviewRib = re.sub(r"\%MATERIAL\%", MATERIAL, data_PreviewRib)

    data_PreviewRib = re.sub(r"\%DISPLAYRIB\%", data_DisplayRib, data_PreviewRib)
    data_PreviewRib = re.sub(r"\%SHADERRIB\%", data_ShaderRib, data_PreviewRib)
    data_PreviewRib = re.sub(r"\%MESHRIB\%", data_MeshRib, data_PreviewRib)


    # write to file
    path_RenderRib = os.path.join(directory, "render.rib")
    toolkit.system.stream.filewrite(path_RenderRib, data_PreviewRib)

    return path_RenderRib





def createShaderPreview (directory, periodic=True, echo=False):

    # render
    path_RenderRib = createShaderRIB(directory, filldisplay=periodic)
    if os.path.exists(path_RenderRib):
        command = ["prman", path_RenderRib]
        toolkit.system.stream.terminal(command, echo=True)
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
        if echo:
            message = 'INFO: preview saved to directory: "{}"'
            print(message.format(outputPng))
        return outputPng
    elif echo:
        message = 'INFO: preview creation failed'
        print(message)
