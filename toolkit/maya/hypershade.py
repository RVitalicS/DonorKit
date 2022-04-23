#!/usr/bin/env python



import os
import toolkit.maya.misc


import xml.etree.ElementTree as ET
import oslquery


import maya.OpenMaya as OpenMaya





class Manager (object):


    def __init__ (self, data):
        
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



    def parseArgs (self, root, data={}):

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



    def getShaderDefaults (self, shader):

        shaderType = shader.typeName()


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
            shaderData = self.RMAN_DEFAULTS[shaderType]


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

            shaderDefaults = self.getShaderDefaults(shader)

            for index in range(shader.attributeCount()):

                MObject = shader.attribute(index)
                attribute = OpenMaya.MFnAttribute(MObject)

                attrName = attribute.name()

                MPlug = shader.findPlug(attrName)

                if attribute.isWritable():

                    if MPlug.isConnected() and shaderType != "PxrManifold2D":

                        if not prman and attrName not in [
                                "diffuseColor",
                                "roughness",
                                "uvCoord"]:
                            continue
                        
                        valueType = toolkit.maya.misc.getMPlugAs( MPlug, asType=True )

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



                    elif prman:
                        data = shaderDefaults.get(attrName, None)
                        value = toolkit.maya.misc.getMPlugAs( MPlug, asValue=True )

                        if data != None and value != None:

                            valueDefault = data["default"]
                            valueType    = data["type"]

                            isDefault = True

                            if isinstance(value, tuple) and isinstance(valueDefault, tuple):
                                if len(value) == len(valueDefault):

                                    for index in range( len(valueDefault) ):
                                        defaultComponent = valueDefault[index]

                                        if isinstance(defaultComponent, float):
                                            exponent = len(str(defaultComponent).split(".")[1])
                                            valueComponent = round(value[index], exponent)
                                            if valueComponent != defaultComponent:
                                                isDefault = False
                                                break
                                        elif value[index] != valueDefault[index]:
                                                isDefault = False
                                                break

                            elif value != valueDefault:
                                    isDefault = False

                            if not isDefault:
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

                        value = toolkit.maya.misc.getMPlugAs( MPlug, asValue=True )
                        if not value is None:
                            typeString = toolkit.maya.misc.getMPlugAs( MPlug, asType=True )

                            inputs[attrName] = dict(
                                value=value,
                                type=typeString,
                                connection=False )


        return collector



    def getPrmanNetwork (self, shaderGroup):

        shGroupName = shaderGroup.name()

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

        shGroupName = shaderGroup.name()
        
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

                shader = toolkit.maya.misc.getShaderByName(shaderName)
                repeatUV = toolkit.maya.misc.getNodeAttribute(shader, "repeatUV")
                rotateUV = toolkit.maya.misc.getNodeAttribute(shader, "rotateUV")
                offset = toolkit.maya.misc.getNodeAttribute(shader, "offset")

                network[nameTransform] = dict(
                    id="UsdTransform2d",
                    inputs={
                        "in": {
                            "value": outputManifold,
                            "type": "float2",
                            "connection": True
                        },
                        "scale": {
                            "value": toolkit.maya.misc.getMPlugAs(repeatUV, asValue=True),
                            "type": toolkit.maya.misc.getMPlugAs(repeatUV, asType=True),
                            "connection": False
                        },
                        "rotation": {
                            "value": toolkit.maya.misc.getMPlugAs(rotateUV, asValue=True),
                            "type": toolkit.maya.misc.getMPlugAs(rotateUV, asType=True),
                            "connection": False
                        },
                        "translation": {
                            "value": toolkit.maya.misc.getMPlugAs(offset, asValue=True),
                            "type": toolkit.maya.misc.getMPlugAs(offset, asType=True),
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
