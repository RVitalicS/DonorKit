#!/usr/bin/env python

"""
Qt GUI

Import QtGui module if it exists.
"""

import os
preferred = os.getenv("QT_PREFERRED_BINDING", "")

try:
    if preferred == "PySide2":
        from PySide2 import QtGui
    else:
        from PyQt5 import QtGui

except ImportError:
    try:
        if preferred == "PySide2":
            from PyQt5 import QtGui
        else:
            from PySide2 import QtGui

    except ImportError:
        raise ImportError(
            "Error while importing Qt modules")
