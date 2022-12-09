#!/usr/bin/env python

"""
Signals

Import Signal module if it exists.
"""

import os
preferred = os.getenv("QT_PREFERRED_BINDING", "")

try:
    if preferred == "PySide2":
        from PySide2.QtCore import Signal
    else:
        from PyQt5.QtCore import pyqtSignal as Signal

except ImportError:
    try:
        if preferred == "PySide2":
            from PyQt5.QtCore import pyqtSignal as Signal
        else:
            from PySide2.QtCore import Signal

    except ImportError:
        raise ImportError(
            "Error while importing Qt modules")
