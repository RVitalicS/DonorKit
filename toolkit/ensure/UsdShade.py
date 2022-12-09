#!/usr/bin/env python

"""
USD Shading Schema 

Import UsdShade module if it exists.
"""

try:
    from pxr import UsdShade
except ImportError:
    try:
        from fnpxr import UsdShade
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
