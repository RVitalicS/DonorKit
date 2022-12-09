#!/usr/bin/env python

"""
Asset Manager

The UI plug-in to add to Katana Tabs.
"""

from widgets import DonorWidget
from Katana import UI4
from toolkit.katana import actions


class DonorManager (DonorWidget.Make(UI4.Tabs.BaseTab)):
    """Create a Katana version of the UI
    and override methods to use scripts
    that is specific for this app

    Arguments:
        parent: A parent widget
    """
    def __init__ (self, parent):
        super(DonorManager, self).__init__(parent)
        self.setWindowTitle("Donor Manager")
        self.setObjectName("DonorManager")

    def loadUsdFile (self, path):
        actions.loadUsdFile(path)

    def loadMaterial (self, path):
        actions.loadMaterial(path)

    def loadColor (self, data):
        actions.loadColor(data)


# register the class as an KatanaPanel plug-in type
PluginRegistry = [("KatanaPanel", 2.0, "Donor Manager", DonorManager)]
