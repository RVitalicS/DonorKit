#!/usr/bin/env python



import os
import re

from . import tools

from Qt import QtWidgets, QtCore, QtGui

from .items import LibraryDelegate
from .items import DirectoryDelegate
from .items import FolderDelegate
from .items import AssetUsdDelegate

from . import Metadata
from . import Settings








class Bookmark (QtWidgets.QWidget):



    def bookmarkIndex (self):

        pathUI = self.getPathUI()
        count = self.BarBottom.bookmarkCombobox.count()

        for index in range(count):
            text = self.BarBottom.bookmarkCombobox.itemText(index)

            if pathUI == text:
                return index



    def actionBookmark (self):

        index = self.bookmarkIndex()
        if index is not None:

            pathID = self.BarBottom.bookmarkCombobox.itemData(index)
            with Settings.Manager(update=True) as settings:
                if pathID in settings["bookmarks"]:
                    settings["bookmarks"].remove(pathID)

            self.BarBottom.bookmarkCombobox.removeItem(index)

        else:
            pathUI = self.getPathUI()
            pathID = self.getPathID()

            with Settings.Manager(update=True) as settings:
                settings["bookmarks"] += [pathID]

            self.BarBottom.bookmarkCombobox.addItem(pathUI, pathID)
            self.sortBookmarks()



    def getPathUI (self):

        root   = self.AssetPath.pathRoot.text()
        subdir = self.AssetPath.pathLine.text()

        if subdir:
            return root +"/"+ subdir
        else:
            return root



    def getPathID (self, asset=None):

        library = self.AssetPath.pathRoot.text()
        subdir  = self.AssetPath.pathLine.text()

        path = "{"+ library +"}" + subdir

        if asset is not None:
            path += "/" + asset

        return path



    def jumpBookmark (self, pathID):

        bookmark = self.interpretID(pathID)
        if bookmark is not None:
            library, subdir = bookmark

            newRoot = False
            if library != self.AssetPath.pathRoot.text():
                newRoot = True

            newSubd = False
            if subdir != self.AssetPath.pathLine.text():
                newSubd = True

            if not newRoot and not newSubd:
                return

            self.setLibrary(library, finish=False)
            success = self.AssetPath.changeSubdir(subdir)

            if not success:
                with Settings.Manager(update=True) as settings:
                    if pathID in settings["bookmarks"]:
                        settings["bookmarks"].remove(pathID)

                count = self.BarBottom.bookmarkCombobox.count()
                for index in range(count):
                    data = self.BarBottom.bookmarkCombobox.itemData(index)
                    if pathID == data:
                        self.BarBottom.bookmarkCombobox.removeItem(index)
                        break

            self.BarBottom.bookmarkCombobox.setCurrentIndex(-1)



    def interpretID (self, pathID):

        key = re.search(r"\{.*\}", pathID)
        if key:
            key = key.group()

            library = re.sub(r"[\{\}]", "", key)
            subdir = re.sub(key, "", pathID)

            return (library, subdir)



    def translateID (self, pathID):

        path = ""
        bookmark = self.interpretID(pathID)

        if bookmark is not None:
            root, subdir = bookmark

            root = self.libraries.get(root)
            if root is not None:

                if subdir:
                    path = root +"/"+ subdir
                else:
                    path = root

        return path



    def sortBookmarks (self):

        count = self.BarBottom.bookmarkCombobox.count()
        bookmarks = []

        for index in range(count):
            pathUI = self.BarBottom.bookmarkCombobox.itemText(index)
            pathID = self.BarBottom.bookmarkCombobox.itemData(index)
            bookmarks += [ { "UI":pathUI, "ID":pathID } ]

        self.BarBottom.bookmarkCombobox.clear()
        bookmarks.sort( key=lambda item : item.get("ID") )

        for item in bookmarks:
            pathUI = item.get("UI")
            pathID = item.get("ID")
            self.BarBottom.bookmarkCombobox.addItem(pathUI, pathID)



    def applySettings (self):

        blacklist = []
        with Settings.Manager(update=False) as settings:

            if settings.get("favoriteFilter"):
                self.BarBottom.favorite.button.setChecked(True)


            self.BarBottom.bookmarkCombobox.clear()
            bookmarks = settings.get("bookmarks")
            for data in bookmarks:
                bookmark = self.interpretID(data)
                if bookmark is not None:
                    library, subdir = bookmark

                    name = library
                    if subdir: name += "/"+ subdir

                    if library not in self.libraries:
                        blacklist.append(data)
                        continue

                    root = self.libraries.get(library, "")
                    path = os.path.join(root, name)
                    if os.path.exists(path):
                        blacklist.append(data)
                        continue

                    self.BarBottom.bookmarkCombobox.addItem(name, data)

        if blacklist:
            with Settings.Manager(update=True) as settings:
                for data in blacklist:
                    settings["bookmarks"].remove(data)


        self.sortBookmarks()
        self.BarBottom.bookmarkCombobox.setCurrentIndex(-1)







