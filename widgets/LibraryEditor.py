#!/usr/bin/env python



from Qt import QtCore

from . import ItemBase
from . import LibraryPainter







class Editor (ItemBase.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = LibraryPainter.Item(theme)
        self.Item.index = index



    def mouseReleaseEvent (self, event):

        if event.button() == QtCore.Qt.LeftButton:

            pointer = QtCore.QPoint(
                event.x(),
                event.y())

            if self.Item.iconRect.contains(pointer):
                self.clicked.emit(self.Item.index)
