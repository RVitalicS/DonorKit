#!/usr/bin/env python

"""
Hypershade

Implement a Maya hypershade manager with utility functions.
"""

import os
import re
from typing import Union
from typing import Any
from toolkit.core import Metadata
import toolkit.maya.mplug as mplugCommand
import toolkit.maya.find as findCommand
import toolkit.usd.naming as nameMirror
import toolkit.usd.read as readUSD
import xml.etree.ElementTree as ET
import oslquery
import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya


def getSelectionName () -> Union[str, None]:
    """Get a name of a selected material

    Returns:
        A material name
    """
    selection = mayaCommand.ls(selection=True)
    if not selection:
        return
    material = selection[0]
    if mayaCommand.nodeType(material) == "shadingEngine":
        return material


class Manager (object):
    """A class to get a dictionary data that describe material network
    to create USD Material Asset for RenderMan and Hydra renderers.

    A description data will contain all connected nodes
    and attributes that have not default values.

    Arguments:
        data: Default settings for the RenderMan nodes
        assets: A description data of USD Material Assets
                that were used in a Maya material network
    """
    def __init__ (self, data: Union[None, dict] = None,
                  assets: Union[None, dict] = None) -> None:

        self.RMAN_DEFAULTS = dict() if data is None else data
        self.ASSETS = dict() if assets is None else data

    def typeEditor (self, paramdefault: str,
                    paramtype: str) -> Any:
        """Convert a value that represented
        as a string to a python data type

        Arguments:
            paramdefault: The string value
            paramtype: The type name
        Returns:
            A converted value
        """
        if paramtype in ["color", "normal", "vector"]:
            return tuple([float(i) for i in paramdefault.split(" ")])
        elif paramtype == "float":
            paramdefault = paramdefault.replace("f", "")
            return float(paramdefault)
        elif paramtype == "int":
            return int(paramdefault)
        elif paramtype == "string":
            return str(paramdefault)

    def parseArgs (self, root: ET.Element,
                   data: Union[None, dict] = None) -> dict:
        """Parse a XML data of default settings for a RenderMan node
        and create a Python dictionary as a default settings data

        Arguments:
            root: The XML hierarchical data
        Keyword Arguments:
            data: The exchange data object for the iterations
        Returns:
            A default settings data
        """
        if data is None:
            data = dict()
        for child in root:
            if child.tag == "param":
                paramname = child.attrib["name"]
                paramtype = child.attrib["type"]
                paramdefault = None
                isDynamicArray = False
                for key in child.attrib:
                    if key == "isDynamicArray":
                        isDynamicArray = True
                    elif key == "default":
                        paramdefault = child.attrib["default"]
                if paramdefault and not isDynamicArray:
                    paramdefault = self.typeEditor(paramdefault, paramtype)
                    data[paramname] = dict(
                        type=paramtype,
                        default=paramdefault)
            data = self.parseArgs(child, data=data)
        return data

    def getShaderDefaults (self, shaderType: str) -> dict:
        """Get default settings for the specified RenderMan node.
        If a settings data for this node has gotten before, use that one.

        Arguments:
            shaderType: The type name of a RenderMan node
        Returns:
            A default settings data
        """
        if shaderType not in self.RMAN_DEFAULTS:
            shaderData = dict()
            RMANTREE = os.getenv("RMANTREE", "")
            ArgsPath = os.path.join(
                os.path.join(RMANTREE, "lib", "plugins", "Args"),
                f"{shaderType}.args")
            OslPath = os.path.join(
                os.path.join(RMANTREE, "lib", "shaders"),
                f"{shaderType}.oso")
            # xml data
            if os.path.exists(ArgsPath):
                tree = ET.ElementTree(file=ArgsPath)
                root = tree.getroot()
                shaderData = self.parseArgs(root)
                self.RMAN_DEFAULTS[shaderType] = shaderData
            # osl data
            elif os.path.exists(OslPath):
                shader = oslquery.OslQuery()
                shader.open(OslPath)
                for index in range(shader.nparams()):
                    parameter = shader.getparam(index)
                    if not parameter["isoutput"]:
                        if not parameter["isstruct"]:
                            paramname = parameter["name"]
                            shaderData[paramname] = dict(
                                type=parameter["type"],
                                default=parameter["default"])
                self.RMAN_DEFAULTS[shaderType] = shaderData
        else:
            shaderData = self.RMAN_DEFAULTS.get(shaderType, dict())
        return shaderData

    def getNetworkGroup (self, shader: OpenMaya.MFnDependencyNode,
                         prman: bool = True, collector: Union[None, dict] = None) -> dict:
        """For the specified shader node create a data that describes
        a network group of connected nodes for a particular renderer

        Arguments:
            shader: The dependency graph node
        Keyword Arguments:
            prman: A flag used to specify a network type
            collector: The exchange data object for the iterations
        Returns:
            A network description data
        """
        if collector is None:
            collector = dict()
        shaderType = str(shader.typeName())
        shaderName = str(shader.name())
        if not prman and shaderType not in [
                "usdPreviewSurface", "file", "place2dTexture"]:
            return collector

        # avoid doubles (diamond connection)
        if shaderName not in collector:
            inputs = dict()
            shaderData = dict(id=shaderType, inputs=inputs)
            assetID = self.getAssetID(shaderName)
            if assetID:
                shaderData["asset"] = assetID
            collector[shaderName] = shaderData
            if prman:
                shaderDefaults = self.getShaderDefaults(shaderType)
            for index in range(shader.attributeCount()):
                MObject = shader.attribute(index)
                attribute = OpenMaya.MFnAttribute(MObject)
                attrName = attribute.name()
                MPlug = shader.findPlug(attrName)
                if not attribute.isWritable():
                    continue

                # input connections
                if MPlug.isConnected() and shaderType != "PxrManifold2D":
                    if not prman and attrName not in [
                            "diffuseColor", "metallic", "roughness",
                            "normal", "displacement", "opacity", "uvCoord"]:
                        continue
                    valueType = mplugCommand.getAs(MPlug, asType=True)
                    if prman:
                        data = shaderDefaults.get(attrName, None)
                        if data is not None:
                            valueType = data["type"]
                    MPlugSource = MPlug.source()
                    sourceNode = OpenMaya.MFnDependencyNode(
                        MPlugSource.node())
                    if MPlugSource.info():
                        inputs[attrName] = dict(
                            value=MPlugSource.name().split("."),
                            type=valueType,
                            connection=True)
                        collector = self.getNetworkGroup(
                            sourceNode,
                            prman=prman,
                            collector=collector)

                # RenderMan overrides
                elif prman:
                    data = shaderDefaults.get(attrName, None)
                    value = mplugCommand.getAs(MPlug, asValue=True)
                    if data is not None and value is not None:
                        valueDefault = data["default"]
                        valueType = data["type"]
                        if not self.isValuesEqual(value, valueDefault):
                            if type(value) == float:
                                value = round(value, 4)
                            elif type(value) == tuple:
                                value = tuple(round(i, 4) for i in value)
                            elif type(value) == list:
                                value = [round(i, 4) for i in value]
                            inputs[attrName] = dict(
                                value=value, type=valueType,
                                connection=False)

                # Hydra overrides
                elif attrName in [
                        "diffuseColor", "emissiveColor", "opacity",
                        "ior", "metallic", "roughness", "clearcoat",
                        "clearcoatRoughness", "fileTextureName",
                        "colorSpace" ] and not MPlug.isDefaultValue():
                    value = mplugCommand.getAs(MPlug, asValue=True)
                    if value is not None:
                        typeString = mplugCommand.getAs(MPlug, asType=True)
                        inputs[attrName] = dict(
                            value=value,
                            type=typeString,
                            connection=False)
                elif shaderType == "place2dTexture" and attrName in [
                        "repeatUV", "rotateUV", "offset"]:
                    value = mplugCommand.getAs(MPlug, asValue=True)
                    if value is not None:
                        typeString = mplugCommand.getAs(MPlug, asType=True)
                        inputs[attrName] = dict(
                            value=value,
                            type=typeString,
                            connection=False)

        return collector

    def getPrmanNetwork (self, shaderGroup: OpenMaya.MFnDependencyNode) -> dict:
        """For the specified material node create a data
        that describes a RenderMan network

        Arguments:
            shaderGroup: The dependency graph node
        Returns:
            A network description data of RenderMan nodes
        """
        inputs = dict()
        material = dict(
            material=dict(
                name=str(shaderGroup.name()),
                inputs=inputs),
            shaders=dict())
        for connection in ["displacement", "surface"]:
            attrName = "rman__" + connection
            shaderPlug = shaderGroup.findPlug(attrName)
            if shaderPlug.isConnected():
                connectionSource = shaderPlug.source()
                inputs[attrName] = connectionSource.name().split(".")
                shader = OpenMaya.MFnDependencyNode(
                    connectionSource.node())
                material["shaders"] = self.getNetworkGroup(
                    shader, prman=True,
                    collector=material.get("shaders"))
        return material

    def getHydraNetwork (self, shaderGroup: OpenMaya.MFnDependencyNode) -> dict:
        """For the specified material node create a data,
        that describes its network and then will be converted to a Hydra network

        Arguments:
            shaderGroup: The dependency graph node
        Returns:
            A network description data
        """
        inputs = dict()
        material = dict(
            material=dict(
                name=str(shaderGroup.name()),
                inputs=inputs),
            shaders=dict())
        attrName = "surfaceShader"
        shaderPlug = shaderGroup.findPlug(attrName)
        if shaderPlug.isConnected():
            connectionSource = shaderPlug.source()
            inputs[attrName] = connectionSource.name().split(".")
            shader = OpenMaya.MFnDependencyNode(
                connectionSource.node())
            network = self.getNetworkGroup(
                shader, prman=False,
                collector=material.get("shaders"))
        return material

    def makeUsdScheme (self, data: dict, renderer: str,
                       inherit: bool = False) -> dict:
        """Change the specified network description data
        to a build scheme for creating a USD Material Layer

        Arguments:
            data: The network description data of a Maya material
            renderer: The name of the renderer the description data belongs
        Keyword Arguments:
            inherit: The switch to use USD Material Assets (nodes, networks)
                     from a library as references for creating new one
        Returns:
            A build scheme data for a USD file
        """
        data = self.applyUsdNaming(data)
        if renderer == "hydra":
            data["shaders"] = self.editHydraNetwork(
                data.get("shaders", {}))
        elif renderer == "prman":
            data["shaders"] = self.editPrmanNetwork(
                data.get("shaders", {}))

        if not inherit:
            return data
        data = self.groupReferences(data)
        shaders = data.get("shaders", {})
        references = data.get("references", {})
        lostConnections = dict()
        for ID, schemeRef in references.items():
            scheme = self.ASSETS.get(ID, {})
            schemeUsd = scheme.get(renderer, {})
            assetName = schemeUsd.get("name")
            assetPath = schemeUsd.get("path")
            if not assetPath:
                continue
            schemeRef["name"] = assetName
            schemeRef["path"] = assetPath
            overrideShaders = dict()
            shadersUsd = schemeUsd.get("shaders", {})
            shadersRef = schemeRef.get("shaders", {})

            # block reference node
            # with name used for new one
            for nodeName in shadersUsd:
                if nodeName in shaders:
                    overrideShaders[nodeName] = None

            # find out overrides
            for nodeName, specRef in shadersRef.items():
                specUsd = shadersUsd.get(nodeName, {})
                idUsd = specUsd.get("id", {})
                idRef = specRef.get("id", {})
                inputsUsd = specUsd.get("inputs", {})
                inputsRef = specRef.get("inputs", {})

                # mark node as inactive
                if idRef != idUsd:
                    overrideShaders[nodeName] = None
                    lostConnections[nodeName] = dict(
                        id=idRef, inputs=inputsRef)
                    continue

                # find changed values
                overrideInputs = dict()
                for inplug, inputRef in inputsRef.items():
                    inputUsd = inputsUsd.get(inplug, {})
                    if inplug in inputsUsd:
                        inputsUsd.pop(inplug)
                    valueRef = inputRef.get("value")
                    valueUsd = inputUsd.get("value")
                    if not self.isValuesEqual(valueRef, valueUsd):
                        overrideInputs[inplug] = inputRef

                # if attribute go back to its defaults
                for usdInput, dataInput in inputsUsd.items():
                    mayaInput = nameMirror.mayaInput(idRef, usdInput)
                    MFnDependencyNode = findCommand.shaderByName(nodeName)
                    MPlug = MFnDependencyNode.findPlug(mayaInput)
                    specInput = self.getMPlugSpec(MPlug)
                    valueUsd = dataInput.get("value")
                    valueMaya = specInput.get("value")
                    if not self.isValuesEqual(valueUsd, valueMaya):
                        overrideInputs[usdInput] = specInput

                if overrideInputs:
                    overrideShaders[nodeName] = dict(
                        id=None, inputs=overrideInputs)
            schemeRef["shaders"] = overrideShaders

        # create new node for referenced one with changed type
        for nodeName, nodeSpec in lostConnections.items():
            shaders[nodeName] = nodeSpec

        # update lost connections
        for nodeName in lostConnections:
            dataUpdate = self.getOutputData(nodeName)
            for ID, schemeUpdate in dataUpdate.items():
                shadersUpdate = schemeUpdate.get("shaders", {})
                for nodeNameUpdate, specUpdate in shadersUpdate.items():
                    if nodeNameUpdate in shaders:
                        continue
                    schemeRef = references.get(ID, {})
                    references[ID] = schemeRef
                    shadersRef = schemeRef.get("shaders", {})
                    schemeRef["shaders"] = shadersRef
                    specRef = shadersRef.get(nodeNameUpdate, {})
                    shadersRef[nodeNameUpdate] = specRef
                    inputsRef = specRef.get("inputs", {})
                    specRef["inputs"] = inputsRef
                    inputsUpdate = specUpdate.get("inputs", {})
                    for plugName, plugSpec in inputsUpdate.items():
                        inputsRef[plugName] = plugSpec

        return data

    def isValuesEqual (self, valueF: Any, valueS: Any) -> bool:
        """Check if two values are equal

        Arguments:
            valueF: The first value 
            valueS: The second value
        Returns:
            A result of the check
        """
        def roundFloat (value):
            if type(value) == float:
                return round(value, 4)
            return value

        if type(valueF) in [tuple, list]:
            valueF = [roundFloat(i) for i in valueF]
        else:
            valueF = roundFloat(valueF)
        if type(valueS) in [tuple, list]:
            valueS = [roundFloat(i) for i in valueS]
        else:
            valueS = roundFloat(valueS)
        return valueF == valueS

    def getMPlugSpec (self, MPlug: OpenMaya.MPlug) -> dict:
        """Create a data that describes
        an attribute value and its connections

        Arguments:
            MPlug: The dependency node plug
        Returns:
            A description data
        """
        valueType = mplugCommand.getAs(MPlug, asType=True)
        if not MPlug.isConnected():
            return dict(
                value=mplugCommand.getAs(MPlug, asValue=True),
                type=valueType,
                connection=False)
        else:
            nodeName, mayaOutput = MPlug.source().name().split(".")
            Shader = findCommand.shaderByName(nodeName)
            usdOutput = nameMirror.usdOutput(
                Shader.typeName(), mayaOutput)
            return dict(
                value=[nodeName, usdOutput],
                type=valueType,
                connection=True)

    def getOutputData (self, nodeName: str) -> dict:
        """For a node with the specified name get connected nodes
        that are destination ones and create a data that describes input connections

        Arguments:
            nodeName: The dependency node name
        Returns:
            A connection data
        """
        data = dict()
        MFnDependencyNode = findCommand.shaderByName(nodeName)
        for index in range(MFnDependencyNode.attributeCount()):
            MFnAttribute = OpenMaya.MFnAttribute(
                MFnDependencyNode.attribute(index))
            MPlug = MFnDependencyNode.findPlug(
                MFnAttribute.name())
            if MFnAttribute.isHidden() or not MPlug.isConnected():
                continue

            # go to a destination node of a connection
            MPlugArray = OpenMaya.MPlugArray()
            MPlug.destinations(MPlugArray)
            for indexDest in range(MPlugArray.length()):
                MPlugDest = MPlugArray[indexDest]
                nodeDest = OpenMaya.MFnDependencyNode(MPlugDest.node())
                if nodeDest.typeName() == "shadingEngine":
                    continue
                if not nodeDest.hasAttribute("assetID"):
                    continue

                # get input connection
                ID = nodeDest.findPlug("assetID").asString()
                nodeDestName, mayaInput = MPlugDest.name().split(".")
                dataReference = data.get(ID, {})
                data[ID] = dataReference
                dataShaders = dataReference.get("shaders", {})
                dataReference["shaders"] = dataShaders
                dataNode = dataShaders.get(nodeDestName, {})
                dataShaders[nodeDestName] = dataNode
                dataInputs = dataNode.get("inputs", {})
                dataNode["inputs"] = dataInputs
                usdInput = nameMirror.usdInput(
                    nodeDest.typeName(), mayaInput)
                dataInputs[usdInput] = self.getMPlugSpec(MPlugDest)

        return data

    def applyUsdNaming (self, data: dict) -> dict:
        """Change the specified network description data
        by using USD names instead of Maya ones

        Arguments:
            data: The network description data of a Maya material
        Returns:
            A network description data that uses USD naming
        """
        def getShaderID (name: str) -> str:
            """Get a type name for a node with the specified name"""
            Shader = findCommand.shaderByName(name)
            return str(Shader.typeName())

        # material
        inputs = dict()
        material = data.get("material", {})
        inputsMaterial = material.get("inputs", {})
        for mayaInput, inputValue in inputsMaterial.items():
            nodeName, mayaOutput = inputValue
            usdInput = nameMirror.usdInput("shadingEngine", mayaInput)
            usdOutput = nameMirror.usdOutput(
                getShaderID(nodeName), mayaOutput)
            inputs[usdInput] = [nodeName, usdOutput]
        material["inputs"] = inputs

        # shaders
        shadersBuffer = dict()
        shaders = data.get("shaders", {})
        for nameShader, specShader in shaders.items():
            mayaID = specShader.get("id")
            usdID = nameMirror.usdID(mayaID)
            if usdID is None:
                continue

            # inputs
            inputs = dict()
            inputsShader = specShader.get("inputs")
            for mayaInput, specInput in inputsShader.items():
                usdInput = nameMirror.usdInput(mayaID, mayaInput)
                value = specInput.get("value")
                valueType = specInput.get("type")
                connection = specInput.get("connection")
                if connection:
                    nodeName, mayaOutput = specInput.get("value")
                    usdOutput = nameMirror.usdOutput(
                        getShaderID(nodeName), mayaOutput)
                    value = [nodeName, usdOutput]
                inputs[usdInput] = dict(
                    value=value,
                    type=valueType,
                    connection=connection)

            # merge
            buffer = dict(id=usdID,inputs=inputs)
            assetID = specShader.get("asset", None)
            if assetID is not None:
                buffer["asset"] = assetID
            shadersBuffer[nameShader] = buffer

        # override
        data["shaders"] = shadersBuffer
        return data

    def editHydraNetwork (self, data: dict) -> dict:
        """Edit the specified Hydra network description data
        to be used as a build scheme for creating a USD Material Layer.
        Scale attribute values for working in metric units.

        Arguments:
            data: A network description data that uses USD naming
        Returns:
            A build scheme data for a USD file
        """
        units = 0.01           # UNIT DEPEND
        dataPrimvar = None
        for nameShader, specShader in data.items():
            nodeID = specShader.get("id")

            # edit connected textures
            if nodeID == "UsdPreviewSurface":
                inputs = specShader.get("inputs", {})
                for nameInput, specInput in inputs.items():
                    if not specInput.get("connection"):
                        continue
                    childName = specInput.get("value")[0]
                    childShader = data.get(childName, None)
                    if childShader is None:
                        continue
                    data[childName] = childShader
                    childInputs = childShader.get("inputs", {})
                    childShader["inputs"] = childInputs

                    # add scale and offset for displacement texture
                    if nameInput == "displacement":
                        childInputs["bias"] = dict(
                            value=list([round(-0.5*units,4)]*4),
                            type="float4",
                            connection=False)
                        childInputs["scale"] = dict(
                            value=list([round(1.0*units,4)]*4),
                            type="float4",
                            connection=False)

                    # apply color space rules
                    ocioConfig = os.getenv("OCIO")
                    if not ocioConfig:
                        if "sourceColorSpace" in childInputs:
                            childInputs.pop("sourceColorSpace")
                        continue
                    colorSpace = childInputs.get("sourceColorSpace")
                    if not colorSpace:
                        continue
                    value = colorSpace.get("value")
                    if nameInput == "diffuseColor" and value in ["acescg"]:
                        value = "sRGB"
                    elif nameInput in ["displacement", "normal"]:
                        value = "raw"
                    else:
                        value = "auto"
                    colorSpace["value"] = value
            
            # add wrap attributes for textures
            elif nodeID == "UsdUVTexture":
                inputs = specShader.get("inputs", {})
                inputs["wrapS"] = dict(
                    connection=False, 
                    type="token", 
                    value="repeat")
                inputs["wrapT"] = dict(
                    connection=False, 
                    type="token", 
                    value="repeat")
            
            # add a reader for texture coordinates
            elif nodeID == "UsdTransform2d":
                nodePrimvar = f"{nameShader}Primvar"
                dataItem = dict(
                    id="UsdPrimvarReader_float2",
                    inputs=dict(
                        varname=dict(
                            connection=False, 
                            type="token", 
                            value="st")))
                assetID = specShader.get("asset", None)
                if assetID is not None:
                    dataItem["asset"] = assetID
                dataPrimvar = dict()
                dataPrimvar[nodePrimvar] = dataItem
                inputs = specShader.get("inputs", {})
                inputs["in"] = dict(
                    connection=True, 
                    type="float2", 
                    value=[nodePrimvar, "result"])

        if dataPrimvar is not None:
            data.update(dataPrimvar)
        return data

    def editPrmanNetwork (self, data: dict) -> dict:
        """Edit the specified RenderMan network description data
        to be used as a build scheme for creating a USD Material Layer.
        Scale attribute values for working in metric units.

        Arguments:
            data: A network description data that uses USD naming
        Returns:
            A build scheme data for a USD file
        """
        units = 0.01           # UNIT DEPEND
        for nameShader, specShader in data.items():
            nodeID = specShader.get("id")
            # displacement scaling
            if nodeID == "PxrDisplace":
                MFnDependencyNode = findCommand.shaderByName(nameShader)
                MPlug = MFnDependencyNode.findPlug("dispAmount")
                specInput = self.getMPlugSpec(MPlug)
                if not specInput.get("connection"):
                    specInput["value"] = round(
                        specInput.get("value") * units, 4)
                    specShader["inputs"]["dispAmount"] = specInput
            # manifold scaling
            elif nodeID == "PxrRoundCube":
                MFnDependencyNode = findCommand.shaderByName(nameShader)
                MPlug = MFnDependencyNode.findPlug("frequency")
                specInput = self.getMPlugSpec(MPlug)
                if not specInput.get("connection"):
                    specInput["value"] = round(
                        specInput.get("value") / units, 4)
                    specShader["inputs"]["frequency"] = specInput
        return data

    def groupReferences (self, data: dict) -> dict:
        """Split the specified build scheme data into two groups where
        the first one has new nodes and the second one has references

        Arguments:
            data: The build scheme data for a USD file
        Returns:
            A grouped build scheme data
        """
        references = dict()
        shaders    = dict()
        for name, spec in data.get("shaders").items():
            ID = spec.get("asset")
            if not ID:
                shaders[name] = spec
                continue
            scheme = self.getAssetScheme(ID)
            if not scheme:
                shaders[name] = spec
                continue
            reference = references.get(ID, {})
            references[ID] = reference
            overrides = reference.get("shaders", {})
            reference["shaders"] = overrides
            if name not in overrides:
                overrides[name] = dict(
                    id=spec.get("id"),
                    inputs=spec.get("inputs"))
        data["references"] = references
        data["shaders"]    = shaders
        return data

    def getAssetID (self, node: str) -> Union[str, None]:
        """Get a library asset ID for a node with the specified name

        Arguments:
            node: The dependency node name
        Returns:
            A library asset ID
        """
        if mayaCommand.attributeQuery(
                "assetID", node=node, exists=True):
            return mayaCommand.getAttr(f"{node}.assetID")

    def getAssetScheme (self, ID: str) -> Union[dict, None]:
        """Find and get a build scheme data of a USD Material Asset
        using the specified library asset ID.
        If a build scheme data for this ID has gotten before, use that one.

        Arguments:
            ID: The library asset ID
        Returns:
            A build scheme data of a USD Material Asset
        """
        if ID in self.ASSETS:
            return self.ASSETS[ID]
        path = Metadata.findMaterial(ID)
        if not path:
            return
        prman, hydra = dict(), dict()
        for pathRef in readUSD.asReferences(path):
            if re.match(r".*RenderMan\.usd[ac]?$", pathRef):
                prman = readUSD.asUsdBuildScheme(pathRef)
                prman["name"] = readUSD.asDefaultPrim(pathRef)
                prman["path"] = pathRef
            elif re.match(r".*Hydra\.usd[ac]?$", pathRef):
                hydra = readUSD.asUsdBuildScheme(pathRef)
                hydra["name"] = readUSD.asDefaultPrim(pathRef)
                hydra["path"] = pathRef
        scheme = dict(prman=prman, hydra=hydra)
        self.ASSETS[ID] = scheme
        return scheme

    def getNetwork (self, shaderGroup: OpenMaya.MFnDependencyNode) -> dict:
        """Create a network description data for the specified material node

        Arguments:
            shaderGroup: The dependency graph node
        Returns:
            A network description data of the Maya material
        """
        prman = self.getPrmanNetwork(shaderGroup)
        hydra = self.getHydraNetwork(shaderGroup)
        return dict(prman=prman, hydra=hydra)

    def getUsdBuildScheme (self, shaderGroup: OpenMaya.MFnDependencyNode,
                           inherit: bool = False) -> dict:
        """Create a data for the specified material node
        as a build scheme for creating a USD Material Asset

        Arguments:
            shaderGroup: The dependency graph node
        Keyword Arguments:
            inherit: The switch to use USD Material Assets (nodes, networks)
                     from a library as references for creating new one
        Returns:
            A build scheme data for a USD file
        """
        data = self.getNetwork(shaderGroup)
        prman = self.makeUsdScheme(
            data.get("prman"), "prman", inherit)
        hydra = self.makeUsdScheme(
            data.get("hydra"), "hydra", inherit)
        return dict(prman=prman, hydra=hydra)
