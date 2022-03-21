#!/usr/bin/env python



from . import BaseItem

from . import FileUsdPainter
from . import FileUsdEditor







class Delegate (BaseItem.Delegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = FileUsdPainter.Item(theme)



    def createEditor (self, parent, option, index):

        editor = FileUsdEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode

        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)

        return editor

