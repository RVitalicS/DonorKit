#!/usr/bin/env python



import toolkit.core.calculate
import toolkit.core.graphics
from toolkit.core import colorspace

from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from .. import Settings
UIGlobals = Settings.UIGlobals









def background (fill=True):
    def decorated (function):
        def wrapped (self):

            function(self)


            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                QtCore.QRectF(self.iconRect),
                self.radius-1, self.radius-1)
            self.painter.setClipPath(outlinePath)


            if self.hover:
                color = QtGui.QColor(self.theme.color.colorHighlight)
            else:
                color = QtGui.QColor(self.theme.color.colorBackground)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.fillRect(self.iconRect, color)

            fillArea = QtCore.QRect(
                self.pointX, self.pointY,
                self.width,
                self.previewHeight + self.space )

            if fill:
                self.previewColor = QtGui.QColor(
                    self.data.get("color") )
            else:
                self.previewColor = QtGui.QColor(
                    self.theme.color.colorSpace )

            self.painter.fillRect(fillArea, self.previewColor)

        return wrapped
    return decorated





def name (function):
    def wrapped (self):

        function(self)


        # title
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        fontTitle = UIGlobals.IconDelegate.fontColorTitle
        self.painter.setFont(fontTitle)
        self.painter.setPen(
            QtGui.QColor(self.theme.color.black) )

        offsetName = -1
        if self.iconSize == 1:
            offsetName = 0

        if self.iconSize == 1:
            nameArea = QtCore.QRect(
                self.labelArea.x(),
                self.labelArea.y() + offsetName,
                self.spaceName,
                self.labelArea.height() - offsetName)
        else:
            nameArea = QtCore.QRect(
                self.labelArea.x() + self.shiftName ,
                self.labelArea.y() + offsetName,
                self.spaceName,
                self.labelArea.height() - offsetName)

        textTitle = self.data.get("title")
        titleWidth = toolkit.core.calculate.stringWidth(textTitle, fontTitle)
        if titleWidth > self.spaceName:

            while titleWidth > self.spaceName:
                if not textTitle: break

                textTitle = textTitle[:-1]
                titleWidth = toolkit.core.calculate.stringWidth(
                    textTitle + "...", fontTitle)

            textTitle += "..."

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(nameArea),
            textTitle,
            textOption)


        # name
        fontName = UIGlobals.IconDelegate.fontColorName
        self.painter.setFont(fontName)
        self.painter.setPen(
            QtGui.QColor(self.theme.color.colorText) )

        offsetVersion = 14
        nameArea = QtCore.QRect(
            nameArea.x()                      ,
            nameArea.y()      + offsetVersion ,
            nameArea.width()                  ,
            nameArea.height() - offsetVersion )

        textName = self.data.get("name")
        nameWidth = toolkit.core.calculate.stringWidth(textName, fontName)
        if nameWidth > self.spaceName:

            while nameWidth > self.spaceName:
                if not textName: break

                textName = textName[:-1]
                nameWidth = toolkit.core.calculate.stringWidth(
                    textName + "...", fontName)

            textName += "..."

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(nameArea),
            textName,
            textOption)


    return wrapped





def divisionguide (function):
    def wrapped (self):

        function(self)

        infoHeight = UIGlobals.AssetBrowser.Icon.Asset.infoHeight

        if self.iconSize == 1:
            infoWidth = int(self.labelArea.width()/2)
            self.infoArea  = QtCore.QRect(
                self.labelArea.x(),
                self.labelArea.y() + self.labelArea.height() - infoHeight,
                infoWidth,
                infoHeight)

        elif self.iconSize == 2:
            infoWidth = int(((self.labelArea.width() - self.space*4)/2 )/2)
            self.infoArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width()  - infoWidth,
                self.labelArea.y() + self.labelArea.height() - infoHeight,
                infoWidth,
                infoHeight)
            self.spaceName -= infoWidth + self.space

        else:
            infoWidth = int(((self.labelArea.width() - self.space*8)/3 )/2)
            self.infoArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width()  - infoWidth,
                self.labelArea.y() + self.labelArea.height() - infoHeight,
                infoWidth,
                infoHeight)
            self.spaceName -= infoWidth + self.space

    return wrapped





def infoguide (function):
    def wrapped (self):

        function(self)

        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel )
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        # space label
        offsetRaw = 2
        countLabelArea = QtCore.QRect(
            self.infoArea.x(),
            self.infoArea.y() + offsetRaw,
            self.infoArea.width(),
            self.infoArea.height() - offsetRaw)

        self.painter.setPen( QtGui.QColor(self.theme.color.black) )
        self.painter.drawText(
            QtCore.QRectF(countLabelArea),
            "Space", textOption)

        # space value
        offsetColumn = 26
        countValueArea = QtCore.QRect(
            countLabelArea.x() + offsetColumn,
            countLabelArea.y(),
            countLabelArea.width() - offsetColumn,
            countLabelArea.height())

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(countValueArea),
            self.data.get("space"), textOption)

        # count label
        offsetRaw = 12
        spaceLabelArea = QtCore.QRect(
            countLabelArea.x(),
            countLabelArea.y() + offsetRaw,
            countLabelArea.width(),
            countLabelArea.height() - offsetRaw)

        self.painter.setPen( QtGui.QColor(self.theme.color.black) )
        self.painter.drawText(
            QtCore.QRectF(spaceLabelArea),
            "Count", textOption)

        # count value
        spaceValueArea = QtCore.QRect(
            spaceLabelArea.x() + offsetColumn,
            spaceLabelArea.y(),
            spaceLabelArea.width() - offsetColumn,
            spaceLabelArea.height())

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(spaceValueArea),
            str(self.data.get("count")), textOption)

    return wrapped





