#!/usr/bin/env python



import os
import re

import toolkit.system.ostree
import toolkit.system.stream

import toolkit.core.metadata
import toolkit.core.naming
import toolkit.core.timing

from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from .items import LibraryDelegate
from .items import DirectoryDelegate
from .items import FolderDelegate
from .items import AssetUsdDelegate

from . import Metadata
from . import Settings









class Bookmark (object):



    def bookmarkIndex (self):

        pathUI = self.AssetPath.getUI()
        count = self.BarBottom.bookmarkCombobox.count()

        for index in range(count):
            text = self.BarBottom.bookmarkCombobox.itemText(index)

            if pathUI == text:
                return index



    def switchBookmark (self):

        index = self.bookmarkIndex()
        if index != None:

            pathUI = self.BarBottom.bookmarkCombobox.itemText(index)
            with Settings.Manager(self.theme.app, True) as settings:
                if pathUI in settings["bookmarks"]:
                    settings["bookmarks"].remove(pathUI)

            self.BarBottom.bookmarkCombobox.removeItem(index)

        else:
            pathUI = self.AssetPath.getUI()
            with Settings.Manager(self.theme.app, True) as settings:
                settings["bookmarks"].append(pathUI)

            self.BarBottom.bookmarkCombobox.addItem(pathUI)
            self.sortBookmarks()



    def jumpBookmark (self, pathUI):

        if pathUI == self.AssetPath.getUI():
            return
        self.AssetPath.setUI(pathUI)

        self.BarBottom.bookmarkCombobox.setCurrentIndex(-1)



    def sortBookmarks (self):

        bookmarks = []

        count = self.BarBottom.bookmarkCombobox.count()
        for index in range(count):
            pathUI = self.BarBottom.bookmarkCombobox.itemText(index)
            bookmarks.append(pathUI)

        bookmarks.sort()

        self.BarBottom.bookmarkCombobox.clear()
        self.BarBottom.bookmarkCombobox.addItems(bookmarks)








class Favorite (object):



    def favoriteClicked (self, index):

        model = self.AssetBrowser.model()
        iconItem = model.item(index.row())
        data = index.data(QtCore.Qt.EditRole)

        dataType = data.get("type")

        if dataType == "usdasset":
            name = data.get("name")
            pathUI = os.path.join(
                self.AssetPath.getUI(), name)

        elif dataType == "colorguide":
            title = data.get("title")
            name = data.get("name")
            pathUI = os.path.join(
                self.AssetPath.getUI(), title + name )

        elif dataType == "color":
            code = data.get("code")
            pathUI = ":".join([
                self.AssetPath.getUI(), code ])

        else: return


        with Settings.Manager(self.theme.app, True) as settings:

            if pathUI not in settings.get("favorites"):
                settings["favorites"].append(pathUI)
                data["favorite"] = True

            else:
                settings["favorites"].remove(pathUI)
                data["favorite"] = False

        iconItem.setData(data, QtCore.Qt.EditRole)

        if self.BarBottom.favorite.button.isChecked():
            self.favoriteFilter(update=True)



    def favoriteFilter (self, update=False):

        favoriteFilter = self.BarBottom.favorite.button.isChecked()

        if not update:
            with Settings.Manager(self.theme.app, True) as settings:
                settings["favoriteFilter"] = favoriteFilter

                if favoriteFilter:
                    favorites = []
                    for pathUI in settings.get("favorites"):
                        if self.AssetPath.exists(pathUI):
                            favorites.append(pathUI)
                    settings["favorites"] = favorites

        path = self.AssetPath.resolve()
        self.drawDecision(path)








class Slider (object):



    def sliderAction (self, value):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["iconSize"] = value

        self.AssetBrowser.setGrid()
        self.AssetBrowser.adjustSize()








