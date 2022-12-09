#!/usr/bin/env python

"""
Qt Core

Import QtCore module if it exists.
"""

import os
preferred = os.getenv("QT_PREFERRED_BINDING", "")

try:
    if preferred == "PySide2":
        from PySide2 import QtCore
    else:
        from PyQt5 import QtCore

except ImportError:
    try:
        if preferred == "PySide2":
            from PyQt5 import QtCore
        else:
            from PySide2 import QtCore

    except ImportError:
        raise ImportError(
            "Error while importing Qt modules")
