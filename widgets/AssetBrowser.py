#!/bin/python


from Qt import (
    QtWidgets,
    QtCore,
    QtGui
)


from . import Settings
UIsettings = Settings.UIsettings








class AssetBrowser (QtWidgets.QListView):

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

        folderWidth  = IconSettings.Folder.min.width
        folderHeight = IconSettings.Folder.min.height
        assetWidth   = IconSettings.Asset.min.width
        assetHeight  = IconSettings.Asset.min.height

        if iconSize == 2:
            folderWidth  = IconSettings.Folder.mid.width
            folderHeight = IconSettings.Folder.mid.height
            assetWidth   = IconSettings.Asset.mid.width
            assetHeight  = IconSettings.Asset.mid.height

        if iconSize == 3:
            folderWidth  = IconSettings.Folder.max.width
            folderHeight = IconSettings.Folder.max.height
            assetWidth   = IconSettings.Asset.max.width
            assetHeight  = IconSettings.Asset.max.height


        self.setMinimumWidth(assetWidth +margin*2 +scrollWidth)
        self.setMinimumHeight(assetHeight +margin*2 +scrollWidth)


        widgetWidth = self.width() - scrollWidth - margin

        columns     = int(widgetWidth/assetWidth)
        offsetWidth = int(widgetWidth / columns )
        offset      = int( (offsetWidth-assetWidth)/2 )


        model = self.model()


        folderCount = int()
        assetCount  = int()
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.EditRole)

            if   data["type"] == "folder": folderCount += 1
            elif data["type"] == "asset":  assetCount  += 1

        if folderCount <= columns and assetCount <= columns:
            offset = 0


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
                    if positionX + folderWidth + offset*2 > widgetWidth + margin:
                        positionX  = margin
                        positionY += folderHeight

                    item.setSizeHint(
                        QtCore.QSize(
                            folderWidth,
                            folderHeight ))

                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )

                    positionX += folderWidth + offset

            positionX  = margin
            positionY += margin + folderHeight


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
                    if positionX + assetWidth + offset*2 > widgetWidth + margin:
                        positionX  = margin
                        positionY += assetHeight

                    item.setSizeHint(
                        QtCore.QSize(
                            assetWidth,
                            assetHeight ))

                    self.setPositionForIndex(
                        QtCore.QPoint(positionX, positionY), 
                        model.index(index, 0) )

                    positionX += assetWidth + offset


        with Settings.UIManager(update=False) as uiSettings:
            scrollPosition = uiSettings["scrollPosition"]

            self.verticalScrollBar().setValue(
                self.intScrollPosition(scrollPosition) )



    def enterEvent (self, event):

        super(AssetBrowser, self).enterEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)



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

        iconType = index.data(QtCore.Qt.EditRole)["type"]

        model = index.model()
        for raw in range(model.rowCount()):
            item = model.item(raw)

            if raw == index.row() and iconType == "asset":

                if index.data(QtCore.Qt.StatusTipRole) == 1:
                    item.setData(0, QtCore.Qt.StatusTipRole)
                else:
                    item.setData(1, QtCore.Qt.StatusTipRole)

            else:
                item.setData(0, QtCore.Qt.StatusTipRole)


        self.iconClicked.emit(index)








if __name__ == "__main__":

    application = QtWidgets.QApplication([])
    widget = AssetBrowser()
    widget.show()
    application.exec_()
