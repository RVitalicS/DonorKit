#!/usr/bin/env python



from . import BaseItem
from . import LibraryPainter
from . import LibraryEditor







class Delegate (BaseItem.Delegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = LibraryPainter.Item(theme)



    def createEditor (self, parent, option, index):

        editor = LibraryEditor.Editor(parent, index, self.theme)

        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)

        return editor
