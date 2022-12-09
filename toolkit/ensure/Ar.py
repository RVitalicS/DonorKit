#!/usr/bin/env python

"""
Asset Resolution

Import Ar module if it exists.
"""

try:
    from pxr import Ar
except ImportError:
    try:
        from fnpxr import Ar
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
