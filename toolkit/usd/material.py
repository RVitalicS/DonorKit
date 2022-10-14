#!/usr/bin/env python



import os
import re


from pxr import Usd, UsdShade, Sdf, Gf

from toolkit.usd import editor








def pathEnvEncoder (path):

    ENVIRONMENT_VARIABLES = os.getenv(
        "VFX_GLOBALS", "").split(":")
    for VARIABLE in ENVIRONMENT_VARIABLES:
        
        value = os.getenv(VARIABLE, "")
        if not value: continue
        for scope in value.split(":"):

            if not re.match(f"^{scope}.+", path):
                continue
            return re.sub(
                f"^{scope}", "${"+VARIABLE+"}", path)

    return path



def pathEncoder (path, anchor):

    envpath = pathEnvEncoder(path)
    if path != envpath:
        return envpath

    else:
        return editor.makeRelative(path, anchor)







def createInput (shader, name, data):

    value    = data["value"]
    typeName = data["type"]

    connection = data["connection"]

    sdfType = None
    if typeName == "int":
        sdfType = Sdf.ValueTypeNames.Int

    elif typeName in ["float", "double"]:
        sdfType = Sdf.ValueTypeNames.Float

    elif typeName == "string":
        if name in [
                "filename", "filename0",
                "filename1", "filename2",
                "filename3", "filename4",
                "filename5", "filename6",
                "filename7", "filename8",
                "filename9", "file", "b2r_texture"]:
            sdfType = Sdf.ValueTypeNames.Asset
            if not connection:
                value = pathEnvEncoder(value)
        else:
            sdfType = Sdf.ValueTypeNames.String

    elif typeName in ["color", "color3f"]:
        if not connection:
            value = Gf.Vec3f(value)
        sdfType = Sdf.ValueTypeNames.Color3f

    elif typeName == "float2":
        if not connection:
            value = Gf.Vec2f(value)
        sdfType = Sdf.ValueTypeNames.Float2

    elif typeName in ["float3", "vector"]:
        if not connection:
            value = Gf.Vec3f(value)
        if name in [
                "input", "color", "diffuseColor",
                "baseColor", "edgeColor", "reflectivity",
                "material1",  "material2" ]:
            sdfType = Sdf.ValueTypeNames.Color3f

        elif name == "normal":
            sdfType = Sdf.ValueTypeNames.Normal3f
        else:
            sdfType = Sdf.ValueTypeNames.Float3

    elif typeName == "float4":
        if not connection:
            value = Gf.Vec4f(value)
        sdfType = Sdf.ValueTypeNames.Float4

    elif typeName == "normal":
        if not connection:
            value = Gf.Vec3f(value)
        sdfType = Sdf.ValueTypeNames.Float3

    elif typeName == "bool":
        sdfType = Sdf.ValueTypeNames.Bool

    elif typeName == "token":
        sdfType = Sdf.ValueTypeNames.Token


    if sdfType:
        ShaderInput = shader.CreateInput(name, sdfType)

        if not connection:
            ShaderInput.Set(value)







