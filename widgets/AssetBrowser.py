#!/usr/bin/env python



from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







class AssetBrowser (QtWidgets.QListView):

    createFolderQuery = QtCore.Signal(QtCore.QModelIndex)
    createFolder      = QtCore.Signal(QtCore.QModelIndex, str)
    iconClicked  = QtCore.Signal(QtCore.QModelIndex)


    def __init__(self):
        super(AssetBrowser, self).__init__()

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

        self.verticalScrollBar().sliderMoved.connect(
            self.saveScrollPosition)



    def setGrid (self):
        

        margin = UIsettings.AssetBrowser.margin
        scrollWidth = UIsettings.AssetBrowser.scrollWidth


        iconSize = 1
        with Settings.UIManager(update=False) as uiSettings:
            iconSize = uiSettings["iconSize"]


        IconSettings = UIsettings.AssetBrowser.Icon

        folderWidth  = IconSettings.Folder.width
        folderHeight = IconSettings.Folder.height

        assetWidth   = IconSettings.Asset.min.width
        assetHeight  = IconSettings.Asset.min.height

        if iconSize == 2:
            assetWidth   = IconSettings.Asset.mid.width
            assetHeight  = IconSettings.Asset.mid.height

        if iconSize == 3:
            assetWidth   = IconSettings.Asset.max.width
            assetHeight  = IconSettings.Asset.max.height


        self.setMinimumWidth(assetWidth +margin*2 +scrollWidth)
        self.setMinimumHeight(assetHeight +margin*2 +scrollWidth)


        widgetWidth = self.width() - scrollWidth - margin

        columnsAsset     = int(widgetWidth/assetWidth)
        offsetWidthAsset = int(widgetWidth / columnsAsset )
        offsetAsset      = int( (offsetWidthAsset-assetWidth)/2 )


        columnsFolder     = int(widgetWidth/folderWidth)
        offsetWidthFolder = int(widgetWidth / columnsFolder )
        offsetFolder      = int( (offsetWidthFolder-folderWidth)/2 )


        model = self.model()


        folderCount = int()
        assetCount  = int()
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)

            if   data["type"] == "folder": folderCount += 1
            elif data["type"] == "asset" : assetCount  += 1


        if folderCount <= columnsFolder:
            offsetFolder = 0

        if assetCount <= columnsAsset:
            offsetAsset = 0



        # library label
        hasLibrary = False
        positionX = margin
        positionY  = UIsettings.AssetBrowser.margin
        positionY += UIsettings.Path.height
        for index in range(model.rowCount()):

            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)

            if data["type"] == "labellibrary":
                hasLibrary = True

                item.setSizeHint(
                    QtCore.QSize(
                        folderWidth,
                        folderHeight ))

                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )

                positionX  = margin
                positionY +=  folderHeight
                break


        # libraries loop
        if hasLibrary:
            for index in range(model.rowCount()):

                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)

                if data["type"] == "library":
                    
                    if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                        positionX  = margin
                        positionY += folderHeight

                    item.setSizeHint(
                        QtCore.QSize(
                            folderWidth,
                            folderHeight ))

                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )

                    positionX += folderWidth + offsetFolder

            positionX  = margin
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
                    QtCore.QSize(
                        folderWidth,
                        folderHeight ))

                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )

                positionX  = margin
                positionY +=  folderHeight
                break


        # folders loop
        if hasFolder:
            for index in range(model.rowCount()):

                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)

                if data["type"] == "folder":
                    
                    if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                        positionX  = margin
                        positionY += folderHeight

                    item.setSizeHint(
                        QtCore.QSize(
                            folderWidth,
                            folderHeight ))

                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )

                    positionX += folderWidth + offsetFolder


        # folder create
        for index in range(model.rowCount()):

            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)

            if data["type"] == "plusfolder":
                
                if positionX + folderWidth + offsetFolder*2 > widgetWidth + margin:
                    positionX  = margin
                    positionY += folderHeight

                item.setSizeHint(
                    QtCore.QSize(
                        folderWidth,
                        folderHeight ))

                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )

                positionX  = margin
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
                    QtCore.QSize(
                        folderWidth,
                        folderHeight ))

                self.setPositionForIndex(
                    QtCore.QPoint(positionX, positionY), 
                    model.index(index, 0) )

                positionX  = margin
                positionY += folderHeight
                break


        # assets loop
        if hasAsset:
            for index in range(model.rowCount()):

                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)

                if data["type"] == "asset":
                    if positionX + assetWidth + offsetAsset*2 > widgetWidth + margin:
                        positionX  = margin
                        positionY += assetHeight

                    item.setSizeHint(
                        QtCore.QSize(
                            assetWidth,
                            assetHeight ))

                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )

                    positionX += assetWidth + offsetAsset



        with Settings.UIManager(update=False) as uiSettings:
            scrollPosition = uiSettings["scrollPosition"]

            self.verticalScrollBar().setValue(
                self.intScrollPosition(scrollPosition) )




    def enterEvent (self, event):

        super(AssetBrowser, self).enterEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)



    def mouseReleaseEvent (self, event):

        super(AssetBrowser, self).mouseReleaseEvent(event)
        self.iconClickedSignal(QtCore.QModelIndex())



    def resizeEvent (self, event):

        super(AssetBrowser, self).resizeEvent(event)
        self.setGrid()



    def wheelEvent (self, event):

        super(AssetBrowser, self).wheelEvent(event)
        
        value = self.verticalScrollBar().value()
        self.saveScrollPosition(value)



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

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["scrollPosition"] = self.floatScrollPosition(value)



    def iconClickedSignal (self, index):

        self.iconClicked.emit(index)



    def createFolderQueryBridge (self, index):

        self.createFolderQuery.emit(index)



    def createFolderBridge (self, index, name):

        self.createFolder.emit(index, name)
