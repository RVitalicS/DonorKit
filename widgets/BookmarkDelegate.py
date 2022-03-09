#!/usr/bin/env python



from . import ItemBase

from . import BookmarkEditor
from . import BookmarkPainter







class Delegate (ItemBase.Delegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)

        self.Item = BookmarkPainter.Item(theme)



    def paint (self, painter, option, index):

        self.Item.paint(painter, option, index)



    def createEditor (self, parent, option, index):

        editor = BookmarkEditor.Editor(parent, index, self.theme)
        editor.leaveEditor.connect(self.leaveAcion)

        return editor