class Folder (object):



    def createFolderQuery (self, index):

        model = self.AssetBrowser.model()
        iconItem = model.item(index.row())

        dataItem = dict( type="folderquery", name="", items=0 )
        iconItem.setData(dataItem, QtCore.Qt.EditRole)

        self.AssetBrowser.setCurrentIndex(index)
        self.AssetBrowser.edit(index)



    def createFolder (self, index, name):

        model = self.AssetBrowser.model()
        updateItem = model.item(index.row())

        newPath = os.path.join(
            self.AssetPath.resolve(), name)
        if not name or os.path.exists(newPath):
            updateItem.setData(
                dict( type="plusfolder" ), QtCore.Qt.EditRole)
            self.AssetBrowser.repaint()

        else:
            updateItem.setData(
                dict( type="folder", name=name, items=0 ),
                QtCore.Qt.EditRole)

            plusItem = QtGui.QStandardItem()
            plusItem.setCheckable(False)
            plusItem.setEditable(True)
            plusItem.setData(0, QtCore.Qt.StatusTipRole)

            plusItem.setData(dict(type="plusfolder"), QtCore.Qt.EditRole)

            model.appendRow(plusItem)

            self.AssetBrowser.setGrid()
            os.mkdir(newPath)








class Browser (object):


    def __init__(self):
        self.metafile = Metadata.NAME
        self.assetsNames = list()



    def getDirItems (self, path,
            filterFavorites=False,
            showTypes=[
                "foldercolors",
                "usdasset" ] ):

        if not path:
            return []
    
        library = []
        self.assetsNames = []

        favorites = []
        with Settings.Manager(self.theme.app, False) as settings:
            favorites = settings.get("favorites", [])

        for name in os.listdir(path):

            if name == self.metafile:
                continue

            folderPath = os.path.join(path, name)
            dataType = toolkit.core.metadata.getType(folderPath)

            if dataType == "usdasset":
                if dataType not in showTypes:
                    continue

                data = {}
                with Metadata.MetadataManager(
                        folderPath, "usdasset") as metadata:
                    data = metadata

                chosenItem = toolkit.core.naming.chooseAssetItem(folderPath)

                versionCount = toolkit.core.naming.getVersionList(folderPath)
                versionCount = len(versionCount)

                dataTime = data.get("items").get(chosenItem).get("published")
                publishedTime = toolkit.core.timing.getTimeDifference(dataTime)

                favorite = False
                pathUI = os.path.join(self.AssetPath.getUI(), name)
                if pathUI in favorites:
                    favorite = True

                if filterFavorites and not favorite:
                    continue

                library.append(dict(
                    type=dataType,
                    name=name,
                    previews=toolkit.core.naming.getUsdPreviews(folderPath, chosenItem),
                    version=toolkit.core.naming.getVersion(chosenItem),
                    count=versionCount,
                    variant=toolkit.core.naming.getVariantName(chosenItem),
                    animation=toolkit.core.naming.getAnimationName(chosenItem),
                    published=publishedTime,
                    status=data.get("status"),
                    favorite=favorite ))
                self.assetsNames.append(name)


            elif dataType == "foldercolors":
                if dataType not in showTypes:
                    continue

                data = {}
                with Metadata.MetadataManager(
                        folderPath, "foldercolors") as metadata:
                    data = metadata

                library.append(dict(
                    type="foldercolors",
                    name=name,
                    items=toolkit.system.ostree.getGroupCount(folderPath) ))


            elif os.path.exists(folderPath):
                if os.path.isdir(folderPath):
                    library.append(dict(
                        type="folder",
                        name=name,
                        items=toolkit.system.ostree.getItemCount(folderPath) ))


        return library



    def getLibraries (self):
    
        libraries = []
        self.assetsNames = []

        for name, path in self.AssetPath.libraries.items():
            libraries.append(dict( type="library", name=name ))

        return libraries



    def drawDecision (self, path):

        flag = self.BarBottom.favorite.button.isChecked()
        self.drawBrowserItems(path, filterFavorites=flag)



    def drawBrowserItems (self, path,
            filterFavorites=False):


        if not path:
            browserItems = self.getLibraries()
        else:
            browserItems = self.getDirItems(
                path,
                filterFavorites=filterFavorites )


        hasLibrary = False
        hasFolder  = False
        hasAsset   = False
        for item in browserItems:
            if hasLibrary:
                break
            elif hasAsset and hasFolder:
                break

            elif item["type"] == "library" and not hasLibrary:
                hasLibrary = True

            elif item["type"] in ["folder", "foldercolors"] and not hasFolder:
                hasFolder = True

            elif item["type"] == "usdasset" and not hasAsset:
                hasAsset = True

        if hasLibrary:
            browserItems.append(dict( type="labellibrary", text="Libraries" ))

        if hasFolder or not hasLibrary and not hasAsset and not filterFavorites:
            browserItems.append(dict( type="labelfolder", text="Folders" ))
            browserItems.append(dict( type="plusfolder" ))

        if hasAsset:
            browserItems.append(dict( type="labelasset", text="Assets" ))


        iconModel = QtGui.QStandardItemModel(self.AssetBrowser)

        for item in self.sortItems(browserItems):

            iconItem = QtGui.QStandardItem()

            iconItem.setCheckable(False)
            iconItem.setEditable(True)

            iconItem.setData(
                0,
                QtCore.Qt.StatusTipRole)

            iconItem.setData(item, QtCore.Qt.EditRole)

            if self.checkedName == item.get("name"):
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



    def sortItems (self, library):

        labelL    = []
        labelF    = []
        labelA    = []
        plus      = []
        libraries = []
        folders   = []
        usdasset  = []
        usdfile   = []
        guides    = []
        colors    = []

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
            elif dataType in ["folder", "foldercolors"]:
                folders += [data]
            elif dataType == "usdasset":
                usdasset += [data]
            elif dataType == "usdfile":
                usdfile += [data]
            elif dataType == "colorguide":
                guides += [data]
            elif dataType == "color":
                colors += [data]

        for data in [
                libraries,
                folders,
                usdasset,
                guides]:
            data.sort(
                key=lambda item : item.get("name")
            )

        for data in [usdfile]:
            data.sort(
                key=lambda item : "{}{}{}{}".format(
                    item.get("name"),
                    item.get("version"),
                    item.get("variant"),
                    item.get("animation")
                )
            )


        def code (item):

            value = item.get("code")

            match = re.search(r"^\d*-0D", value)
            if match:
                match = match.group()
                string = re.sub(r"0D$", "10D", match)
                value = re.sub(match, string, value)

            match = re.search(r"^\d*-\dD", value)
            if match:
                value = value[:-2] +"0"+ value[-2:]

            dot = False
            sting = ""

            for character in value:

                if character.isdigit():
                    sting += character

                elif character in ["-", " "]:
                    if not dot:
                        dot = True
                        sting += "."
                else:
                    sting += str(ord(character))

            return float(sting)

        for data in [colors]:
            data.sort(key=code)


        library = (
            labelL
            + labelF
            + labelA
            + plus
            + libraries
            + folders
            + usdasset
            + usdfile
            + guides
            + colors
        )

        return library



    def linkAction (self, index):

        data = index.data(QtCore.Qt.EditRole)
        dataType = data.get("type")

        if dataType in ["folder", "usdasset"]:
            path = os.path.join(
                self.AssetPath.resolve(),
                data.get("name") )
            if os.path.exists(path):
                toolkit.system.stream.openFolder(path)
        
        elif dataType == "usdfile":
            path = os.path.join(
                self.AssetPath.resolve(),
                data.get("filename") )
            if os.path.exists(path):
                toolkit.system.stream.openUsd(path)








class State (object):



    def applyUiSettings (self):

        blacklist = []
        with Settings.Manager(self.theme.app, False) as settings:

            if settings.get("favoriteFilter"):
                self.BarBottom.favorite.button.setChecked(True)


            self.BarBottom.bookmarkCombobox.clear()
            bookmarks = settings.get("bookmarks")
            for pathUI in bookmarks:
                if not self.AssetPath.exists(pathUI):
                    blacklist.append(pathUI)

                self.BarBottom.bookmarkCombobox.addItem(pathUI)

            size = settings.get("size")
            self.resize(*size)


        if blacklist:
            with Settings.Manager(self.theme.app, True) as settings:
                for pathUI in blacklist:
                    settings["bookmarks"].remove(pathUI)


        self.sortBookmarks()
        self.BarBottom.bookmarkCombobox.setCurrentIndex(-1)




    def setUiPath (self, pathUI=None):

        if not pathUI:
            with Settings.Manager(self.theme.app, False) as settings:
                pathUI = settings.get("location")

        if not self.AssetPath.exists(pathUI):
            pathUI = ""
        
        self.AssetPath.setUI(pathUI)
