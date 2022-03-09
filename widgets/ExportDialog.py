#!/usr/bin/env python



import os
import re

from . import resources
from . import theme
from . import tools


from Qt import QtWidgets, QtCore, QtGui

from . import LibraryDelegate
from . import DirectoryDelegate
from . import FolderDelegate
from . import AssetUsdDelegate

from . import AssetBrowser
from . import PathBar
from . import BottomBar

from . import ExportUI

from . import Metadata
from . import Settings










class ExportDialog (QtWidgets.QDialog):


    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent)

        self.theme = theme.Theme(application="export")
        
        self.metadata  = Metadata.NAME
        self.libraries = self.getAssetRoots()

        self.assetsNames = []
        self.exported = False

        self.setStyleSheet( self.theme.getStyleSheet() )

        self.browserLayout = QtWidgets.QVBoxLayout()
        self.browserLayout.setContentsMargins(0, 0, 0, 0)
        self.browserLayout.setSpacing(0)

        self.AssetPath = PathBar.PathBar(self.theme)
        self.browserLayout.addWidget(self.AssetPath)

        self.AssetBrowser = AssetBrowser.AssetBrowser()
        self.browserLayout.addWidget(self.AssetBrowser)

        self.BottomBar = BottomBar.BottomBar(self.theme)
        self.browserLayout.addWidget(self.BottomBar)

        ExportUI.setupUi(self, self.browserLayout, self.theme)
        self.connectUi()
        self.applySettings()

        self.setWindowTitle("Asset Export")
        self.setObjectName("ExportDialog")
        self.resize(820, 580)

        self.setLibrary()
        self.AssetBrowser.setFocus(QtCore.Qt.MouseFocusReason)



    def setIsolation (self, flag):

        flag = not flag

        self.AssetPath.setVisible(flag)
        self.BottomBar.setVisible(flag)



    def connectUi (self):

        self.AssetBrowser.iconClicked.connect(self.iconClicked)
        self.AssetBrowser.favoriteClicked.connect(self.favoriteClicked)
        self.AssetBrowser.link.connect(self.openFolder)
        self.AssetBrowser.createFolderQuery.connect(self.createFolderQuery)
        self.AssetBrowser.createFolder.connect(self.createFolder)

        self.AssetPath.pathChanged.connect(self.drawBrowserItems)
        self.AssetPath.bookmarkClicked.connect(self.actionBookmark)

        self.BottomBar.preview.slider.valueChanged.connect(self.sliderAction)
        self.BottomBar.favorite.button.released.connect(self.favoriteFilter)
        self.BottomBar.bookmarkChoosed.connect(self.jumpBookmark)

        self.nameEdit.textChanged.connect(self.setName)

        self.modelingSwitch.released.connect(self.partitionExport)
        self.surfacingSwitch.released.connect(self.partitionExport)
        self.animationSwitch.released.connect(self.partitionExport)

        self.modelingOverwrite.released.connect(self.overwriteState)
        self.surfacingOverwrite.released.connect(self.overwriteState)
        self.animationOverwrite.released.connect(self.overwriteState)

        self.modelingOverwrite.released.connect(
            self.modelingOverwriteSetting )
        self.surfacingOverwrite.released.connect(
            self.surfacingOverwriteSetting )
        self.animationOverwrite.released.connect(
            self.animationOverwriteSetting )

        self.animationOpions.animationNameCombobox.currentTextChanged.connect(self.interpretTags)
        self.animationOpions.rangeStartSpinbox.valueChanged.connect(self.setRangeStart)
        self.animationOpions.rangeEndSpinbox.valueChanged.connect(self.setRangeEnd)

        self.animationOpions.rangeButton.released.connect(self.getRange)

        self.mainOpions.variantCombobox.currentTextChanged.connect(self.interpretTags)
        self.mainOpions.versionCombobox.currentTextChanged.connect(self.versionChoice)

        self.mainOpions.linkButton.released.connect(self.linkWrap)

        self.exportButton.pressed.connect(self.exportQuery)
        self.exportButton.released.connect(self.exportAction)



    def bookmarkIndex (self):

        pathUI = self.getPathUI()
        count = self.BottomBar.bookmarkCombobox.count()

        for index in range(count):
            text = self.BottomBar.bookmarkCombobox.itemText(index)

            if pathUI == text:
                return index



    def actionBookmark (self):

        index = self.bookmarkIndex()
        if not index is None:

            pathID = self.BottomBar.bookmarkCombobox.itemData(index)
            with Settings.Manager(update=True) as settings:
                if pathID in settings["bookmarks"]:
                    settings["bookmarks"].remove(pathID)

            self.BottomBar.bookmarkCombobox.removeItem(index)

        else:
            pathUI = self.getPathUI()
            pathID = self.getPathID()

            with Settings.Manager(update=True) as settings:
                settings["bookmarks"] += [pathID]

            self.BottomBar.bookmarkCombobox.addItem(pathUI, pathID)
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

        if not asset is None:
            path += "/" + asset

        return path



    def jumpBookmark (self, pathID):

        bookmark = self.interpretID(pathID)
        if not bookmark is None:
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

                count = self.BottomBar.bookmarkCombobox.count()
                for index in range(count):
                    data = self.BottomBar.bookmarkCombobox.itemData(index)
                    if pathID == data:
                        self.BottomBar.bookmarkCombobox.removeItem(index)
                        break

            self.BottomBar.bookmarkCombobox.setCurrentIndex(-1)



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

        if not bookmark is None:
            root, subdir = bookmark

            root = self.libraries.get(root)
            if not root is None:

                if subdir:
                    path = root +"/"+ subdir
                else:
                    path = root

        return path



    def setRangeStart (self, valueStart):

        with Settings.Export(update=True) as settings:
            settings["rangeStart"] = valueStart

        valueEnd = self.animationOpions.rangeEndSpinbox.value()
        if valueStart > valueEnd:
            self.animationOpions.rangeEndSpinbox.setValue(valueStart)



    def setRangeEnd (self, valueEnd):

        with Settings.Export(update=True) as settings:
            settings["rangeEnd"] = valueEnd

        valueStart =  self.animationOpions.rangeStartSpinbox.value()
        if valueStart > valueEnd:
            self.animationOpions.rangeStartSpinbox.setValue(valueEnd)



    def getRange (self):

        from maya.OpenMayaAnim import MAnimControl

        valueStart = MAnimControl.minTime().value()
        valueEnd   = MAnimControl.maxTime().value()
        
        self.animationOpions.rangeStartSpinbox.setValue(valueStart)
        self.animationOpions.rangeEndSpinbox.setValue(valueEnd)



    def overwriteState (self):

        lockVersion = True
        if self.modelingOverwrite.isEnabled():
            if self.modelingOverwrite.isChecked():
                lockVersion = False

        if self.surfacingOverwrite.isEnabled():
            if self.surfacingOverwrite.isChecked():
                lockVersion = False

        if self.animationOverwrite.isEnabled():
            if self.animationOverwrite.isChecked():
                lockVersion = False

        if lockVersion:
            itemCount = self.mainOpions.versionCombobox.count()

            lastVersion = 0
            for index in range(itemCount):
                version = self.mainOpions.versionCombobox.itemText(index)
                version = int(version)

                if version > lastVersion:
                    lastVersion = version
                    self.mainOpions.versionCombobox.setCurrentIndex(index)

            self.mainOpions.versionCombobox.setEnabled(False)
        else:
            self.mainOpions.versionCombobox.setEnabled(True)



    def linkWrap (self):

        with Settings.Export(update=True) as settings:
            settings["link"] = self.mainOpions.linkButton.isChecked()

        self.interpretTags("")



    def interpretTags (self, choice):

        hilight = False


        assetpath = self.getAssetPath()
        assetname = self.getAssetName()

        path = os.path.join(assetpath, assetname)
        if os.path.exists(path):

            realpath = os.path.realpath(path)
            realname = os.path.basename(realpath)

            comboVersion = self.mainOpions.versionCombobox.currentText()
            comboVersion = int(comboVersion)

            nameVersion  = tools.getVersion(realname)

            if nameVersion == comboVersion:
                hilight = True


        filename = self.getAssetName(final=False)
        comment = tools.getComment(assetpath, filename)
        if not comment:
            self.commentEdit.setDefault()
        else:
            self.commentEdit.set(comment)


        if hilight:
            self.animationOpions.animationNameCombobox.setProperty("textcolor", "violet")
            self.animationOpions.animationNameCombobox.setStyleSheet("")
            self.mainOpions.variantCombobox.setProperty("textcolor", "violet")
            self.mainOpions.variantCombobox.setStyleSheet("")
            self.mainOpions.linkButton.setProperty("overwrite", "true")
        else:
            self.animationOpions.animationNameCombobox.setProperty("textcolor", "on")
            self.animationOpions.animationNameCombobox.setStyleSheet("")
            self.mainOpions.variantCombobox.setProperty("textcolor", "on")
            self.mainOpions.variantCombobox.setStyleSheet("")
            self.mainOpions.linkButton.setProperty("overwrite", "false")

        self.mainOpions.linkButton.setStyleSheet("")



    def versionChoice (self, text):

        if text:
            directory = self.AssetPath.get()
            name = self.nameEdit.text()
            path = os.path.join(directory, name)

            version = int(text)


            self.animationOpions.animationNameCombobox.clear()

            animationList = tools.getAnimationList(path, version=version)
            for animation in animationList:
                self.animationOpions.animationNameCombobox.addItem(
                     animation )
            self.animationOpions.animationNameCombobox.setCurrentIndex(-1)


            self.mainOpions.variantCombobox.clear()

            variantList = tools.getVariantList(path, version=version)
            for variant in variantList:
                self.mainOpions.variantCombobox.addItem(
                     variant )
            self.mainOpions.variantCombobox.setCurrentIndex(-1)


            versionList = tools.getVersionList(path)
            if version not in versionList:
                self.mainOpions.versionCombobox.setProperty("textcolor", "on")
            else:
                self.mainOpions.versionCombobox.setProperty("textcolor", "violet")

            self.mainOpions.versionCombobox.setStyleSheet("")


            self.interpretTags("")



    def sliderAction (self, value):

        with Settings.Manager(update=True) as settings:
            settings["iconSize"] = value

        self.AssetBrowser.setGrid()
        self.AssetBrowser.adjustSize()



    def getAssetPath (self):

        return os.path.join(
            self.AssetPath.get(),
            self.nameEdit.text() )



    def getAssetName (self, final=True, extension="usda"):

        name = self.nameEdit.text()

        version = self.mainOpions.versionCombobox.currentText()
        version = int(version)

        variant = self.mainOpions.variantCombobox.currentText()
        animation = self.animationOpions.animationNameCombobox.currentText()

        if final:
            final = self.mainOpions.linkButton.isChecked()

        return tools.createAssetName(
            name, version,
            variant=variant,
            animation=animation,
            final=final,
            extension=extension )



    def partitionExport (self):

        animationSwitchChanged = False

        with Settings.Export(update=True) as settings:

            animationSwitchBefore = settings["animation"]
            animationSwitchAfter = self.animationSwitch.isChecked()
            if animationSwitchBefore != animationSwitchAfter:
                animationSwitchChanged = True

            settings["modelling"] = self.modelingSwitch.isChecked()
            settings["surfacing"] = self.surfacingSwitch.isChecked()
            settings["animation"] = self.animationSwitch.isChecked()

        self.applySettings()

        if animationSwitchChanged:
            version = self.mainOpions.versionCombobox.currentText()
            self.versionChoice(version)



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

        if self.BottomBar.favorite.button.isChecked():
            self.favoriteFilter(update=True)



    def iconClicked (self, index):

        data = index.data(QtCore.Qt.EditRole)
        force = False

        if data:
            dataType = data["type"]

            if dataType == "library":
                name = data["data"]["name"]
                self.setLibrary(name)
                return

            elif dataType == "folder":
                name = data["data"]["name"]
                self.AssetPath.moveForward(name)
                self.checkedName = ""

            elif dataType == "asset":
                assetdata = data["data"]
                assetType = assetdata["type"]

                if assetType == "usdasset":
                    name = assetdata["name"]
                    force = True

                    if self.checkedName == name:
                        self.checkedName = ""
                    else:
                        self.checkedName = name

                else:
                    self.checkedName = ""
        else:
            self.checkedName = ""

        self.setOptions(force=force)



    def loadStatus (self):

        directory = self.AssetPath.get()
        name = self.nameEdit.text()
        path = os.path.join(directory, name)

        metadataPath = os.path.join(path, self.metadata)
        data = tools.dataread(metadataPath)
        self.status.set(
            data.get("status", "") )



    def setName (self, text):

        text = tools.nameFilter(text)
        self.nameEdit.setText(text)


        if text == self.defaultName:
            self.nameEdit.setProperty("textcolor", "off")
            self.currentName = ""
            self.checkedName = ""
            self.status.set()

        elif text in self.assetsNames:
            self.nameEdit.setProperty("textcolor", "violet")
            
            inputMatch = False
            if not text == self.checkedName:
                inputMatch = True

            self.currentName = ""
            self.checkedName = text

            self.loadStatus()
            if inputMatch:
                self.setOptions()

        else:
            self.nameEdit.setProperty("textcolor", "kicker")

            inputMatchBreak = False
            if not self.checkedName == "":
                inputMatchBreak = True

            self.currentName = text
            self.checkedName = ""

            if inputMatchBreak:
                self.status.set()
                self.setOptions(force=True)


        self.nameEdit.setStyleSheet("")


        model = self.AssetBrowser.model()
        for raw in range(model.rowCount()):
            item = model.item(raw)
            data = item.data(QtCore.Qt.EditRole)
            iconType = data["type"]

            if iconType == "asset":

                if data["data"]["name"] == self.checkedName:
                    item.setData(1, QtCore.Qt.StatusTipRole)
                else:
                    item.setData(0, QtCore.Qt.StatusTipRole)

            else:
                item.setData(0, QtCore.Qt.StatusTipRole)



    def setOptions (self, force=False):

        # in name the same do nothing
        if not force:
            name = self.currentName
            text = self.nameEdit.text()
            if name:
                if name == text: return


        # set asset name text
        if self.checkedName:
            name = self.checkedName
        elif self.currentName:
            name = self.currentName
        else:
            name = self.defaultName

        self.nameEdit.setText(name)


        # set default options
        self.mainOpions.versionCombobox.clear()

        if name == self.defaultName:
            self.mainOpions.versionCombobox.addItem("01")


        # load asset options
        else:
            directory = self.AssetPath.get()
            name = self.nameEdit.text()
            path = os.path.join(directory, name)

            versionList = tools.getVersionList(path)

            newItem = 0
            for version in versionList:
                if version > newItem:
                    newItem = version
            versionList.append(newItem+1)

            lastItem = 0
            for version in versionList:
                self.mainOpions.versionCombobox.addItem(
                     "{:02d}".format(version) )
                if version > lastItem:
                    lastItem = version
                    self.mainOpions.versionCombobox.setCurrentIndex(lastItem-1)



    def getOptions (self):

        if self.exported:

            class DataClass: pass
            options = DataClass()

            options.modelling = self.modelingSwitch.isChecked()
            options.modellingOverride = self.modelingOverwrite.isChecked()

            options.surfacing = self.surfacingSwitch.isChecked()
            options.surfacingOverride = self.surfacingOverwrite.isChecked()

            options.animation = self.animationSwitch.isChecked()
            options.animationOverride = self.animationOverwrite.isChecked()

            options.animationName = self.animationOpions.animationNameCombobox.currentText()

            options.minTime = self.animationOpions.rangeStartSpinbox.value()
            options.maxTime = self.animationOpions.rangeEndSpinbox.value()

            options.assetPath    = self.getAssetPath()
            options.assetName    = self.getAssetName(final=False)
            options.assetFinal   = self.getAssetName(final=True )

            options.version = int(self.mainOpions.versionCombobox.currentText())
            options.link = self.mainOpions.linkButton.isChecked()

            options.comment = self.commentEdit.get()
            options.status = self.status.get()

            return options



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
        assets    = []

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
                assets += [data]

        for data in [libraries, folders, assets]:
            data.sort( key=lambda item : item.get("data").get("name") )

        library = (
            labelL
            + labelF
            + labelA
            + plus
            + libraries
            + folders
            + assets
        )

        return library



    def sortBookmarks (self):

        count = self.BottomBar.bookmarkCombobox.count()
        bookmarks = []

        for index in range(count):
            pathUI = self.BottomBar.bookmarkCombobox.itemText(index)
            pathID = self.BottomBar.bookmarkCombobox.itemData(index)
            bookmarks += [ { "UI":pathUI, "ID":pathID } ]

        self.BottomBar.bookmarkCombobox.clear()
        bookmarks.sort( key=lambda item : item.get("ID") )

        for item in bookmarks:
            pathUI = item.get("UI")
            pathID = item.get("ID")
            self.BottomBar.bookmarkCombobox.addItem(pathUI, pathID)



    def getDirItems (self, path, filterFavotires=False):

        if not path:
            return []
    
        library = []
        self.assetsNames = []

        favorites = []
        with Settings.Manager(update=False) as settings:
            favorites = settings.get("favorites", [])

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
                chosenItem = tools.chooseAssetItem(folderPath)

                versionCount = tools.getVersionList(folderPath)
                versionCount = len(versionCount)

                if dataType == "usdasset":

                    favorite = False
                    pathID = self.getPathID(asset=name)
                    if pathID in favorites:
                        favorite = True

                    if filterFavotires and not favorite:
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



    def favoriteFilter (self, update=False):

        favoriteFilter = self.BottomBar.favorite.button.isChecked()

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
                filterFavotires=self.BottomBar.favorite.button.isChecked() )


        hasCheckedName = False

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
                hasCheckedName = True

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

        if not hasCheckedName:
            self.checkedName = ""
            self.setOptions()



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



    def modelingOverwriteSetting (self):
        with Settings.Export(update=True) as settings:
            settings["modellingOverwrite"] = self.modelingOverwrite.isChecked()

    def surfacingOverwriteSetting (self):
        with Settings.Export(update=True) as settings:
            settings["surfacingOverwrite"] = self.surfacingOverwrite.isChecked()

    def animationOverwriteSetting (self):
        with Settings.Export(update=True) as settings:
            settings["animationOverwrite"] = self.animationOverwrite.isChecked()



    def applySettings (self):

        blacklist = []
        with Settings.Manager(update=False) as settings:

            if settings.get("favoriteFilter"):
                self.BottomBar.favorite.button.setChecked(True)


            self.BottomBar.bookmarkCombobox.clear()
            bookmarks = settings.get("bookmarks")
            for data in bookmarks:
                bookmark = self.interpretID(data)
                if not bookmark is None:
                    library, subdir = bookmark

                    name = library
                    if subdir: name += "/"+ subdir

                    if not library in self.libraries:
                        blacklist.append(data)
                        continue

                    root = self.libraries.get(library, "")
                    path = os.path.join(root, name)
                    if os.path.exists(path):
                        blacklist.append(data)
                        continue

                    self.BottomBar.bookmarkCombobox.addItem(name, data)

        if blacklist:
            with Settings.Manager(update=True) as settings:
                for data in blacklist:
                    settings["bookmarks"].remove(data)


        self.sortBookmarks()
        self.BottomBar.bookmarkCombobox.setCurrentIndex(-1)


        with Settings.Export(update=False) as settings:

            self.animationOpions.rangeStartSpinbox.setValue(settings.get("rangeStart"))
            self.animationOpions.rangeEndSpinbox.setValue(settings.get("rangeEnd"))

            modelingOn  = settings.get("modelling")
            surfacingOn = settings.get("surfacing")
            animationOn = settings.get("animation")

            if modelingOn:
                self.modelingSwitch.setChecked(True)
                self.modelingOverwrite.setEnabled(True)
            else:
                self.modelingSwitch.setChecked(False)
                self.modelingOverwrite.setEnabled(False)
            
            if settings.get("modellingOverwrite"):
                self.modelingOverwrite.setChecked(True)
            else:
                self.modelingOverwrite.setChecked(False)
            
            if surfacingOn:
                self.surfacingSwitch.setChecked(True)
                self.surfacingOverwrite.setEnabled(True)
            else:
                self.surfacingSwitch.setChecked(False)
                self.surfacingOverwrite.setEnabled(False)
            
            if settings.get("surfacingOverwrite"):
                self.surfacingOverwrite.setChecked(True)
            else:
                self.surfacingOverwrite.setChecked(False)

            if animationOn:
                self.animationOpions.setVisible(True)
                self.animationSwitch.setChecked(True)
                self.animationOverwrite.setEnabled(True)
            else:
                self.animationOpions.setVisible(False)
                self.animationSwitch.setChecked(False)
                self.animationOverwrite.setEnabled(False)
            
            if settings.get("animationOverwrite"):
                self.animationOverwrite.setChecked(True)
            else:
                self.animationOverwrite.setChecked(False)

            if modelingOn or surfacingOn or animationOn:
                self.mainOpions.setVisible(True)
            else:
                self.mainOpions.setVisible(False)

            if settings.get("link"):
                self.mainOpions.linkButton.setChecked(True)
            else:
                self.mainOpions.linkButton.setChecked(False)

        self.overwriteState()



    def exportQuery (self):

        modelingOn  = self.modelingSwitch.isChecked()
        surfacingOn = self.surfacingSwitch.isChecked()
        animationOn = self.animationSwitch.isChecked()
        text = self.animationOpions.animationNameCombobox.currentText()

        self.exportButton.setProperty("state", "disabled")

        if not modelingOn and not surfacingOn and not animationOn:
            pass
        elif animationOn and not text:
            pass
        elif self.nameEdit.text() == self.defaultName:
            pass
        elif self.AssetPath.isHidden():
            pass
        else:
            self.exportButton.setProperty("state", "enabled")

        self.exportButton.setStyleSheet("")



    def exportAction (self):

        if self.exportButton.property("state") == "enabled":
            self.exported = True
            self.close()
