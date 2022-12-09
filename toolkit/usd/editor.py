#!/usr/bin/env python

"""
Edit Scene Description

This module defines functions to copy and edit USD data,
to change its hierarchy, to edit attributes.
"""

import os
import re
import toolkit.usd.attribute as attributeCommand
from pxr import Usd
from pxr import UsdGeom
from pxr import UsdShade
from pxr import Sdf
from pxr import Vt
from pxr import Work
from typing import Union
from typing import Callable

# Set the concurrency limit to be the maximum recommended
# for the hardware on which it's running
Work.SetMaximumConcurrencyLimit()


def makeRelative (path: str, anchor: str) -> str:
    """Make the path relative

    Arguments:
        path: The fully qualified file path
        anchor: The path to use as source context
    Returns:
        An relative path
    """
    return os.path.relpath(path, start=os.path.dirname(anchor) )


def getDisplayColorName (name: str) -> str:
    """Get a displayColor name
    from the namespaced attribute

    Arguments:
        name: The attribute name
    Returns:
        A displayColor name
    """
    for part in name.split(":"):
        if "displayColor" in part:
            name = part
            break
    return name


def copyAttributes (source: Usd.Prim, target: Usd.Prim,
                    units: float = 1.0, time: float = 1.0) -> None:
    """Copy all attributes from one UsdPrim to another.
    Scale attribute values for working in metric units.
    Edit displayColor attribute.

    Arguments:
        source: The UsdPrim to get attributes
        target: The UsdPrim to create attributes
    Keyword Arguments:
        units: The scale factor for attributes (extent, points, translate)
               where 1.0 is source values in meter units
               and 0.01 is source values in centimeter units
        time: The value for time-sampled data 
    """
    colorData = dict()
    isMeter = UsdGeom.LinearUnitsAre(units, UsdGeom.LinearUnits.meters)
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
            attrName = f"{attrSpace}:{attrName}"
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
            attrName, attrType, custom=Attribute.IsCustom() )
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


def editTexCoord (Prim: Usd.Prim) -> None:
    """Rename texture coordinate attributes
    with the names from metadata

    Arguments:
        Prim: The UsdPrim to edit
    """
    coords = dict()
    for Attribute in Prim.GetAttributes():
        attrName  = Attribute.GetBaseName()
        attrType  = Attribute.GetTypeName()
        if attrType != Sdf.ValueTypeNames.TexCoord2fArray:
            continue

        # get Maya attribute name
        attrMetadata = Attribute.GetAllMetadata()
        customData = attrMetadata.get("customData", {})
        mayaData = customData.get("Maya", {})
        mayaName = mayaData.get("name")
        if type(mayaName) == str:
            coords[attrName] = mayaName

    # manage 'st' name conflict
    deleteName = None
    for attrName, mayaName in coords.items():
        if attrName == "st": continue
        if mayaName != "st": continue
        if "st" in coords:
            deleteName = attrName
            break

    # do rename (remove/create)
    for attrName, mayaName in coords.items():
        nameCoord = f"primvars:{attrName}"
        nameIndex = f"primvars:{attrName}:indices"

        if attrName != deleteName:
            AttrCoord = Prim.GetAttribute(nameCoord)
            AttrIndex = Prim.GetAttribute(nameIndex)
            valueCoord = AttrCoord.Get()
            valueIndex = AttrIndex.Get()
            typeCoord = AttrCoord.GetTypeName()
            typeIndex = AttrIndex.GetTypeName()
            customCoord = AttrCoord.IsCustom()
            customIndex = AttrIndex.IsCustom()

        Prim.RemoveProperty(nameCoord)
        Prim.RemoveProperty(nameIndex)
        if attrName != deleteName:
            if attrName != "st":
                attrName = mayaName.replace(" ", "_")
            AttrCoord = Prim.CreateAttribute(
                f"primvars:{attrName}", typeCoord, custom=customCoord)
            AttrCoord.Set(value=valueCoord)
            AttrCoord.SetMetadata("interpolation", "faceVarying")
            AttrIndex = Prim.CreateAttribute(
                f"primvars:{attrName}:indices", typeIndex, custom=customIndex)
            AttrIndex.Set(value=valueIndex)


