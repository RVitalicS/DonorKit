#!/usr/bin/env python

"""
"""

from widgets.items import BaseItem
from widgets.items import ColorPainter
from widgets.items import ColorEditor


class Delegate (BaseItem.Delegate):
    
    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = ColorPainter.Item(theme)
    
    def createEditor (self, parent, option, index):
        editor = ColorEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode
        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)
        editor.favoriteClicked.connect(self.favoriteAction)
        return editor
    
    def paint (self, painter, option, index):
        self.Item.controlMode = self.parent().controlMode
        super(Delegate, self).paint(painter, option, index)
    
    def favoriteAction (self, index):
        self.parent().favoriteClickedSignal(index)
