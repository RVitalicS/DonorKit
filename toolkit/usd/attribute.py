#!/usr/bin/env python


from pxr import UsdGeom, Sdf, Work





def getTranslateOp (Xformable):

    OpMatch = UsdGeom.XformOp.TypeTranslate

    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation

    return Xformable.AddTranslateOp()





def getRotateXYZOp (Xformable):

    OpMatch = UsdGeom.XformOp.TypeRotateXYZ

    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation

    return Xformable.AddRotateXYZOp()





def getScaleOp (Xformable):

    OpMatch = UsdGeom.XformOp.TypeScale

    for Operation in Xformable.GetOrderedXformOps():
        if Operation.GetOpType() == OpMatch:
            return Operation

    return Xformable.AddScaleOp()
