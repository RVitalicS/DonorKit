

import os
import re

from pxr import (
    Usd,
    UsdGeom,
    Sdf,
    Gf,
    Work)

Work.SetMaximumConcurrencyLimit()







def copyAttrubutes (source, target, units=1.0):


    isMeter = UsdGeom.LinearUnitsAre(
        units,
        UsdGeom.LinearUnits.meters)


    for Attribute in source.GetAttributes():

        if not Attribute.IsAuthored():
            continue


        attrName  = Attribute.GetBaseName()
        attrSpace = Attribute.GetNamespace()
        if attrSpace:
            attrName = "{}:{}".format(
                attrSpace, attrName)

        attrType  = Attribute.GetTypeName()

        newAttribute = target.CreateAttribute(
            attrName, attrType,
            custom=Attribute.IsCustom() )


        attrValue = Attribute.Get()

        if not isMeter and attrName in ["extent", "points"]:
            for index in range( len(attrValue) ):
                attrValue[index] *= float(units)

        newAttribute.Set(attrValue)


        attrMetadata = Attribute.GetAllMetadata()
        for key, value in attrMetadata.items():
            if key not in ["documentation"]:
                newAttribute.SetMetadata(key, value)







def copyStage (
    source,
    target,
    root="/",
    units=None,
    children=None):
    

    if not units:
        units = UsdGeom.GetStageMetersPerUnit(source)

        UsdGeom.SetStageMetersPerUnit(
            target,
            UsdGeom.LinearUnits.meters )
    
    
    if isinstance(children, type(None)):

        RootPath = Sdf.Path( root )
        RootPrim = source.GetPrimAtPath(RootPath)

        children = [RootPrim]


    scope = os.path.dirname(root)
    if scope == "/": scope = ""


    for ChildPrim in children:

        childpath = ChildPrim.GetPath().pathString
        cutedpath = re.sub(scope, "", childpath)

        NewPath = Sdf.Path(cutedpath)
        NewPrim = target.DefinePrim(
            NewPath, ChildPrim.GetTypeName())

        if os.path.dirname(cutedpath) == "/":
            target.SetDefaultPrim(NewPrim)

        copyAttrubutes(ChildPrim, NewPrim, units=units)


        copyStage(
            source,
            target,
            root=root,
            units=units,
            children=ChildPrim.GetAllChildren())






def addMayaAttributes (stage, tree, path="/"):

    for item in tree:


        name = item["name"]
        itempath = os.path.join(path, name)
        PrimPath = Sdf.Path(itempath)
        Prim = stage.GetPrimAtPath(PrimPath)


        attributes = item["attributes"]
        for key, value in attributes.items():


            if key == "visibility":
                if not value:
                    Prim.SetActive(False)


            elif key == "subdivScheme":
                if not Prim.HasAttribute("subdivisionScheme"):
                    subdivisionScheme = Prim.CreateAttribute(
                        "subdivisionScheme",
                        Sdf.ValueTypeNames.Token,
                        variability=UsdGeom.Tokens.uniform )

                else:
                    subdivisionScheme = Prim.GetAttribute("subdivisionScheme")

                    subdivisionScheme.Set(value)


            elif key == "rman_displacementBound":
                Schema  = UsdGeom.PrimvarsAPI(Prim)
                Primvar = Schema.CreatePrimvar(
                    "ri:attributes:displacementbound:sphere",
                    Sdf.ValueTypeNames.Float,
                    interpolation=UsdGeom.Tokens.constant )
                Primvar.Set(value)


        addMayaAttributes(
            stage,
            item["children"],
            path=itempath)
