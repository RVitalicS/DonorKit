#!/usr/bin/env python

"""
"""

from toolkit.ensure.QtCore import *
from widgets.items import DirectoryPainter
from widgets.items import FolderEditor
from widgets.items import AssetUsdEditor


class Editor (FolderEditor.Editor, AssetUsdEditor.Editor):
    
    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)
        self.Item = DirectoryPainter.Item(theme)
        self.Item.index = index
    
    def mouseReleaseEvent (self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pointer = QtCore.QPoint(event.x(), event.y())
            if self.Item.favoriteArea.contains(pointer):
                self.favoriteClicked.emit(self.Item.index)
                self.repaint()
                return
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
