#!/usr/bin/env python


from widgets import DonorWidget
from Katana import UI4

from toolkit.katana import actions





class DonorManager (
    DonorWidget.Make(UI4.Tabs.BaseTab) ):


    def __init__ (self, parent):
        super(DonorManager, self).__init__(parent)

        self.setWindowTitle("Donor Manager")
        self.setObjectName("DonorManager")


    def loadUsdFile (self, path):
        actions.loadUsdFile(path)





PluginRegistry = [("KatanaPanel", 2.0, "Donor Manager", DonorManager)]