class Favorite (QtWidgets.QWidget):



    def favoriteClicked (self, index):

        model = self.AssetBrowser.model()
        iconItem = model.item(index.row())
        data = index.data(QtCore.Qt.EditRole)

        name = data.get("data").get("name")
        pathID = self.getPathID(asset=name)

        with Settings.Manager(update=True) as settings:

            if pathID not in settings.get("favorites"):
                settings["favorites"] += [pathID]
                data["data"]["favorite"] = True

            else:
                settings["favorites"].remove(pathID)
                data["data"]["favorite"] = False

        iconItem.setData(data, QtCore.Qt.EditRole)

        if self.BarBottom.favorite.button.isChecked():
            self.favoriteFilter(update=True)



    def favoriteFilter (self, update=False):

        favoriteFilter = self.BarBottom.favorite.button.isChecked()

        if not update:
            with Settings.Manager(update=True) as settings:
                settings["favoriteFilter"] = favoriteFilter

                if favoriteFilter:
                    favorites = []
                    for pathID in settings.get("favorites"):
                        path = self.translateID(pathID)
                        if os.path.exists(path):
                            favorites.append(pathID)
                    settings["favorites"] = favorites

        self.drawBrowserItems( self.AssetPath.get() )








class Slider (QtWidgets.QWidget):



    def sliderAction (self, value):

        with Settings.Manager(update=True) as settings:
            settings["iconSize"] = value

        self.AssetBrowser.setGrid()
        self.AssetBrowser.adjustSize()








class Folder (QtWidgets.QWidget):



    def createFolderQuery (self, index):

        model = self.AssetBrowser.model()
        iconItem = model.item(index.row())

        dataItem = dict(type="folderquery", data=dict(
                            name="",
                            items=0 ))
        iconItem.setData(dataItem, QtCore.Qt.EditRole)

        self.AssetBrowser.setCurrentIndex(index)
        self.AssetBrowser.edit(index)



    def createFolder (self, index, name):

        model = self.AssetBrowser.model()
        updateItem = model.item(index.row())

        newPath = os.path.join(
            self.AssetPath.get(), name)
        if not name or os.path.exists(newPath):
            updateData = dict(type="plusfolder", data=dict())
            updateItem.setData(updateData, QtCore.Qt.EditRole)
            self.AssetBrowser.repaint()

        else:
            updateData = dict(type="folder", data=dict(
                            name=name, items=0 ))
            updateItem.setData(updateData, QtCore.Qt.EditRole)

            plusItem = QtGui.QStandardItem()
            plusItem.setCheckable(False)
            plusItem.setEditable(True)
            plusItem.setData(0, QtCore.Qt.StatusTipRole)

            plusItem.setData(
                dict(type="plusfolder", data=dict()),
                QtCore.Qt.EditRole)

            model.appendRow(plusItem)

            self.AssetBrowser.setGrid()
            os.mkdir(newPath)



    def openFolder (self, index):

        model = self.AssetBrowser.model()
        updateItem = model.item(index.row())
        data = index.data(QtCore.Qt.EditRole)

        path = os.path.join(
            self.AssetPath.get(),
            data.get("data").get("name") )

        if os.path.exists(path):
            tools.openFolder(path)








