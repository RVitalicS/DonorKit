

import re
import os
import ostree


from pxr import Usd, UsdGeom, UsdShade, Gf, Vt, Sdf









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








def wrap (
        source,
        target,
        tree,
        scope=None,
        path="/" ):


    for item in tree:


        name = item["name"]
        itempath = os.path.join(path, name)

        PrimPath = Sdf.Path(itempath)
        Prim = source.GetPrimAtPath(PrimPath)

        OverPrim = target.OverridePrim(PrimPath)


        if path=="/":
            layer = target.GetRootLayer()
            layer.defaultPrim = name



        MaterialName = item["material"]
        if MaterialName:


            ParentPath = Sdf.Path( os.path.dirname(itempath) )

            ParentPrim = target.GetPrimAtPath(ParentPath)
            Usd.ModelAPI(ParentPrim).SetKind("component")

            if scope:
                ParentPath = ParentPath.AppendChild(scope)
                UsdGeom.Scope.Define(target, ParentPath)


            MaterialPrim = target.GetPrimAtPath(PrimPath)
            MaterialPrim.ApplyAPI(UsdShade.MaterialBindingAPI)


            DefaultMaterialPath = ParentPath.AppendChild(MaterialName)
            DefaultMaterial = UsdShade.Material.Define(target, DefaultMaterialPath)

            MaterialList = getMaterialList(target, MaterialName)
            for RelPath in MaterialList:
                OverMaterial = target.OverridePrim(DefaultMaterialPath)
                OverMaterial.GetReferences().AddReference(RelPath)


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


        wrap(
            source,
            target,
            item["children"],
            scope=scope,
            path=itempath )
