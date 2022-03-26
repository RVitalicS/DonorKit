#!/usr/bin/env python



try:
    from pxr import Usd
except ImportError:
    try:
        from fnpxr import Usd
    except ImportError:
        raise ImportError(
            "Error while importing pxr module")
