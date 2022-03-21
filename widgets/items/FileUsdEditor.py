#!/usr/bin/env python



from Qt import QtCore

from . import BaseItem
from . import FileUsdPainter







class Editor (BaseItem.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = FileUsdPainter.Item(theme)
        self.Item.index = index



    def mouseReleaseEvent (self, event):

        if event.button() == QtCore.Qt.LeftButton:

            pointer = QtCore.QPoint(
                event.x(),
                event.y())

            if self.Item.iconRect.contains(pointer):
                self.clicked.emit(self.Item.index)
                return
