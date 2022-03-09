#!/usr/bin/env python



from Qt import QtWidgets, QtCore

from . import ItemBase

from . import FolderPainter
from . import FolderEditor







class Delegate (ItemBase.Delegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = FolderPainter.Item(theme)



    def createEditor (self, parent, option, index):

        editor = FolderEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode

        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAcion)
        
        editor.createFolderQuery.connect(self.createFolderQuery)
        editor.createFolder.connect(self.createFolderAction)
        editor.link.connect(self.linkAction)

        return editor



    def createFolderQuery (self, index):
        
        self.leaveAcion()
        self.parent().createFolderQueryBridge(index)



    def createFolderAction (self, index, name):
        
        self.parent().createFolderBridge(index, name)



    def linkAction (self, index):
        
        self.parent().linkBridge(index)
