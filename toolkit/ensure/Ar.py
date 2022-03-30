#!/usr/bin/env python



try:
    from pxr import Ar
except ImportError:
    try:
        from fnpxr import Ar
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
