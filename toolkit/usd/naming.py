#!/usr/bin/env python

"""
Naming Registry

This module defines functions to convert a USD node names, attribute names,
data names, etc. to used one in Maya and vice versa.
"""

import os
from databank import shadertag
from typing import Union


def getMayaBuildType (usdID: str) -> str:
    """Get a type name to classify Maya node

    Arguments:
        usdID: The ID name of the UsdShader
    Returns:
        A name to classify the Maya node
    """
    mayatype = "utility"
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID != USD:
                continue
            mayatype = item.get("mayatype")
            if mayatype:
                return mayatype
    return mayatype


def mayaID (usdID: str) -> str:
    """Get a type name to create Maya node

    Arguments:
        usdID: The ID name of the UsdShader
    Returns:
        A Maya node type name
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID == USD:
                return Maya
    return usdID


def mayaInput (usdID: str, usdInput: str) -> str:
    """Get a name of a Maya node input attribute

    Arguments:
        usdID: The ID name of the UsdShader
        usdInput: The name of the UsdShader input
    Returns:
        A Maya node input attribute name
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID != USD:
                continue
            inputs = item.get("inputs", {})
            if usdInput in inputs:
                return inputs.get(usdInput)
    return usdInput


def mayaOutput (usdID: str, usdOutput: str) -> str:
    """Get a name of a Maya node output attribute

    Arguments:
        usdID: The ID name of the UsdShader
        usdOutput: The name of the UsdShader output
    Returns:
        A Maya node output attribute name
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID != USD:
                continue
            outputs = item.get("outputs", {})
            if usdOutput in outputs:
                return outputs.get(usdOutput)
    return usdOutput


def mayaSpace (space: str) -> Union[str, None]:
    """Change the color space name that used in a USD file
    to a Maya corresponding one, depending on OCIO setup

    Arguments:
        space: The color space name
    Returns:
        A color space name
    """
    ocioConfig = os.getenv("OCIO")
    if not ocioConfig:
        return
    if space == "sRGB":
        return "acescg"
    elif space == "auto":
        return "raw"
    return space


def mayaType (token: str) -> str:
    """Rename USD data type name to used one in Maya

    Arguments:
        token: The data type name
    Returns:
        A type name
    """
    if token in ["normal3f", "color3f"]:
        return "float3"
    elif token in ["asset", "token"]:
        return "string"
    return token


def usdID (mayaID: str) -> str:
    """Get an ID name of the UsdShader

    Arguments:
        mayaID: The type name of a Maya node
    Returns:
        An ID name of the UsdShader
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID == Maya:
                return USD
    return mayaID


def usdInput (mayaID: str, mayaInput: str) -> str:
    """Get a name of the UsdShader input

    Arguments:
        mayaID: The type name of a Maya node
        mayaInput: The input attribute name of a Maya node
    Returns:
        A name of the UsdShader input
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID != Maya:
                continue
            inputs = item.get("inputs", {})
            for inputUSD, inputMaya in inputs.items():
                if inputMaya == mayaInput:
                    return inputUSD
    return mayaInput


def usdOutput (mayaID: str, mayaOutput: str) -> str:
    """Get a name of the UsdShader output

    Arguments:
        mayaID: The type name of a Maya node
        mayaOutput: The output attribute name of a Maya node
    Returns:
        A name of the UsdShader output
    """
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID != Maya:
                continue
            outputs = item.get("outputs", {})
            for outputUSD, outputMaya in outputs.items():
                if outputMaya == mayaOutput:
                    return outputUSD
    return mayaOutput
