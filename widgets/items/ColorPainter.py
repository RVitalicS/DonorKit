#!/usr/bin/env python



from .BasePainterGeneral import (
    initialize,
    clear,
    label)

from .BasePainterColor import (
    divisionguide,
    background,
    infocolor,
    favorite,
    hover,
    name )

from toolkit.ensure.QtCore import *
from . import BaseItem

from .. import Settings
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
    @infocolor
    @divisionguide
    @background(fill=True)
    @initialize
    def paintColor (self):
        pass





class Item (BaseItem.Painter, Base):


    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        Base.__init__(self)


    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)

        if self.type == "labelasset":
            self.paintLabel()

        elif self.type == "color":
            self.favorite = self.data.get("favorite", False)
            self.paintColor()
