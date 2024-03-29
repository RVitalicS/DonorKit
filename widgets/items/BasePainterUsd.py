#!/usr/bin/env python

"""
"""

import toolkit.core.calculate as calculate
import toolkit.core.graphics as graphics
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets import Settings

UIGlobals = Settings.UIGlobals


def token (function):
    def wrapped (self):
        function(self)
        if self.token or self.hover:
            image = QtGui.QImage(":/icons/check.png")
            offset = UIGlobals.IconDelegate.space
            position = QtCore.QPoint(
                self.iconRect.x() + self.iconRect.width() - image.width() - offset,
                self.iconRect.y() + offset)
            self.tokenArea = QtCore.QRect(
                position.x(),
                position.y(),
                image.width(),
                image.height())
            if self.token:
                image = graphics.recolor(image, self.theme.color.violet)
            else:
                image = graphics.recolor(
                    image, self.getOverlayHex(self.tokenArea), opacity=0.25)
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(position, image)
    return wrapped


def favorite (function):
    def wrapped (self):
        function(self)
        if self.hover or self.controlMode:
            image = QtGui.QImage(":/icons/star.png")
            offset = UIGlobals.IconDelegate.space
            position = QtCore.QPoint(
                self.iconRect.x() + self.iconRect.width() - image.width() - offset,
                self.iconRect.y() + offset)
            self.favoriteArea = QtCore.QRect(
                position.x(), position.y(),
                image.width(), image.height())
            if self.favorite:
                image = graphics.recolor(image, self.theme.color.iconFavorite)
            else:
                image = graphics.recolor(
                    image, self.getOverlayHex(self.favoriteArea), opacity=0.25)
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(position, image)
    return wrapped


def background (function):
    def wrapped (self):
        function(self)
        if self.hover:
            color = QtGui.QColor(self.theme.color.iconOutlineHover)
        else:
            color = QtGui.QColor(self.theme.color.iconOutline)
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillRect(self.option.rect, color)
        thickness = 1
        shape = QtCore.QRect(
            self.iconRect.x() + thickness,
            self.iconRect.y() + thickness,
            self.iconRect.width() - thickness*2,
            self.iconRect.height() - thickness*2)
        outlinePath = QtGui.QPainterPath()
        outlinePath.addRoundedRect(
            QtCore.QRectF(shape), self.radius, self.radius)
        if self.hover:
            color = QtGui.QColor(self.theme.color.iconHighlight)
        else:
            color = QtGui.QColor(self.theme.color.iconBackground)
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillPath(outlinePath, QtGui.QBrush(color))
        clearBackground = QtCore.QRect(
            self.pointX, self.pointY, self.width,
            self.previewHeight + self.space)
        self.previewColor = QtGui.QColor(self.theme.color.iconSpace)
        self.painter.fillRect(clearBackground, self.previewColor)
    return wrapped


def accent (status=True):
    def decorated (function):
        def wrapped (self):
            function(self)
            if status:
                text = self.data.get("status")
                color = self.theme.color.statusWIP
                if text == "Final":
                    color = self.theme.color.statusFinal
                elif text == "Completed":
                    color = self.theme.color.statusCompleted
                elif text == "Revise":
                    color = self.theme.color.statusRevise
                elif text == "Pending Review":
                    color = self.theme.color.statusPendingReview
            else:
                color = self.theme.color.textlock
            self.accentColor = QtGui.QColor(color)
        return wrapped
    return decorated


def preview (function):
    def wrapped (self):
        function(self)
        previewList = self.data.get("previews")
        previewCount = len(previewList)
        if previewCount > 0:
            previewX = float(self.iconRect.x())
            pointerX = float(self.pointer.x())
            rightX = float(self.iconRect.x() + self.iconRect.width())
            step = self.iconRect.width()/previewCount
            index = 0
            while pointerX > previewX+step < rightX:
                previewX += step
                index += 1
                if index == previewCount-1:
                    break
            previewPath = previewList[index]
            previewImport = QtGui.QImage(previewPath)
            self.previewImage = previewImport.scaledToWidth(
                self.iconRect.width(),
                QtCore.Qt.SmoothTransformation)
            previewY = (
                self.pointY + self.space + self.previewHeight - self.previewImage.height())
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(
                QtCore.QPoint(self.iconRect.x(), previewY), self.previewImage)
    return wrapped


