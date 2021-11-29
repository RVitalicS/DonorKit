

import os
import re


from pxr import (
    Usd,
    UsdGeom,
    UsdShade,
    Sdf )









def keydata (dictionary, keyname):
    if isinstance(dictionary, dict):

        for key, value in dictionary.items():
            
            if key == keyname:
                return value







def nameditor (outputName, prman=True):

    if not prman:

        if outputName == "fileTextureName":
            outputName = "file"

        elif outputName == "uvCoord":
            outputName = "st"

        elif outputName == "outUV":
            outputName = "result"

        elif outputName == "outColor":
            outputName = "rgb"

        elif outputName == "outColorR":
            outputName = "r"

        return outputName


    if outputName == "outColor":
        outputName = "out"

    return outputName







def patheditor (path):

    ENVIRONMENT_VARIABLES = os.getenv(
        "VFX_GLOBALS", "").split(":")

    for VARIABLE in ENVIRONMENT_VARIABLES:
        
        value = os.getenv(VARIABLE, "")
        if value:

            for scope in value.split(":"):

                if re.match( "^{}.+".format(scope), path):
                    return re.sub(
                        "^{}".format(scope),
                        "${"+VARIABLE+"}",
                        path )

    return path







def CreateInput (shader, name, data):


    inputType  = keydata(data, "type")
    inputValue = keydata(data, "value")

    connection = keydata(data, "connection")

    sdfType = None
    if inputType == "int":
        sdfType = Sdf.ValueTypeNames.Int

    elif inputType in ["float", "double"]:
        sdfType = Sdf.ValueTypeNames.Float

    elif inputType == "string":
        if name in ["filename", "file", "b2r_texture"]:
            sdfType = Sdf.ValueTypeNames.Asset
            inputValue = patheditor(inputValue)
        else:
            sdfType = Sdf.ValueTypeNames.String

    elif inputType in ["color", "color3f"]:
        sdfType = Sdf.ValueTypeNames.Color3f

    elif inputType == "float2":
        if name == "repeatUV":
            pass
        else:
            sdfType = Sdf.ValueTypeNames.Float2

    elif inputType == "float3":
        if name in [
            "input",
            "color",
            "diffuseColor",
            "baseColor",
            "edgeColor",
            "reflectivity",
            "material1",
            "material2" ]:
            sdfType = Sdf.ValueTypeNames.Color3f
        else:
            sdfType = Sdf.ValueTypeNames.Float3

    elif inputType == "normal":
        sdfType = Sdf.ValueTypeNames.Float3

    elif inputType == "bool":
        sdfType = Sdf.ValueTypeNames.Bool

    elif inputType == "token":
        sdfType = Sdf.ValueTypeNames.Token


    if sdfType:
        ShaderInput = shader.CreateInput(name, sdfType)

        if not connection:
            ShaderInput.Set(inputValue)





def make (
        pathusd,
        data,
        root="/",
        scope="",
        comment="",
        documentation="",
        prman=True ):


    MaterialName         = keydata(data, "name")
    MaterialSurface      = keydata(data, "surface")
    MaterialDisplacement = keydata(data, "displacement")
    MaterialShaders      = keydata(data, "shaders")


    if MaterialName:
        defaultPrim = MaterialName

        stage = Usd.Stage.CreateNew(pathusd)


        pathitems = root.split("/")
        pathitems = [ i for i in pathitems if i]

        root = Sdf.Path("/")
        for item in pathitems:
            if not defaultPrim: defaultPrim = item
            root = root.AppendChild(item)


        if scope:
            if not defaultPrim: defaultPrim = scope
            root = root.AppendChild(scope)
            UsdGeom.Scope.Define(stage, root)


        MaterialPath = root.AppendChild(MaterialName)
        ShadingGroup = UsdShade.Material.Define(stage, MaterialPath)


        for ShaderName in MaterialShaders:
            ShaderData = MaterialShaders[ShaderName]


            ShaderPath = MaterialPath.AppendChild(ShaderName)
            Shader = UsdShade.Shader.Define(stage, ShaderPath)

            ShaderInputs = keydata(ShaderData, "inputs")
            ShaderID = keydata(ShaderData, "id")

            if not prman:
                if ShaderID == "file":
                    ShaderID = "UsdUVTexture"
                    ShaderInputs["wrapS"] = dict(
                        connection=False, 
                        type="token", 
                        value="repeat")
                    ShaderInputs["wrapT"] = dict(
                        connection=False, 
                        type="token", 
                        value="repeat")

                elif ShaderID == "place2dTexture":
                    ShaderID = "UsdPrimvarReader_float2"
                    ShaderInputs["varname"] = dict(
                        connection=False, 
                        type="token", 
                        value="st")

                elif ShaderID in  [
                    "pxrUsdPreviewSurface",
                    "usdPreviewSurface"]:
                    ShaderID = "UsdPreviewSurface"

            Shader.CreateIdAttr(ShaderID)


            for inputName in ShaderInputs:
                inputData = ShaderInputs[inputName]
                inputName = nameditor(inputName, prman=prman)
                CreateInput(Shader, inputName, inputData)


        for ShaderName in MaterialShaders:
            ShaderData = MaterialShaders[ShaderName]

            inputPath = MaterialPath.AppendChild(ShaderName)
            ShaderIn = UsdShade.NodeGraph.Get(stage, inputPath)


            ShaderInputs = keydata(ShaderData, "inputs")
            for inputName in ShaderInputs:
                inputData = ShaderInputs[inputName]
                inputName = nameditor(inputName, prman=prman)

                connection = keydata(inputData, "connection")
                if connection:


                    ShaderInput = ShaderIn.GetInput(inputName)
                    if ShaderInput:

                        Source  = keydata(inputData, "value")
                        SourceConnection  = Source.split(".")

                        outputName = SourceConnection[1]
                        outputName = nameditor(outputName, prman=prman)

                        outputPath = MaterialPath.AppendChild(SourceConnection[0])
                        ShaderOut = UsdShade.NodeGraph.Get(stage, outputPath)

                        ShaderInput.ConnectToSource(
                            ShaderOut.ConnectableAPI(), outputName)



        def makeOutputConnection (Source, materialOutputName):

            SourceConnection = Source.split(".")

            outputName = SourceConnection[1]
            if prman:
                outputName = nameditor(outputName, prman=prman)
            else:
                outputName = "surface"

            outputPath = MaterialPath.AppendChild(SourceConnection[0])
            ShaderOutput = UsdShade.NodeGraph.Get(stage, outputPath)

            SurfaceOutput = ShadingGroup.CreateOutput(
                materialOutputName,
                Sdf.ValueTypeNames.Token)

            SurfaceOutput.ConnectToSource(
                ShaderOutput.ConnectableAPI(), outputName)


        if MaterialSurface:
            makeOutputConnection(
                MaterialSurface,
                "{}surface".format("ri:" if prman else "") )

        if MaterialDisplacement:
            makeOutputConnection(
                MaterialDisplacement,
                "{}displacement".format("ri:" if prman else "") )



        layer = stage.GetRootLayer()

        if comment:
            layer.comment = comment
        if documentation:
            layer.documentation = documentation
        if defaultPrim:
            layer.defaultPrim = defaultPrim

        layer.Save()

