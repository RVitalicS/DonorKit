#!/usr/bin/env python



from toolbox.ensure.QtCore import *

from . import BaseItem
from . import AssetUsdPainter







class Editor (BaseItem.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = AssetUsdPainter.Item(theme)
        self.Item.index = index



    def mouseReleaseEvent (self, event):

        if event.button() == QtCore.Qt.LeftButton:

            pointer = QtCore.QPoint(
                event.x(),
                event.y())

            if self.Item.favoriteArea.contains(pointer):
                self.favoriteClicked.emit(self.Item.index)
                self.repaint()
                return

            if self.Item.linkArea.contains(pointer):
                self.link.emit(self.Item.index)
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
