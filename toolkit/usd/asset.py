#!/usr/bin/env python



import re
import os


from toolkit.system.ostree import SUBDIR_SURFACING
import toolkit.usd.editor


from pxr import Usd, UsdGeom, UsdShade, Gf, Sdf






def getMaterialList (stage, name):

    materialList = []

    stagePath = stage.GetRootLayer().realPath
    directory = os.path.dirname(stagePath)


    stageName = os.path.basename(stagePath)
    version = re.search(r"\.v\d+-*[A-Za-z]*\.", stageName)
    if not version:
        return materialList

    version = version.group()
    version = re.sub(r"\.", "", version)


    searchPath = os.path.join(
        directory,
        SUBDIR_SURFACING, name )

    for shaderName in os.listdir(searchPath):
        if re.match(r"{}\.usd[ac]*$".format(version), shaderName):

            shaderPath = os.path.join(searchPath, shaderName)
            shaderPath = toolkit.usd.editor.makeRelative(shaderPath, stagePath)

            materialList.append(shaderPath)

    return materialList






def bind (
        source,
        target,
        tree,
        root=None,
        path="/" ):


    for item in tree:


        name = item["name"]
        itempath = os.path.join(path, name)

        PrimPath = Sdf.Path(itempath)
        Prim = source.GetPrimAtPath(PrimPath)

        if Prim:

            if root: overpath = root + itempath
            else: overpath = itempath

            OverPrimPath = Sdf.Path(overpath)
            OverPrim = target.OverridePrim(OverPrimPath)


            materials = item["materials"]
            if materials:

                ParentPath = Sdf.Path( os.path.dirname(overpath) )
                ParentPrim = target.GetPrimAtPath(ParentPath)
                Usd.ModelAPI(ParentPrim).SetKind("component")

                ScopePath = Sdf.Path(root).AppendChild("Looks")
                if not target.GetPrimAtPath(ScopePath).IsValid():
                    UsdGeom.Scope.Define(target, ScopePath)

                isSubset = len(materials) > 1
                for name in materials:

                    MaterialPath = ScopePath.AppendChild(name)
                    if target.GetPrimAtPath(MaterialPath).IsValid():
                        Material = UsdShade.Material.Get(target, MaterialPath)
                    else:
                        Material = UsdShade.Material.Define(target, MaterialPath)
                        MaterialPrim = target.GetPrimAtPath(MaterialPath)
                        for relpath in getMaterialList(target, name):
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


            bind(
                source,
                target,
                item["children"],
                root=root,
                path=itempath )






def make (
        sourcePath,
        assetPath,
        tree,
        root,
        name = None ):


    sourceStage = Usd.Stage.Open(sourcePath)
    assetStage = Usd.Stage.CreateNew(assetPath)

    rootName = os.path.basename(root)

    if not name:
        name = os.path.dirname(assetPath)
        name = os.path.basename(name)


    RootPath = Sdf.Path( "/{}".format(name) )
    Xform = UsdGeom.Xform.Define(assetStage, RootPath)

    ModelAPI = Usd.ModelAPI(Xform)
    ModelAPI.SetKind("assembly")
    ModelAPI.SetAssetName( name )


    RootPrim = assetStage.GetPrimAtPath(RootPath)
    VariantSet = RootPrim.GetVariantSets().AddVariantSet("geo")

    for variant in ["proxy", "render"]:
        VariantSet.AddVariant(variant)
        VariantSet.SetVariantSelection(variant)

        with VariantSet.GetVariantEditContext():
            TreeRootPath = RootPath.AppendChild(rootName)
            overroot = assetStage.OverridePrim(TreeRootPath)

            if variant == "render":
                payloadPath = toolkit.usd.editor.makeRelative(sourcePath, assetPath)
                overroot.GetPayloads().AddPayload(payloadPath)

                bind( sourceStage, assetStage,
                    tree,
                    root=RootPath.pathString )


    if sourceStage.GetStartTimeCode() != sourceStage.GetEndTimeCode():
        assetStage.SetStartTimeCode( sourceStage.GetStartTimeCode() )
        assetStage.SetEndTimeCode( sourceStage.GetEndTimeCode() )
        assetStage.SetFramesPerSecond( sourceStage.GetFramesPerSecond() )

    layer = assetStage.GetRootLayer()
    layer.defaultPrim = name
    layer.Save()