def copyStage (source: Usd.Stage, target: Usd.Stage,
               root: Union[None, str] = None, units: Union[None, float] = None,
               proxy: bool = False, children: Union[None, list] = None,
               namingGeomSubset: Union[None, Callable] = None) -> None:
    """Copy scene data from one UsdStage to another.
    Edit hierarchy, attributes, subset names.
    Scale attribute values for working in metric units.

    Arguments:
        source: The UsdStage to get data
        target: The UsdStage to create data
    Keyword Arguments:
        root: The path of the UsdStage to use as root for a new hierarchy
        units: The scale factor for attributes (extent, points, translate)
               where 1.0 is source values in meter units
               and 0.01 is source values in centimeter units
        proxy: Is the UsdStage has proxy purpose
        children: The exchange data object for the iterations
        namingGeomSubset: The function that renames GeomSubset objects
    """
    if root is None:
        root = "/"
    if units is None:
        units = UsdGeom.GetStageMetersPerUnit(source)
        UsdGeom.SetStageMetersPerUnit(
            target,
            UsdGeom.LinearUnits.meters )
    if children is None:
        RootPath = Sdf.Path(root)
        RootPrim = source.GetPrimAtPath(RootPath)
        children = [RootPrim]

    scope = os.path.dirname(root)
    if scope == "/": scope = ""
    for ChildPrim in children:
        typeName = ChildPrim.GetTypeName()
        childname = ChildPrim.GetName()
        childpath = ChildPrim.GetPath().pathString
        cutedpath = re.sub(scope, "", childpath)

        if childname == "Looks" and typeName == "Scope":
            continue
        elif typeName == "GeomSubset":
            parentpath = re.sub(f"{childname}$", "", cutedpath)
            if proxy:
                parentpath = re.sub("Shape/$", "Proxy/", parentpath)
            if namingGeomSubset:
                childname = namingGeomSubset(childname)
            cutedpath = parentpath + childname
        elif proxy:
            cutedpath = re.sub("Shape$", "Proxy", cutedpath)

        NewPath = Sdf.Path(cutedpath)
        NewPrim = target.DefinePrim(
            NewPath, ChildPrim.GetTypeName())
        if os.path.dirname(cutedpath) == "/":
            target.SetDefaultPrim(NewPrim)
        copyAttributes(ChildPrim, NewPrim, units=units)

        if typeName == "Mesh":
            editTexCoord(NewPrim)
            Mesh = UsdGeom.Mesh(NewPrim)
            if not proxy:
                Mesh.CreatePurposeAttr("render")
            else:
                Mesh.CreatePurposeAttr("proxy")

        copyStage(source, target, root=root, units=units, proxy=proxy,
                  children=ChildPrim.GetAllChildren(),
                  namingGeomSubset=namingGeomSubset)


def copyTimeSamples (source: Usd.Prim, target: Usd.Stage,
                     units: float = 1.0) -> None:
    """Copy all time-sampled values from one UsdPrim to another.
    Scale attribute values for working in metric units.

    Arguments:
        source: The UsdPrim to get time-sampled data
        target: The UsdStage to create time-sampled data
    Keyword Arguments:
        units: The scale factor for attributes (extent, points, translate)
               where 1.0 is source values in meter units
               and 0.01 is source values in centimeter units
    """
    for Attribute in source.GetAttributes():
        timeSamples = Attribute.GetTimeSamples()
        if len(timeSamples) > 1:
            attrBaseName = Attribute.GetBaseName()
            if attrBaseName in [
                    "points", "normals", "translate",
                    "scale", "rotateXYZ", "extent"]:
                # TODO: check animation if root has changed
                OverPrim = target.OverridePrim(source.GetPath())

                if attrBaseName == "translate":
                    newAttribute = attributeCommand.getTranslateOp(OverPrim)
                elif attrBaseName == "rotateXYZ":
                    newAttribute = attributeCommand.getRotateXYZOp(OverPrim)
                elif attrBaseName == "scale":
                    newAttribute = attributeCommand.getScaleOp(OverPrim)
                else:
                    newAttribute = OverPrim.CreateAttribute(
                        Attribute.GetName(), Attribute.GetTypeName(),
                        custom=Attribute.IsCustom() )

                for sample in timeSamples:
                    attrValue = Attribute.Get(time=sample)
                    if attrBaseName in ["points", "translate", "extent"]:
                        for index in range( len(attrValue) ):
                            attrValue[index] *= float(units)
                    newAttribute.Set(value=attrValue, time=sample)


