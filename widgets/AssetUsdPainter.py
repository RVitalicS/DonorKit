#!/usr/bin/env python



from . import tools
from .paintblock import (
    clear,
    label,
    background,
    usdInitialize,
    usdColorAccent,
    usdPreview,
    usdAnimation,
    usdLink,
    usdIcon,
    usdStatus,
    usdName,
    favorite,
    checked
)


from Qt import QtCore, QtGui
from . import ItemBase

from . import Settings
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
    @usdName(hasCount=True)
    @usdStatus
    @usdIcon
    @usdLink
    @usdAnimation
    @usdPreview
    @background
    @usdInitialize
    @usdColorAccent(status=True)
    def paintAssetUsd (self):
        pass





class Item (ItemBase.Painter, Base):


    def __init__ (self, theme):
        ItemBase.Painter.__init__(self, theme)
        Base.__init__(self)


    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)

        if self.type == "labelasset":
            self.paintLabel()

        elif self.type == "asset":
            self.favorite = self.data.get("favorite", False)
            self.paintAssetUsd()