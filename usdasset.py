

import re
import os
encModel = os.getenv("PYTHONIOENCODING")


import ostree
import mayatree


from pxr import (
    Usd,
    UsdGeom,
    UsdShade,
    Gf,
    Vt,
    Sdf )






def makeRelative (path, assetpath):

    relpath = re.sub( os.path.dirname(assetpath), ".", path)

    return relpath






def getMaterialList (stage, name):

    materialList = []

    usdFile = stage.GetRootLayer().realPath
    usdDirectory = os.path.dirname(usdFile)

    searchpath = os.path.join(
        usdDirectory,
        ostree.SUBDIR_SURFACING )

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
        path="/" ):


    for item in tree:


        name = item["name"]
        itempath = os.path.join(path, name)

        PrimPath = Sdf.Path(itempath)
        Prim = source.GetPrimAtPath(PrimPath)

        OverPrim = target.OverridePrim(PrimPath)



        Material = item["material"]
        if Material:
            MaterialName = Material.name().encode(encModel)


            ParentPath = Sdf.Path( os.path.dirname(itempath) )

            ParentPrim = target.GetPrimAtPath(ParentPath)
            Usd.ModelAPI(ParentPrim).SetKind("component")


            MaterialPrim = target.GetPrimAtPath(PrimPath)
            MaterialPrim.ApplyAPI(UsdShade.MaterialBindingAPI)


            DefaultMaterialPath = ParentPath.AppendChild(MaterialName)
            DefaultMaterial = UsdShade.Material.Define(target, DefaultMaterialPath)

            MaterialList = getMaterialList(target, MaterialName)
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
            path=itempath )






def make (
        modelPath,
        assetPath,
        tree,
        name = None ):


    modelStage = Usd.Stage.Open(modelPath)
    assetStage = Usd.Stage.CreateNew(assetPath)

    root = mayatree.getroot(tree)
    rootName = os.path.basename(root)

    if not name:
        name = os.path.basename(assetPath)
        name = os.path.splitext(name)[0]


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
                modelPath = makeRelative(modelPath, assetPath)
                overroot.GetPayloads().AddPayload(modelPath)

                bind( modelStage, assetStage,
                    tree,
                    path=RootPath.pathString )


    layer = assetStage.GetRootLayer()
    layer.defaultPrim = name
    layer.Save()
