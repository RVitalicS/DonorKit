#!/usr/bin/env python

"""
Asset Manager

The dockable UI plug-in for Maya.
"""

from widgets import DonorWidget
import inspect
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as mayaCommand
from toolkit.maya import actions

MIXIN_WIDGET = None


class Donor (DonorWidget.Make(MayaQWidgetDockableMixin)):
    """Create a Maya version of the UI
    and override methods to use scripts
    that is specific for this app"""

    def __init__(self, *args, **kwargs):
        super(Donor, self).__init__(*args, **kwargs)
        self.setWindowTitle("Donor Manager")
        self.setObjectName("DonorManager")

    def loadUsdFile (self, path):
        actions.loadUsdFile(path)

    def loadMaterial (self, path):
        actions.loadMaterial(path)

    def loadColor (self, data):
        actions.loadColor(data)


def show (restore=False):
    """Create new UI or restore it on startup"""
    global MIXIN_WIDGET

    # do not setup in batch mode
    if mayaCommand.about(batch=True):
        return

    # create a widget for the first time
    if MIXIN_WIDGET is None:
        MIXIN_WIDGET = Donor()

    # restore the workspace control that has already been created
    name_ui = MIXIN_WIDGET.objectName() + "WorkspaceControl"
    if mayaCommand.workspaceControl(name_ui, query=True, exists=True):
        if restore is True:
            raised = mayaCommand.workspaceControl(name_ui, query=True, r=True)
            mayaCommand.deleteUI(name_ui)
            if raised is True:
                show()
        else:
            mayaCommand.workspaceControl(name_ui, edit=True, restore=True)

    # initiate the workspace control with the deferred script
    else:
        module = inspect.getmodule(MIXIN_WIDGET).__name__
        script_show = "\n".join([
            'import {0}'.format(module),
            'import maya.cmds as cmds',
            'cmds.evalDeferred("{0}.show(restore=True)")'.format(module)])
        MIXIN_WIDGET.show(
            dockable=True, loadImmediately=False,
            retain=True, visible=False, uiScript=script_show)
