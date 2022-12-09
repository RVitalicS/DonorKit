#!/usr/bin/env python

"""
Asset Manager

The dockable UI plug-in for Maya.
"""

from widgets import DonorWidget
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as mayaCommand
from toolkit.maya import actions


class Donor (DonorWidget.Make(MayaQWidgetDockableMixin)):
    """Create a Maya version of the UI
    and override methods to use scripts
    that is specific for this app

    Keyword Arguments:
        parent: A parent widget
    """
    def __init__(self, parent=None):
        super(Donor, self).__init__(parent=parent)
        self.setWindowTitle("Donor Manager")
        self.setObjectName("DonorManager")

    def loadUsdFile (self, path):
        actions.loadUsdFile(path)

    def loadMaterial (self, path):
        actions.loadMaterial(path)

    def loadColor (self, data):
        actions.loadColor(data)


def show () -> None:
    """Show the Asset Manager widget"""
    DonorManager = Donor()
    nameUI = DonorManager.objectName()+"WorkspaceControl"
    if mayaCommand.workspaceControl(nameUI, query=True, exists=True):
        mayaCommand.workspaceControl(nameUI, edit=True, close=True)
        mayaCommand.deleteUI(nameUI)
    DonorManager.show(dockable=True)
