#!/usr/bin/env python



import os


from Qt import QtWidgets, QtCore

from . import IconPainter
from . import IconEditor







class Delegate (QtWidgets.QStyledItemDelegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent)

        self.theme = theme
        self.Icon = IconPainter.Icon(theme)



    def paint (self, painter, option, index):

        iconArea = self.parent().rectForIndex(index)

        self.Icon.pointer = QtCore.QPoint(
            iconArea.x() ,
            iconArea.y() )
        self.Icon.controlMode = self.parent().controlMode

        self.Icon.paint(painter, option, index)



    def sizeHint (self, option, index):

        self.Icon.index = index
        return  self.Icon.sizeHint()



    def createEditor (self, parent, option, index):

        editor = IconEditor.Editor(
                    option, index,
                    self.theme,
                    parent=parent )
        editor.Icon.controlMode = self.parent().controlMode

        editor.clicked.connect(self.clickAction)
        editor.createFolderQuery.connect(self.createFolderQuery)
        editor.createFolder.connect(self.createFolderAction)
        editor.folderLink.connect(self.folderLinkAction)
        editor.favoriteClicked.connect(self.favoriteAction)
        editor.leaveEditor.connect(self.leaveAcion)

        return editor



    def setModelData (self, editor, model, index):

        model.setData(
            index,
            index.data(QtCore.Qt.EditRole) )



    def editorEvent (self, event, model, option, index):

        if event.type() == QtCore.QEvent.MouseMove:

            self.parent().setCurrentIndex(index)
            self.parent().edit(index)

        return True



    def favoriteAction (self, index):

        self.parent().favoriteClickedSignal(index)



    def leaveAcion (self):

        self.setModelData(
            self.sender(),
            self.parent().model(),
            self.sender().Icon.index )

        self.closeEditor.emit(
            self.sender(),
            QtWidgets.QAbstractItemDelegate.NoHint )



    def clickAction (self, index):

        self.parent().iconClickedSignal(index)



    def createFolderQuery (self, index):
        
        self.leaveAcion()
        self.parent().createFolderQueryBridge(index)



    def createFolderAction (self, index, name):
        
        self.parent().createFolderBridge(index, name)



    def folderLinkAction (self, index):
        
        self.parent().folderLinkBridge(index)