def animation (function):
    def wrapped (self):
        function(self)
        textAnimation = self.data.get("animation")
        if textAnimation:
            textAnimation = textAnimation.replace("_", " ")
            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            fontAnimation = UIGlobals.IconDelegate.Animation.font
            self.painter.setFont(fontAnimation)
            self.painter.setPen( QtGui.QColor(self.theme.color.paper))
            offsetTag = UIGlobals.IconDelegate.Animation.offset
            spaceTag = UIGlobals.IconDelegate.Animation.space
            heightTag = UIGlobals.IconDelegate.Animation.height
            radiusTag = int(round(heightTag/2))
            animationWidth = calculate.stringWidth(textAnimation, fontAnimation)
            spaceAnimation = self.iconRect.width() - spaceTag - offsetTag*2
            if animationWidth > spaceAnimation:
                while animationWidth > spaceAnimation:
                    if not textAnimation: break
                    textAnimation = textAnimation[:-1]
                    animationWidth = calculate.stringWidth(
                        textAnimation + "...", fontAnimation)
                textAnimation += "..."
            tagArea = QtCore.QRect(
                self.iconRect.x() + offsetTag,
                self.iconRect.y() + offsetTag,
                animationWidth + spaceTag, heightTag)
            path = QtGui.QPainterPath()
            path.addRoundedRect(
                QtCore.QRectF(tagArea), radiusTag, radiusTag)
            brush = QtGui.QBrush( QtGui.QColor(self.theme.color.iconAnimation))
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.fillPath(path, brush)
            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(QtCore.QRectF(tagArea), textAnimation, textOption)
    return wrapped


def link (function):
    def wrapped (self):
        function(self)
        if self.hover and self.controlMode:
            linkImage = QtGui.QImage(":/icons/linkarrow.png")
            linkOffset = linkImage.width() + self.space
            linkPosition = QtCore.QPoint(
                self.iconRect.x() + self.iconRect.width() - linkOffset,
                self.iconRect.y() + self.previewHeight - linkOffset)
            self.linkArea = QtCore.QRect(
                linkPosition.x(), linkPosition.y(),
                linkImage.width(), linkImage.height())
            linkImage = graphics.recolor(
                linkImage, self.getOverlayHex(self.linkArea), opacity=0.25)
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(linkPosition, linkImage)
    return wrapped


def icon (function):
    def wrapped (self):
        function(self)
        typeImage = QtGui.QImage(":/icons/typeusd.png")
        offsetIcon = 0
        if self.iconSize == 1:
            iconPosition = QtCore.QPoint(
                self.labelArea.x() + self.labelArea.width() - typeImage.width(),
                self.labelArea.y() + offsetIcon)
        else:
            iconPosition = QtCore.QPoint(
                self.labelArea.x(), self.labelArea.y() + offsetIcon)
            self.shiftName += typeImage.width()
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.drawImage(iconPosition, typeImage)
        self.spaceName -= typeImage.width()
    return wrapped


def division (function):
    def wrapped (self):
        function(self)
        statusHeight = UIGlobals.Browser.Icon.Asset.infoHeight
        if self.iconSize == 1:
            halfInfoWidth = int(self.labelArea.width()/2)
            self.leftInfoArea = QtCore.QRect(
                self.labelArea.x(),
                self.labelArea.y() + self.labelArea.height() - statusHeight,
                halfInfoWidth, statusHeight)
        elif self.iconSize == 2:
            halfInfoWidth = int(((self.labelArea.width() - self.space*4)/2)/2)
            self.leftInfoArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width() - halfInfoWidth*2,
                self.labelArea.y() + self.labelArea.height() - statusHeight,
                halfInfoWidth, statusHeight)
            self.spaceName -= halfInfoWidth*2 + self.space*2
        else:
            halfInfoWidth = int(((self.labelArea.width() - self.space*8)/3)/2)
            self.leftInfoArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width() - halfInfoWidth*2,
                self.labelArea.y() + self.labelArea.height() - statusHeight,
                halfInfoWidth, statusHeight)
            self.spaceName -= halfInfoWidth*2 + self.space*2
        self.rightInfoArea = QtCore.QRect(
            self.leftInfoArea.x() + halfInfoWidth,
            self.leftInfoArea.y(),
            halfInfoWidth,
            self.leftInfoArea.height())
    return wrapped


def published (function):
    def wrapped (self):
        function(self)
        offsetPublished = UIGlobals.Browser.Icon.Asset.infoLabel
        dateArea = QtCore.QRect(
            self.leftInfoArea.x(), self.leftInfoArea.y() + offsetPublished,
            self.leftInfoArea.width(), self.leftInfoArea.height() - offsetPublished)
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel)
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.painter.setPen( QtGui.QColor(self.theme.color.textlock))
        self.painter.drawText(
            QtCore.QRectF(self.leftInfoArea), "Published", textOption)
        self.painter.setPen( QtGui.QColor(self.theme.color.text))
        self.painter.drawText(
            QtCore.QRectF(dateArea), self.data.get("published"), textOption)
    return wrapped


