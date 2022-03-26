#!/usr/bin/env python


import os
prefered = os.getenv("QT_PREFERRED_BINDING", "")



try:
    if prefered == "PySide2":
        from PySide2.QtCore import Signal
    else:
        from PyQt5.QtCore import pyqtSignal as Signal

except ImportError:

    try:
        if prefered == "PySide2":
            from PyQt5.QtCore import pyqtSignal as Signal
        else:
            from PySide2.QtCore import Signal

    except ImportError:

        raise ImportError(
            "Error while importing Qt modules")
