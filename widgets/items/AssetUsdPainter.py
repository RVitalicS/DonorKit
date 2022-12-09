#!/usr/bin/env python

"""
"""

from widgets.items.BasePainterGeneral import *
from widgets.items.BasePainterUsd import *
from toolkit.ensure.QtCore import *
from widgets.items import BaseItem
from widgets import Settings

UIGlobals = Settings.UIGlobals


class Base (object):
    
    def __init__ (self):
        self.linkArea = QtCore.QRect()
        self.favorite = False
        self.favoriteArea = QtCore.QRect()
        self.controlMode = False

    @label(UIGlobals.IconDelegate.fontCategory)
    @clear
    def paintLabel (self):
        pass

    @checked
    @favorite
    @name(hasCount=True)
    @status
    @published
    @division
    @icon
    @link
    @animation
    @preview
    @background
    @initialize
    @accent(status=True)
    def paintAssetUsd (self):
        pass


class Item (BaseItem.Painter, Base):

    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        Base.__init__(self)

    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)
        if self.type in ["labelasset", "labelmaterial"]:
            self.paintLabel()
        elif self.type in ["usdasset", "usdmaterial"]:
            self.favorite = self.data.get("favorite", False)
            self.paintAssetUsd()
