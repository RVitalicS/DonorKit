#!/usr/bin/env python


import os
import sys

this = os.path.dirname(__file__)
toolbox = os.path.dirname(this)
root = os.path.dirname(toolbox)

if root not in sys.path:
    sys.path.append(root)


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from widgets import DonorWidget
from toolkit.system import actions





class Donor (
    DonorWidget.Make(QtWidgets.QWidget) ):


    def __init__(self, parent=None):
        super(Donor, self).__init__(parent=parent)

        item = self.UsdLoadOptions.loadLayout
        item.setEnabled(False)
        self.UsdLoadOptions.mainLayout.removeItem(item)
        self.UsdLoadOptions.loadButton.hide()

        self.setWindowTitle("Donor Manager")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(
                root, "install", "icons", "DonorManager.svg" ) ))
        self.setObjectName("DonorManager")


    def loadUsdFile (self, path):
        actions.loadUsdFile(path)


    def loadColor (self, data):
        actions.loadColor(data)





if __name__ == "__main__":

    application = QtWidgets.QApplication([])
    DonorManager = Donor()
    DonorManager.show()
    application.exec_()
