#!/usr/bin/env python



import os, re

from . import resources
from . import theme

import toolbox.usd.reporter
import toolbox.system.ostree
import toolbox.system.stream
import toolbox.core.naming
import toolbox.core.timing

from Qt import QtWidgets, QtCore, QtGui

from .items import FileUsdDelegate
from . import BaseWidget
from . import ManagerUI

from . import Metadata
from . import Settings
UIGlobals = Settings.UIGlobals








def Make (base):


    class ManagerBase (base):


        def __init__(self, parent=None):
            super(ManagerBase, self).__init__(parent)

            self.theme = theme.Theme(application="manager")
            self.setStyleSheet( self.theme.getStyleSheet() )



    class Manager (
            ManagerBase,
            BaseWidget.Library,
            BaseWidget.Browser,
            BaseWidget.Bookmark,
            BaseWidget.Favorite,
            BaseWidget.Slider,
            BaseWidget.Folder ):



        def __init__(self, parent=None):
            super(Manager, self).__init__(parent)
            ManagerUI.setupUi(self, self.theme)
            self.connectUi()

            self.metafile    = Metadata.NAME
            self.metapath    = str()
            self.metadata    = dict()

            self.libraries   = self.getAssetRoots()
            self.assetsNames = list()

            self.applyUiSettings()
            self.setLibrary()

            self.setWindowTitle("Asset Manager")
            self.setObjectName("AssetManager")
            self.resize(820, 580)

            self.AssetBrowser.setFocus(QtCore.Qt.MouseFocusReason)



        def connectUi (self):

            self.AssetBrowser.iconClicked.connect(self.iconClicked)
            self.AssetBrowser.tokenClicked.connect(self.tokenClicked)
            self.AssetBrowser.favoriteClicked.connect(self.favoriteClicked)
            self.AssetBrowser.link.connect(self.openFolder)
            self.AssetBrowser.createFolderQuery.connect(self.createFolderQuery)
            self.AssetBrowser.createFolder.connect(self.createFolder)

            self.AssetPath.pathChanged.connect(self.drawBrowserItems)
            self.AssetPath.pathChanged.connect(self.uiVisibility)
            self.AssetPath.bookmarkClicked.connect(self.actionBookmark)

            self.BarBottom.preview.slider.valueChanged.connect(self.sliderAction)
            self.BarBottom.favorite.button.released.connect(self.favoriteFilter)
            self.BarBottom.bookmarkChosen.connect(self.jumpBookmark)

            self.ResizeButton.moveStart.connect(self.resizeMath)

            self.UsdLoadOptions.status.clicked.connect(self.changeStatus)
            self.UsdLoadOptions.infoEdit.loseFocus.connect(self.saveUsdInfo)
            self.UsdLoadOptions.commentEdit.loseFocus.connect(self.saveUsdComment)

            self.UsdLoadOptions.link.released.connect(self.tokenButton)

            self.UsdLoadOptions.loadButton.pressed.connect(self.loadQuery)
            self.UsdLoadOptions.loadButton.released.connect(self.loadFilter)



        def tokenClicked (self, index):

            model = self.AssetBrowser.model()
            item = model.item(index.row())
            data = index.data(QtCore.Qt.EditRole)

            state = not data.get("data").get("token")
            data["data"]["token"] = state


            statusdata = item.data(QtCore.Qt.StatusTipRole)
            if statusdata == 1:
                state = self.UsdLoadOptions.link.setChecked(state)

            item.setData(data, QtCore.Qt.EditRole)
            self.linkManager(data)



        def tokenButton (self):

            model = self.AssetBrowser.model()
            for index in range(model.rowCount()):

                item = model.item(index)
                statusdata = item.data(QtCore.Qt.StatusTipRole)
                if statusdata == 1:

                    data = item.data(QtCore.Qt.EditRole)
                    state = self.UsdLoadOptions.link.isChecked()
                    data["data"]["token"] = state
                    item.setData(data, QtCore.Qt.EditRole)
                    self.linkManager(data)
                    break



        def linkManager (self, data):

            data = data.get("data")
            name      = data.get("name")
            version   = data.get("version")
            variant   = data.get("variant")
            animation = data.get("animation")

            filename = toolbox.core.naming.createAssetName (
                name, version,
                variant=variant,
                animation=animation )

            toolbox.system.ostree.linkUpdate(
                os.path.join(self.AssetPath.get(), name),
                filename,
                create = data.get("token") )

            self.tokensUpdate()



        def tokensUpdate (self):

            directory = self.AssetPath.get()

            model = self.AssetBrowser.model()
            for index in range(model.rowCount()):

                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)

                if data.get("type") != "asset":
                    continue

                filedata = data.get("data")
                name      = filedata.get("name")
                version   = filedata.get("version")
                variant   = filedata.get("variant")
                animation = filedata.get("animation")

                filename = toolbox.core.naming.createAssetName(
                    name, version,
                    variant=variant,
                    animation=animation,
                    final=False )
                finalname = toolbox.core.naming.makeFinal(filename)

                token = False
                finalpath = os.path.join(directory, name, finalname)
                if os.path.exists(finalpath):
                    realpath = os.path.realpath(finalpath)
                    realname = os.path.basename(realpath)
                    if realname == filename:
                        token = True

                if filedata.get("token") != token:
                    data["data"]["token"] = token

                item.setData(data, QtCore.Qt.EditRole)



        def uiVisibility (self, path=""):
            
            if self.AssetPath.group:
                self.ResizeButton.show()
                self.AssetPath.bookmarkButton.setEnabled(False)
                self.BarBottom.favoriteHideForce = True
                self.BarBottom.bookmarkHideForce = True
                self.BarBottom.themeHideForce    = True
                self.BarBottom.groupsLayout.setStretch(2, 0)
                self.BarBottom.groupsLayout.setStretch(5, 1)
                self.BarBottom.uiVisibility()
                
                self.UsdLoadOptions.show()

                self.checkedName = ""
                self.assetChecked()

            else:
                self.ResizeButton.hide()
                self.AssetPath.bookmarkButton.setEnabled(True)
                self.BarBottom.favoriteHideForce = False
                self.BarBottom.bookmarkHideForce = False
                self.BarBottom.themeHideForce    = False
                self.BarBottom.groupsLayout.setStretch(2, 1)
                self.BarBottom.groupsLayout.setStretch(5, 0)
                self.BarBottom.uiVisibility()

                self.UsdLoadOptions.hide()



        def iconClicked (self, index):

            data = index.data(QtCore.Qt.EditRole)
            if not data:
                self.checkedName = ""
                self.assetChecked()

            else:
                dataType = data.get("type")


                if dataType == "library":
                    name = data.get("data").get("name")

                    self.checkedName = ""
                    self.setLibrary(name)


                elif dataType == "folder":
                    name = data.get("data").get("name")

                    self.checkedName = ""
                    self.AssetPath.moveForward(name)


                elif dataType == "asset":
                    assetdata = data.get("data")
                    assetType = assetdata.get("type")


                    if assetType == "usdasset":

                        self.checkedName = ""
                        path = self.AssetPath.get()
                        name = assetdata.get("name")
                        self.drawUsdItems(path, name)


                    elif assetType == "usdfile":
                        name = data.get("data").get("filename")

                        if self.checkedName == name:
                            self.checkedName = ""
                        else:
                            self.checkedName = name

                        self.assetChecked()



        def getUsdItems (self, root, name):

            path = os.path.join(root, name)

            if not os.path.exists(path):
                return []

            library = [dict(
                type="labelasset",
                data=dict(text="Files") )]

            self.assetsNames = []
            data = {}
            with Metadata.MetadataManager(
                    path, "usdasset") as metadata:
                data = metadata

            for filename in os.listdir(path):

                if re.search(r"\.usd[ac]*$", filename):
                    if not re.search(r"\.Final", filename):

                        dataTime = data["items"][filename]["published"]
                        publishedTime = toolbox.core.timing.getTimeDifference(dataTime)

                        version   = toolbox.core.naming.getVersion(filename)
                        variant   = toolbox.core.naming.getVariantName(filename)
                        animation = toolbox.core.naming.getAnimationName(filename)

                        finalname = toolbox.core.naming.createAssetName(
                            name, version,
                            variant=variant,
                            animation=animation,
                            final=True )

                        token = False
                        finalpath = os.path.join(path, finalname)
                        if os.path.exists(finalpath):
                            realpath = os.path.realpath(finalpath)
                            realname = os.path.basename(realpath)
                            if realname == filename:
                                token = True

                        filesize = toolbox.usd.reporter.getResolvedSize(
                            os.path.join(path, filename) )

                        library.append(
                            dict(type="asset",  data=dict(
                                filename=filename,
                                name=name,
                                previews=toolbox.core.naming.getUsdPreviews(path, filename),
                                type="usdfile",
                                size=filesize,
                                version=version,
                                variant=variant,
                                animation=animation,
                                published=publishedTime,
                                token=token )) )
                        self.assetsNames.append(filename)

            return library



        def drawUsdItems (self, path, name):


            iconModel = QtGui.QStandardItemModel(self.AssetBrowser)

            library = self.getUsdItems(path, name)
            for item in self.sort(library):

                iconItem = QtGui.QStandardItem()

                iconItem.setCheckable(False)
                iconItem.setEditable(True)

                iconItem.setData(
                    0,
                    QtCore.Qt.StatusTipRole)

                iconItem.setData(
                    dict(type=item.get("type"), data=item.get("data")),
                    QtCore.Qt.EditRole)

                iconModel.appendRow(iconItem)


            self.AssetBrowser.setModel(iconModel)
            self.AssetBrowser.setItemDelegate(
                FileUsdDelegate.Delegate(self.AssetBrowser, self.theme) )


            self.loadUsdInfo(path, name)
            self.loadUsdComment()

            self.AssetBrowser.setGrid()
            self.AssetPath.group = name
            self.uiVisibility()



        def assetChecked (self):

            self.loadUsdComment()
            self.UsdLoadOptions.link.setChecked(False)

            self.UsdLoadOptions.commentEdit.setEnabled(False)
            self.UsdLoadOptions.link.setEnabled(False)

            model = self.AssetBrowser.model()
            for raw in range(model.rowCount()):

                item = model.item(raw)
                data = item.data(QtCore.Qt.EditRole)
                dataType = data.get("type")


                item.setData(0, QtCore.Qt.StatusTipRole)
                if dataType == "asset":
                    assetType = data.get("data").get("type")

                    if assetType == "usdfile":
                        filename = data.get("data").get("filename")

                        if filename == self.checkedName:
                            item.setData(1, QtCore.Qt.StatusTipRole)
                            self.loadUsdComment(filename)
                            self.UsdLoadOptions.link.setChecked(
                                data.get("data").get("token"))

                            self.UsdLoadOptions.commentEdit.setEnabled(True)
                            self.UsdLoadOptions.link.setEnabled(True)



        def loadUsdInfo (self, path, name):

            metadataPath = os.path.join(
                path, name, self.metafile)

            if os.path.exists(metadataPath):
                self.metapath = os.path.join(path, name)
                self.metadata = toolbox.system.stream.dataread(metadataPath)

                info = self.metadata.get("info")
                if info:
                    self.UsdLoadOptions.infoEdit.set(info)
                else:
                    self.UsdLoadOptions.infoEdit.setDefault()

                status = self.metadata.get("status")
                if status:
                    self.UsdLoadOptions.status.set(status)



        def loadUsdComment (self, filename=""):

            items = self.metadata.get("items", dict())
            itemdata = items.get(filename, dict())
            text = itemdata.get("comment", "")

            if text:
                self.UsdLoadOptions.commentEdit.set(text)
                return

            self.UsdLoadOptions.commentEdit.setDefault()



        def saveUsdComment (self):

            setDefault = False


            metadataFile = os.path.join(
                self.metapath, self.metafile)
            if not os.path.exists(metadataFile):
                self.UsdLoadOptions.commentEdit.setDefault()
                return

            if not self.checkedName:
                self.UsdLoadOptions.commentEdit.setDefault()
                return

            text = self.UsdLoadOptions.commentEdit.get()
            if not text:
                setDefault = True

            default = self.UsdLoadOptions.commentEdit.defaultName
            if text == default:
                setDefault = True

            solid = re.sub(r"[\s\n]", "", text)
            if len(solid) == 0:
                setDefault = True


            if setDefault:
                self.UsdLoadOptions.commentEdit.setDefault()
                text = ""

            with Metadata.MetadataManager(
                    self.metapath, "usdasset") as data:
                data["items"][self.checkedName]["comment"] = text
                self.metadata = data



        def saveUsdInfo (self):

            setDefault = False


            metadataFile = os.path.join(
                self.metapath, self.metafile)
            if not os.path.exists(metadataFile):
                return

            text = self.UsdLoadOptions.infoEdit.get()
            if not text:
                setDefault = True

            default = self.UsdLoadOptions.infoEdit.defaultName
            if text == default:
                setDefault = True

            solid = re.sub(r"[\s\n]", "", text)
            if len(solid) == 0:
                setDefault = True


            if setDefault:
                self.UsdLoadOptions.infoEdit.setDefault()
                text = ""

            with Metadata.MetadataManager(
                    self.metapath, "usdasset") as data:
                data["info"] = text



        def changeStatus (self, status):

            with Metadata.MetadataManager(
                    self.metapath, "usdasset") as data:
                data["status"] = status



        def resizeMath (self, value):

            minimunWidth = UIGlobals.Options.minimumWidth
            maximunWidth = UIGlobals.Options.maximumWidth
            margin = UIGlobals.Options.margin

            optionWidth = (
                self.width()
                - value
                - margin*2 )

            space = (
                self.width()
                - self.AssetBrowser.minimumWidth()
                - optionWidth
                - margin*2 )

            if maximunWidth >= optionWidth >= minimunWidth and space > 0:
                self.UsdLoadOptions.setOptionWidth(optionWidth)



        def loadQuery (self):

            state = "enabled"

            if not self.checkedName:
                state = "disabled"

            self.UsdLoadOptions.loadButton.setProperty("state", state)
            self.UsdLoadOptions.loadButton.setStyleSheet("")



        def loadFilter (self):

            if self.UsdLoadOptions.loadButton.property("state") != "enabled":
                return

            directory = self.AssetPath.get()
            path = ""

            model = self.AssetBrowser.model()
            for index in range(model.rowCount()):

                item = model.item(index)
                statusdata = item.data(QtCore.Qt.StatusTipRole)
                if statusdata == 1:

                    data = item.data(QtCore.Qt.EditRole)
                    state = self.UsdLoadOptions.link.isChecked()

                    filedata = data.get("data")
                    name      = filedata.get("name")
                    version   = filedata.get("version")
                    variant   = filedata.get("variant")
                    animation = filedata.get("animation")

                    filename = toolbox.core.naming.createAssetName(
                        name, version,
                        variant=variant,
                        animation=animation,
                        final=state )

                    path = os.path.join(directory, name, filename)
                    break

            if os.path.exists(path):
                self.loadUsdFile(path)



        def loadUsdFile (self, path):

            pass



    return Manager