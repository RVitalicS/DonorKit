#!/usr/bin/env python


from widgets import ManagerWidget
from maya.app.general.mayaMixin import (
    MayaQWidgetDockableMixin )

from . import actions





class Manager (
    ManagerWidget.Make(MayaQWidgetDockableMixin) ):


    def __init__(self, parent):
        super(Manager, self).__init__(parent)
        

    def loadUsdFile (self, path):
        actions.loadUsdFile(path)





def show ():

    AssetManager = Manager(None)
    nameUI = AssetManager.objectName()+"WorkspaceControl"

    import maya.cmds as cmds
    if cmds.workspaceControl(nameUI, query=True, exists=True):
        cmds.workspaceControl(nameUI, edit=True, close=True)
        cmds.deleteUI(nameUI)

    AssetManager.show(dockable=True)
