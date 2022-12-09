#!/usr/bin/env python

"""
Read USD data

This module defines utilities to read a USD file
as prepared data for other functions.
"""

import os
from toolkit.usd import naming as nameMirror
from toolkit.ensure.Usd import *
from toolkit.ensure.UsdShade import *
from toolkit.ensure.Ar import *
from typing import Union


def asDefaultPrim (path: str) -> Union[str, None]:
    """Return a name of a root UsdPrim of this stage.
    Return an invalid prim if there is no such prim.

    Arguments:
        path: The path to the USD file
    Returns:
        The name of the default prim
    """
    Resolver = Ar.GetResolver()
    path = Resolver.Resolve(path)
    Stage = Usd.Stage.Open(
        path, load=Usd.Stage.LoadNone)
    DefaultPrim = Stage.GetDefaultPrim()
    if DefaultPrim.IsValid():
        return DefaultPrim.GetName()


def asReferences (path: str) -> list:
    """Find the paths of all layers
    referred to by reference, payload,
    and sublayer fields in this layer.

    Arguments:
        path: The path to the USD file
    Returns:
        The paths of all assets this layer depends on
    """
    Resolver = Ar.GetResolver()
    path = Resolver.Resolve(path)
    if not os.path.exists(path):
        return []
    root = os.path.dirname(path)
    os.chdir(root)

    Stage = Usd.Stage.Open(
        path, load=Usd.Stage.LoadNone)
    Layer = Stage.GetRootLayer()
    References = []
    # TODO: deprecated, use GetCompositionAssetDependencies
    for path in Layer.GetExternalReferences():
        realpath = os.path.realpath(path)
        if os.path.exists(realpath):
            resolved = Resolver.Resolve(realpath)
            References.append(os.path.realpath(resolved))

    return References


def asUsdBuildScheme (path: str) -> dict:
    """Create a dictionary data from the USD file
    that describe material and its shaders using USD type names

    Arguments:
        path: The path to the USD file
    Returns:
        A description data
    """
    Stage = Usd.Stage.Open(
        path, load=Usd.Stage.LoadNone)
    Layer = Stage.GetRootLayer()
    DefaultPrim = Stage.GetDefaultPrim()
    material = dict()
    material["name"] = DefaultPrim.GetName()
    data = material.get("inputs", {})

    Material = UsdShade.Shader(DefaultPrim)
    for Output in Material.GetOutputs():
        if Output.HasConnectedSource():
            OutputName = Output.GetBaseName()
            InputName = Output.GetConnectedSource()[1]
            ConnectableAPI = Output.GetConnectedSource()[0]
            InputPrim = ConnectableAPI.GetPrim()
            data[OutputName] = [
                InputPrim.GetName(), InputName]
    material["inputs"] = data

    shaders = dict()
    for Prim in Stage.Traverse():
        if not Prim.IsActive():
            continue
        if Prim.GetTypeName() != "Shader":
            continue

        Shader = UsdShade.Shader(Prim)
        ShaderName = Prim.GetName()
        inputs = dict()
        description = dict(
            id=Shader.GetShaderId(),
            inputs=inputs)
        shaders[ShaderName] = description
        for Input in Shader.GetInputs():
            InputName = Input.GetBaseName()
            data = dict()
            inputs[InputName] = data
            data["type"] = str(Input.GetTypeName())

            if Input.HasConnectedSource():
                data["connection"] = True
                ConnectableAPI = Input.GetConnectedSource()[0]
                OutputName = Input.GetConnectedSource()[1]
                OutputPrim = ConnectableAPI.GetPrim()
                data["value"] = [
                    OutputPrim.GetName(), OutputName]
            else:
                data["connection"] = False
                Attribute = Input.GetAttr()
                value = Attribute.Get()
                if value is None:
                    continue
                if data["type"] in [
                        "float2", "float3", "normal3f",
                        "color3f", "float4" ]:
                    value = [round(i,4) for i in list(value)]
                elif data["type"] == "asset":
                    value = value.resolvedPath
                data["value"] = value

    def getRoots (data: dict) -> list:
        """Get the firsts connected nodes to a material"""
        nodes = []
        inputs = data.get("inputs", {})
        for inplug, connection in inputs.items():
            node, output = connection
            nodes.append(node)
        return nodes

    def getUsed (data: dict, root: str,
                 nodes: Union[None, list] = None) -> list:
        """Get nodes that are connected to a material"""
        if nodes is None:
            nodes = []
        inputs = data.get(root, {}).get("inputs", {})
        for name, spec in inputs.items():
            if not spec.get("connection"):
                continue
            node, output = spec.get("value")
            if node in nodes: continue
            nodes.append(node)
            nodes = getUsed(data, node, nodes=nodes)
        return nodes

    def deleteUnused (data: dict, used: list) -> dict:
        """Delete nodes that are not connected to a material"""
        buffer = dict()
        for name, spec in data.items():
            if name in used:
                buffer[name] = spec
        return buffer

    used = []
    for node in getRoots(material):
        used.append(node)
        used += getUsed(shaders, node)
    shaders = deleteUnused(shaders, used)

    return dict(material=material, shaders=shaders)


def asMayaBuildScheme (path: str) -> dict:
    """Create a dictionary data from the USD file
    that describe material and its shaders using MAYA type names

    Arguments:
        path: The path to the USD file
    Returns:
        A description data
    """
    def getShaderID (name: str, data: dict) -> str:
        shadersData = data.get("shaders", {})
        for shaderName, shaderData in shadersData.items():
            if name == shaderName:
                return shaderData["id"]

    data = asUsdBuildScheme(path)
    materialData = data.get("material", {})
    material = dict()
    material["name"] = materialData.get("name", "") + "_SG"

    connection = dict()
    material["inputs"] = connection
    connections = materialData.get("inputs", {})
    for inplug, outplug in connections.items():
        inplug = nameMirror.mayaInput("Material", inplug)
        connection[inplug] = [outplug[0], "outColor"]
    data["material"] = material

    shaders = dict()
    shadersData = data.get("shaders", {})
    for shaderName, shaderData in shadersData.items():
        usdID = shaderData["id"]
        mayaID = nameMirror.mayaID(usdID)
        if mayaID is None:
            continue
        item = dict()
        item["id"] = mayaID
        item["mayatype"] = nameMirror.getMayaBuildType(usdID)
        inputs = dict()
        item["inputs"] = inputs

        inputsData = shaderData["inputs"]
        for usdInput, inputData in inputsData.items():
            mayaInput = nameMirror.mayaInput(usdID, usdInput)
            if mayaInput is None:
                continue
            usdType  = inputData.get("type")
            inputData["type"] = nameMirror.mayaType(usdType)

            if inputData.get("connection"):
                nodeName, nodeOutput = inputData.get("value")
                nodeID = getShaderID(nodeName, data)
                mayaOutput = nameMirror.mayaOutput(
                    nodeID, nodeOutput)
                inputData["value"] = [nodeName, mayaOutput]
            elif mayaInput == "colorSpace":
                spaceUsd = inputData.get("value")
                spaceMaya = nameMirror.mayaSpace(spaceUsd)
                if spaceMaya is None:
                    continue
                inputData["value"] = spaceMaya

            inputs[mayaInput] = inputData
        shaders[shaderName] = item

    data["shaders"] = shaders
    return data
