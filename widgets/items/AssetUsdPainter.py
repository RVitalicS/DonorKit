#!/usr/bin/env python



from .BasePainterGeneral import (
    initialize,
    checked,
    clear,
    label )

from .BasePainterUsd import (
    background,
    accent,
    preview,
    animation,
    link,
    icon,
    division,
    published,
    status,
    name,
    favorite )


from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from . import BaseItem

from .. import Settings
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

        if self.type == "labelasset":
            self.paintLabel()

        elif self.type == "usdasset":
            self.favorite = self.data.get("favorite", False)
            self.paintAssetUsd()
