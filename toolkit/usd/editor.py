#!/usr/bin/env python



import os
import re


import toolkit.core.naming
import toolkit.usd.attribute


from pxr import UsdGeom, Sdf, Vt, Gf, Work

Work.SetMaximumConcurrencyLimit()






def makeRelative (target, source):

    targetSdfPath = Sdf.Path( os.path.dirname( target ) )
    sourceSdfPath = Sdf.Path( os.path.dirname( source ) )

    relativeSdfPath = targetSdfPath.MakeRelativePath(sourceSdfPath)

    relative = "{}/{}".format(
        relativeSdfPath.pathString,
        os.path.basename( target ) )

    if re.match( r"^\w+.*", relative ):
        relative = "./" + relative

    return relative







def getDisplayColorName (name):

    for part in name.split(":"):
        if "displayColor" in part:
            name = part
            break

    return name







def copyAttrubutes (source, target, units=1.0, time=1.0):


    isMeter = UsdGeom.LinearUnitsAre(
        units,
        UsdGeom.LinearUnits.meters)


    colorData = dict()

    for Attribute in source.GetAttributes():

        if not Attribute.IsAuthored():
            continue


        attrName  = Attribute.GetBaseName()
        attrType  = Attribute.GetTypeName()


        if attrType == Sdf.ValueTypeNames.Token:
            if attrName in ["familyType", "familyName"]:
                continue


        attrSpace = Attribute.GetNamespace()
        if attrSpace:
            attrName = "{}:{}".format(
                attrSpace, attrName)


        if "displayColor" in attrName:

            colorName = getDisplayColorName(attrName)
            if colorName not in colorData:
                colorData[colorName] = dict(colors={}, indices={})

            if attrType == Sdf.ValueTypeNames.Color3fArray:
                colorData[colorName]["colors"] = Attribute.Get(time=time)
                continue

            elif attrType == Sdf.ValueTypeNames.IntArray:
                colorData[colorName]["indices"] = Attribute.Get(time=time)
                continue


        newAttribute = target.CreateAttribute(
            attrName, attrType,
            custom=Attribute.IsCustom() )


        attrValue = Attribute.Get(time=time)

        if not isMeter and attrName in [
                "extent", "points",
                "xformOp:translate" ]:

            for index in range( len(attrValue) ):
                attrValue[index] *= float(units)

        newAttribute.Set(value=attrValue)


        attrMetadata = Attribute.GetAllMetadata()
        for key, value in attrMetadata.items():
            if key not in ["documentation", "allowedTokens"]:
                newAttribute.SetMetadata(key, value)


    # edit displayColor
    if colorData:
        colors, indices = [],[]
        for name, data in colorData.items():

            rule = dict()
            for indexData, color in enumerate(data["colors"]):
                if not color in colors:
                    colors.append(color)
                indexColor = colors.index(color)
                rule["{}".format(indexData)] = indexColor

            bindmap = []
            for colorCode in data["indices"]:
                newCode = rule["{}".format(colorCode)]
                bindmap.append(newCode)

            if not indices:
                indices = bindmap
            else:
                for index in range(len(indices)):
                    valueI = indices[index]
                    valueB = bindmap[index]
                    indices[index] = max(valueI, valueB)

        colorsAttr = target.CreateAttribute(
            "primvars:displayColor",
            Sdf.ValueTypeNames.Color3fArray,
            custom=False)
        colorsAttr.Set(
            value=Vt.Vec3fArray(colors) )

        if len(colors) > 1:
            colorsAttr.SetMetadata("interpolation", "uniform")
            if indices:
                indicesAttr = target.CreateAttribute(
                    "primvars:displayColor:indices",
                    Sdf.ValueTypeNames.IntArray,
                    custom=False)
                indicesAttr.Set(
                    value=Vt.IntArray(indices) )






