

import os
import re

from pxr import Usd, UsdGeom, UsdShade, Gf, Vt, Sdf





def makeRelative (path, assetpath):

    relpath = re.sub( os.path.dirname(assetpath), ".", path)

    return relpath







def make (
        assetPath,
        render   = None,
        proxy    = None,
        name     = None,
        root     = None,
        instance = True ):


    stage = Usd.Stage.CreateNew(assetPath)

    if not root: root = "root"

    if not name:
        name = os.path.basename(assetPath)
        name = os.path.splitext(name)[0]


    RootPath = Sdf.Path( "/{}".format(name) )
    Xform = UsdGeom.Xform.Define(stage, RootPath)

    ModelAPI = Usd.ModelAPI(Xform)
    ModelAPI.SetKind("assembly")
    ModelAPI.SetAssetName( name )


    RootPrim = stage.GetPrimAtPath(RootPath)
    VariantSet = RootPrim.GetVariantSets().AddVariantSet("geo")

    for variant in ["proxy", "render"]:
        VariantSet.AddVariant(variant)
        VariantSet.SetVariantSelection(variant)

        with VariantSet.GetVariantEditContext():
            TreeRootPath = RootPath.AppendChild(root)
            overroot = stage.OverridePrim(TreeRootPath)

            if proxy and variant == "proxy":
                proxy = makeRelative(proxy, assetPath)
                overroot.GetPayloads().AddPayload(proxy)

            elif render and variant == "render":
                render = makeRelative(render, assetPath)
                overroot.GetPayloads().AddPayload(render)


    if instance:
        RootPrim.SetInstanceable(True)


    layer = stage.GetRootLayer()
    layer.defaultPrim = name
    layer.Save()
