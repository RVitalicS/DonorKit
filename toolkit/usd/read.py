#!/usr/bin/env python


import os
import re

from databank import shadertag
from pxr import Usd, UsdShade







def getShaderID (name, data):

    shadersData = data.get("shaders", {})
    for shaderName, shaderData in shadersData.items():

        if name == shaderName:
            return shaderData["id"]


def getMayaType (ID):

    mayatype = "utility"

    for item in shadertag:

        IDs = item.get("id")
        for USD, Maya in IDs.items():

            if ID != USD:
                continue

            mayatype = item.get("mayatype")
            if mayatype:
                return mayatype

    return mayatype


def makeMayaID (ID):

    for item in shadertag:

        IDs = item.get("id")
        for USD, Maya in IDs.items():

            if ID == USD:
                return Maya

    return ID


def makeMayaInput (ID, name):

    for item in shadertag:

        IDs = item.get("id")
        for USD, Maya in IDs.items():

            if ID != USD: continue

            inputs = item.get("inputs", {})
            if name in inputs:
                return inputs.get(name)

    return name


def makeMayaOutput (ID, name):

    for item in shadertag:

        IDs = item.get("id")
        for USD, Maya in IDs.items():

            if ID != USD: continue

            outputs = item.get("outputs", {})
            if name in outputs:
                return outputs.get(name)

    return name


def makeMayaSpace (value):

    ocioConfig = os.getenv("OCIO", None)
    if ocioConfig == None:
        return None

    if value == "sRGB":
        return "acescg"

    elif value == "auto":
        return "raw"

    return value


def makeMayaType (value):

    if value in ["normal3f", "color3f"]:
        return "float3"

    elif value in ["asset", "token"]:
        return "string"

    return value






def asUsdBuildScheme (path):

    Stage = Usd.Stage.Open(path)
    Layer = Stage.GetRootLayer()

    material = dict()
    shaders = dict()
    for Prim in Stage.Traverse():


        if Prim.GetTypeName() == "Material":

            Material = UsdShade.Shader(Prim)
            MaterialName = Prim.GetName()

            material["name"] = MaterialName


            data = material.get("inputs", {})

            for Output in Material.GetOutputs():
                if Output.HasConnectedSource():
                    OutputName = Output.GetBaseName()

                    InputName = Output.GetConnectedSource()[1]
                    ConnectableAPI = Output.GetConnectedSource()[0]
                    InputPrim = ConnectableAPI.GetPrim()
                    data[OutputName] = [
                        InputPrim.GetName(), InputName]
                
                material["inputs"] = data

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

                if data["type"] in [
                        "float2", "normal3f",
                        "color3f", "float4" ]:
                    value = list(value)
                    value = [round(i, 4) for i in value]
                elif data["type"] == "asset":
                    value = value.resolvedPath

                data["value"] = value

    return dict(material=material, shaders=shaders)






def asMayaBuildScheme (path):


    data = asUsdBuildScheme(path)
    materialData = data.get("material", {})


    material = dict()
    material["name"] = materialData.get("name", "") + "_SG"

    connection = dict()
    material["inputs"] = connection

    connections = materialData.get("inputs", {})
    for inplug, outplug in connections.items():

        outplug = [outplug[0], "outColor"]
        if inplug == "surface":
            connection["surfaceShader"] = outplug
        elif inplug == "ri:surface":
            connection["rman__surface"] = outplug
        elif inplug == "ri:displacement":
            connection["rman__displacement"] = outplug

    data["material"] = material


    shadersData = data.get("shaders", {})

    replace = dict()
    for shaderName, shaderData in shadersData.items():
        ID = shaderData["id"]
        if ID == "UsdTransform2d":
            nameSub = re.sub(r"Transform$", "", shaderName)
            replace[shaderName] = nameSub

    shaders = dict()
    for shaderName, shaderData in shadersData.items():
        usdID = shaderData["id"]

        mayaID = makeMayaID(usdID)
        if mayaID == None: continue

        item = dict()
        item["id"] = mayaID
        item["mayatype"] = getMayaType(usdID)

        inputs = dict()
        item["inputs"] = inputs

        inputsData = shaderData["inputs"]
        for inputName, inputData in inputsData.items():

            mayaInput = makeMayaInput(usdID, inputName)
            if mayaInput == None:
                continue

            usdType  = inputData.get("type")
            inputData["type"] = makeMayaType(usdType)

            if inputData.get("connection"):
                nodeName   = inputData.get("value")[0]
                nodeOutput = inputData.get("value")[1]

                nodeID = getShaderID(nodeName, data)
                mayaOutput = makeMayaOutput(
                    nodeID, nodeOutput)

                if nodeName in replace:
                    nodeName = replace.get(nodeName)

                inputData["value"][0] = nodeName
                inputData["value"][1] = mayaOutput

            elif mayaInput == "colorSpace":
                value = inputData.get("value")
                value = makeMayaSpace(value)
                if value == None:
                    continue
                inputData["value"] = value

            inputs[mayaInput] = inputData

        if shaderName in replace:
            shaderName = replace.get(shaderName)

        shaders[shaderName] = item

    data["shaders"] = shaders


    return data