def make (pathusd, data, comment="", documentation=""):


    # extract data
    dataMaterial   = data.get("material", {})
    dataShaders    = data.get("shaders", {})

    dataReferences = data.get("references", {})
    StageStack     = dict()

    nameMaterial   = dataMaterial.get("name")


    # define local functions
    def getRefPath (name):

        def getLogic (stage, name):
            for prim in stage.Traverse():
                if prim.GetName() != name:
                    continue
                if not prim.IsActive():
                    continue
                return prim.GetPath().pathString

        if rootReference:
            RefStage = Usd.Stage.Open(rootReference)
            path = getLogic(RefStage, name)
            if path:
                defaultPrim = RefStage.GetDefaultPrim()
                pattern = f"^/{defaultPrim.GetName()}"
                return re.sub(pattern, "", path)

        for ID, scheme in dataReferences.items():
            if not ID in StageStack:
                StageStack[ID] = Usd.Stage.Open(
                    scheme.get("path") )
            RefStage = StageStack.get(ID)
            path = getLogic(RefStage, name)
            if path: return path


    def getShaderPath (name):
        root = f"/{nameMaterial}"

        for shader in dataShaders:
            if name != shader: continue
            path = f"{root}/{shader}"
            return Sdf.Path(path)
        
        pathRef = getRefPath(name)
        if pathRef:
            path = f"{root}{pathRef}"
            return Sdf.Path(path)


    def manageConnection (prim, name, data):
        
        NodeGraph = UsdShade.NodeGraph.Get(
            prim.GetStage(), prim.GetPath())
        ConnectableAPI = NodeGraph.ConnectableAPI()

        name = f"inputs:{name}"
        if not prim.HasAttribute(name):
            return

        Attribute = prim.GetAttribute(name)
        if not ConnectableAPI.HasConnectedSource(Attribute):
            return

        if not data["connection"]:
            ConnectableAPI.DisconnectSource(Attribute)


    def makeConnections (data):

        for nameNode, specNode in data.items():
            if not specNode: continue
            Shader = UsdShade.NodeGraph.Get(
                Stage, getShaderPath(nameNode))

            inputs = specNode.get("inputs", {})
            for namePlug, dataPlug in inputs.items():
                if not dataPlug.get("connection"):
                    continue
                ShaderInput = Shader.GetInput(namePlug)
                if not ShaderInput:
                    continue

                sourceNode, sourcePlug = dataPlug["value"]
                ShaderSource = UsdShade.NodeGraph.Get(
                    Stage, getShaderPath(sourceNode))
                ShaderInput.ConnectToSource(
                    ShaderSource.ConnectableAPI(), sourcePlug)


    # check if material
    # has previous version reference
    rootReference = None
    justReference = False
    overShaders = dict()
    for ID, scheme in dataReferences.items():
        if scheme.get("name") != nameMaterial:
            continue
        shaders = scheme.get("shaders", {})
        useForRoot = True
        for name in shaders:
            if name in dataShaders:
                useForRoot = False
        if useForRoot:
            rootReference = scheme.get("path")
            overShaders = shaders
            dataReferences.pop(ID)
            break

    if rootReference and not dataShaders:
        if not dataReferences and not overShaders:
            justReference = True


    # create stage and define material
    Stage = Usd.Stage.CreateNew(pathusd)
    Layer = Stage.GetRootLayer()

    MaterialPath = Sdf.Path(f"/{nameMaterial}")
    Material = UsdShade.Material.Define(Stage, MaterialPath)

    if rootReference:
        Material.GetPrim().GetReferences().AddReference(
            pathEncoder(rootReference, pathusd) )


    # define material references and shader overrides
    for ID, scheme in dataReferences.items():

        refMaterial = scheme.get("name")
        refUsdPath = pathEnvEncoder(scheme.get("path"))

        RefMaterial = UsdShade.Material.Define(Stage, 
            Sdf.Path(f"/{nameMaterial}/{refMaterial}") )
        RefMaterial.GetPrim().GetReferences().AddReference(
            pathEncoder(refUsdPath, pathusd) )

        shaders = scheme.get("shaders", {})
        for refShader, shaderSpec in shaders.items():

            refStagePath = getRefPath(refShader)
            if not refStagePath: continue

            OverPrimPath = Sdf.Path(f"/{nameMaterial}{refStagePath}" )
            OverPrim = Stage.OverridePrim(OverPrimPath)

            if not shaderSpec:
                OverPrim.SetActive(False)
                continue

            Shader = UsdShade.Shader(OverPrim)
            ShaderInputs = shaderSpec.get("inputs", {})
            for inputName, inputData in ShaderInputs.items():
                manageConnection(OverPrim, inputName, inputData)
                createInput(Shader, inputName, inputData)


    # override shaders for root reference
    for nameShader, specShader in overShaders.items():

        refPath = getRefPath(nameShader)
        if not refPath: continue

        OverPath = Sdf.Path(f"/{nameMaterial}{refPath}" )
        OverPrim = Stage.OverridePrim(OverPath)

        Shader = UsdShade.Shader(OverPrim)
        inputs = specShader.get("inputs", {})
        for inputName, inputData in inputs.items():
            manageConnection(OverPrim, inputName, inputData)
            createInput(Shader, inputName, inputData)


    # create new shader nodes
    for nameShader, specShader in dataShaders.items():

        ShaderPath = MaterialPath.AppendChild(nameShader)
        Shader = UsdShade.Shader.Define(Stage, ShaderPath)

        ShaderID = specShader.get("id")
        Shader.CreateIdAttr(ShaderID)

        inputs = specShader.get("inputs", {})
        for inputName, inputData in inputs.items():
            createInput(Shader, inputName, inputData)


    # connect shaders to network
    makeConnections(overShaders)
    makeConnections(dataShaders)
    for ID, scheme in dataReferences.items():
        dataShadersRef = scheme.get("shaders", {})
        makeConnections(dataShadersRef)


    # connect material with shaders
    if not justReference:
        for inPlug, connection in dataMaterial.get("inputs", {}).items():
            nodeName, outPlug = connection

            ShaderPath = getShaderPath(nodeName)
            ShaderOutput = UsdShade.NodeGraph.Get(Stage, ShaderPath)

            MaterialOutput = Material.CreateOutput(
                inPlug, Sdf.ValueTypeNames.Token)
            MaterialOutput.ConnectToSource(
                ShaderOutput.ConnectableAPI(), outPlug)


    # save material
    Layer.defaultPrim = nameMaterial

    if comment:
        Layer.comment = comment
    if documentation:
        Layer.documentation = documentation

    Layer.Save()







def weld (pathusd, name, references):

    Stage = Usd.Stage.CreateNew(pathusd)
    Path = Sdf.Path("/{}".format(name))

    Material = UsdShade.Material.Define(Stage, Path)
    MaterialPrim = Stage.GetPrimAtPath(Path)

    for path in references:
        path = editor.makeRelative(path, pathusd)
        MaterialPrim.GetReferences().AddReference(path)

    layer = Stage.GetRootLayer()
    layer.defaultPrim = name
    layer.Save()
