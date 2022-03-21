#!/usr/bin/env python



from .. import tools
from .paintblock import (
    clear,
    label
)

from Qt import QtCore, QtGui
from . import BaseItem

from .. import Settings
UIGlobals = Settings.UIGlobals







class Item (BaseItem.Painter):


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

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        libraryImage = QtGui.QImage(":/icons/library.png")
        if self.hover:
            colorBackground = QtGui.QColor(self.theme.color.libraryHover)
            colorText = self.theme.color.kicker
            libraryImage = tools.recolor(libraryImage, self.theme.color.violet)

        else:
            colorBackground = QtGui.QColor(self.theme.color.libraryBackground)
            colorText = self.theme.color.text
            libraryImage = tools.recolor(libraryImage, self.theme.color.text)


        # BACKGROUND
        colorOutline = QtGui.QColor(self.theme.color.libraryOutline)
        self.painter.fillRect(self.option.rect, colorOutline)

        borderWidth = 1
        borderRect = QtCore.QRect(
            self.iconRect.x()      + borderWidth    ,
            self.iconRect.y()      + borderWidth    ,
            self.iconRect.width()  - borderWidth *2 ,
            self.iconRect.height() - borderWidth *2 )

        self.painter.fillRect(borderRect, colorBackground)


        # ICON
        offsetIcon = int((
            self.height - self.space*2 - libraryImage.height() )/2)

        iconPosition = QtCore.QPoint(
                self.pointX + self.space + offsetIcon,
                self.pointY + self.space + offsetIcon)

        self.painter.drawImage(iconPosition, libraryImage)


        # NAME
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(colorText) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        offsetText = 1
        self.painter.setFont( UIGlobals.IconDelegate.fontLibraryName )

        offsetName = libraryImage.width() + offsetIcon*2
        nameArea = QtCore.QRect(
            self.iconRect.x()      + offsetName ,
            self.iconRect.y()                   ,
            self.iconRect.width()  - offsetName ,
            self.iconRect.height()              )


        text = self.data.get("name")

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)
