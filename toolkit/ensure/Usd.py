#!/usr/bin/env python

"""
Universal Scene Description (Core)

Import Usd module if it exists.
"""

try:
    from pxr import Usd
except ImportError:
    try:
        from fnpxr import Usd
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
