#!/usr/bin/env python

"""
"""

from widgets.items import BaseItem
from widgets.items import PopupEditor
from widgets.items import PopupPainter


class Delegate (BaseItem.Delegate):

    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = PopupPainter.Item(theme)

    def paint (self, painter, option, index):
        self.Item.paint(painter, option, index)

    def createEditor (self, parent, option, index):
        editor = PopupEditor.Editor(parent, index, self.theme)
        editor.leaveEditor.connect(self.leaveAction)
        return editor
