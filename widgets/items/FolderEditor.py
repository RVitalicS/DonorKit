#!/usr/bin/env python


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from toolkit.core.naming import rule_Input

from . import BaseItem
from . import FolderPainter

from .. import Settings
UIGlobals = Settings.UIGlobals





class NameLine (QtWidgets.QLineEdit):


    def __init__ (self, parent):
        super(NameLine, self).__init__(parent)

        self.setProperty("background", "transparent")
        self.setProperty("border", "none")
        self.setProperty("textcolor", "on")
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setFont(UIGlobals.IconDelegate.fontFolderName)
        self.setContentsMargins( 0, 0, 0, 0)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.textChanged.connect(self.setName)


    def setName (self, text):

        text = rule_Input(text)
        self.setText(text)





class Editor (BaseItem.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = FolderPainter.Item(theme)
        self.Item.index = index

        self.inputFolderName = False



    def paintEvent (self, event):
        super(Editor, self).paintEvent(event)

        if not self.inputFolderName:
            dataType = self.Item.index.data(QtCore.Qt.EditRole).get("type", "")
            if dataType == "folderquery":
                self.inputFolderName = True

                self.iconName = NameLine(self)
                self.iconName.setGeometry(self.Item.folderNameArea)
                self.iconName.show()
                self.iconName.setFocus()



    def mouseReleaseEvent (self, event):

        if event.button() == QtCore.Qt.LeftButton:

            pointer = QtCore.QPoint(
                event.x(),
                event.y())

            if self.Item.linkArea.contains(pointer):
                self.link.emit(self.Item.index)
                self.repaint()
                return

            if self.Item.createFolderArea.contains(pointer):
                self.createFolderQuery.emit(self.Item.index)
                self.repaint()
                return

            if self.Item.iconRect.contains(pointer):
                self.clicked.emit(self.Item.index)
                return



    def keyPressEvent (self, event):
        super(Editor, self).keyReleaseEvent(event)

        if event.key() == QtCore.Qt.Key_Control:
            self.Item.controlMode = True
            self.repaint()



    def keyReleaseEvent (self, event):
        super(Editor, self).keyReleaseEvent(event)
        
        if event.key() == QtCore.Qt.Key_Control:
            self.Item.controlMode = False
            self.repaint()



    def leaveEvent (self, event):
        super(Editor, self).leaveEvent(event)

        if self.inputFolderName:
            self.inputFolderName = False

            self.createFolder.emit(
                self.Item.index,
                self.iconName.text())
