#!/usr/bin/env python

"""
Attribute Handling

This module holds utilities to work with attributes.
"""

from pxr import Usd
from pxr import UsdGeom


def getTranslateOp (Prim: Usd.Prim) -> UsdGeom.XformOp:
    """Get a wrapper for UsdAttribute for authoring
    and computing translate operations

    Arguments:
        Prim: The UsdPrim to get translate wrapper
    Returns:
        A translation wrapper
    """
    Xformable = UsdGeom.Xformable(Prim)
    OpMatch = UsdGeom.XformOp.TypeTranslate
    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation
    return Xformable.AddTranslateOp()


def getRotateXYZOp (Prim: Usd.Prim) -> UsdGeom.XformOp:
    """Get a wrapper for UsdAttribute for authoring
    and computing rotate operations

    Arguments:
        Prim: The UsdPrim to get rotate wrapper
    Returns:
        A rotation wrapper
    """
    Xformable = UsdGeom.Xformable(Prim)
    OpMatch = UsdGeom.XformOp.TypeRotateXYZ
    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation
    return Xformable.AddRotateXYZOp()


def getScaleOp (Prim: Usd.Prim) -> UsdGeom.XformOp:
    """Get a wrapper for UsdAttribute for authoring
    and computing scale operations

    Arguments:
        Prim: The UsdPrim to get scale wrapper
    Returns:
        A scale wrapper
    """
    Xformable = UsdGeom.Xformable(Prim)
    OpMatch = UsdGeom.XformOp.TypeScale
    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation
    return Xformable.AddScaleOp()
