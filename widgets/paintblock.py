#!/usr/bin/env python



from . import tools


from Qt import QtCore, QtGui

from . import Settings
UIGlobals = Settings.UIGlobals





def clear (function):
    def wrapped (self):

        function(self)

        self.painter.fillRect(
            self.option.rect,
            QtGui.QColor(self.theme.browserBackground)
        )

    return wrapped





def label (font):
    def decorated (function):
        def wrapped (self):

            function(self)

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.setPen(
                QtGui.QPen(
                    QtGui.QBrush( QtGui.QColor(self.theme.text) ),
                    0,
                    QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin) )

            self.painter.setFont(font)

            text = self.data.get("text")

            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

            self.painter.drawText(
                QtCore.QRectF(self.iconRect),
                text,
                textOption)

        return wrapped
    return decorated





def checked (function):
    def wrapped (self):

        function(self)

        if self.checked == 1:

            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                self.iconRect, 
                self.radius, 
                self.radius)

            color = QtGui.QColor(self.theme.checkedHilight)
        
            pen = QtGui.QPen(
                    QtGui.QBrush(color),
                    4,
                    QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.strokePath(outlinePath, pen)

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

            if self.favorite:
                image = tools.recolor(image, self.theme.checkedHilight)
            else:
                image = tools.recolor(image, self.theme.kicker, opacity=0.25)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(position, image)

    return wrapped





def background (function):
    def wrapped (self):

        function(self)

        if self.hover:
            color = QtGui.QColor(self.theme.iconOutlineHover)
        else:
            color = QtGui.QColor(self.theme.iconOutline)

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillRect(self.option.rect, color)

        thickness = 1
        shape = QtCore.QRect(
            self.iconRect.x()      + thickness   ,
            self.iconRect.y()      + thickness   ,
            self.iconRect.width()  - thickness*2 ,
            self.iconRect.height() - thickness*2 )

        outlinePath = QtGui.QPainterPath()
        outlinePath.addRoundedRect(
            shape, 
            self.radius, 
            self.radius)

        if self.hover:
            color = QtGui.QColor(self.theme.iconHilight)
        else:
            color = QtGui.QColor(self.theme.iconBackground)

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillPath(outlinePath, QtGui.QBrush(color))


        clearBackground = QtCore.QRect(
            self.pointX                ,
            self.pointY                ,
            self.width                 ,
            self.previewHeight + self.space )
        previewColor = QtGui.QColor(self.theme.iconSpace)
        self.painter.fillRect(clearBackground, previewColor)

    return wrapped





def usdColorAccent (status=True):
    def decorated (function):
        def wrapped (self):

            function(self)

            if status:
                color = self.theme.statusWIP

                text = self.data.get("status")
                if text == "Completed":
                    color = self.theme.statusCompleted

                elif text == "Final":
                    color = self.theme.statusFinal

            else:
                color = self.theme.textlock

            self.accentColor = QtGui.QColor(color)

        return wrapped
    return decorated





def usdInitialize (function):
    def wrapped (self):

        function(self)

        self.iconSize = 1
        with Settings.Manager(update=False) as settings:
            self.iconSize = settings["iconSize"]

        IconSettings = UIGlobals.AssetBrowser.Icon

        labelHeight = IconSettings.Asset.min.label
        if self.iconSize == 2:
            labelHeight = IconSettings.Asset.mid.label
        elif self.iconSize == 3:
            labelHeight = IconSettings.Asset.max.label

        self.previewHeight = self.height - labelHeight - self.space*2


        self.labelArea = QtCore.QRect(
            self.pointX + self.space*2 ,
            self.pointY + self.height - labelHeight ,
            self.width  - self.space*4 ,
            labelHeight - self.space*2 )

        self.spaceName = self.labelArea.width()
        self.shiftName = 0

    return wrapped





def usdPreview (function):
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
            previewImage = QtGui.QImage(previewPath)

            scaledImage = previewImage.scaledToWidth(
                self.iconRect.width(),
                QtCore.Qt.SmoothTransformation )

            previewY  = (self.previewHeight - scaledImage.height())/2
            previewY  = int(round(previewY))
            previewY += self.pointY + self.space

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(
                QtCore.QPoint(self.iconRect.x(), previewY),
                scaledImage )

    return wrapped





def usdAnimation (function):
    def wrapped (self):

        function(self)

        textAnimation = self.data.get("animation")
        if textAnimation:
            textAnimation = textAnimation.replace("_", " ")

            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

            fontAnimation = UIGlobals.IconDelegate.Animation.font
            self.painter.setFont(fontAnimation)
            self.painter.setPen( QtGui.QColor(self.theme.paper) )

            offsetTag = UIGlobals.IconDelegate.Animation.offset
            spaceTag  = UIGlobals.IconDelegate.Animation.space
            heightTag = UIGlobals.IconDelegate.Animation.height
            radiusTag = int(round(heightTag/2))

            animationWidth = tools.getStringWidth(textAnimation, fontAnimation)

            spaceAnimation = self.iconRect.width() - spaceTag - offsetTag*2
            if animationWidth > spaceAnimation:

                while animationWidth > spaceAnimation:
                    if not textAnimation: break

                    textAnimation = textAnimation[:-1]
                    animationWidth = tools.getStringWidth(
                        textAnimation + "...", fontAnimation)

                textAnimation += "..."

            tagArea = QtCore.QRect(
                self.iconRect.x() + offsetTag ,
                self.iconRect.y() + offsetTag ,
                animationWidth    + spaceTag  ,
                heightTag                     )


            path = QtGui.QPainterPath()
            path.addRoundedRect(tagArea, radiusTag, radiusTag)

            brush = QtGui.QBrush( QtGui.QColor(self.theme.iconAnimation) )

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.fillPath(path, brush)


            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(tagArea),
                textAnimation,
                textOption)

    return wrapped





