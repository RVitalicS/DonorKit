#!/usr/bin/env python



try:
    from pxr import UsdShade
except ImportError:
    try:
        from fnpxr import UsdShade
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
