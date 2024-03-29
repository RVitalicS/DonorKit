#!/usr/bin/env python

"""
"""

from widgets.items import DirectoryPainter
from widgets.items import DirectoryEditor
from widgets.items import FolderDelegate
from widgets.items import AssetUsdDelegate


class Delegate (FolderDelegate.Delegate, AssetUsdDelegate.Delegate):

    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = DirectoryPainter.Item(theme)

    def createEditor (self, parent, option, index):
        editor = DirectoryEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode
        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAction)
        editor.link.connect(self.linkAction)
        editor.createFolderQuery.connect(self.createFolderQuery)
        editor.createFolder.connect(self.createFolderAction)
        editor.favoriteClicked.connect(self.favoriteAction)
        return editor
