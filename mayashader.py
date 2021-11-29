

import os
encModel = os.getenv("PYTHONIOENCODING")


import xml.etree.ElementTree as ET
import oslquery


import maya.OpenMaya as OpenMaya








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
                paramdefault = typeEditor(paramdefault, paramtype)

                value = function(paramname, paramtype, paramdefault)
                if not isinstance(value, type(None)):
                    return value


        value = treeRunner(function, child, value=value, page=page)
        if not isinstance(value, type(None)):
            return value






def getDefault (shader, attrname):

    shaderType = shader.typeName().encode(encModel)
    shaderName = shader.name().encode(encModel)

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






def getMPlugAs (MPlug, asValue=False, asType=False, echo=False):


    MObject = MPlug.attribute()

    attribute = OpenMaya.MFnAttribute(MObject)
    attrName  = attribute.name()

    apiType = MObject.apiType()


    if apiType == OpenMaya.MFn.kNumericAttribute:

        MFnNumericAttribute = OpenMaya.MFnNumericAttribute(MObject)
        unitType = MFnNumericAttribute.unitType()

        if unitType == OpenMaya.MFnNumericData.kBoolean:
            if echo: print( "{}: bool".format(attrName) )
            if asType: return "bool"
            if asValue: return MPlug.asBool()
            
        elif unitType in [ 
            OpenMaya.MFnNumericData.kInt,
            OpenMaya.MFnNumericData.kByte,
            OpenMaya.MFnNumericData.kShort,
            OpenMaya.MFnNumericData.kLong ]:

            if echo: print( "{}: int".format(attrName) )
            if asType: return "int"
            if asValue: return MPlug.asInt()
            
        elif unitType == OpenMaya.MFnNumericData.kFloat:
            if echo: print( "{}: float".format(attrName) )
            if asType: return "float"
            if asValue: return MPlug.asFloat()
            
        elif unitType == OpenMaya.MFnNumericData.kDouble:
            if echo: print( "{}: double".format(attrName) )
            if asType: return "double"
            if asValue: return MPlug.asDouble()


    elif apiType == OpenMaya.MFn.kEnumAttribute:

        if echo: print( "{}: int".format(attrName) )
        if asType: return "int"
        if asValue: return MPlug.asInt()


    elif apiType == OpenMaya.MFn.kTypedAttribute:

        MFnTypedAttribute = OpenMaya.MFnTypedAttribute(MObject)
        attrType = MFnTypedAttribute.attrType()

        if attrType == OpenMaya.MFnData.kString:
            if echo: print( "{}: string".format(attrName) )
            if asType: return "string"
            if asValue: return MPlug.asString().encode(encModel)

        elif attrType == OpenMaya.MFnData.kMatrix:
            MFnMatrixData = OpenMaya.MFnMatrixData( MPlug.asMObject() )

            if echo: print( "{}: matrix".format(attrName) )
            if asType: return "matrix"
            if asValue: return MFnMatrixData.matrix()


    elif apiType in [ 
        OpenMaya.MFn.kAttribute3Float,
        OpenMaya.MFn.kAttribute3Double,
        OpenMaya.MFn.kCompoundAttribute ]:

        result = []
        for index in xrange( MPlug.numChildren() ):

            value = getMPlugAs( MPlug.child(index),
                   asValue=True )
            result.append( value )
        

        typeString = "float3"
        if attribute.isUsedAsColor():
            typeString = "color3f"

        if echo: print( "{}: {}".format(attrName, typeString) )
        if asType: return typeString
        if asValue: return tuple(result)






def getNetwork (shader, prman=True, collector={}):

    shaderType = shader.typeName().encode(encModel)
    shaderName = shader.name().encode(encModel)

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

        for index in range(shader.attributeCount()):

            MObject = shader.attribute(index)
            attribute = OpenMaya.MFnAttribute(MObject)

            attrName = attribute.name().encode(encModel)

            MPlug = shader.findPlug(attrName)

            if attribute.isWritable():
                if MPlug.isConnected():

                    if not prman and attrName not in [
                        "diffuseColor",
                        "roughness",
                        "uvCoord"]:
                        continue
                    
                    valueType = getMPlugAs( MPlug, asType=True )

                    if prman:
                        data = getDefault(shader, attrName)
                        if data:
                            valueType = data["type"]

                    MPlugSource = MPlug.source()
                    sourceNode = OpenMaya.MFnDependencyNode(
                        MPlugSource.node() )

                    if MPlugSource.info():

                        inputs[attrName] = dict(
                            value=MPlugSource.name().encode(encModel),
                            type=valueType,
                            connection=True )
                        
                        collector = getNetwork(
                            sourceNode,
                            prman=prman,
                            collector=collector )

                elif prman:
                    data = getDefault(shader, attrName)
                    value = getMPlugAs( MPlug, asValue=True )

                    if ( not isinstance(data, type(None)) and
                         not isinstance(value, type(None)) ):

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
                    "fileTextureName",
                    "repeatUV" ] and not MPlug.isDefaultValue():

                    value = getMPlugAs( MPlug, asValue=True )
                    if not isinstance(value, type(None)):
                        typeString = getMPlugAs( MPlug, asType=True )

                        inputs[attrName] = dict(
                            value=value,
                            type=typeString,
                            connection=False )


    return collector






def getPrmanNetwork (shaderGroup):

    shGroupName = shaderGroup.name().encode(encModel)

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

            material[connection] = connectionSource.name().encode(encModel)
                
            shader = OpenMaya.MFnDependencyNode(
                connectionSource.node() )

            material["shaders"] = getNetwork(
                shader,
                prman=True,
                collector=material["shaders"] )

    return material






def getPreviewNetwork (shaderGroup):

    shGroupName = shaderGroup.name().encode(encModel)
    
    material = dict(
        surface=None,
        shaders=dict())

    attrName = "surfaceShader"
    shaderPlug = shaderGroup.findPlug(attrName)
    
    if shaderPlug.isConnected():
        connectionSource = shaderPlug.source()

        material["surface"] = connectionSource.name().encode(encModel)

        shader = OpenMaya.MFnDependencyNode(
            connectionSource.node() )

        material["shaders"] = getNetwork(
            shader,
            prman=False,
            collector=material["shaders"] )

    return material
