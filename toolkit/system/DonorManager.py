#!/usr/bin/env python

"""
Asset Manager

PySide/PyQt UI code to run the asset manager as standalone application.
"""

import os
import sys

this = os.path.dirname(__file__)
tool = os.path.dirname(this)
root = os.path.dirname(tool)
if root not in sys.path:
    sys.path.append(root)

from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets import DonorWidget


class Donor (DonorWidget.Make(QtWidgets.QWidget)):
    """Create a standalone app version of the UI

    Keyword Arguments:
        parent: A QWidget parent to avoid untimely garbage collection
    """
    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super(Donor, self).__init__(parent=parent)

        # hide load option UI part
        item = self.UsdLoadOptions.loadLayout
        item.setEnabled(False)
        self.UsdLoadOptions.mainLayout.removeItem(item)
        self.UsdLoadOptions.loadButton.hide()

        # set the app name and icon
        self.setWindowTitle("Donor Manager")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(
                root, "install", "icons", "store.svg" ) ))
        self.setObjectName("DonorManager")

        # add hotkey to close app
        self.exit = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_Q), self)
        self.exit.activated.connect(self.close)


# run the app if it's entry point
if __name__ == "__main__":
    application = QtWidgets.QApplication([])
    DonorManager = Donor()
    DonorManager.show()
    application.exec_()
