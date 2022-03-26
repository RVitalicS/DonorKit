#!/usr/bin/env python


from widgets import ManagerWidget
from Katana import UI4

from toolbox.katana import actions





class Manager (
    ManagerWidget.Make(UI4.Tabs.BaseTab) ):


    def __init__ (self, parent):
        super(Manager, self).__init__(parent)


    def loadUsdFile (self, path):
        actions.loadUsdFile(path)





PluginRegistry = [("KatanaPanel", 2.0, "Assets Manager", Manager)]