def status (function):
    def wrapped (self):
        function(self)
        # label
        self.painter.setPen( QtGui.QColor(self.theme.color.textlock))
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel)
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(self.rightInfoArea), "STATUS", textOption)
        # button rect
        offsetButton = UIGlobals.Browser.Icon.Asset.infoLabel + 2
        buttonArea = QtCore.QRect(
            self.rightInfoArea.x(), self.rightInfoArea.y() + offsetButton,
            self.rightInfoArea.width(), self.rightInfoArea.height() - offsetButton)
        path = QtGui.QPainterPath()
        path.addRoundedRect(
            QtCore.QRectF(buttonArea),
            UIGlobals.IconDelegate.radiusStatus, 
            UIGlobals.IconDelegate.radiusStatus)
        brush = QtGui.QBrush(self.accentColor)
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillPath(path, brush)
        # status text
        fontText = UIGlobals.IconDelegate.fontAssetStatus
        self.painter.setPen( QtGui.QColor(self.theme.color.white))
        self.painter.setFont( fontText)
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        text = self.data.get("status")
        textWidth = calculate.stringWidth(text, fontText)
        textMargin = 3
        availableWidth = buttonArea.width() - textMargin*2
        addDots = False
        while textWidth > availableWidth:
            text = text[:-1]
            textWidth = calculate.stringWidth(
                text+"...", fontText)
            addDots = True
        if addDots:
            text += "..."
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(buttonArea),
            text,
            textOption)
    return wrapped


def size (function):
    def wrapped (self):
        function(self)
        # button rect
        offsetSize = (
            UIGlobals.Browser.Icon.Asset.infoLabel + 0)
        sizeArea = QtCore.QRect(
            self.rightInfoArea.x(),
            self.rightInfoArea.y() + offsetSize,
            self.rightInfoArea.width(),
            self.rightInfoArea.height() - offsetSize)
        # label
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.painter.setPen( QtGui.QColor(self.theme.color.textlock))
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel)
        self.painter.drawText(
            QtCore.QRectF(self.rightInfoArea), "SIZE", textOption)
        # size text
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.painter.setPen( QtGui.QColor(self.theme.color.kicker))
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetSize)
        self.painter.drawText(
            QtCore.QRectF(sizeArea), self.data.get("size") + " MB", textOption)
    return wrapped


def name (hasCount=True):
    def decorated (function):
        def wrapped (self):
            function(self)
            # name
            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            fontName = UIGlobals.IconDelegate.fontAssetName
            self.painter.setFont(fontName)
            if self.hover or self.checked == 1:
                self.painter.setPen( QtGui.QColor(self.theme.color.kicker))
            else:
                self.painter.setPen( QtGui.QColor(self.theme.color.text))
            offsetName = -1
            if self.iconSize == 1:
                offsetName = 0
            self.spaceName -= self.space
            if self.iconSize == 1:
                nameArea = QtCore.QRect(
                    self.labelArea.x(), self.labelArea.y() + offsetName,
                    self.spaceName, self.labelArea.height() - offsetName)
            else:
                nameArea = QtCore.QRect(
                    self.labelArea.x() + self.shiftName + self.space*2,
                    self.labelArea.y() + offsetName,
                    self.spaceName, self.labelArea.height() - offsetName)
            textName = self.data.get("name")
            textName = textName.replace("_", " ")
            nameWidth = calculate.stringWidth(textName, fontName)
            spaceVariant = self.spaceName - nameWidth
            if nameWidth > self.spaceName:
                while nameWidth > self.spaceName:
                    if not textName: break
                    textName = textName[:-1]
                    nameWidth = calculate.stringWidth(
                        textName + "...", fontName)
                textName += "..."
            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(nameArea), textName, textOption)
            # variant
            variant = self.data.get("variant")
            if variant and spaceVariant > self.space:
                offsetPixel = 1
                variantArea = QtCore.QRect(
                    nameArea.x() + nameWidth + offsetPixel, nameArea.y(),
                    nameArea.width() - nameWidth - offsetPixel, nameArea.height())
                textVariant = " {}".format(variant)
                textVariant = textVariant.replace("_", " ")
                variantWidth = calculate.stringWidth(textVariant, fontName)
                if variantWidth > spaceVariant:
                    while variantWidth > spaceVariant-self.space:
                        if not textVariant: break
                        textVariant = textVariant[:-1]
                        variantWidth = calculate.stringWidth(
                            textVariant + "...", fontName)
                    textVariant += "..."
                self.painter.setPen( QtGui.QColor(self.theme.color.text))
                self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
                self.painter.drawText(
                    QtCore.QRectF(variantArea), textVariant, textOption)
            # version
            fontVersion = UIGlobals.IconDelegate.fontAssetVersion
            self.painter.setFont(fontVersion)
            offsetVersion = 14
            nameArea = QtCore.QRect(
                nameArea.x(), nameArea.y() + offsetVersion,
                nameArea.width(), nameArea.height() - offsetVersion)
            version = self.data.get("version")
            textVersion = "version {}".format(version)
            self.painter.setPen( self.accentColor)
            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(nameArea), textVersion, textOption)
            if hasCount and self.hover and self.controlMode:
                versionWidth = calculate.stringWidth(textVersion, fontVersion)
                offsetPixel = 1
                nameArea = QtCore.QRect(
                    nameArea.x() + versionWidth + offsetPixel, nameArea.y(),
                    nameArea.width() - versionWidth - offsetPixel, nameArea.height())
                count = self.data.get("count")
                textCount = " // {}".format(count)
                self.painter.setPen( QtGui.QColor(self.theme.color.text))
                self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
                self.painter.drawText(
                    QtCore.QRectF(nameArea), textCount, textOption)
        return wrapped
    return decorated
