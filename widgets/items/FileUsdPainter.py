#!/usr/bin/env python



from .paintblock import (
    clear,
    label,
    background,
    usdInitialize,
    usdColorAccent,
    usdPreview,
    usdAnimation,
    usdIcon,
    usdName,
    checked
)

from . import BaseItem

from .. import Settings
UIGlobals = Settings.UIGlobals





class Base (object):



    @label(UIGlobals.IconDelegate.fontCategory)
    @clear
    def paintLabel (self):
        pass



    @checked
    @usdName(hasCount=False)
    @usdIcon
    @usdAnimation
    @usdPreview
    @background
    @usdInitialize
    @usdColorAccent(status=False)
    def paintFileUsd (self):
        pass





class Item (BaseItem.Painter, Base):


    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)


    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)

        if self.type == "labelasset":
            self.paintLabel()

        elif self.type == "asset":
            if self.data.get("type") == "usdfile":
                self.paintFileUsd()
