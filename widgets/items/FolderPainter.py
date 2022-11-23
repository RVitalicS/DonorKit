#!/usr/bin/env python



import toolkit.core.calculate
import toolkit.core.graphics

from .BasePainterGeneral import (
    clear,
    label )

from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from . import BaseItem

from .. import Settings
UIGlobals = Settings.UIGlobals





class Base (object):


    def __init__ (self):

        self.folderNameArea  = QtCore.QRect()
        self.createFolderArea = QtCore.QRect()

        self.linkArea = QtCore.QRect()

        self.controlMode = False



    @label(UIGlobals.IconDelegate.fontCategory)
    @clear
    def paintLabel (self):
        pass



    def paintFolder (self):

        # BACKGROUND
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.hover:
            color = QtGui.QColor(self.theme.color.iconHighlight)
        else:
            color = QtGui.QColor(self.theme.color.iconBackground)
        self.painter.fillRect(self.iconRect, color)


        # ICON
        if self.type == "foldercolors":
            folderImage = QtGui.QImage(":/icons/colors.png")
        else:
            folderImage = QtGui.QImage(":/icons/folder.png")

        folderOffset = int((
            self.height - self.space*2 - folderImage.height() )/2)

        folderPosition = QtCore.QPoint(
                self.iconRect.x() + folderOffset,
                self.iconRect.y() + folderOffset)
        
        folderImage = toolkit.core.graphics.recolor(
            folderImage, self.theme.color.folderColor)
        self.painter.drawImage(folderPosition, folderImage)


        # NAME
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(self.theme.color.text) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        offsetText = 1
        fontName = UIGlobals.IconDelegate.fontFolderName
        self.painter.setFont(fontName)

        offsetName = folderImage.width() + folderOffset*2
        self.folderNameArea = QtCore.QRect(
            self.pointX + self.space + offsetName   ,
            self.pointY + self.space ,
            self.width  - self.space*2 - offsetName ,
            int(self.height/2) - int(self.space/2) -offsetText )


        textName = self.data.get("name")

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom)

        nameWidth = toolkit.core.calculate.stringWidth(textName, fontName)
        nameSpace = self.folderNameArea.width() - self.space

        if nameWidth > nameSpace:

            while nameWidth > nameSpace:
                if not textName: break

                textName = textName[:-1]
                nameWidth = toolkit.core.calculate.stringWidth(
                    textName + "...", fontName)

            textName += "..."

        self.painter.drawText(
            QtCore.QRectF(self.folderNameArea),
            textName,
            textOption)


        # ITEMS
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(self.theme.color.textlock) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        self.painter.setFont( UIGlobals.IconDelegate.fontFolderItems )

        offsetName = folderImage.width() + folderOffset*2
        countArea = QtCore.QRect(
            self.pointX + self.space + offsetName   ,
            self.pointY + int(self.height/2) +offsetText ,
            self.width  - self.space*2 - offsetName ,
            int(self.height/2) )


        count = self.data.get("items")
        if count == 1:
            text = "1 item"
        elif count > 1:
            text = "{} items".format(count)
        else:
            text = "empty"

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        self.painter.drawText(
            QtCore.QRectF(countArea),
            text,
            textOption)


        # LINK
        if self.hover and self.controlMode and textName != "":

            linkImage = QtGui.QImage(":/icons/linkarrow.png")
            linkImage = toolkit.core.graphics.recolor(
                linkImage, self.theme.color.kicker, opacity=0.25)

            linkOffset = linkImage.width() + UIGlobals.IconDelegate.offsetLink

            linkPosition = QtCore.QPoint(
                    self.iconRect.x() + self.iconRect.width()  - linkOffset,
                    self.iconRect.y() + self.iconRect.height() - linkOffset)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(linkPosition, linkImage)

            self.linkArea = QtCore.QRect(
                linkPosition.x() ,
                linkPosition.y() ,
                linkImage.width() ,
                linkImage.height() )



    def paintPlus (self):

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        libraryImage = QtGui.QImage(":/icons/plus.png")

        offsetIcon = int((
            self.height - self.space*2 - libraryImage.height() )/2)

        iconPosition = QtCore.QPoint(
                self.pointX + self.space + offsetIcon,
                self.pointY + self.space + offsetIcon)

        self.createFolderArea = QtCore.QRect(
            iconPosition.x() ,
            iconPosition.y() ,
            libraryImage.width() ,
            libraryImage.height() )

        if self.createFolderArea.contains(self.pointer):
            libraryImage = toolkit.core.graphics.recolor(
                libraryImage, self.theme.color.plusHover)
        else:
            libraryImage = toolkit.core.graphics.recolor(
                libraryImage, self.theme.color.plusColor)

        self.painter.drawImage(iconPosition, libraryImage)






class Item (BaseItem.Painter, Base):


    def __init__ (self, theme):
        BaseItem.Painter.__init__(self, theme)
        Base.__init__(self)


    def paint (self, painter, option, index):
        super(Item, self).paint(painter, option, index)

        if self.type == "labelfolder":
            self.paintLabel()

        elif self.type in [
                "folder"      ,
                "folderquery",
                "foldercolors" ]:
            self.paintFolder()

        elif self.type == "plusfolder":
            self.paintPlus()
