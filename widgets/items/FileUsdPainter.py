#!/usr/bin/env python

"""
"""

from widgets.items.BasePainterGeneral import *
from widgets.items.BasePainterUsd import *
from widgets.items import BaseItem
from widgets import Settings
from toolkit.ensure.QtCore import *

UIGlobals = Settings.UIGlobals


class Base (object):

    def __init__ (self):
        self.linkArea = QtCore.QRect()
        self.token = False
        self.tokenArea = QtCore.QRect()
        self.controlMode = False

    @label(UIGlobals.IconDelegate.fontCategory)
    @clear
    def paintLabel (self):
        pass

    @checked
    @token
    @name(hasCount=False)
    @size
    @published
    @division
    @icon
    @link
    @animation
    @preview
    @background
    @initialize
    @accent(status=False)
    def paintFileUsd (self):
        pass


class Item (BaseItem.Painter, Base):
    
    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        Base.__init__(self)
    
    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)
        if self.type == "labelasset":
            self.paintLabel()
        elif self.type == "usdfile":
            self.token = self.data.get("token", False)
            self.paintFileUsd()