def usdLink (function):
    def wrapped (self):

        function(self)

        if self.hover and self.controlMode:

            linkImage = QtGui.QImage(":/icons/link.png")
            linkImage = tools.recolor(linkImage, self.theme.kicker, opacity=0.25)

            linkOffset = linkImage.width() + self.space

            linkPosition = QtCore.QPoint(
                    self.iconRect.x() + self.iconRect.width()  - linkOffset,
                    self.iconRect.y() + self.previewHeight          - linkOffset)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(linkPosition, linkImage)

            self.linkArea = QtCore.QRect(
                linkPosition.x() ,
                linkPosition.y() ,
                linkImage.width() ,
                linkImage.height() )


    return wrapped





def usdIcon (function):
    def wrapped (self):

        function(self)

        typeImage = QtGui.QImage(":/icons/typeusd.png")

        offsetIcon = 0
        if self.iconSize == 1:
            iconPosition = QtCore.QPoint(
                    self.labelArea.x() + self.labelArea.width() - typeImage.width(),
                    self.labelArea.y() + offsetIcon )
        else:
            iconPosition = QtCore.QPoint(
                    self.labelArea.x()              ,
                    self.labelArea.y() + offsetIcon )

            self.shiftName += typeImage.width()

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.drawImage(iconPosition, typeImage)
        self.spaceName -= typeImage.width()

    return wrapped