def copyAnimation (source: Usd.Stage, target: Usd.Stage, root: str = "/",
                   reference: Union[None, str] = None, units: float = 1.0,
                   children: Union[None, list] = None) -> None:
    """Copy all time dependent attributes from one UsdStage to another.
    Scale attribute values for working in metric units.

    Arguments:
        source: The UsdStage to get data
        target: The UsdStage to create data
    Keyword Arguments:
        root: The UsdPrim path to use as entry point
        reference: The USD file to use as reference layer
        units: The scale factor for attributes (extent, points, translate)
               where 1.0 is source values in meter units
               and 0.01 is source values in centimeter units
        children: The exchange data object for the iterations
    """
    if children is None:
        defaultPrim = source.GetDefaultPrim()
        if not reference:
            reference = str(source.GetRootLayer().resolvedPath)
        animationPath = str(target.GetRootLayer().resolvedPath)
        reference = makeRelative(reference, animationPath)

        OverPrim = target.OverridePrim(defaultPrim.GetPath())
        OverPrim.GetReferences().AddReference( reference )

        target.SetDefaultPrim(OverPrim)
        target.SetStartTimeCode(source.GetStartTimeCode())
        target.SetEndTimeCode(source.GetEndTimeCode())
        target.SetFramesPerSecond(source.GetFramesPerSecond())

        RootPath = Sdf.Path(root)
        RootPrim = source.GetPrimAtPath(RootPath)
        children = [RootPrim]

    for ChildPrim in children:
        copyTimeSamples(ChildPrim, target, units=units)
        copyAnimation(source, target, root=root,
                      units=units, children=ChildPrim.GetAllChildren())


def addMayaAttributes (stage: Usd.Stage, tree: list, path: str = "/") -> None:
    """Translate Maya attributes to USD stage

    Arguments:
        stage: The UsdStage to add Maya data
        tree: Tha data that describes Maya scene
    Keyword Arguments:
        path: The UsdPrim path to use as entry point
    """
    for item in tree:
        name = item["name"]
        itempath = os.path.join(path, name)
        PrimPath = Sdf.Path(itempath)
        Prim = stage.GetPrimAtPath(PrimPath)

        if Prim:
            attributes = item["attributes"]
            for key, value in attributes.items():
                # add visibility attribute
                if key == "visibility":
                    if not value:
                        Prim.SetActive(False)
                # add subdivision scheme attribute
                elif key == "subdivScheme":
                    if not Prim.HasAttribute("subdivisionScheme"):
                        subdivisionScheme = Prim.CreateAttribute(
                            "subdivisionScheme",
                            Sdf.ValueTypeNames.Token,
                            variability=Sdf.VariabilityUniform )
                    else:
                        subdivisionScheme = Prim.GetAttribute("subdivisionScheme")
                    subdivisionScheme.Set(value)
                # add displacement attribute
                elif key == "rman_displacementBound":
                    Schema  = UsdGeom.PrimvarsAPI(Prim)
                    Primvar = Schema.CreatePrimvar(
                        "ri:attributes:displacementbound:sphere",
                        Sdf.ValueTypeNames.Float,
                        interpolation=UsdGeom.Tokens.constant )
                    Primvar.Set(value)

            addMayaAttributes(stage, item["children"], path=itempath)


def addMaterialPayload (Material: Usd.Prim, *payloads: str) -> None:
    """Add payload(s) to material UsdPrim and
    create override attributes scale(x2) and bias(-1)
    for textures used as normal map

    Arguments:
        Material: The material path of the UsdStage
      * payloads: The path(s) to material USD layer
    """

    # add payload and read it
    Stage = Material.GetStage()
    for payload in payloads:
        Material.GetPayloads().AddPayload(payload)
        PayloadStage = Usd.Stage.Open(
            payload, load=Usd.Stage.LoadNone)
        DefaultPrim = PayloadStage.GetDefaultPrim()
        if not DefaultPrim.IsValid():
            continue

        # find shader and get normal input
        for Prim in PayloadStage.Traverse():
            if Prim.GetTypeName() != "Shader":
                continue
            Shader = UsdShade.Shader(Prim)
            if Shader.GetShaderId() != "UsdPreviewSurface":
                continue

            # edit normals attribute
            for Input in Shader.GetInputs():
                if Input.GetBaseName() != "normal":
                    continue
                if not Input.HasConnectedSource():
                    continue
                ConnectableAPI = Input.GetConnectedSource()[0]
                Prim = ConnectableAPI.GetPrim()

                # define override primitive
                OverridePath = Sdf.Path(Material.GetPath())
                defaultScope = False
                for Path in Prim.GetPath().GetPrefixes():
                    if Path == DefaultPrim.GetPath():
                        defaultScope = True
                        continue
                    OverridePath = OverridePath.AppendChild(Path.name)
                if not defaultScope:
                    continue
                OverridePrim = Stage.OverridePrim(OverridePath)

                # create attributes
                AttributeScale = OverridePrim.CreateAttribute(
                    "inputs:scale",
                    Sdf.ValueTypeNames.Float4,
                    custom=False)
                AttributeScale.Set(value=(2.0, 2.0, 2.0, 2.0))
                AttributeBias = OverridePrim.CreateAttribute(
                    "inputs:bias",
                    Sdf.ValueTypeNames.Float4,
                    custom=False)
                AttributeBias.Set(value=(-1.0,-1.0,-1.0,-1.0))
                break
