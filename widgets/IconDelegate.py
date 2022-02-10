#!/usr/bin/env python



import os


from Qt import QtWidgets, QtCore

from . import IconPainter
from . import IconEditor







class Delegate (QtWidgets.QStyledItemDelegate):


    def __init__ (self, parent):
        super(Delegate, self).__init__(parent)

        self.Icon = IconPainter.Icon()



    def paint (self, painter, option, index):

        self.Icon.paint(painter, option, index)



    def sizeHint (self, option, index):

        self.Icon.index = index
        return  self.Icon.sizeHint()



    def createEditor (self, parent, option, index):

        editor = IconEditor.Editor(
                    option, index,
                    parent=parent )

        editor.clicked.connect(self.clickAction)
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
