#!/usr/bin/env python

"""
"""

from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *
from widgets import Settings

UIGlobals = Settings.UIGlobals


class Browser (QtWidgets.QListView):
    refreshLibrary = Signal(QtCore.QModelIndex)
    createFolderQuery = Signal(QtCore.QModelIndex)
    createFolder = Signal(QtCore.QModelIndex, str)
    link = Signal(QtCore.QModelIndex)
    favoriteClicked = Signal(QtCore.QModelIndex)
    tokenClicked = Signal(QtCore.QModelIndex)
    iconClicked = Signal(QtCore.QModelIndex)

    def __init__(self, theme, parent=None):
        super(Browser, self).__init__(parent)
        self.theme = theme
        self.message = None
        self.setProperty("background", "browser")
        self.setProperty("border", "none")
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setMovement(QtWidgets.QListView.Free)
        self.setUniformItemSizes(False)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setMouseTracking(True)
        self.setSpacing(0)
        self.verticalScrollBar().sliderMoved.connect(self.saveScrollPosition)
        self.controlMode = False

    def setGrid (self):
        margin = UIGlobals.Browser.margin
        scrollWidth = UIGlobals.Browser.scrollWidth

        IconSettings = UIGlobals.Browser.Icon
        folderWidth = IconSettings.Folder.width
        folderHeight = IconSettings.Folder.height
        with Settings.Manager(self.theme.app, update=False) as settings:
            iconSize = settings["iconSize"]
        if iconSize == 1:
            assetWidth = IconSettings.Asset.min.width
            assetHeight = IconSettings.Asset.min.height
        elif iconSize == 2:
            assetWidth = IconSettings.Asset.mid.width
            assetHeight = IconSettings.Asset.mid.height
        elif iconSize == 3:
            assetWidth = IconSettings.Asset.max.width
            assetHeight = IconSettings.Asset.max.height
        self.setMinimumWidth(assetWidth +margin*2 +scrollWidth)
        self.setMinimumHeight(assetHeight +margin*2 +scrollWidth)

        widgetWidth = self.width() - scrollWidth - margin
        columnsAsset = int(widgetWidth / assetWidth)
        offsetWidthAsset = int(widgetWidth / columnsAsset )
        offsetAsset = int( (offsetWidthAsset-assetWidth)/2 )
        offsetMaterial = offsetAsset
        columnsFolder = int(widgetWidth / folderWidth)
        offsetWidthFolder = int(widgetWidth / columnsFolder)
        offsetFolder = int( (offsetWidthFolder-folderWidth)/2 )
        model = self.model()
        if not model:
            return

        folderCount = int()
        assetCount = int()
        materialCount = int()
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] in [
                    "folder", "foldercolors" ]:
                folderCount += 1
            elif data["type"] in [
                    "usdasset", "usdfile",
                    "colorguide", "color" ]:
                assetCount  += 1
            elif data["type"] == "usdmaterial":
                materialCount += 1
        if folderCount <= columnsFolder:
            offsetFolder = 0
        if assetCount <= columnsAsset:
            offsetAsset = 0
        if materialCount <= columnsAsset:
            offsetMaterial = 0

        # library label
        hasLibrary = False
        positionX = margin
        positionY = UIGlobals.Browser.margin
        positionY += UIGlobals.Path.height
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] == "labellibrary":
                hasLibrary = True
                item.setSizeHint(
                    QtCore.QSize(folderWidth, folderHeight))
                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )
                positionX = margin
                positionY += folderHeight
                break

        # libraries loop
        if hasLibrary:
            for index in range(model.rowCount()):
                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)
                if data["type"] == "library":
                    if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                        positionX = margin
                        positionY += folderHeight
                    item.setSizeHint(
                        QtCore.QSize(folderWidth, folderHeight))
                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )
                    positionX += folderWidth + offsetFolder
            positionX = margin
            positionY += margin + folderHeight
        
        # folders label
        hasFolder = False
        positionX = margin
        positionY = 0
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] == "labelfolder":
                hasFolder = True
                item.setSizeHint(
                    QtCore.QSize(folderWidth, folderHeight))
                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0))
                positionX = margin
                positionY += folderHeight
                break

        # folders loop
        if hasFolder:
            for index in range(model.rowCount()):
                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)
                if data["type"] in ["folder", "foldercolors"]:
                    if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                        positionX = margin
                        positionY += folderHeight
                    item.setSizeHint(
                        QtCore.QSize(folderWidth, folderHeight))
                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0))
                    positionX += folderWidth + offsetFolder

        # folder create
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] == "plusfolder":
                if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                    positionX = margin
                    positionY += folderHeight
                item.setSizeHint(
                    QtCore.QSize(folderWidth, folderHeight))
                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )
                positionX = margin
                positionY += margin + folderHeight
                break
        
        # assets label
        hasAsset = False
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] == "labelasset":
                hasAsset = True
                item.setSizeHint(
                    QtCore.QSize(folderWidth, folderHeight))
                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )
                positionX = margin
                positionY += folderHeight
                break
        
        # assets loop
        if hasAsset:
            for index in range(model.rowCount()):
                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)
                if data["type"] in [
                        "usdasset", "usdfile",
                        "colorguide", "color"]:
                    if positionX + assetWidth + offsetAsset*2 > widgetWidth + margin:
                        positionX = margin
                        positionY += assetHeight
                    item.setSizeHint(
                        QtCore.QSize(assetWidth, assetHeight))
                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )
                    positionX += assetWidth + offsetAsset
        
        # material label
        hasMaterial = False
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)
            if data["type"] == "labelmaterial":
                hasMaterial = True
                item.setSizeHint(
                    QtCore.QSize(folderWidth, folderHeight))
                if hasAsset:
                    positionX = margin
                    positionY += assetHeight
                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )
                positionX = margin
                positionY += folderHeight
                break
        
        # material loop
        if hasMaterial:
            for index in range(model.rowCount()):
                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)
                if data["type"] == "usdmaterial":
                    if positionX + assetWidth + offsetMaterial*2 > widgetWidth + margin:
                        positionX = margin
                        positionY += assetHeight
                    item.setSizeHint(
                        QtCore.QSize(assetWidth, assetHeight))
                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )
                    positionX += assetWidth + offsetMaterial

        with Settings.Manager(self.theme.app, update=False) as settings:
            scrollPosition = settings["scrollPosition"]
            self.verticalScrollBar().setValue(
                self.intScrollPosition(scrollPosition) )

    def enterEvent (self, event):
        super(Browser, self).enterEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)
    
    def leaveEvent (self, event):
        super(Browser, self).leaveEvent(event)
        self.controlMode = False
        self.repaint()
    
    def mouseReleaseEvent (self, event):
        super(Browser, self).mouseReleaseEvent(event)
        self.iconClickedSignal(QtCore.QModelIndex())
    
    def keyPressEvent (self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.controlMode = True
            self.repaint()
    
    def keyReleaseEvent (self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.controlMode = False
            self.repaint()

    def resizeEvent (self, event):
        super(Browser, self).resizeEvent(event)
        self.setGrid()

    def wheelEvent (self, event):
        super(Browser, self).wheelEvent(event)
        value = self.verticalScrollBar().value()
        self.saveScrollPosition(value)
    
    def setMessage (self, text):
        self.message = text
        self.repaint()
    
    def clearMessage (self):
        self.message = None
        self.repaint()
    
    def paintEvent (self, event):
        if self.message:
            painter = QtGui.QPainter(self.viewport())
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.theme.color.text)))
            painter.setFont(UIGlobals.Browser.fontMessage)
            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            painter.drawText(
                QtCore.QRectF(self.contentsRect()),
                self.message, textOption)
            painter.end()
        super(Browser, self).paintEvent(event)
    
    def floatScrollPosition (self, value):
        maxim = 1 + self.verticalScrollBar().maximum()
        value = 1 + value
        value = round(value/maxim, 4)
        return value
    
    def intScrollPosition (self, value):
        maxim = self.verticalScrollBar().maximum()
        value = int( round(value*maxim, 0) )
        return value
    
    def saveScrollPosition (self, value):
        with Settings.Manager(self.theme.app, update=True) as settings:
            settings["scrollPosition"] = self.floatScrollPosition(value)
    
    def favoriteClickedSignal (self, index):
        self.favoriteClicked.emit(index)
    
    def tokenClickedSignal (self, index):
        self.tokenClicked.emit(index)
    
    def iconClickedSignal (self, index):
        self.iconClicked.emit(index)
    
    def createFolderQueryBridge (self, index):
        self.createFolderQuery.emit(index)
    
    def createFolderBridge (self, index, name):
        self.createFolder.emit(index, name)
    
    def linkBridge (self, index):
        self.link.emit(index)
    
    def refreshLibrarySignal (self, index):
        self.refreshLibrary.emit(index)
