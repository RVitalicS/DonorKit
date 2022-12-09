#!/usr/bin/env python

"""
"""

from widgets.items.BasePainterGeneral import *
from widgets.items.BasePainterColor import *
from widgets.items import BaseItem
from widgets import Settings
from toolkit.ensure.QtCore import *

UIGlobals = Settings.UIGlobals


class Base (object):
    def __init__ (self):
        self.favorite = False
        self.favoriteArea = QtCore.QRect()
        self.controlMode = False

    @label(UIGlobals.IconDelegate.fontCategory)
    @clear
    def paintLabel (self):
        pass

    @hover
    @name
    @favorite
    @infoguide
    @divisionguide
    @background(fill=False)
    @initialize
    def paintColorGuide (self):
        pass


class Item (BaseItem.Painter, Base):
    
    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        Base.__init__(self)
    
    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)
        if self.type == "labelasset":
            self.paintLabel()
        elif self.type == "colorguide":
            self.favorite = self.data.get("favorite", False)
            self.paintColorGuide()
