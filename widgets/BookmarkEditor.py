#!/usr/bin/env python



from Qt import QtWidgets, QtCore, QtGui

from . import ItemBase
from . import BookmarkPainter







class Editor (ItemBase.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = BookmarkPainter.Item(theme)
        self.Item.index = index