def infocolor (function):
    def wrapped (self):

        function(self)

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)


        if not self.hover:

            self.painter.setFont( UIGlobals.IconDelegate.fontColorName )
            textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom)
            self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
            self.painter.drawText(
                QtCore.QRectF(self.infoArea),
                self.data.get("color"), textOption)
            return


        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel )
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        value = self.data.get("rgb")

        offsetBlock = 0
        offsetRaw = 9
        offsetColumn = 13

        # R label
        redLabelArea = QtCore.QRect(
            self.infoArea.x(),
            self.infoArea.y() + offsetBlock,
            self.infoArea.width(),
            self.infoArea.height() - offsetBlock)

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(redLabelArea),
            "R:", textOption)

        # R value
        redValueArea = QtCore.QRect(
            redLabelArea.x() + offsetColumn,
            redLabelArea.y(),
            redLabelArea.width() - offsetColumn,
            redLabelArea.height())

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(redValueArea),
            "{:8.6f}".format(value[0]), textOption)

        # G label
        greenLabelArea = QtCore.QRect(
            redLabelArea.x(),
            redLabelArea.y() + offsetRaw,
            redLabelArea.width(),
            redLabelArea.height() - offsetRaw)

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(greenLabelArea),
            "G:", textOption)

        # G value
        greenValueArea = QtCore.QRect(
            greenLabelArea.x() + offsetColumn,
            greenLabelArea.y(),
            greenLabelArea.width() - offsetColumn,
            greenLabelArea.height())

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(greenValueArea),
            "{:8.6f}".format(value[1]), textOption)

        # B label
        blueLabelArea = QtCore.QRect(
            greenLabelArea.x(),
            greenLabelArea.y() + offsetRaw,
            greenLabelArea.width(),
            greenLabelArea.height() - offsetRaw)

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(blueLabelArea),
            "B:", textOption)

        # B value
        blueValueArea = QtCore.QRect(
            blueLabelArea.x() + offsetColumn,
            blueLabelArea.y(),
            blueLabelArea.width() - offsetColumn,
            blueLabelArea.height())

        self.painter.setPen( QtGui.QColor(self.theme.color.colorText) )
        self.painter.drawText(
            QtCore.QRectF(blueValueArea),
            "{:8.6f}".format(value[2]), textOption)

    return wrapped





def favorite (function):
    def wrapped (self):

        function(self)

        if self.hover or self.controlMode:

            image = QtGui.QImage(":/icons/star.png")

            offset = UIGlobals.IconDelegate.space
            position = QtCore.QPoint(
                self.iconRect.x() + self.iconRect.width() - image.width() - offset,
                self.iconRect.y() + offset )

            self.favoriteArea = QtCore.QRect(
                position.x()   ,
                position.y()   ,
                image.width()  ,
                image.height() )


            hexStar = self.theme.color.iconFavorite
            xyzFill = self.data.get("xyz", None)
            if xyzFill != None:

                labStar = colorspace.HEX_Lab(hexStar)
                hueStar = colorspace.getHue(labStar)

                labFill = colorspace.XYZ_Lab(xyzFill)
                hueFill = colorspace.getHue(labFill)

                chroma = colorspace.getChroma(labFill)

                diffL = colorspace.differenceLightness(labStar, labFill)
                lightnessShift = (1.0 - diffL) * 10 + 10 * chroma
                if labStar[0] < labFill[0]:
                    lightnessShift *= -1
                labStar[0] += lightnessShift

                diffH = abs(hueStar - hueFill)
                if diffH > 180: diffH = 360 - diffH

                if int(hueFill + diffH) == int(hueStar):
                    hueStar -= diffH * chroma
                else:
                    hueStar += diffH * chroma

                labStar = colorspace.setHue(labStar, hueStar)
                hexStar = colorspace.Lab_HEX(labStar)


            if self.favorite:
                image = toolkit.core.graphics.recolor(image, hexStar)
            else:
                image = toolkit.core.graphics.recolor(
                    image, 
                    self.getOverlayHex(self.favoriteArea),
                    opacity=0.25)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(position, image)

    return wrapped





def hover (function):
    def wrapped (self):

        function(self)


        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        outlineRect = QtCore.QRect(
            self.iconRect.x() - 1,
            self.iconRect.y() - 1,
            self.iconRect.width()  + 2,
            self.iconRect.height() + 2)

        outlinePath = QtGui.QPainterPath()
        outlinePath.addRoundedRect(
            QtCore.QRectF(outlineRect),
            self.radius+1, self.radius+1,
            mode=QtCore.Qt.AbsoluteSize)
        self.painter.setClipPath(outlinePath)


        if self.hover:
            color = QtGui.QColor(self.theme.color.colorOutlineHover)
            pen = QtGui.QPen(
                    QtGui.QBrush(color), 4,
                    QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin)
            self.painter.strokePath(outlinePath, pen)
            return


        color = QtGui.QColor(self.theme.color.colorOutline)
        pen = QtGui.QPen(
                QtGui.QBrush(color), 2,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin)
        self.painter.strokePath(outlinePath, pen)


    return wrapped
