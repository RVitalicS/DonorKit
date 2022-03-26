#!/usr/bin/env python


import os
import sys

thisDir = os.path.dirname(__file__)
toolboxDir = os.path.dirname(thisDir)
rootDir = os.path.dirname(toolboxDir)

if rootDir not in sys.path:
    sys.path.append(rootDir)


from toolbox.ensure.QtWidgets import *
from toolbox.ensure.QtCore import *

from widgets import ManagerWidget
from toolbox.system import actions





class Manager (
    ManagerWidget.Make(QtWidgets.QWidget) ):


    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)

        item = self.UsdLoadOptions.loadLayout
        item.setEnabled(False)
        self.UsdLoadOptions.mainLayout.removeItem(item)
        self.UsdLoadOptions.loadButton.hide()


    def loadUsdFile (self, path):
        actions.loadUsdFile(path)





if __name__ == "__main__":

    application = QtWidgets.QApplication([])
    widget = Manager()
    widget.show()
    application.exec_()
