#!/usr/bin/env python


from widgets import DonorWidget

from maya.app.general.mayaMixin import (
    MayaQWidgetDockableMixin )
import maya.cmds as cmds

from . import actions





class Donor (
    DonorWidget.Make(MayaQWidgetDockableMixin) ):


    def __init__(self, parent=None):
        super(Donor, self).__init__(parent=parent)

        self.setWindowTitle("Donor Manager")
        self.setObjectName("DonorManager")


    def loadUsdFile (self, path):
        actions.loadUsdFile(path)


    def loadColor (self, data):
        actions.loadColor(data)





def show ():

    DonorManager = Donor()
    nameUI = DonorManager.objectName()+"WorkspaceControl"

    if cmds.workspaceControl(nameUI, query=True, exists=True):
        cmds.workspaceControl(nameUI, edit=True, close=True)
        cmds.deleteUI(nameUI)

    DonorManager.show(dockable=True)
