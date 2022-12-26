#!/usr/bin/env python

"""
Asset Building

This module defines functions to create Assets
as layered structures of geometry, animation and materials.
"""

import re
import os
from toolkit.system.ostree import SUBDIR_SURFACING
from toolkit.usd import editor
from pxr import Usd
from pxr import UsdGeom
from pxr import UsdShade
from pxr import Sdf
from typing import Union


def getMaterialList (stage: Usd.Stage, name: str) -> list:
    """Get material file paths with a corresponding version and name
    that used in the specified USD scene

    Arguments:
        stage: The scene that has the material
        name: The name of material
    Returns:
        Material file paths
    """
    materialList = []

    stagePath = stage.GetRootLayer().realPath
    stageName = os.path.basename(stagePath)
    # TODO: use naming module
    version = re.search(
        r"\.v\d+-*[A-Za-z]*\.", stageName)
    if not version:
        return materialList
    version = re.sub(r"\.", "", version.group())

    searchPath = os.path.join(
        os.path.dirname(stagePath), SUBDIR_SURFACING, name)
    if not os.path.exists(searchPath):
        return materialList
    for shaderName in os.listdir(searchPath):
        if re.match(r"{}\.usd[ac]?$".format(version), shaderName):
            shaderPath = os.path.join(searchPath, shaderName)
            shaderPath = editor.makeRelative(shaderPath, stagePath)
            materialList.append(shaderPath)

    return materialList


def bind (source: Usd.Stage, target: Usd.Stage, tree: list,
          root: Union[str, None] = None, path: str = "/" ) -> None:
    """Create 'Look' scope at the root of the UsdStage
    and collect materials that used in this scene.
    Assign those materials to objects or faces.

    Arguments:
        source: The scene to read hierarchy
        target: The scene to create overrides
        tree: The description data for material bindings
    Keyword Arguments:
        root: The scene path to create 'Look' scope
        path: The scene path point of the current iteration
    """
    for item in tree:
        name = item["name"]
        itempath = os.path.join(path, name)
        PrimPath = Sdf.Path(itempath)
        Prim = source.GetPrimAtPath(PrimPath)
        if not Prim:
            continue
        if root:
            overpath = root + itempath
        else:
            # root = itempath
            overpath = itempath
        OverPrimPath = Sdf.Path(overpath)
        OverPrim = target.OverridePrim(OverPrimPath)

        # get material names for this Prim
        materials = item["materials"]
        if materials:
            ParentPath = Sdf.Path(os.path.dirname(overpath))
            ParentPrim = target.GetPrimAtPath(ParentPath)
            Usd.ModelAPI(ParentPrim).SetKind("component")

            ScopePath = Sdf.Path(root).AppendChild("Looks")
            if not target.GetPrimAtPath(ScopePath).IsValid():
                UsdGeom.Scope.Define(target, ScopePath)

            # define materials and make bindings
            isSubset = len(materials) > 1
            for name in materials:
                pathlist = getMaterialList(target, name)
                if not pathlist:
                    continue
                MaterialPath = ScopePath.AppendChild(name)
                if target.GetPrimAtPath(MaterialPath).IsValid():
                    Material = UsdShade.Material.Get(target, MaterialPath)
                else:
                    Material = UsdShade.Material.Define(target, MaterialPath)
                    MaterialPrim = target.GetPrimAtPath(MaterialPath)
                    for relpath in pathlist:
                        MaterialPrim.GetPayloads().AddPayload(relpath)
                if isSubset:
                    GeomSubsetPath = OverPrimPath.AppendChild(name)
                    GeomSubsetPrim = target.OverridePrim(GeomSubsetPath)
                    GeomSubsetPrim.ApplyAPI(UsdShade.MaterialBindingAPI)
                    UsdShade.MaterialBindingAPI(GeomSubsetPrim).Bind(Material)
                else:
                    ShapePrim = target.GetPrimAtPath(OverPrimPath)
                    ShapePrim.ApplyAPI(UsdShade.MaterialBindingAPI)
                    UsdShade.MaterialBindingAPI(OverPrim).Bind(Material)

        bind(source, target, item["children"], root=root, path=itempath)


def make (assetPath: str, sourcePath: str, proxyPath: str,
          tree: list, root: str, name: Union[str, None] = None) -> None:
    """Create USD Asset with a referenced geometry and assigned materials

    Arguments:
        assetPath: The path to create a USD file
        sourcePath:The path of the USD file reference
        proxyPath: The path of the USD file for proxy purpose
        tree: The description data for material bindings
        root: The scene path to use as root
    Keyword Arguments:
        name: The name of the scene root
    """
    sourceStage = Usd.Stage.Open(sourcePath, load=Usd.Stage.LoadNone)
    assetStage = Usd.Stage.CreateNew(assetPath, load=Usd.Stage.LoadNone)
    rootName = os.path.basename(root)
    if not name:
        name = os.path.dirname(assetPath)
        name = os.path.basename(name)

    RootPath = Sdf.Path( "/{}".format(name) )
    Xform = UsdGeom.Xform.Define(assetStage, RootPath)
    ModelAPI = Usd.ModelAPI(Xform)
    ModelAPI.SetKind("assembly")

    # add layers
    TreeRootPath = RootPath.AppendChild(rootName)
    overroot = assetStage.OverridePrim(TreeRootPath)
    overroot.GetPayloads().AddPayload(
        editor.makeRelative(sourcePath, assetPath) )
    if os.path.exists(proxyPath):
        overroot.GetPayloads().AddPayload(
            editor.makeRelative(proxyPath, assetPath) )

    # assign materials
    bind(sourceStage, assetStage, tree, root=RootPath.pathString)

    # scene metadata
    if sourceStage.GetStartTimeCode() != sourceStage.GetEndTimeCode():
        assetStage.SetStartTimeCode( sourceStage.GetStartTimeCode() )
        assetStage.SetEndTimeCode( sourceStage.GetEndTimeCode() )
        assetStage.SetFramesPerSecond( sourceStage.GetFramesPerSecond() )
    Layer = assetStage.GetRootLayer()
    Layer.defaultPrim = name
    Layer.Export(assetPath, args=dict(format="usda"))