class Library (QtWidgets.QWidget):



    def getAssetRoots (self):

        libraries = dict()
        path = os.getenv("ASSETLIBS", "")

        for rootPath in path.split(":"):
            assetPath = os.path.join(rootPath, self.metafile)

            if os.path.exists(assetPath):
                data = tools.dataread(assetPath)

                if data["type"] == "root":
                    name = data["name"]
                    libraries[name] = rootPath

        return libraries



    def setLibrary (self, name=None, finish=True):

        self.setIsolation(False)

        if name:

            path = self.libraries.get(name, None)
            if path is not None:

                with Settings.Manager(update=True) as settings:

                    settings["subdirLibrary"] = ""
                    settings["focusLibrary"]  = name
                    self.AssetPath.setRoot(name, path, finish)
                    return


        with Settings.Manager(update=False) as settings:

            name = settings["focusLibrary"]
            
            path = self.libraries.get(name, None)
            if path is not None:
                
                self.AssetPath.setRoot(name, path, finish)
                return

            elif name == "":
                self.drawBrowserItems("")
                return


        for name, path in self.libraries.items():
            with Settings.Manager(update=True) as settings:

                settings["subdirLibrary"] = ""
                settings["focusLibrary"]  = name
            
            self.AssetPath.setRoot(name, path, finish)
            return


        self.AssetPath.setRoot("", "", finish)



    def sort (self, library):

        labelL    = []
        labelF    = []
        labelA    = []
        plus      = []
        libraries = []
        folders   = []
        usdasset  = []
        usdfile   = []

        for data in library:
            dataType = data.get("type")

            if dataType == "labellibrary":
                labelL += [data]
            elif dataType == "labelfolder":
                labelF += [data]
            elif dataType == "labelasset":
                labelA += [data]
            elif dataType == "plusfolder":
                plus += [data]
            elif dataType == "library":
                libraries += [data]
            elif dataType == "folder":
                folders += [data]

            elif dataType == "asset":
                assetType = data.get("data").get("type")

                if assetType == "usdasset":
                    usdasset += [data]
                elif assetType == "usdfile":
                    usdfile += [data]

        for data in [libraries, folders, usdasset]:
            data.sort(
                key=lambda item : item.get("data").get("name") )

        for data in [usdfile]:
            data.sort(
                key=lambda item : "{}{}{}{}".format(
                    item.get("data").get("name"),
                    item.get("data").get("version"),
                    item.get("data").get("variant"),
                    item.get("data").get("animation") ))

        library = (
            labelL
            + labelF
            + labelA
            + plus
            + libraries
            + folders
            + usdasset
            + usdfile
        )

        return library








