#!/usr/bin/env python

import os
from databank import shadertag






def getMayaBuildType (usdID):
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

def mayaID (usdID):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID == USD:
                return Maya
    return usdID

def mayaInput (usdID, usdInput):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID != USD: continue
            inputs = item.get("inputs", {})
            if usdInput in inputs:
                return inputs.get(usdInput)
    return usdInput

def mayaOutput (usdID, usdOutput):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if usdID != USD: continue
            outputs = item.get("outputs", {})
            if usdOutput in outputs:
                return outputs.get(usdOutput)
    return usdOutput

def mayaSpace (space):
    ocioConfig = os.getenv("OCIO")
    if not ocioConfig:
        return None
    if space == "sRGB":
        return "acescg"
    elif space == "auto":
        return "raw"
    return space

def mayaType (token):
    if token in ["normal3f", "color3f"]:
        return "float3"
    elif token in ["asset", "token"]:
        return "string"
    return token






def usdID (mayaID):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID == Maya:
                return USD
    return mayaID

def usdInput (mayaID, mayaInput):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID != Maya: continue
            inputs = item.get("inputs", {})
            for inputUSD, inputMaya in inputs.items():
                if inputMaya == mayaInput:
                    return inputUSD
    return mayaInput

def usdOutput (mayaID, mayaOutput):
    for item in shadertag:
        IDs = item.get("id")
        for USD, Maya in IDs.items():
            if mayaID != Maya: continue
            outputs = item.get("outputs", {})
            for outputUSD, outputMaya in outputs.items():
                if outputMaya == mayaOutput:
                    return outputUSD
    return mayaOutput
