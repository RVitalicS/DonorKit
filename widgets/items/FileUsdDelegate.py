#!/usr/bin/env python

"""
"""

from widgets.items import BaseItem
from widgets.items import FileUsdPainter
from widgets.items import FileUsdEditor


class Delegate (BaseItem.Delegate):

    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = FileUsdPainter.Item(theme)

    def createEditor (self, parent, option, index):
        editor = FileUsdEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode
        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)
        editor.link.connect(self.linkAction)
        editor.tokenClicked.connect(self.tokenAction)
        return editor

    def tokenAction (self, index):
        self.parent().tokenClickedSignal(index)

    def linkAction (self, index):
        self.parent().linkBridge(index)