def copyStage (source, target,
               root=None,
               units=None,
               children=None):
    

    if root is None:
        root = "/"


    if units is None:
        units = UsdGeom.GetStageMetersPerUnit(source)

        UsdGeom.SetStageMetersPerUnit(
            target,
            UsdGeom.LinearUnits.meters )
    
    
    if children is None:

        RootPath = Sdf.Path( root )
        RootPrim = source.GetPrimAtPath(RootPath)

        children = [RootPrim]


    scope = os.path.dirname(root)
    if scope == "/": scope = ""


    for ChildPrim in children:

        childname = ChildPrim.GetName()
        childpath = ChildPrim.GetPath().pathString
        cutedpath = re.sub(scope, "", childpath)

        if childname == "Looks":
            if ChildPrim.GetTypeName() == "Scope":
                continue

        if ChildPrim.GetTypeName() == "GeomSubset":
            newname = toolkit.core.naming.nameFilterSG(childname)
            cutedpath = re.sub("{}$".format(childname), newname, cutedpath)

        NewPath = Sdf.Path(cutedpath)
        NewPrim = target.DefinePrim(
            NewPath, ChildPrim.GetTypeName())

        if os.path.dirname(cutedpath) == "/":
            target.SetDefaultPrim(NewPrim)

        copyAttrubutes(ChildPrim, NewPrim, units=units)


        copyStage(source, target,
                  root=root,
                  units=units,
                  children=ChildPrim.GetAllChildren())






def copyTimeSamples (source, target, units=1.0):


    for Attribute in source.GetAttributes():

        timeSamples = Attribute.GetTimeSamples()
        if len(timeSamples) > 1:

            attrBaseName = Attribute.GetBaseName()
            if attrBaseName in [
                    "points",
                    "normals",
                    "translate",
                    "scale",
                    "rotateXYZ",
                    "extent" ]:

                OverPrim = target.OverridePrim(source.GetPath())

                if attrBaseName == "translate":
                    Xformable = UsdGeom.Xformable(OverPrim)
                    newAttribute = toolkit.usd.attribute.getTranslateOp(Xformable)

                elif attrBaseName == "rotateXYZ":
                    Xformable = UsdGeom.Xformable(OverPrim)
                    newAttribute = toolkit.usd.attribute.getRotateXYZOp(Xformable)

                elif attrBaseName == "scale":
                    Xformable = UsdGeom.Xformable(OverPrim)
                    newAttribute = toolkit.usd.attribute.getScaleOp(Xformable)

                else:
                    newAttribute = OverPrim.CreateAttribute(
                        Attribute.GetName(),
                        Attribute.GetTypeName(),
                        custom=Attribute.IsCustom() )

                for sample in timeSamples:

                    attrValue = Attribute.Get(time=sample)

                    if attrBaseName in ["points", "translate", "extent"]:
                        for index in range( len(attrValue) ):
                            attrValue[index] *= float(units)

                    newAttribute.Set(value=attrValue, time=sample)






def copyAnimation ( source, target,
                    root="/",
                    reference=None,
                    units=1.0,
                    children=None ):
    

    if children is None:

        defaultPrim = source.GetDefaultPrim()

        if not reference:
            reference = str(source.GetRootLayer().resolvedPath)

        animationPath = str(target.GetRootLayer().resolvedPath)
        reference = makeRelative(reference, animationPath)

        OverPrim = target.OverridePrim(defaultPrim.GetPath())
        OverPrim.GetReferences().AddReference( reference )
        
        target.SetDefaultPrim(OverPrim)


        target.SetStartTimeCode( source.GetStartTimeCode() )
        target.SetEndTimeCode( source.GetEndTimeCode() )
        target.SetFramesPerSecond( source.GetFramesPerSecond() )


        RootPath = Sdf.Path( root )
        RootPrim = source.GetPrimAtPath(RootPath)

        children = [RootPrim]


    for ChildPrim in children:
        copyTimeSamples(ChildPrim, target, units=units)

        copyAnimation(
            source,
            target,
            root=root,
            units=units,
            children=ChildPrim.GetAllChildren() )






def addMayaAttributes (stage, tree, path="/"):

    for item in tree:


        name = item["name"]
        itempath = os.path.join(path, name)
        PrimPath = Sdf.Path(itempath)
        Prim = stage.GetPrimAtPath(PrimPath)

        if Prim:
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
                            variability=Sdf.VariabilityUniform )

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


            addMayaAttributes(stage, item["children"], path=itempath)
