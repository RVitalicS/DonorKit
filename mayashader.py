

import os

import xml.etree.ElementTree as ET
import oslquery


from pymel.core import connectionInfo as PyMelConnectionInfo
from pymel.core import ls as PyMelLS


encModel = os.getenv("PYTHONIOENCODING")








def keydata (dictionary, keyname):
    if isinstance(dictionary, dict):

        for key, value in dictionary.items():
            
            if key == keyname:
                return value






def typeEditor (paramdefault, paramtype):

    if paramtype in ["color", "normal"]:
        return tuple([float(i) for i in paramdefault.split(" ")])

    elif paramtype == "float":
        paramdefault = paramdefault.replace("f", "")
        return float(paramdefault)

    elif paramtype == "int":
        return int(paramdefault)

    elif paramtype == "string":
        return str(paramdefault)






def treeRunner (function, root, value=None, page=""):

    for child in root:
        if child.tag == "param":


            paramname = keydata(child.attrib, "name")
            if paramname:

                paramtype = keydata(child.attrib, "type")
                if paramtype:

                    paramdefault = keydata(child.attrib, "default")
                    if paramdefault:

                        dynamicArray = keydata(child.attrib, "isDynamicArray")
                        if not dynamicArray:
                            paramdefault = typeEditor(paramdefault, paramtype)
                            value = function(paramname, paramtype, paramdefault)
                            if not isinstance(value, type(None)):
                                return value


        value = treeRunner(function, child, value=value, page=page)
        if not isinstance(value, type(None)):
            return value






def getDefault (shader, attrname):


    RMANTREE = os.getenv("RMANTREE", "")

    ArgsPath = os.path.join(
        os.path.join(RMANTREE, "lib", "plugins", "Args"),
        "{}.args".format(shader.typeName()) )
        
    OslPath = os.path.join(
        os.path.join(RMANTREE, "lib", "shaders"),
        "{}.oso".format(shader.typeName()) )


    if os.path.exists(ArgsPath):
        tree = ET.ElementTree(file=ArgsPath)
        root = tree.getroot()

        def match (paramname, paramtype, paramdefault):

            if paramname == attrname:
                return dict(
                    type=paramtype,
                    default=paramdefault )

        return treeRunner(match, root)


    elif os.path.exists(OslPath):
        shader = oslquery.OslQuery()
        shader.open(OslPath)

        for index in range(shader.nparams()):
            parameter = shader.getparam(index)

            if parameter["name"] == attrname:
                if not parameter["isoutput"]:
                    if not parameter["isstruct"]:

                        return dict(
                            type=parameter["type"],
                            default=parameter["default"] )






def getNetwork (shader, prman=True, collector={}):

    shaderType = shader.typeName().encode(encModel)
    shaderName = shader.getName().encode(encModel)

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

        for attribute in shader.listAttr():
            attrName = attribute.attrName(longName=True).encode(encModel)

            if attribute.isConnected() and attribute.inputs():
                connectionSource = PyMelConnectionInfo(
                    attribute,
                    sourceFromDestination=True ).encode(encModel)

                if not prman and attrName not in [
                    "diffuseColor",
                    "roughness",
                    "uvCoord"]:
                    continue

                if connectionSource:

                    valueType = attribute.type().encode(encModel)
                    if prman:
                        data = getDefault(shader, attrName)
                        dataType = keydata(data, "type")
                        if dataType:
                            valueType = dataType

                    inputs[attrName] = dict(
                        value=connectionSource,
                        type=valueType,
                        connection=True )

                    collector = getNetwork(
                        attribute.inputs()[0],
                        prman=prman,
                        collector=collector )

            elif prman:
                data = getDefault(shader, attrName)
                valueDefault = keydata(data, "default")
                valueType    = keydata(data, "type")

                if not isinstance(valueDefault, type(None)):

                    isDefault = True
                    value = attribute.get()

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

            else:
                if shaderType in ["file", "place2dTexture"]:
                    if attrName in ["fileTextureName", "repeatUV"]:
                        inputs[attrName] = dict(
                            value=attribute.get(),
                            type=attribute.type(),
                            connection=False )


    return collector






def getPrmanNetwork (shGroup):

    shGroupName = shGroup.getName()

    material = dict(
        surface=None,
        displacement=None,
        shaders=dict())
        
    for connection in [
        "displacement",
        "surface" ]:

        attrName = "rman__" + connection
        if shGroup.hasAttr(attrName):
            attribute = shGroup.attr(attrName)

            if attribute.inputs():
                connectionSource = PyMelConnectionInfo(
                    attribute,
                    sourceFromDestination=True )

                if connectionSource:
                    material[connection] = connectionSource.encode(encModel)
                    
                    shader = attribute.inputs()[0]
                    material["shaders"] = getNetwork(
                        shader,
                        prman=True,
                        collector=material["shaders"])

    return material






def getPreviewNetwork (shGroup):

    shGroupName = shGroup.getName()
    
    material = dict(
        surface=None,
        shaders=dict())
        
    attrName = "surfaceShader"
    if shGroup.hasAttr(attrName):
        attribute = shGroup.attr(attrName)

        if attribute.inputs():
            connectionSource = PyMelConnectionInfo(
                attribute,
                sourceFromDestination=True )

            if connectionSource:
                material["surface"] = connectionSource.encode(encModel)
                
                shader = attribute.inputs()[0]
                material["shaders"] = getNetwork(
                    shader,
                    prman=False,
                    collector=material["shaders"])

    return material







def getShadingEngine (name):

    engineList = PyMelLS(
        type="shadingEngine" )

    for engine in engineList:
        if engine.name().encode(encModel) == name:

            return engine
