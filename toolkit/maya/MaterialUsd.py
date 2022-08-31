#!/usr/bin/env python



import re
import os
import shutil
import importlib

from widgets import (
    MaterialExport,
    Metadata)

import toolkit.core.naming
import toolkit.core.timing
import toolkit.system.ostree

import toolkit.maya.outliner
import toolkit.maya.message
import toolkit.maya.attribute
import toolkit.maya.renderman

import toolkit.maya.hypershade
importlib.reload(toolkit.maya.hypershade)

import toolkit.usd.material
import toolkit.usd.imaging

import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya




def Export (options=None, data=None):

    """
        options.materialPath = "/server/library"
        options.materialName = "Plastic"
        options.version      = 1
        options.variant      = None/"Red"
        options.link         = True
        options.maya         = False
        options.info         = ""
        options.comment      = ""
        options.status       = "WIP"
        options.prman        = False
        options.hydra        = False
    """


    # selection filter
    selection = toolkit.maya.hypershade.getSelectionName()
    if not selection and not data:
        text = "Select Any Material"
        toolkit.maya.message.warning(text)
        toolkit.maya.message.viewport(text)
        return


    # create export data
    if not data:

        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName(
            selection, MSelectionList)
        MPlug = OpenMaya.MPlug()
        MSelectionList.getPlug(0, MPlug)
        Material = OpenMaya.MFnDependencyNode(MPlug.node())
    
        HypershadeManager = toolkit.maya.hypershade.Manager()
        data = dict(
            render = HypershadeManager.getPrmanNetwork(Material),
            preview= HypershadeManager.getPreviewNetwork(Material))


    # show dialog
    if not options:
        dialog = MaterialExport.Dialog(initname=selection)
        dialog.exec()
        options = dialog.getOptions()
        if not options: return


    # get attributes
    periodic = False
    if selection and mayaCommand.attributeQuery(
            "periodic", node=selection, exists=True):
        periodic = mayaCommand.getAttr(
            "{}.periodic".format(selection) )


    # version tag
    version = "v{:02d}".format(options.version)
    if options.variant:
        version += "-{}".format(options.variant)

    MaterialRoot = os.path.join(options.materialPath, options.materialName)
    MaterialName = "{}.usda".format(version)
    MaterialPath = os.path.join(MaterialRoot, MaterialName)


    # create shader asset directory
    if not os.path.exists(MaterialRoot):
        os.mkdir(MaterialRoot)
    os.chdir(MaterialRoot)


    # make usd files
    payloads = []
    for target, scheme in data.items():
        message = "Shader Saved: "

        if scheme.get("shaders"):

            if target == "render":
                prman=True
                fileName = "{}.RenderMan.usda".format(version)

            else:
                prman=False
                fileName = "{}.Hydra.usda".format(version)

            pathusd = os.path.join(MaterialRoot, fileName)
            payloads.append(pathusd)

            if os.path.exists(pathusd):
                message = "Shader Overwritten: "

            scheme["name"] = options.materialName
            toolkit.usd.material.make(
                pathusd, scheme, prman=prman )


    # weld shaders
    toolkit.usd.material.weld(
        MaterialPath, options.materialName, payloads)


    # create/update symbolic link
    if options.link:
        FinalName = re.sub(r"^v\d+", "Final", MaterialName)
        FinalPath = os.path.join(MaterialRoot, FinalName)

        if os.path.exists(FinalPath):
            os.remove(FinalPath)

        os.symlink(MaterialName, FinalName)


    # create/update .metadata.json
    with Metadata.MetadataManager(
            MaterialRoot,
            metatype="usdmaterial") as data:

        data["info"] = options.info
        data["status"] = options.status
        data["items"][MaterialName] = dict(
            published = toolkit.core.timing.getTimeCode(),
            comment   = options.comment,
            periodic  = periodic,
            lama      = True,      # FIGURE IT OUT
            mix       = False )    # FIGURE IT OUT


    # generate preview image
    if os.path.exists(MaterialPath):
        if options.prman or options.hydra:
            toolkit.system.ostree.buildUsdRoot(
                MaterialRoot, previews=True)

            previewsPath = os.path.join( MaterialRoot,
                toolkit.system.ostree.SUBDIR_PREVIEWS, version)
            if os.path.exists(previewsPath):
                shutil.rmtree(previewsPath)
            os.mkdir(previewsPath)

            if options.prman:
                toolkit.maya.renderman.createShaderPreview(
                    previewsPath, periodic=periodic)

            if options.hydra:
                toolkit.usd.imaging.recordMaterialPreview(
                    MaterialPath, periodic=periodic,
                    displacement=True )    # FIGURE IT OUT


    # export selected as maya File
    if options.maya:
        toolkit.system.ostree.buildUsdRoot(
            MaterialRoot, sources=True)

        MayaFileName = "{}.ma".format(options.materialName)
        MayaPath = os.path.join(
            MaterialRoot,
            toolkit.system.ostree.SUBDIR_SOURCES,
            MayaFileName )

        if os.path.exists(MayaPath):
            mayaMessage = "Source Overwritten: "
        else:
            mayaMessage = "Source Saved: "

        toolkit.maya.export.Maya(MayaPath, binary=False)

        toolkit.maya.message.info(mayaMessage + MayaFileName)


    # result message
    toolkit.maya.message.info(message + options.materialName)
