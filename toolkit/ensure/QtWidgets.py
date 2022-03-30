#!/usr/bin/env python


import os
prefered = os.getenv("QT_PREFERRED_BINDING", "")



try:
    if prefered == "PySide2":
        from PySide2 import QtWidgets
    else:
        from PyQt5 import QtWidgets

except ImportError:

    try:
        if prefered == "PySide2":
            from PyQt5 import QtWidgets
        else:
            from PySide2 import QtWidgets

    except ImportError:

        raise ImportError(
            "Error while importing Qt modules")
