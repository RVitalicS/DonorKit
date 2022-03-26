#!/usr/bin/env python



from .BasePainterGeneral import (
    clear,
    label )

from .BasePainterUsd import (
    background,
    initialize,
    accent,
    preview,
    animation,
    icon,
    division,
    published,
    size,
    name,
    token,
    checked )

from toolbox.ensure.QtCore import *
from . import BaseItem

from .. import Settings
UIGlobals = Settings.UIGlobals





class Base (object):



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

        self.token = False
        self.tokenArea = QtCore.QRect()


    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)

        if self.type == "labelasset":
            self.paintLabel()

        elif self.type == "asset":
            if self.data.get("type") == "usdfile":
                self.token = self.data.get("token", False)
                self.paintFileUsd()