class Browser (QtWidgets.QWidget):



    def setIsolation (self, flag):

        flag = not flag

        self.AssetPath.setVisible(flag)
        self.BarBottom.setVisible(flag)



    def getDirItems (self, path, filterFavorites=False):

        if not path:
            return []
    
        library = []
        self.assetsNames = []

        favorites = []
        with Settings.Manager(update=False) as settings:
            favorites = settings.get("favorites", [])

        for name in os.listdir(path):

            if name == self.metafile:
                continue

            folderPath = os.path.join(path, name)

            assetPath = os.path.join(
                folderPath, self.metafile)

            if os.path.exists(assetPath):

                data = {}
                with Metadata.MetadataManager(
                        folderPath, "usdasset") as metadata:
                    data = metadata

                chosenItem = tools.chooseAssetItem(folderPath)

                versionCount = tools.getVersionList(folderPath)
                versionCount = len(versionCount)

                dataType = data["type"]
                dataTime = data["items"][chosenItem]["published"]
                publishedTime = tools.getTimeDifference(dataTime)

                if dataType == "usdasset":

                    favorite = False
                    pathID = self.getPathID(asset=name)
                    if pathID in favorites:
                        favorite = True

                    if filterFavorites and not favorite:
                        continue

                    library.append(
                        dict(type="asset",  data=dict(
                            name=name,
                            previews=tools.getUsdPreviews(folderPath, chosenItem),
                            type=dataType,
                            version=tools.getVersion(chosenItem),
                            count=versionCount,
                            variant=tools.getVariantName(chosenItem),
                            animation=tools.getAnimationName(chosenItem),
                            published=publishedTime,
                            status=data["status"],
                            favorite=favorite )) )
                    self.assetsNames.append(name)


            elif os.path.exists(folderPath):
                if os.path.isdir(folderPath):
                    library.append(
                        dict(type="folder", data=dict(
                            name=name,
                            items=tools.getItemsCount(folderPath) )) )


        return library



    def getLibraries (self):
    
        libraries = []
        self.assetsNames = []

        for name, path in self.libraries.items():
            libraries.append(
                dict(type="library", data=dict(
                    name=name )) )

        return libraries



    def drawBrowserItems (self, path):
        
        if not self.bookmarkIndex() is None:
            self.AssetPath.bookmarkButton.setChecked(True)
        else:
            self.AssetPath.bookmarkButton.setChecked(False)


        if not path:
            self.setIsolation(True)
            library = self.getLibraries()
        else:
            library = self.getDirItems(
                path,
                filterFavorites=self.BarBottom.favorite.button.isChecked() )


        hasLibrary = False
        hasFolder  = False
        hasAsset   = False
        for item in library:
            if hasLibrary:
                break
            elif hasAsset and hasFolder:
                break

            elif item["type"] == "library" and not hasLibrary:
                hasLibrary = True

            elif item["type"] == "folder" and not hasFolder:
                hasFolder = True

            elif item["type"] == "asset" and not hasAsset:
                hasAsset = True

        if hasLibrary:
            library.append( dict(type="labellibrary", data=dict(text="Libraries")) )

        if hasFolder or not hasLibrary and not hasAsset:
            library.append( dict(type="labelfolder", data=dict(text="Folders")) )
            library.append( dict(type="plusfolder", data=dict()) )

        if hasAsset:
            library.append( dict(type="labelasset", data=dict(text="Assets")) )


        iconModel = QtGui.QStandardItemModel(self.AssetBrowser)

        for item in self.sort(library):

            iconItem = QtGui.QStandardItem()

            iconItem.setCheckable(False)
            iconItem.setEditable(True)

            iconItem.setData(
                0,
                QtCore.Qt.StatusTipRole)

            iconItem.setData(
                dict(type=item["type"], data=item["data"]),
                QtCore.Qt.EditRole)

            if self.checkedName == item.get("data").get("name"):
                iconItem.setData(1, QtCore.Qt.StatusTipRole)

            iconModel.appendRow(iconItem)


        self.AssetBrowser.setModel(iconModel)

        if hasLibrary:
            self.AssetBrowser.setItemDelegate(
                LibraryDelegate.Delegate(self.AssetBrowser, self.theme) )

        elif not hasAsset:
            self.AssetBrowser.setItemDelegate(
                FolderDelegate.Delegate(self.AssetBrowser, self.theme) )

        elif not hasFolder:
            self.AssetBrowser.setItemDelegate(
                AssetUsdDelegate.Delegate(self.AssetBrowser, self.theme) )

        else:
            self.AssetBrowser.setItemDelegate(
                DirectoryDelegate.Delegate(self.AssetBrowser, self.theme) )


        self.AssetBrowser.setGrid()
