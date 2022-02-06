#!/bin/python


import os


from Qt import (
    QtWidgets,
    QtCore,
    QtGui
)


from . import AssetBrowser
from . import IconDelegate
from . import PathWidget

from . import ExportUI


from . import Settings
UIsettings = Settings.UIsettings

from . import tools

from . import resources
from . import stylesheet








class ExportWidget (QtWidgets.QWidget, ExportUI.Widget):


    def __init__(self):
        super(ExportWidget, self).__init__()

        self.setStyleSheet( stylesheet.UI )

        self.browserLayout = QtWidgets.QVBoxLayout()
        self.browserLayout.setContentsMargins(0, 0, 0, 0)
        self.browserLayout.setSpacing(0)

        self.pathLayout = QtWidgets.QHBoxLayout()
        self.pathLayout.setContentsMargins(0, 0, 0, 0)
        self.pathLayout.setSpacing(0)
        self.browserLayout.addItem(self.pathLayout)


        self.assetPath = PathWidget.PathWidget()
        self.assetPath.pathChanged.connect(self.drawBrowserItems)
        self.pathLayout.addWidget(self.assetPath)


        self.AssetBrowser = AssetBrowser.AssetBrowser()
        self.AssetBrowser.iconClicked.connect(self.iconClicked)
        self.browserLayout.addWidget(self.AssetBrowser)


        self.setupUi(self, self.browserLayout)

        self.metadata  = ".metadata.json"
        self.libraries = self.getAssetRoots()
        self.setLibrary()



    def getAssetRoots (self):

        libraries = dict()
        path = os.getenv("ASSETLIBS", "")

        for rootPath in path.split(":"):
            assetPath = os.path.join(rootPath, self.metadata)

            if os.path.exists(assetPath):
                data = tools.dataread(assetPath)

                if data["type"] == "root":
                    name = data["name"]
                    libraries[name] = rootPath

        return libraries



    def setLibrary (self, name=None):

        if name:
            path = tools.keydata(self.libraries, name)
            if path:
                with Settings.UIManager(update=True) as uiSettings:

                    uiSettings["subdirLibrary"] = ""
                    uiSettings["focusLibrary"]  = name
                    self.assetPath.setRoot(name, path)
                    return


        with Settings.UIManager(update=False) as uiSettings:

            name = uiSettings["focusLibrary"]
            path = tools.keydata(self.libraries, name)

            if path:
                self.assetPath.setRoot(name, path)
                return


        for name, path in self.libraries.items():
            with Settings.UIManager(update=True) as uiSettings:

                uiSettings["subdirLibrary"] = ""
                uiSettings["focusLibrary"]  = name
            
            self.assetPath.setRoot(name, path)
            return


        self.assetPath.setRoot("", "")



    def iconClicked (self, index):

        data = index.data()
        dataType = data["type"]

        if dataType == "folder":
            name = data["data"]["name"]
            self.assetPath.moveForward(name)



    def getDirItems (self, path):

        if not path:
            return []
    
        library = []

        for name in os.listdir(path):

            if name == self.metadata:
                continue

            folderPath = os.path.join(path, name)

            assetPath = os.path.join(
                folderPath, self.metadata)

            if os.path.exists(assetPath):
                data = tools.dataread(assetPath)

                dataType = data["type"]
                dataTime = data["published"]

                publishedTime = tools.getTimeDifference(dataTime)
                leadItem = tools.getUsdLeadItem(folderPath)

                if dataType == "usdasset":
                    library.append(
                        dict(type="asset",  data=dict(
                            name=name,
                            preview=tools.getUsdPreview(folderPath, leadItem),
                            type=dataType,
                            version=tools.getVersion(leadItem),
                            published=publishedTime,
                            status=data["status"] )) )


            elif os.path.exists(folderPath):
                if os.path.isdir(folderPath):
                    library.append(
                        dict(type="folder", data=dict(
                            name=name,
                            items=tools.getItemsCount(folderPath) )) )


        return library



    def drawBrowserItems (self, path):

        library = self.getDirItems(path)

        hasFolder = False
        hasAsset  = False
        for item in library:
            if hasFolder and hasAsset:
                break

            elif item["type"] == "folder" and not hasFolder:
                hasFolder = True
                library.append( dict(type="labelfolder", data=dict(text="Folders")) )

            elif item["type"] == "asset" and not hasAsset:
                hasAsset = True
                library.append( dict(type="labelasset", data=dict(text="Assets")) )


        iconModel = QtGui.QStandardItemModel(self.AssetBrowser)

        for item in library:

            if item["type"] == "asset":
                hasAsset = True
            else:
                hasFolder = True

            iconItem = QtGui.QStandardItem()

            iconItem.setCheckable(False)
            iconItem.setEditable(True)

            iconItem.setData(
                0,
                QtCore.Qt.StatusTipRole)

            iconItem.setData(
                dict(type=item["type"], data=item["data"]),
                QtCore.Qt.EditRole)


            iconModel.appendRow(iconItem)


        self.AssetBrowser.setModel(iconModel)
        self.AssetBrowser.setItemDelegate(
            IconDelegate.Delegate(self.AssetBrowser) )


        self.AssetBrowser.setGrid()







if __name__ == "__main__":

    application = QtWidgets.QApplication([])
    widget = ExportWidget()
    widget.show()
    application.exec_()
