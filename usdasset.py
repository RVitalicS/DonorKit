

import re
import os
encModel = os.getenv("PYTHONIOENCODING")


import ostree
import mayatree
import usdeditor


from pxr import (
    Usd,
    UsdGeom,
    UsdShade,
    Gf, Sdf )






def getMaterialList (stage, name):

    materialList = []

    usdFile = stage.GetRootLayer().realPath
    usdDirectory = os.path.dirname(usdFile)

    searchpath = os.path.join(
        usdDirectory,
        ostree.SUBDIR_SURFACING )
    if os.path.exists(searchpath):
        for item in os.listdir(searchpath):
            if re.match(r"{}\..+".format(name), item):
                RelPath = "./{}/{}".format(
                    ostree.SUBDIR_SURFACING, item)
                materialList.append(RelPath)

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



            Material = item["material"]
            if Material:
                MaterialName = Material.name().encode(encModel)
                MaterialList = getMaterialList(target, MaterialName)
                if MaterialList:

                    ParentPath = Sdf.Path( os.path.dirname(overpath) )

                    ParentPrim = target.GetPrimAtPath(ParentPath)
                    Usd.ModelAPI(ParentPrim).SetKind("component")


                    MaterialPrim = target.GetPrimAtPath(OverPrimPath)
                    MaterialPrim.ApplyAPI(UsdShade.MaterialBindingAPI)


                    DefaultMaterialPath = ParentPath.AppendChild(MaterialName)
                    DefaultMaterial = UsdShade.Material.Define(target, DefaultMaterialPath)

                    for RelPath in MaterialList:

                        OverMaterial = target.OverridePrim(DefaultMaterialPath)
                        OverMaterial.GetPayloads().AddPayload(RelPath)


                    UsdShade.MaterialBindingAPI(OverPrim).Bind(DefaultMaterial)

                    attributes = item["attributes"]
                    for key, value in attributes.items():

                        if key == "displayColor":
                            Schema  = UsdGeom.PrimvarsAPI(OverPrim)
                            Primvar = Schema.CreatePrimvar(
                                "primvars:displayColor",
                                Sdf.ValueTypeNames.Color3fArray )
                            Primvar.Set([Gf.Vec3f(value)])
                            break


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
        name = None ):


    sourceStage = Usd.Stage.Open(sourcePath)
    assetStage = Usd.Stage.CreateNew(assetPath)

    root = mayatree.getroot(tree)
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
                payloadPath = usdeditor.makeRelative(sourcePath, assetPath)
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
