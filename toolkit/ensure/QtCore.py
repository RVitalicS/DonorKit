#!/usr/bin/env python


import os
prefered = os.getenv("QT_PREFERRED_BINDING", "")



try:
    if prefered == "PySide2":
        from PySide2 import QtCore
    else:
        from PyQt5 import QtCore

except ImportError:

    try:
        if prefered == "PySide2":
            from PyQt5 import QtCore
        else:
            from PySide2 import QtCore

    except ImportError:

        raise ImportError(
            "Error while importing Qt modules")
