#!/usr/bin/env python

"""
"""

from widgets.items import BaseItem
from widgets.items import FolderPainter
from widgets.items import AssetUsdPainter


class Item (BaseItem.Painter, FolderPainter.Base, AssetUsdPainter.Base ):

    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        FolderPainter.Base.__init__(self)
        AssetUsdPainter.Base.__init__(self)

    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)
        if self.type in ["labelfolder", "labelasset", "labelmaterial" ]:
            self.paintLabel()
        elif self.type in ["folder", "folderquery"]:
            self.paintFolder()
        elif self.type == "plusfolder":
            self.paintPlus()
        elif self.type in ["usdasset", "usdmaterial"]:
            self.favorite = self.data.get("favorite", False)
            self.paintAssetUsd()
