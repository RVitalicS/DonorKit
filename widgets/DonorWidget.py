#!/usr/bin/env python

"""
"""

import os
import re
from widgets import theme
import toolkit.usd.reporter as reporterUSD
import toolkit.system.ostree as ostree
import toolkit.system.stream as stream
import toolkit.core.naming as naming
import toolkit.core.timing as timing
from toolkit.core import colorspace
from toolkit.core import Metadata
from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets.items import FileUsdDelegate
from widgets.items import ColorGuideDelegate
from widgets.items import ColorDelegate
from widgets import BaseWidget
from widgets import DonorUI
from widgets import Settings

OCIO = os.getenv("OCIO")
UIGlobals = Settings.UIGlobals


def Make (base):
    pack = [base]
    widget = QtWidgets.QWidget
    if base != widget:
        pack.append(widget)


    class Base (*pack):

        def __init__(self, parent=None):
            super(Base, self).__init__(parent=parent)
            self.theme = theme.Theme("Manager")
            self.setStyleSheet( self.theme.getStyleSheet() )


    class Donor (BaseWidget.Make(Base)):

        def __init__(self, parent=None):
            super(Donor, self).__init__(parent=parent)
            DonorUI.setupUi(self, self.theme)
            self.connectUi()
            self.metapath = str()
            self.metadata = dict()
            self.setUiPath()
            self.applyUiSettings()
            self.Browser.setFocus(QtCore.Qt.MouseFocusReason)

        def connectUi (self):
            self.Browser.refreshLibrary.connect(self.refreshLibrary)
            self.Browser.iconClicked.connect(self.iconClicked)
            self.Browser.tokenClicked.connect(self.tokenClicked)
            self.Browser.favoriteClicked.connect(self.favoriteClicked)
            self.Browser.link.connect(self.linkAction)
            self.Browser.createFolderQuery.connect(self.createFolderQuery)
            self.Browser.createFolder.connect(self.createFolder)
            self.BrowserPath.pathChanged.connect(self.drawDecision)
            self.BrowserPath.pathChanged.connect(self.uiVisibility)
            self.BrowserPath.bookmarkClicked.connect(self.switchBookmark)
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
            model = self.Browser.model()
            item = model.item(index.row())
            data = index.data(QtCore.Qt.EditRole)
            state = not data.get("token")
            data["token"] = state
            statusdata = item.data(QtCore.Qt.StatusTipRole)
            if statusdata == 1:
                self.UsdLoadOptions.link.setChecked(state)
            item.setData(data, QtCore.Qt.EditRole)
            self.linkManager(data)

        def tokenButton (self):
            model = self.Browser.model()
            for index in range(model.rowCount()):
                item = model.item(index)
                statusdata = item.data(QtCore.Qt.StatusTipRole)
                if statusdata == 1:
                    data = item.data(QtCore.Qt.EditRole)
                    state = self.UsdLoadOptions.link.isChecked()
                    data["token"] = state
                    item.setData(data, QtCore.Qt.EditRole)
                    self.linkManager(data)
                    break

        def linkManager (self, data):
            kind = data.get("kind")
            name = data.get("name")
            version = data.get("version")
            variant = data.get("variant")
            animation = data.get("animation")
            directory = self.BrowserPath.resolve()
            assetname = naming.createAssetName (
                name=name if kind == "assembly" else None,
                version=version,
                variant=variant,
                animation=animation )
            filepath = ostree.getPathUSD(
                directory, assetname)
            filename = os.path.basename(filepath)
            ostree.linkUpdate(
                directory, filename,
                create = data.get("token") )
            self.tokensUpdate()

        def tokensUpdate (self):
            directory = self.BrowserPath.resolve()
            model = self.Browser.model()
            for index in range(model.rowCount()):
                item = model.item(index)
                data = item.data(QtCore.Qt.EditRole)
                if data.get("type") not in ["usdfile"]:
                    continue
                kind = data.get("kind")
                name = data.get("name")
                version = data.get("version")
                variant = data.get("variant")
                animation = data.get("animation")
                filename = naming.createAssetName(
                    name=name if kind == "assembly" else None,
                    version=version,
                    variant=variant,
                    animation=animation,
                    final=False )
                token = False
                filepath = ostree.getPathUSD(
                    directory, filename)
                if ostree.isFinal(filepath):
                    token = True
                if data.get("token") != token:
                    data["token"] = token
                item.setData(data, QtCore.Qt.EditRole)

        def uiVisibility (self, path):
            if self.BrowserPath.isRoot(path):
                self.BrowserPath.hide()
                self.BarBottom.hide()
            elif (self.BrowserPath.isUsdAsset(path) or
                    self.BrowserPath.isUsdMaterial(path)):
                self.ResizeButton.show()
                self.UsdLoadOptions.show()
                self.checkedName = ""
                self.usdfileChecked()
            else:
                self.BrowserPath.show()
                self.BarBottom.show()
                self.ResizeButton.hide()
                self.UsdLoadOptions.hide()

        def iconClicked (self, index):
            data = index.data(QtCore.Qt.EditRole)
            if not data:
                self.checkedName = ""
                self.usdfileChecked()
            else:
                dataType = data.get("type")
                if dataType == "library":
                    libname = data.get("name")
                    self.checkedName = ""
                    self.setUiPath(libname)
                elif dataType in [
                        "folder", "foldercolors",
                        "usdasset", "usdmaterial" ]:
                    self.checkedName = ""
                    name = data.get("name")
                    self.BrowserPath.goForward(name)
                elif dataType == "usdfile":
                    name = data.get("filename")
                    if self.checkedName == name:
                        self.checkedName = ""
                    else:
                        self.checkedName = name
                    self.usdfileChecked()
                elif dataType == "colorguide":
                    title = data.get("title")
                    name = data.get("name")
                    self.BrowserPath.goForward(title + name)
                elif dataType == "color":
                    data = data.get("rgb")
                    self.loadColor(data)

        def drawDecision (self, path):
            flag = self.BarBottom.favorite.button.isChecked()
            if (self.BrowserPath.isUsdAsset(path) or 
                    self.BrowserPath.isUsdMaterial(path)):
                self.drawUsdItems(path)
            elif self.BrowserPath.isFolderColors(path):
                self.drawColorGuideItems(path, filterFavorites=flag)
            elif self.BrowserPath.isColors(path):
                self.drawColorItems(path, filterFavorites=flag)
            else:
                self.drawBrowserItems(path, filterFavorites=flag)

        def getUsdItems (self, path):
            with Metadata.MetadataManager(path, update=False) as metadata:
                data = metadata
            if data.get("type") == "usdasset":
                kind = "assembly"
            elif data.get("type") == "usdmaterial":
                kind = "material"
            else:
                return []
            library = [dict(type="labelasset", text="USD Files")]
            name = os.path.basename(path)
            for filename in os.listdir(path):
                if naming.rule_Ignore(filename):
                    continue
                dataTime = data["items"][filename]["published"]
                publishedTime = timing.getTimeDifference(dataTime)
                version = naming.getVersion(filename)
                variant = naming.getVariantName(filename)
                animation = naming.getAnimationName(filename)
                token = False
                filepath = ostree.getPathUSD(path, filename)
                if ostree.isFinal(filepath):
                    token = True
                filesize = reporterUSD.getResolvedSize(
                    os.path.join(path, filename) )
                library.append(dict(
                    type="usdfile",
                    kind=kind,
                    filename=filename,
                    name=name,
                    previews=naming.getUsdPreviews(path, filename),
                    size=filesize,
                    version=version,
                    variant=variant,
                    animation=animation,
                    published=publishedTime,
                    token=token ))
            return library

        def drawUsdItems (self, path):
            iconModel = QtGui.QStandardItemModel(self.Browser)
            self.Browser.setModel(iconModel)
            self.Browser.setMessage("Loading")
            browserItems = self.getUsdItems(path)
            for item in self.sortItems(browserItems):
                iconItem = QtGui.QStandardItem()
                iconItem.setCheckable(False)
                iconItem.setEditable(True)
                iconItem.setData(0, QtCore.Qt.StatusTipRole)
                iconItem.setData(item, QtCore.Qt.EditRole)
                iconModel.appendRow(iconItem)
            self.Browser.setModel(iconModel)
            self.Browser.setItemDelegate(
                FileUsdDelegate.Delegate(self.Browser, self.theme) )
            self.loadUsdInfo(path)
            self.loadUsdComment()
            self.Browser.setGrid()
            self.Browser.clearMessage()

        def getColorGuideItems (self, path, filterFavorites=False ):
            library = [dict(type="labelasset", text="Color Guides")]
            with Settings.Manager(self.theme.app, False) as settings:
                favorites = settings.get("favorites", [])
            for filename in os.listdir(path):
                if not re.search(r"\.json*$", filename):
                    continue
                elif filename == self.metafile:
                    continue
                filepath = os.path.join(path, filename)
                if stream.validJSON(filepath):
                    data = stream.dataread(filepath)
                    prefix = data.get("prefix", "")
                    prefix = re.sub(r"\s*$", "", prefix)
                    title = data.get("title", "")
                    name = re.sub(prefix, "", title)
                    name = re.sub(r"^[^\w]+", "", name)
                    favorite = False
                    pathUI = os.path.join(self.BrowserPath.getUI(), title + name)
                    if pathUI in favorites:
                        favorite = True
                    if filterFavorites and not favorite:
                        continue
                    library.append(dict(
                        filename=filename,
                        type="colorguide",
                        title=title.replace(name, ""),
                        name=name,
                        count=data.get("colorCount", int()),
                        space=data.get("colorSpace", "<colorSpace>"),
                        favorite=favorite ))
            return library

        def drawColorGuideItems (self, path, filterFavorites=False):
            iconModel = QtGui.QStandardItemModel(self.Browser)
            browserItems = self.getColorGuideItems(path, filterFavorites=filterFavorites)
            for item in self.sortItems(browserItems):
                iconItem = QtGui.QStandardItem()
                iconItem.setCheckable(False)
                iconItem.setEditable(True)
                iconItem.setData(0, QtCore.Qt.StatusTipRole)
                iconItem.setData(item, QtCore.Qt.EditRole)
                iconModel.appendRow(iconItem)
            self.Browser.setModel(iconModel)
            self.Browser.setItemDelegate(
                ColorGuideDelegate.Delegate(self.Browser, self.theme) )
            self.Browser.setGrid()

        def getColorItems (self, filepath, filterFavorites=False ):
            library = list()
            if not stream.validJSON(filepath):
                return library
            library.append(dict(
                type="labelasset", text="Colors" ))
            with Settings.Manager(self.theme.app, False) as settings:
                favorites = settings.get("favorites", [])
            data = stream.dataread(filepath)
            prefix = data.get("prefix")
            space = data.get("colorSpace")

            CGATS = dict()
            if space == "CMYK":
                CGATS = stream.readCGATS()
            for key, item in data.get("records").items():   
                favorite = False
                pathUI = ":".join([
                    self.BrowserPath.getUI(),
                    item.get("code") ])
                if pathUI in favorites:
                    favorite = True
                if filterFavorites and not favorite:
                    continue
                RGB = None
                color = None
                components = item.get("components")
                if space == "CMYK":
                    XYZ = colorspace.CMYK_XYZ(components, CGATS)
                elif space == "LAB":
                    XYZ = colorspace.Lab_XYZ(components)
                elif space == "RGB":
                    RGB = components
                    XYZ = colorspace.lRGB_XYZ(components)
                elif space == "HEX":
                    color = components
                    XYZ = colorspace.HEX_XYZ(components)
                elif space == "XYZ":
                    XYZ = components
                else:
                    XYZ = [0.0,0.0,0.0]
                RGB = colorspace.XYZ_lRGB(XYZ) if not RGB else RGB
                color = colorspace.lRGB_HEX(RGB) if not color else color
                if OCIO:
                    RGB = colorspace.lRGB_ACEScg(RGB)
                RGB = colorspace.clampBlack(RGB)
                library.append(dict(
                    type="color",
                    title=prefix,
                    name=item.get("name").replace(prefix, ""),
                    code=item.get("code"),
                    color=color,
                    rgb=RGB,
                    xyz=XYZ,
                    favorite=favorite ))
            return library

        def drawColorItems (self, filepath, filterFavorites=False):
            iconModel = QtGui.QStandardItemModel(self.Browser)
            self.Browser.setModel(iconModel)
            self.Browser.setMessage("Loading")
            browserItems = self.getColorItems(filepath, filterFavorites=filterFavorites)
            for item in self.sortItems(browserItems):
                iconItem = QtGui.QStandardItem()
                iconItem.setCheckable(False)
                iconItem.setEditable(True)
                iconItem.setData(0, QtCore.Qt.StatusTipRole)
                iconItem.setData(item, QtCore.Qt.EditRole)
                iconModel.appendRow(iconItem)
            self.Browser.setModel(iconModel)
            self.Browser.setItemDelegate(
                ColorDelegate.Delegate(self.Browser, self.theme) )
            self.Browser.setGrid()
            self.Browser.clearMessage()

        def usdfileChecked (self):
            self.loadUsdComment()
            self.UsdLoadOptions.link.setChecked(False)
            self.UsdLoadOptions.commentEdit.setEnabled(False)
            self.UsdLoadOptions.link.setEnabled(False)
            model = self.Browser.model()
            for raw in range(model.rowCount()):
                item = model.item(raw)
                item.setData(0, QtCore.Qt.StatusTipRole)
                data = item.data(QtCore.Qt.EditRole)
                dataType = data.get("type")
                if dataType == "usdfile":
                    filename = data.get("filename")
                    if filename == self.checkedName:
                        item.setData(1, QtCore.Qt.StatusTipRole)
                        self.loadUsdComment(filename)
                        self.UsdLoadOptions.link.setChecked(
                            data.get("token"))
                        self.UsdLoadOptions.commentEdit.setEnabled(True)
                        self.UsdLoadOptions.link.setEnabled(True)

        def loadUsdInfo (self, path):
            self.metapath = path
            self.metadata = stream.dataread(
                os.path.join(path, self.metafile) )
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
            with Metadata.MetadataManager(self.metapath) as data:
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
            with Metadata.MetadataManager(self.metapath) as data:
                data["info"] = text

        def changeStatus (self, status):
            with Metadata.MetadataManager(self.metapath) as data:
                data["status"] = status

        def resizeMath (self, value):
            optionWidth = super(Donor, self).resizeMath(value)
            if optionWidth is not None:
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
            directory = self.BrowserPath.resolve()
            filepath = ""
            kind = None
            model = self.Browser.model()
            for index in range(model.rowCount()):
                item = model.item(index)
                statusdata = item.data(QtCore.Qt.StatusTipRole)
                if statusdata == 1:
                    data = item.data(QtCore.Qt.EditRole)
                    kind = data.get("kind")
                    name = data.get("name")
                    version = data.get("version")
                    variant = data.get("variant")
                    animation = data.get("animation")
                    filename = naming.createAssetName(
                        name=name if kind == "assembly" else None,
                        version=version,
                        variant=variant,
                        animation=animation,
                        final=False )
                    filepath = ostree.getPathUSD(
                        directory, filename,
                        final=self.UsdLoadOptions.link.isChecked() )
                    break
            if os.path.exists(filepath):
                if kind == "assembly":
                    self.loadUsdFile(filepath)
                elif kind == "material":
                    self.loadMaterial(filepath)

        def loadUsdFile (self, path):
            pass

        def loadMaterial (self, path):
            pass

        def loadColor (self, data):
            pass

    return Donor
