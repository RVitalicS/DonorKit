#!/usr/bin/env python


from toolbox.ensure.QtCore import *

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

            if self.Item.tokenArea.contains(pointer):
                self.tokenClicked.emit(self.Item.index)
                self.repaint()
                return

            if self.Item.iconRect.contains(pointer):
                self.clicked.emit(self.Item.index)
                return
