#!/usr/bin/env python

"""
Material Export

Define an interface to create USD Material Asset with version control.
"""

import os
import shutil
from typing import Union
import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya
from widgets import MaterialExport
from toolkit.system import ostree
from toolkit.core import Metadata
from toolkit.core import naming
from toolkit.core import timing
import toolkit.maya.find as findCommand
import toolkit.maya.attribute as attributeCommand
import toolkit.maya.renderman as rendermanCommand
import toolkit.maya.message as messageCommand
import toolkit.maya.export as exportCommand
import toolkit.usd.material as materialUSD
import toolkit.usd.imaging as imagingUSD
from toolkit.maya import hypershade


def hasSelfReference (path: str, data: dict) -> bool:
    """Check if the USD material file reference itself 

    Arguments:
        path: The path to the USD file
        data: The description data to create a USD material
    Returns:
        A result of the check
    """
    filename  = os.path.basename(path)
    directory = os.path.dirname(path)
    assetID = Metadata.getID(directory, filename)
    if not assetID:
        return False
    for renderer, scheme in data.items():
        references = scheme.get("references", {})
        for referenceID in references:
            if assetID == referenceID:
                return True
    return False


def Export (options: object = None,
            data: Union[None, dict] = None) -> None:
    """Create USD Material Asset from a Maya material

    Keyword Arguments:
        data: The description data to create a USD material
        options: The options of the export dialog
                 that returns DataClass object
                 with the attributes listed below

        options.library      : str
        options.materialPath : str
        options.materialName : str
        options.version      : int
        options.variant      : str
        options.link         : bool
        options.maya         : bool
        options.info         : str
        options.comment      : str
        options.status       : str
        options.prman        : bool
        options.hydra        : bool
        options.inherit      : bool
    """

    # selection filter
    selection = hypershade.getSelectionName()
    if not selection and not data:
        text = "Select Any Material"
        messageCommand.warning(text)
        messageCommand.viewport(text)
        return
    # show dialog
    if not options:
        name = naming.rule_Material(selection)
        dialog = MaterialExport.Dialog(initname=name)
        dialog.exec()
        options = dialog.getOptions()
        if not options:
            return
    # create export data
    if not data:
        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getSelectionListByName(
            selection, MSelectionList)
        MPlug = OpenMaya.MPlug()
        MSelectionList.getPlug(0, MPlug)
        Material = OpenMaya.MFnDependencyNode(MPlug.node())
        HypershadeManager = hypershade.Manager()
        data = HypershadeManager.getUsdBuildScheme(
            Material, options.inherit)
    # get attributes
    periodic = True
    if selection and mayaCommand.attributeQuery(
            "periodic", node=selection, exists=True):
        periodic = mayaCommand.getAttr(f"{selection}.periodic")

    # version tag
    version = f"v{options.version:02d}"
    if options.variant:
        version += f"-{options.variant}"
    MaterialRoot = os.path.join(options.materialPath, options.materialName)
    MaterialName = f"{version}.usd"
    MaterialPath = os.path.join(MaterialRoot, MaterialName)

    # check for self reference
    if hasSelfReference(MaterialPath, data):
        text = "Export Stopped: Reference Loop"
        messageCommand.warning(text)
        messageCommand.viewport(text)
        return
    # create shader asset directory
    if not os.path.exists(MaterialRoot):
        os.mkdir(MaterialRoot)
    os.chdir(MaterialRoot)

    # make usd files
    references = []
    overwritten = False
    for renderer, scheme in data.items():
        if renderer == "prman":
            fileName = f"{version}.RenderMan.usd"
        elif renderer == "hydra":
            fileName = f"{version}.Hydra.usd"
        else:
            continue
        if not scheme.get("shaders"):
            if not scheme.get("references"):
                continue
        pathusd = os.path.join(MaterialRoot, fileName)
        references.append(pathusd)
        if os.path.exists(pathusd):
            overwritten = True
        materialUSD.make(pathusd, scheme)
    materialUSD.weld(
        MaterialPath, options.materialName, references)

    # create/update symbolic link
    if options.link:
        ostree.linkUpdate(MaterialRoot, MaterialName)

    # create/update .metadata.json
    with Metadata.MetadataManager(
            MaterialRoot, metatype="usdmaterial") as data:
        dataLast = data.get("items").get(MaterialName)
        if dataLast:
            ID = dataLast.get("id")
        else:
            ID = Metadata.generateID(asset="usdmaterial")
        data["info"] = options.info
        data["status"] = options.status
        assetSpec = dict(
            published = timing.getTimeCode(),
            comment   = options.comment,
            periodic  = periodic,
            lama      = True,      # FIGURE IT OUT
            mix       = False,     # FIGURE IT OUT
            id        = ID)
        data["items"][MaterialName] = assetSpec

    # add/update shader to library
    if options.library and not overwritten:
        with Metadata.MetadataManager(
                options.library, metatype="root") as data:
            relpath = MaterialPath.replace(options.library, "")
            data["usdmaterial"][ID] = relpath

    # add/overwrite ID attribute
    if options.library:
        MFnDependencyNode = findCommand.shaderByName(selection)
        attributeCommand.assignNetworkID(MFnDependencyNode, ID)

    # generate preview image
    if os.path.exists(MaterialPath):
        if options.prman or options.hydra:
            ostree.buildUsdRoot(MaterialRoot, previews=True)
            previewsPath = os.path.join(
                MaterialRoot, ostree.SUBDIR_PREVIEWS, version)
            if os.path.exists(previewsPath):
                shutil.rmtree(previewsPath)
            os.mkdir(previewsPath)
            if options.prman and rendermanCommand.isDefined():
                rendermanCommand.createShaderPreview(
                    previewsPath, periodic=periodic)
            if options.hydra:
                imagingUSD.recordMaterialPreview(
                    MaterialPath, periodic=periodic,
                    displacement=True)    # FIGURE IT OUT

    # export selected as maya File
    if options.maya:
        ostree.buildUsdRoot(MaterialRoot, sources=True)
        MayaFileName = f"{version}.ma"
        MayaPath = os.path.join(
            MaterialRoot, ostree.SUBDIR_SOURCES, MayaFileName)
        if os.path.exists(MayaPath):
            mayaMessage = "Source Overwritten: "
        else:
            mayaMessage = "Source Saved: "
        exportCommand.Maya(MayaPath, binary=False)
        messageCommand.info(mayaMessage + MayaFileName)

    # a summary message
    text = "Shader Saved: "
    if overwritten:
        text = "Shader Overwritten: "
    messageCommand.info(text + options.materialName)
