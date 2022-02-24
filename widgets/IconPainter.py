#!/usr/bin/env python



import os
from . import tools
from . import stylesheet


from Qt import QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings





def background (function):

    def wrapped(self):

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.iconRect.contains(self.pointer):
            color = QtGui.QColor(stylesheet.folderHilight)
        else:
            color = QtGui.QColor(stylesheet.iconBackground)
        self.painter.fillRect(self.iconRect, color)

        function(self)

    return wrapped






class Icon (object):



    def __init__ (self):
        super(Icon, self).__init__()

        self.index = QtCore.QModelIndex()

        self.pointer  = QtCore.QPoint(-1, -1)
        self.iconRect = QtCore.QRect()



    def sizeHint (self):
        
        model = self.index.model()
        raw = self.index.row()
        item = model.item(raw)

        return item.sizeHint()



    def paint (self, painter, option, index, editing=False):
        
        self.painter = painter
        self.option  = option
        self.index   = index
        self.editing = editing

        self.space = UIsettings.IconDelegate.space
        self.radius = UIsettings.IconDelegate.radius

        self.checked = self.index.data(QtCore.Qt.StatusTipRole)

        iconType = self.index.data(QtCore.Qt.EditRole)["type"]
        
        if iconType != "asset":
            self.radius = 0

        self.width  = self.option.rect.width()
        self.height = self.option.rect.height()

        self.pointX = self.option.rect.x()
        self.pointY = self.option.rect.y()

        self.iconRect = QtCore.QRect(
            self.pointX + self.space   ,
            self.pointY + self.space   ,
            self.width  - self.space*2 ,
            self.height - self.space*2 )


        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(
            self.iconRect.x()     , self.iconRect.y()      ,
            self.iconRect.width() , self.iconRect.height() ,
            self.radius           , self.radius            ,
            mode=QtCore.Qt.AbsoluteSize                    )

        self.painter.setClipPath(clipPath)
        self.painter.setPen(QtCore.Qt.NoPen)
        

        if iconType in [ "labellibrary" ]:
            if not self.editing:
                self.paintCategory()
        
        elif iconType in [
                "labelfolder" ,
                "labelasset"  ]:
            if not self.editing:
                self.paintLabel()

        elif iconType == "library":
            self.paintLibrary()

        elif iconType == "folder":
            self.paintFolder()

        elif iconType == "asset":
            self.paintAsset()



    def paintCategory (self):
        
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(stylesheet.text) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        self.painter.setFont( UIsettings.IconDelegate.fontLibraries )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["text"]

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        self.painter.drawText(
            QtCore.QRectF(self.iconRect),
            text,
            textOption)



    def paintLabel (self):
        
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(stylesheet.text) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        self.painter.setFont( UIsettings.IconDelegate.fontCategory )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["text"]

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        self.painter.drawText(
            QtCore.QRectF(self.iconRect),
            text,
            textOption)



    def paintLibrary (self):

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        if self.iconRect.contains(self.pointer):
            colorBackground = QtGui.QColor(stylesheet.folderHilight)
            colorText = stylesheet.white
            libraryImage = QtGui.QImage(":/icons//library-hover.png")

        else:
            colorBackground = QtGui.QColor(stylesheet.iconBackground)
            colorText = stylesheet.text
            libraryImage = QtGui.QImage(":/icons//library.png")


        # BACKGROUND
        self.painter.fillRect(self.iconRect, colorBackground)

        borderWidth = 1
        borderRect = QtCore.QRect(
            self.iconRect.x()      + borderWidth    ,
            self.iconRect.y()      + borderWidth    ,
            self.iconRect.width()  - borderWidth *2 ,
            self.iconRect.height() - borderWidth *2 )

        color = QtGui.QColor(stylesheet.browserBackground)
        self.painter.fillRect(borderRect, color.lighter(107))


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
        self.painter.setFont( UIsettings.IconDelegate.fontFolderName )

        offsetName = libraryImage.width() + offsetIcon*2
        nameArea = QtCore.QRect(
            self.iconRect.x()      + offsetName ,
            self.iconRect.y()                   ,
            self.iconRect.width()  - offsetName ,
            self.iconRect.height()              )


        text = self.index.data(QtCore.Qt.EditRole)["data"]["name"]

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)



    def paintFolder (self):

        # BACKGROUND
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.iconRect.contains(self.pointer):
            color = QtGui.QColor(stylesheet.folderHilight)
        else:
            color = QtGui.QColor(stylesheet.iconBackground)
        self.painter.fillRect(self.iconRect, color)


        # ICON
        folderImage = QtGui.QImage(":/icons/folder.png")
        offsetIcon = int((
            self.height - self.space*2 - folderImage.height() )/2)

        iconPosition = QtCore.QPoint(
                self.pointX + self.space + offsetIcon,
                self.pointY + self.space + offsetIcon)

        self.painter.drawImage(iconPosition, folderImage)


        # NAME
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(stylesheet.text) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        offsetText = 1
        self.painter.setFont( UIsettings.IconDelegate.fontFolderName )

        offsetName = folderImage.width() + offsetIcon*2
        nameArea = QtCore.QRect(
            self.pointX + self.space + offsetName   ,
            self.pointY + self.space ,
            self.width  - self.space*2 - offsetName ,
            int(self.height/2) - int(self.space/2) -offsetText )


        text = self.index.data(QtCore.Qt.EditRole)["data"]["name"]

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom)

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)


        # ITEMS
        self.painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(stylesheet.textlock) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        self.painter.setFont( UIsettings.IconDelegate.fontFolderItems )

        offsetName = folderImage.width() + offsetIcon*2
        nameArea = QtCore.QRect(
            self.pointX + self.space + offsetName   ,
            self.pointY + int(self.height/2) +offsetText ,
            self.width  - self.space*2 - offsetName ,
            int(self.height/2) )


        count = self.index.data(QtCore.Qt.EditRole)["data"]["items"]
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
            QtCore.QRectF(nameArea),
            text,
            textOption)



    def paintAsset (self):

        # BACKGROUND
        previewColor = QtGui.QColor(stylesheet.iconHilight)
        self.painter.fillRect(self.option.rect, previewColor)


        # DEFINE STATUS
        color = stylesheet.statusWIP

        status = self.index.data(QtCore.Qt.EditRole)["data"]["status"]
        if status == "Final":
            color = stylesheet.statusFinal
        elif status == "Completed":
            color = stylesheet.statusCompleted

        statusColor = QtGui.QColor(color)


        # GET SIZE
        iconSize = 1
        with Settings.UIManager(update=False) as uiSettings:
            iconSize = uiSettings["iconSize"]

        IconSettings = UIsettings.AssetBrowser.Icon

        labelHeight = IconSettings.Asset.min.label
        if iconSize == 2:
            labelHeight = IconSettings.Asset.mid.label
        elif iconSize == 3:
            labelHeight = IconSettings.Asset.max.label

        previewHeight = self.height - labelHeight - self.space*2


        labelArea = QtCore.QRect(
            self.pointX + self.space*2 ,
            self.pointY + self.height - labelHeight ,
            self.width  - self.space*4 ,
            labelHeight - self.space*2 )

        spaceName = labelArea.width()



        # PREVIEW IMAGE
        previewList = self.index.data(QtCore.Qt.EditRole)["data"]["previews"]
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

            previewY  = (previewHeight - scaledImage.height())/2
            previewY  = int(round(previewY))
            previewY += self.pointY + self.space

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.drawImage(
                QtCore.QPoint(self.iconRect.x(), previewY),
                scaledImage )



        # ANIMATION TAG
        textAnimation = self.index.data(QtCore.Qt.EditRole)["data"]["animation"]
        if textAnimation:
            textAnimation = textAnimation.replace("_", " ")

            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

            fontAnimation = UIsettings.IconDelegate.Animation.font
            self.painter.setFont(fontAnimation)
            self.painter.setPen( QtGui.QColor(stylesheet.paper) )

            offsetTag = UIsettings.IconDelegate.Animation.offset
            spaceTag  = UIsettings.IconDelegate.Animation.space
            heightTag = UIsettings.IconDelegate.Animation.height
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

            brush = QtGui.QBrush( QtGui.QColor(stylesheet.iconAnimation) )

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.fillPath(path, brush)


            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(tagArea),
                textAnimation,
                textOption)



        # INFO AREA
        labelBackground = QtCore.QRect(
            self.pointX                              ,
            self.pointY + previewHeight + self.space ,
            self.width                               ,
            labelHeight + self.space                 )

        if self.iconRect.contains(self.pointer):
            color = QtGui.QColor(stylesheet.iconHilight)
        else:
            color = QtGui.QColor(stylesheet.iconBackground)

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillRect(labelBackground, color)



        # TYPE ICON
        typeImage = QtGui.QImage(":/icons/typeusd.png")

        offsetIcon = 0
        if iconSize == 1:
            iconPosition = QtCore.QPoint(
                    labelArea.x() + labelArea.width() - typeImage.width(),
                    labelArea.y() + offsetIcon )
        else:
            iconPosition = QtCore.QPoint(
                    labelArea.x()              ,
                    labelArea.y() + offsetIcon )

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.drawImage(iconPosition, typeImage)
        spaceName -= typeImage.width()



        # PUBLISHED & STATUS LABELS
        self.painter.setPen( QtGui.QColor(stylesheet.textlock) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetLabel )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        statusHeight = UIsettings.AssetBrowser.Icon.Asset.statusHeight

        if iconSize == 1:
            publishedWidth = int(labelArea.width()/2)
            publishedArea  = QtCore.QRect(
                labelArea.x()                                           ,
                labelArea.y() + int(labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
        elif iconSize == 2:
            publishedWidth = int(((labelArea.width() - self.space*4)/2 )/2)
            publishedArea = QtCore.QRect(
                labelArea.x() + labelArea.width() - publishedWidth*2    ,
                labelArea.y() + int(labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
            spaceName -= publishedWidth*2 + self.space*2
        else:
            publishedWidth = int(((labelArea.width() - self.space*8)/3 )/2)
            publishedArea = QtCore.QRect(
                labelArea.x() + labelArea.width() - publishedWidth*2    ,
                labelArea.y() + int(labelArea.height() - statusHeight ) ,
                publishedWidth                                          ,
                statusHeight                                            )
            spaceName -= publishedWidth*2 + self.space*2

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



        # PUBLISHED DATE
        self.painter.setPen( QtGui.QColor(stylesheet.text) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetLabel )
        
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        offsetPublished = 10
        dateArea = QtCore.QRect(
            publishedArea.x()                        ,
            publishedArea.y()      + offsetPublished ,
            publishedArea.width()                    ,
            publishedArea.height() - offsetPublished )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["published"]

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(dateArea),
            text,
            textOption)

        

        # STATUS BUTTON
        offsetButton = offsetPublished + 2
        buttonArea = QtCore.QRect(
            statusArea.x()                     ,
            statusArea.y()      + offsetButton ,
            statusArea.width()                 ,
            statusArea.height() - offsetButton )

        path = QtGui.QPainterPath()
        path.addRoundedRect(
            buttonArea, 
            UIsettings.IconDelegate.radiusStatus, 
            UIsettings.IconDelegate.radiusStatus)

        brush = QtGui.QBrush(statusColor)

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.fillPath(path, brush)

        

        # STATUS TEXT
        self.painter.setPen( QtGui.QColor(stylesheet.white) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetStatus )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(buttonArea),
            status,
            textOption)



        # NAME
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        fontName = UIsettings.IconDelegate.fontAssetName
        self.painter.setFont(fontName)

        self.painter.setPen( QtGui.QColor(stylesheet.text) )

        offsetName = -2
        spaceName -= self.space

        if iconSize == 1:
            nameArea = QtCore.QRect(
                labelArea.x()                   ,
                labelArea.y()      + offsetName ,
                spaceName               ,
                labelArea.height() - offsetName )
        else:
            nameArea = QtCore.QRect(
                labelArea.x() + typeImage.width() + self.space*2 ,
                labelArea.y()      + offsetName                ,
                spaceName                       ,
                labelArea.height() - offsetName                )

        textName = self.index.data(QtCore.Qt.EditRole)["data"]["name"]
        textName = textName.replace("_", " ")
        
        nameWidth = tools.getStringWidth(textName, fontName)
        spaceVariant = spaceName - nameWidth

        if nameWidth > spaceName:

            while nameWidth > spaceName:
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



        # VARIANT
        variant = self.index.data(QtCore.Qt.EditRole)["data"]["variant"]
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

            self.painter.setPen( QtGui.QColor(stylesheet.textlock) )

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(variantArea),
                textVariant,
                textOption)


        # VERSION
        fontVersion = UIsettings.IconDelegate.fontAssetVersion
        self.painter.setFont(fontVersion)

        # draw version text
        offsetVersion = 13
        nameArea = QtCore.QRect(
            nameArea.x()                      ,
            nameArea.y()      + offsetVersion ,
            nameArea.width()                  ,
            nameArea.height() - offsetVersion )

        version = self.index.data(QtCore.Qt.EditRole)["data"]["version"]
        textVersion = "version {}".format(version)

        self.painter.setPen( statusColor )

        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.painter.drawText(
            QtCore.QRectF(nameArea),
            textVersion,
            textOption)

        if self.iconRect.contains(self.pointer):

            versionWidth = tools.getStringWidth(textVersion, fontVersion)
            offsetPixel = 1

            nameArea = QtCore.QRect(
                nameArea.x()      + versionWidth + offsetPixel ,
                nameArea.y()                                   ,
                nameArea.width()  - versionWidth - offsetPixel ,
                nameArea.height()                              )

            count = self.index.data(QtCore.Qt.EditRole)["data"]["count"]
            textCount = " // {}".format(count)

            self.painter.setPen( QtGui.QColor(stylesheet.text) )

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.drawText(
                QtCore.QRectF(nameArea),
                textCount,
                textOption)



        # CHECKED STATE
        if self.checked == 1:

            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                self.iconRect, 
                self.radius, 
                self.radius)

            color = QtGui.QColor(stylesheet.checkedHilight)
        
            pen = QtGui.QPen(
                    QtGui.QBrush(color),
                    4,
                    QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin)

            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.strokePath(outlinePath, pen)