def usdStatus (function):
    def wrapped (self):

        function(self)


        # labels
        self.painter.setPen( QtGui.QColor(self.theme.textlock) )
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        statusHeight = UIGlobals.AssetBrowser.Icon.Asset.statusHeight

        if self.iconSize == 1:
            publishedWidth = int(self.labelArea.width()/2)
            publishedArea  = QtCore.QRect(
                self.labelArea.x()                                           ,
                self.labelArea.y() + int(self.labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
        elif self.iconSize == 2:
            publishedWidth = int(((self.labelArea.width() - self.space*4)/2 )/2)
            publishedArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width() - publishedWidth*2    ,
                self.labelArea.y() + int(self.labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
            self.spaceName -= publishedWidth*2 + self.space*2
        else:
            publishedWidth = int(((self.labelArea.width() - self.space*8)/3 )/2)
            publishedArea = QtCore.QRect(
                self.labelArea.x() + self.labelArea.width() - publishedWidth*2    ,
                self.labelArea.y() + int(self.labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
            self.spaceName -= publishedWidth*2 + self.space*2

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        self.painter.drawText(
            QtCore.QRectF(publishedArea),
            "Published",
            textOption)


        statusArea = QtCore.QRect(
            publishedArea.x() + publishedWidth ,
            publishedArea.y()                  ,
            publishedArea.width()              ,
            publishedArea.height()             )

        self.painter.drawText(
            QtCore.QRectF(statusArea),
            "STATUS",
            textOption)



        # date
        self.painter.setPen( QtGui.QColor(self.theme.text) )
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetLabel )
        
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        offsetPublished = 10
        dateArea = QtCore.QRect(
            publishedArea.x()                        ,
            publishedArea.y()      + offsetPublished ,
            publishedArea.width()                    ,
            publishedArea.height() - offsetPublished )

        text = self.data.get("published")

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(dateArea),
            text,
            textOption)

        

        # status button
        offsetButton = offsetPublished + 2
        buttonArea = QtCore.QRect(
            statusArea.x()                     ,
            statusArea.y()      + offsetButton ,
            statusArea.width()                 ,
            statusArea.height() - offsetButton )

        path = QtGui.QPainterPath()
        path.addRoundedRect(
            buttonArea, 
            UIGlobals.IconDelegate.radiusStatus, 
            UIGlobals.IconDelegate.radiusStatus)

        brush = QtGui.QBrush(self.accentColor)

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillPath(path, brush)

        

        # status text
        self.painter.setPen( QtGui.QColor(self.theme.white) )
        self.painter.setFont( UIGlobals.IconDelegate.fontAssetStatus )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

        text = self.data.get("status")

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(buttonArea),
            text,
            textOption)


    return wrapped





def usdName (hasCount=True):
    def decorated (function):
        def wrapped (self):

            function(self)


            # name
            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

            fontName = UIGlobals.IconDelegate.fontAssetName
            self.painter.setFont(fontName)

            if self.hover or self.checked == 1:
                self.painter.setPen( QtGui.QColor(self.theme.kicker) )
            else:
                self.painter.setPen( QtGui.QColor(self.theme.text) )

            offsetName = -2
            self.spaceName -= self.space

            if self.iconSize == 1:
                nameArea = QtCore.QRect(
                    self.labelArea.x()                   ,
                    self.labelArea.y()      + offsetName ,
                    self.spaceName               ,
                    self.labelArea.height() - offsetName )
            else:
                nameArea = QtCore.QRect(
                    self.labelArea.x() + self.shiftName + self.space*2 ,
                    self.labelArea.y()      + offsetName                ,
                    self.spaceName                       ,
                    self.labelArea.height() - offsetName                )

            textName = self.data.get("name")
            textName = textName.replace("_", " ")
            
            nameWidth = tools.getStringWidth(textName, fontName)
            spaceVariant = self.spaceName - nameWidth

            if nameWidth > self.spaceName:

                while nameWidth > self.spaceName:
                    if not textName: break

                    textName = textName[:-1]
                    nameWidth = tools.getStringWidth(
                        textName + "...", fontName)

                textName += "..."

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(nameArea),
                textName,
                textOption)



            # variant
            variant = self.data.get("variant")
            if variant and spaceVariant > self.space:

                offsetPixel = 1

                variantArea = QtCore.QRect(
                    nameArea.x()      + nameWidth + offsetPixel ,
                    nameArea.y()                                ,
                    nameArea.width()  - nameWidth - offsetPixel ,
                    nameArea.height()                           )

                textVariant = " {}".format(variant)
                textVariant = textVariant.replace("_", " ")
            
                variantWidth = tools.getStringWidth(textVariant, fontName)
                if variantWidth > spaceVariant:

                    while variantWidth > spaceVariant-self.space:
                        if not textVariant: break

                        textVariant = textVariant[:-1]
                        variantWidth = tools.getStringWidth(
                            textVariant + "...", fontName)

                    textVariant += "..."

                self.painter.setPen( QtGui.QColor(self.theme.text) )

                self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
                self.painter.drawText(
                    QtCore.QRectF(variantArea),
                    textVariant,
                    textOption)


            # version
            fontVersion = UIGlobals.IconDelegate.fontAssetVersion
            self.painter.setFont(fontVersion)

            offsetVersion = 13
            nameArea = QtCore.QRect(
                nameArea.x()                      ,
                nameArea.y()      + offsetVersion ,
                nameArea.width()                  ,
                nameArea.height() - offsetVersion )

            version = self.data.get("version")
            textVersion = "version {}".format(version)

            self.painter.setPen( self.accentColor )

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(nameArea),
                textVersion,
                textOption)

            if hasCount and self.hover and self.controlMode:

                versionWidth = tools.getStringWidth(textVersion, fontVersion)
                offsetPixel = 1

                nameArea = QtCore.QRect(
                    nameArea.x()      + versionWidth + offsetPixel ,
                    nameArea.y()                                   ,
                    nameArea.width()  - versionWidth - offsetPixel ,
                    nameArea.height()                              )

                count = self.data.get("count")
                textCount = " // {}".format(count)

                self.painter.setPen( QtGui.QColor(self.theme.text) )

                self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
                self.painter.drawText(
                    QtCore.QRectF(nameArea),
                    textCount,
                    textOption)
 

        return wrapped
    return decorated
