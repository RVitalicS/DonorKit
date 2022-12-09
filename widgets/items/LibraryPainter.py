#!/usr/bin/env python

"""
"""

import toolkit.core.graphics as graphics
from widgets.items.BasePainterGeneral import clear
from widgets.items.BasePainterGeneral import label
from widgets.items import BaseItem
from widgets import Settings
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

UIGlobals = Settings.UIGlobals


class Item (BaseItem.Painter):
    
    def __init__ (self, theme):
        super(Item, self).__init__(theme)
        self.controlMode = False
        self.refreshArea = QtCore.QRect()
    
    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)
        if self.type in [ "labellibrary" ]:
            self.paintLabel()
        elif self.type == "library":
            self.paintLibrary()
    
    @label(UIGlobals.IconDelegate.fontLibraries)
    @clear
    def paintLabel (self):
        pass
    
    def paintLibrary (self):
        # BACKGROUND
        colorOutline = QtGui.QColor(self.theme.color.libraryOutline)
        self.painter.fillRect(self.option.rect, colorOutline)
        borderWidth = 1
        borderRect = QtCore.QRect(
            self.iconRect.x() + borderWidth,
            self.iconRect.y() + borderWidth,
            self.iconRect.width() - borderWidth *2,
            self.iconRect.height() - borderWidth *2)
        if self.hover:
            colorBackground = QtGui.QColor(self.theme.color.libraryHover)
        else:
            colorBackground = QtGui.QColor(self.theme.color.libraryBackground)
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillRect(borderRect, colorBackground)
        # ICON
        libraryImage = QtGui.QImage(":/icons/library.png")
        offsetIcon = int((
            self.height - self.space*2 - libraryImage.height())/2)
        iconPosition = QtCore.QPoint(
            self.pointX + self.space + offsetIcon,
            self.pointY + self.space + offsetIcon)
        if self.controlMode:
            refreshImage = QtGui.QImage(":/icons/librefresh.png")
            offsetArea = 10
            self.refreshArea = QtCore.QRect(
                iconPosition.x() - offsetArea,
                iconPosition.y() - offsetArea,
                refreshImage.width() + offsetArea * 2,
                refreshImage.height() + offsetArea * 2)
            deltaX = refreshImage.width() / 2 - libraryImage.width() / 2
            deltaY = refreshImage.height()/ 2 - libraryImage.height()/ 2
            iconPosition = QtCore.QPointF(
                iconPosition.x() - deltaX,
                iconPosition.y() - deltaY)
            drawImage = refreshImage
        else:
            self.refreshArea = QtCore.QRect(0,0,0,0)
            drawImage = libraryImage
        if self.hover:
            colorText = self.theme.color.kicker
            drawImage = graphics.recolor(drawImage, self.theme.color.violet)
        else:
            colorText = self.theme.color.text
            drawImage = graphics.recolor(drawImage, self.theme.color.text)
        self.painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.painter.drawImage(iconPosition, drawImage)
        # NAME
        self.painter.setPen(QtGui.QPen(
            QtGui.QBrush(QtGui.QColor(colorText)), 0,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.painter.setFont( UIGlobals.IconDelegate.fontLibraryName)
        offsetName = libraryImage.width() + offsetIcon*2
        nameArea = QtCore.QRect(
            self.iconRect.x() + offsetName, self.iconRect.y(),
            self.iconRect.width() - offsetName, self.iconRect.height())
        text = self.data.get("name")
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(QtCore.QRectF(nameArea), text, textOption)
