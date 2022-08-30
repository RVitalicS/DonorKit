#!/usr/bin/env python



import os

import toolkit.maya.mplug
import toolkit.maya.find
import toolkit.maya.attribute


import xml.etree.ElementTree as ET
import oslquery


import maya.cmds as mayaCommand
import maya.OpenMaya as OpenMaya





def getSelectionName ():

    selection = mayaCommand.ls( selection=True )
    if not selection: return

    material = selection[0]
    if mayaCommand.nodeType(material) == "shadingEngine":
        return material





class Manager (object):


    def __init__ (self, data=dict()):
        
        self.RMAN_DEFAULTS = data



    def typeEditor (self, paramdefault, paramtype):

        if paramtype in ["color", "normal"]:
            return tuple([float(i) for i in paramdefault.split(" ")])

        elif paramtype == "float":
            paramdefault = paramdefault.replace("f", "")
            return float(paramdefault)

        elif paramtype == "int":
            return int(paramdefault)

        elif paramtype == "string":
            return str(paramdefault)



    def parseArgs (self, root, data=None):

        if data == None:
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
                            default=paramdefault )

            data = self.parseArgs(child, data=data)
        
        return data



    def getShaderDefaults (self, shaderType):

        if shaderType not in self.RMAN_DEFAULTS:

            shaderData = dict()
            RMANTREE = os.getenv("RMANTREE", "")

            ArgsPath = os.path.join(
                os.path.join(RMANTREE, "lib", "plugins", "Args"),
                "{}.args".format(shaderType) )
                
            OslPath = os.path.join(
                os.path.join(RMANTREE, "lib", "shaders"),
                "{}.oso".format(shaderType) )

            if os.path.exists(ArgsPath):
                tree = ET.ElementTree(file=ArgsPath)
                root = tree.getroot()

                shaderData = self.parseArgs(root)
                self.RMAN_DEFAULTS[shaderType] = shaderData


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
                                default=parameter["default"] )

                self.RMAN_DEFAULTS[shaderType] = shaderData

        else:
            shaderData = self.RMAN_DEFAULTS.get(shaderType, dict())

        return shaderData



    def getNetwork (self, shader, prman=True, collector={}):

        shaderType = shader.typeName()
        shaderName = shader.name()

        if not prman and shaderType not in [
            "usdPreviewSurface",
            "file",
            "place2dTexture"]:

            return collector

        if shaderName not in collector:
            inputs = dict()
            shaderData = dict(
                id=shaderType,
                inputs=inputs )
            
            collector[shaderName] = shaderData

            if prman:
                shaderDefaults = self.getShaderDefaults(shaderType)

            for index in range(shader.attributeCount()):

                MObject = shader.attribute(index)
                attribute = OpenMaya.MFnAttribute(MObject)

                attrName = attribute.name()

                MPlug = shader.findPlug(attrName)

                if attribute.isWritable():

                    if MPlug.isConnected() and shaderType != "PxrManifold2D":

                        if not prman and attrName not in [
                                "diffuseColor", "metallic", "roughness",
                                "normal", "displacement",
                                "opacity", "uvCoord"]:
                            continue

                        valueType = toolkit.maya.mplug.getAs( MPlug, asType=True )

                        if prman:
                            data = shaderDefaults.get(attrName, None)
                            if data != None:
                                valueType = data["type"]

                        MPlugSource = MPlug.source()
                        sourceNode = OpenMaya.MFnDependencyNode(
                            MPlugSource.node() )

                        if MPlugSource.info():

                            inputs[attrName] = dict(
                                value=MPlugSource.name(),
                                type=valueType,
                                connection=True )
                            
                            collector = self.getNetwork(
                                sourceNode,
                                prman=prman,
                                collector=collector )
                        

                            if shaderType == "usdPreviewSurface":
                                sourceName = sourceNode.name()

                                if attrName == "displacement":
                                    units = 0.1           # UNIT DEPEND
                                    collector[sourceName]["inputs"]["bias"] = dict(
                                        value=tuple([-0.5*units]*4),
                                        type="float4",
                                        connection=False )
                                    collector[sourceName]["inputs"]["scale"] = dict(
                                        value=tuple([1.0*units]*4),
                                        type="float4",
                                        connection=False )

                                if attrName == "diffuseColor":
                                    space = "sRGB"
                                elif attrName in ["displacement", "normal"]:
                                    space = "raw"
                                else:
                                    space = "auto"
                                collector[sourceName]["inputs"]["sourceColorSpace"] = dict(
                                    value=space,
                                    type="token",
                                    connection=False )



                    elif prman:
                        data = shaderDefaults.get(attrName, None)
                        value = toolkit.maya.mplug.getAs( MPlug, asValue=True )

                        if data != None and value != None:

                            valueDefault = data["default"]
                            valueType    = data["type"]

                            collectAttibue = False

                            if isinstance(value, tuple) and isinstance(valueDefault, tuple):
                                if len(value) == len(valueDefault):

                                    for index in range( len(valueDefault) ):
                                        defaultComponent = valueDefault[index]

                                        if isinstance(defaultComponent, float):
                                            exponent = len(str(defaultComponent).split(".")[1])
                                            valueComponent = round(value[index], exponent)
                                            if valueComponent != defaultComponent:
                                                collectAttibue = True
                                                break
                                        elif value[index] != valueDefault[index]:
                                                collectAttibue = True
                                                break

                            elif value != valueDefault:
                                    collectAttibue = True

                            if shaderType == "PxrDisplace":
                                if attrName == "dispAmount":
                                    if not collectAttibue:
                                        value = 0.01          # UNIT DEPEND
                                        collectAttibue = True

                            if collectAttibue:
                                inputs[attrName] = dict(
                                value=value,
                                type=valueType,
                                connection=False )



                    elif attrName in [
                        "diffuseColor",
                        "emissiveColor",
                        "opacity",
                        "ior",
                        "metallic",
                        "roughness",
                        "clearcoat",
                        "clearcoatRoughness",
                        "fileTextureName" ] and not MPlug.isDefaultValue():

                        value = toolkit.maya.mplug.getAs( MPlug, asValue=True )
                        if not value is None:
                            typeString = toolkit.maya.mplug.getAs( MPlug, asType=True )

                            inputs[attrName] = dict(
                                value=value,
                                type=typeString,
                                connection=False )


        return collector



    def getPrmanNetwork (self, shaderGroup):

        material = dict(
            surface=None,
            displacement=None,
            shaders=dict())

        for connection in [
            "displacement",
            "surface" ]:

            attrName = "rman__" + connection
            shaderPlug = shaderGroup.findPlug(attrName)
            if shaderPlug.isConnected():
                connectionSource = shaderPlug.source()

                material[connection] = connectionSource.name()
                    
                shader = OpenMaya.MFnDependencyNode(
                    connectionSource.node() )

                material["shaders"] = self.getNetwork(
                    shader,
                    prman=True,
                    collector=material["shaders"] )

        return material



    def getPreviewNetwork (self, shaderGroup):
        
        material = dict(
            surface=None,
            shaders=dict())

        attrName = "surfaceShader"
        shaderPlug = shaderGroup.findPlug(attrName)
        
        if shaderPlug.isConnected():
            connectionSource = shaderPlug.source()

            material["surface"] = connectionSource.name()

            shader = OpenMaya.MFnDependencyNode(
                connectionSource.node() )

            network = self.getNetwork(
                shader,
                prman=False,
                collector=material["shaders"] )
            material["shaders"] = self.editPreviewNetwork(network)

        return material



    def editPreviewNetwork (self, data):

        network = dict()
        replace = dict()


        # add manifold transform node
        for shaderName, value in data.items():

            if value.get("id") == "place2dTexture":
                nameTransform = shaderName + "Transform"

                outputManifold  = shaderName + ".outUV"
                outputTransform = nameTransform + ".outUV"

                shader = toolkit.maya.find.shaderByName(shaderName)
                repeatUV = toolkit.maya.attribute.get(shader, "repeatUV")
                rotateUV = toolkit.maya.attribute.get(shader, "rotateUV")
                offset = toolkit.maya.attribute.get(shader, "offset")

                network[nameTransform] = dict(
                    id="UsdTransform2d",
                    inputs={
                        "in": {
                            "value": outputManifold,
                            "type": "float2",
                            "connection": True
                        },
                        "scale": {
                            "value": toolkit.maya.mplug.getAs(repeatUV, asValue=True),
                            "type": toolkit.maya.mplug.getAs(repeatUV, asType=True),
                            "connection": False
                        },
                        "rotation": {
                            "value": toolkit.maya.mplug.getAs(rotateUV, asValue=True),
                            "type": toolkit.maya.mplug.getAs(rotateUV, asType=True),
                            "connection": False
                        },
                        "translation": {
                            "value": toolkit.maya.mplug.getAs(offset, asValue=True),
                            "type": toolkit.maya.mplug.getAs(offset, asType=True),
                            "connection": False
                        }
                    } )

                replace[outputManifold] = outputTransform


        # edit manifold bindings
        for shaderName, item in data.items():
            for key, value in item.get("inputs").items():
                output = value.get("value")
                if output in replace:
                    value["value"] = replace.get(output)

            network[shaderName] = item


        return network
