#!/bin/python


import os

from Qt import (
    QtWidgets,
    QtCore,
    QtGui
)


from . import Settings
UIsettings = Settings.UIsettings

from . import stylesheet







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
        

        if iconType in ["labelfolder", "labelasset"]:
            if not self.editing:
                self.paintLabel()

        elif iconType == "folder":
            self.paintFolder()

        elif iconType == "asset":
            self.paintAsset()



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

        nameArea = QtCore.QRect(
            self.pointX + self.space   ,
            self.pointY + self.space   ,
            self.width  - self.space*2 ,
            self.height - self.space*2 )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["text"]

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
                QtGui.QBrush( QtGui.QColor(stylesheet.textgrey) ),
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
        if count > 0:
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

        color = stylesheet.statusWIP

        status = self.index.data(QtCore.Qt.EditRole)["data"]["status"]
        if status == "Final":
            color = stylesheet.statusFinal
        elif status == "Completed":
            color = stylesheet.statusCompleted

        statusColor = QtGui.QColor(color)


        iconSize = 1
        with Settings.UIManager(update=False) as uiSettings:
            iconSize = uiSettings["iconSize"]

        previewBase = self.index.data(QtCore.Qt.EditRole)["data"]["preview"]

        IconSettings = UIsettings.AssetBrowser.Icon

        previewPath = previewBase + ".min.png"
        labelHeight = IconSettings.Asset.min.label
        if iconSize == 2:
            labelHeight = IconSettings.Asset.mid.label
            previewPath = previewBase + ".mid.png"
        elif iconSize == 3:
            labelHeight = IconSettings.Asset.max.label
            previewPath = previewBase + ".max.png"


        labelArea = QtCore.QRect(
            self.pointX + self.space*2 ,
            self.pointY + self.space + (self.height - labelHeight) ,
            self.width  - self.space*4 ,
            self.height - self.space*3 - (self.height - labelHeight) )


        offsetStatus = 4
        statusArea = QtCore.QRect(
            labelArea.x()                                                 ,
            labelArea.y()      + int(labelArea.height()/2) + offsetStatus ,
            labelArea.width()                                             ,
            labelArea.height() - int(labelArea.height()/2) - offsetStatus )



        # BACKGROUND
        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.iconRect.contains(self.pointer):
            color = QtGui.QColor(stylesheet.iconHilight)
        else:
            color = QtGui.QColor(stylesheet.iconBackground)
        self.painter.fillRect(self.iconRect, color)



        # PREVIEW
        if os.path.exists(previewPath):
            previewImage = QtGui.QImage(previewPath)
            self.painter.drawImage(
                QtCore.QPoint(self.pointX, self.pointY),
                previewImage )
            
        else:
            previewArea = QtCore.QRect(
                self.pointX,
                self.pointY,
                self.width,
                self.height - labelHeight )

            previewColor = QtGui.QColor(stylesheet.iconHilight)
            self.painter.fillRect(previewArea, previewColor)



        # ICON
        typeImage = QtGui.QImage(":/icons/typeusd.png")

        offsetIcon = 4
        iconPosition = QtCore.QPoint(
                labelArea.x() + labelArea.width() - typeImage.width(),
                labelArea.y() + offsetIcon )

        self.painter.drawImage(iconPosition, typeImage)



        # NAME
        self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)


        self.painter.setPen( QtGui.QColor(stylesheet.text) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetName )

        offsetName = 2
        nameArea = QtCore.QRect(
            labelArea.x()                   ,
            labelArea.y()      + offsetName ,
            labelArea.width()               ,
            labelArea.height() - offsetName )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["name"]

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)



        # VERSION
        self.painter.setPen( statusColor )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetVersion )

        offsetVersion = offsetName + 14
        nameArea = QtCore.QRect(
            labelArea.x()                      ,
            labelArea.y()      + offsetVersion ,
            labelArea.width()                  ,
            labelArea.height() - offsetVersion )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["version"]
        text = "Version {}".format(text)

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)



        # PUBLISHED & STATUS LABELS
        self.painter.setPen( QtGui.QColor(stylesheet.textgrey) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetLabel )

        self.painter.drawText(
            QtCore.QRectF(statusArea),
            "Published",
            textOption)


        nameArea = QtCore.QRect(
            statusArea.x()     + int(statusArea.width()/2) ,
            statusArea.y()                             ,
            statusArea.width() - int(statusArea.width()/2) ,
            statusArea.height()                        )

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            "STATUS",
            textOption)



        # PUBLISHED DATE
        self.painter.setPen( QtGui.QColor(stylesheet.text) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetLabel )

        offsetPublished = 10
        nameArea = QtCore.QRect(
            statusArea.x()                        ,
            statusArea.y()      + offsetPublished ,
            statusArea.width()                    ,
            statusArea.height() - offsetPublished )

        text = self.index.data(QtCore.Qt.EditRole)["data"]["published"]

        self.painter.drawText(
            QtCore.QRectF(nameArea),
            text,
            textOption)



        # STATUS BUTTON
        offsetButton = offsetPublished + 2
        buttonArea = QtCore.QRect(
            statusArea.x()      + int(statusArea.width()/2) ,
            statusArea.y()      + offsetButton              ,
            statusArea.width()  - int(statusArea.width()/2) ,
            statusArea.height() - offsetButton              )

        path = QtGui.QPainterPath()
        path.addRoundedRect(
            buttonArea, 
            UIsettings.IconDelegate.radiusStatus, 
            UIsettings.IconDelegate.radiusStatus)

        brush = QtGui.QBrush(statusColor)
        self.painter.fillPath(path, brush)



        # STATUS TEXT
        self.painter.setPen( QtGui.QColor(stylesheet.white) )
        self.painter.setFont( UIsettings.IconDelegate.fontAssetStatus )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

        self.painter.drawText(
            QtCore.QRectF(buttonArea),
            status,
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
            self.painter.strokePath(outlinePath, pen)
