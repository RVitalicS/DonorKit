#!/usr/bin/env python

"""
Qt Widgets

Import QtWidgets module if it exists.
"""

import os
preferred = os.getenv("QT_PREFERRED_BINDING", "")

try:
    if preferred == "PySide2":
        from PySide2 import QtWidgets
    else:
        from PyQt5 import QtWidgets

except ImportError:
    try:
        if preferred == "PySide2":
            from PyQt5 import QtWidgets
        else:
            from PySide2 import QtWidgets

    except ImportError:
        raise ImportError(
            "Error while importing Qt modules")
