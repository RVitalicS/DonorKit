#!/usr/bin/env python



import re
import os
import shutil

from pxr import Usd
from widgets import Metadata

import toolkit.core.naming
import toolkit.core.timing
import toolkit.system.ostree
import toolkit.maya.message
import toolkit.maya.hypershade
import toolkit.maya.renderman
import toolkit.usd.material

import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya




def Export (options=None, data=None):

    """
        options.materialPath = "/"
        options.materialName = ""
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


    if not data:

        # selection filters
        selection = mayaCommand.ls(selection=True)
        if not selection:
            text = "Select Any Object"
            toolkit.maya.message.warning(text)
            toolkit.maya.message.viewport(text)
            return

        nodeName = selection[0]
        if mayaCommand.nodeType(nodeName) != "shadingEngine":
            text = "Wrong Selection"
            toolkit.maya.message.warning(text)
            toolkit.maya.message.viewport(text)
            return

        # get selected material
        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName(
            nodeName, MSelectionList)

        MPlug = OpenMaya.MPlug()
        MSelectionList.getPlug(0, MPlug)

        MObject = MPlug.node()
        Material = OpenMaya.MFnDependencyNode(MObject)
    
        # export data
        HypershadeManager = toolkit.maya.hypershade.Manager()
        data = dict(
            render = HypershadeManager.getPrmanNetwork(Material),
            preview= HypershadeManager.getPreviewNetwork(Material))

        # name = toolkit.core.naming.nameFilterSG(Material.name())



    # GET UI PARAMETERS
    if not options:
        return



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
            periodic  = True,      # FIGURE IT OUT
            lama      = True,      # FIGURE IT OUT
            mix       = False )    # FIGURE IT OUT


    # generate preview image
    if os.path.exists(MaterialPath) and options.prman:
        toolkit.system.ostree.buildUsdRoot(
            MaterialRoot, previews=True)

        previewsPath = os.path.join( MaterialRoot,
            toolkit.system.ostree.SUBDIR_PREVIEWS, version)
        if os.path.exists(previewsPath):
            shutil.rmtree(previewsPath)
        os.mkdir(previewsPath)

        toolkit.maya.renderman.createShaderPreview(
            previewsPath, periodic=True)


    # result message
    toolkit.maya.message.info(message + options.materialName)
