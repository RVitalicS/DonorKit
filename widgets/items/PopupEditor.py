#!/usr/bin/env python



from . import BaseItem
from . import PopupPainter







class Editor (BaseItem.Editor):


    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent, index, theme)

        self.Item = PopupPainter.Item(theme)
        self.Item.index = index
