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
        editor.Item.controlMode = self.parent().controlMode

        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)

        editor.refresh.connect(self.refreshAction)

        return editor



    def paint (self, painter, option, index):

        self.Item.controlMode = self.parent().controlMode
        super(Delegate, self).paint(painter, option, index)



    def refreshAction (self, index):
        
        self.parent().refreshLibrarySignal(index)
