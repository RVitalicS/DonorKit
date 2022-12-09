#!/usr/bin/env python

"""
"""

import os
from widgets import theme
import toolkit.core.naming as naming
import toolkit.system.ostree as ostree
from toolkit.core import Metadata
from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets import BaseExport
from widgets import MaterialExportUI
from widgets import Settings

UIGlobals = Settings.UIGlobals


class Base (QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Base, self).__init__(parent)
        self.theme = theme.Theme("MaterialExport")
        self.setStyleSheet( self.theme.getStyleSheet() )
        self.setWindowTitle("USD Material Export")
        self.setObjectName("UsdMaterialExport")
        self.exit = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        self.exit.activated.connect(self.close)


class Dialog (BaseExport.Make(Base)):

    def __init__(self, initname=None, parent=None):
        super(Dialog, self).__init__(parent)
        MaterialExportUI.setupUi(self, self.theme)
        self.connectUi()
        self.wantedType = "usdmaterial"
        self.exported = False
        self.setUiPath()
        self.applyUiSettings()
        self.Browser.setFocus(QtCore.Qt.MouseFocusReason)
        if initname:
            self.setName(initname)
        self.setOptions()

    def connectUi (self):
        super(Dialog, self).connectUi()
        self.ExportOptions.inheritButton.stateChanged.connect(self.inheritSettings)
        self.ExportOptions.renderOptions.prman.stateChanged.connect(self.prmanSettings)
        self.ExportOptions.renderOptions.hydra.stateChanged.connect(self.hydraSettings)

    def getDirItems (self, path, filterFavorites=False, showTypes=None):
        return super(Dialog, self).getDirItems(
            path, filterFavorites=filterFavorites, showTypes=[self.wantedType])

    def drawBrowserItems (self, path, filterFavorites=False):
        super(Dialog, self).drawBrowserItems(path, filterFavorites=filterFavorites)
        hasCheckedName = False
        model = self.Browser.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            data = item.data(QtCore.Qt.StatusTipRole)
            if data == 1:
                hasCheckedName = True
                break
        if not hasCheckedName:
            self.checkedName = ""
            self.setOptions()

    def interpretTags (self, choice):
        highlightVariant = False
        highlightLink = False

        materialpath = os.path.join(
            self.BrowserPath.resolve(),
            self.ExportOptions.nameEdit.text() )
        materialname = self.getMaterialName()
        self.ExportOptions.commentEdit.hide()
        comment = Metadata.getComment(materialpath, materialname)
        if not comment:
            self.ExportOptions.commentEdit.setDefault()
        else:
            self.ExportOptions.commentEdit.set(comment)
        self.ExportOptions.commentEdit.show()

        path = ostree.getPathUSD(materialpath, materialname)
        if path:
            variantPart = naming.getVariantName(materialname)
            variantName = self.ExportOptions.versionOptions.variantCombobox.getName()
            if variantPart == variantName != "":
                highlightVariant = True
            if ostree.isFinal(path):
                highlightLink = True
        if highlightVariant:
            self.ExportOptions.versionOptions.variantCombobox.setProperty("textcolor", "violet")
        else:
            self.ExportOptions.versionOptions.variantCombobox.setProperty("textcolor", "on")
        if highlightLink:
            self.ExportOptions.versionOptions.linkButton.setProperty("overwrite", "true")
        else:
            self.ExportOptions.versionOptions.linkButton.setProperty("overwrite", "false")
        self.ExportOptions.versionOptions.variantCombobox.setStyleSheet("")
        self.ExportOptions.versionOptions.linkButton.repaint()

    def versionChoice (self, text):
        if text:
            directory = self.BrowserPath.resolve()
            if not directory:
                return
            name = self.ExportOptions.nameEdit.text()
            path = os.path.join(directory, name)
            version = int(text)

            self.ExportOptions.versionOptions.variantCombobox.stealth = True
            self.ExportOptions.versionOptions.variantCombobox.clear()
            variantList = naming.getVariantList(path, version)
            for variant in variantList:
                self.ExportOptions.versionOptions.variantCombobox.addItem(
                     variant )
            self.ExportOptions.versionOptions.variantCombobox.setCurrentIndex(-1)
            self.ExportOptions.versionOptions.variantCombobox.stealth = False

            versionList = naming.getVersionList(path)
            if version not in versionList:
                self.ExportOptions.versionOptions.versionCombobox.setProperty("textcolor", "on")
            else:
                self.ExportOptions.versionOptions.versionCombobox.setProperty("textcolor", "violet")
            self.ExportOptions.versionOptions.versionCombobox.setStyleSheet("")
            self.interpretTags("")

    def getMaterialName (self, final=False, extension="usda"):
        version = self.ExportOptions.versionOptions.versionCombobox.getName()
        variant = self.ExportOptions.versionOptions.variantCombobox.getName()
        if final:
            final = self.ExportOptions.versionOptions.linkButton.isChecked()
        return naming.createAssetName(
            version=int(version),
            variant=variant,
            final=final,
            extension=extension )

    def inheritSettings (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["inherit"] = self.ExportOptions.inheritButton.checked

    def prmanSettings (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["prman"] = self.ExportOptions.renderOptions.prman.checked

    def hydraSettings (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["hydra"] = self.ExportOptions.renderOptions.hydra.checked

    def applyUiSettings (self):
        super(Dialog, self).applyUiSettings()
        with Settings.Manager(self.theme.app, False) as settings:
            self.ExportOptions.versionOptions.setVisible(True)
            if settings.get("link"):
                self.ExportOptions.versionOptions.linkButton.setChecked(True)
            else:
                self.ExportOptions.versionOptions.linkButton.setChecked(False)
            if settings.get("maya"):
                self.ExportOptions.mayaButton.checked = True
            else:
                self.ExportOptions.mayaButton.checked = False
            if settings.get("inherit"):
                self.ExportOptions.inheritButton.checked = True
            else:
                self.ExportOptions.inheritButton.checked = False
            if settings.get("prman"):
                self.ExportOptions.renderOptions.prman.checked = True
            else:
                self.ExportOptions.renderOptions.prman.checked = False
            if settings.get("hydra"):
                self.ExportOptions.renderOptions.hydra.checked = True
            else:
                self.ExportOptions.renderOptions.hydra.checked = False

    def exportQuery (self):
        state = "enabled"
        if self.ExportOptions.nameEdit.text() == self.ExportOptions.nameEdit.defaultName:
            self.ExportOptions.nameEdit.showError(True)
            state = "disabled"
        elif self.ExportOptions.nameEdit.text() == self.ExportOptions.nameEdit.errorName:
            state = "disabled"
        if self.BrowserPath.isHidden():
            state = "disabled"
        self.ExportOptions.exportButton.setProperty("state", state)
        self.ExportOptions.exportButton.setStyleSheet("")

    def getOptions (self):
        if self.exported:
            class DataClass: pass
            options = DataClass()
            options.library = self.BrowserPath.getCurrentLibrary()
            options.materialPath = self.BrowserPath.resolve()
            options.materialName = self.ExportOptions.nameEdit.text()
            options.version = int(self.ExportOptions.versionOptions.versionCombobox.getName())
            options.variant = self.ExportOptions.versionOptions.variantCombobox.getName()
            options.link = self.ExportOptions.versionOptions.linkButton.isChecked()
            options.inherit = self.ExportOptions.inheritButton.checked
            options.maya = self.ExportOptions.mayaButton.checked
            options.info = self.ExportOptions.infoEdit.get()
            options.comment = self.ExportOptions.commentEdit.get()
            options.status = self.ExportOptions.status.get()
            options.prman = self.ExportOptions.renderOptions.prman.checked
            options.hydra = self.ExportOptions.renderOptions.hydra.checked
            return options
