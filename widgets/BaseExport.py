#!/usr/bin/env python

"""
"""

import toolkit.core.naming as naming
from toolkit.core import Metadata
from toolkit.ensure.QtCore import *
from widgets import BaseWidget
from widgets import Settings


def Make (Base):

    class Child (BaseWidget.Make(Base)):

        def __init__(self, parent=None):
            super(Child, self).__init__(parent=parent)

        def connectUi (self):
            self.Browser.iconClicked.connect(self.iconClicked)
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
            self.ExportOptions.nameEdit.textChanged.connect(self.setName)
            self.ExportOptions.versionOptions.variantCombobox.selectionChanged.connect(self.interpretTags)
            self.ExportOptions.versionOptions.versionCombobox.selectionChanged.connect(self.versionChoice)
            self.ExportOptions.versionOptions.linkButton.released.connect(self.linkSettings)
            self.ExportOptions.mayaButton.stateChanged.connect(self.mayaSettings)
            self.ExportOptions.exportButton.pressed.connect(self.exportQuery)
            self.ExportOptions.exportButton.released.connect(self.exportAction)
        
        def uiVisibility (self, path):
            if self.BrowserPath.isRoot(path):
                self.BrowserPath.hide()
                self.BarBottom.hide()
                self.ResizeButton.hide()
                self.ExportOptions.hide()
            else:
                self.BrowserPath.show()
                self.BarBottom.show()
                self.ResizeButton.show()
                self.ExportOptions.show()
        
        def linkSettings (self):
            with Settings.Manager(self.theme.app, True) as settings:
                settings["link"] = self.ExportOptions.versionOptions.linkButton.isChecked()
            self.interpretTags("")
        
        def mayaSettings (self):
            with Settings.Manager(self.theme.app, True) as settings:
                settings["maya"] = self.ExportOptions.mayaButton.checked
        
        def exportAction (self):
            if self.ExportOptions.exportButton.property("state") == "enabled":
                self.exported = True
                self.close()

        def iconClicked (self, index):
            data = index.data(QtCore.Qt.EditRole)
            force = False
            if data:
                dataType = data["type"]
                if dataType == "library":
                    libname = data.get("name")
                    self.setUiPath(libname)
                    return
                elif dataType == "folder":
                    name = data.get("name")
                    self.BrowserPath.goForward(name)
                    self.checkedName = ""
                elif dataType == self.wantedType:
                    name = data.get("name")
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
            path = os.path.join(
                self.BrowserPath.resolve(), 
                self.ExportOptions.nameEdit.text())
            status = Metadata.getStatus(path)
            self.ExportOptions.status.set(status)

        def setName (self, text):
            text = self.ExportOptions.nameEdit.setName(text)
            if text == self.ExportOptions.nameEdit.errorName:
                self.ExportOptions.nameEdit.setProperty("textcolor", "error")
                self.currentName = ""
                self.checkedName = ""
                self.ExportOptions.status.set()
            elif text == self.ExportOptions.nameEdit.defaultName:
                self.ExportOptions.nameEdit.setProperty("textcolor", "weak")
                self.currentName = ""
                self.checkedName = ""
                self.ExportOptions.status.set()
            elif text in self.assetsNames:
                self.ExportOptions.nameEdit.setProperty("textcolor", "violet")
                inputMatch = False
                if not text == self.checkedName:
                    inputMatch = True
                self.currentName = ""
                self.checkedName = text
                self.loadStatus()
                if inputMatch:
                    self.setOptions()
            else:
                self.ExportOptions.nameEdit.setProperty("textcolor", "kicker")
                inputMatchBreak = False
                if not self.checkedName == "":
                    inputMatchBreak = True
                self.currentName = text
                self.checkedName = ""
                if inputMatchBreak:
                    self.ExportOptions.status.set()
                    self.setOptions(force=True)
            self.ExportOptions.nameEdit.setStyleSheet("")
            
            model = self.Browser.model()
            for raw in range(model.rowCount()):
                item = model.item(raw)
                data = item.data(QtCore.Qt.EditRole)
                if data.get("type") == self.wantedType:
                    if data.get("name") == self.checkedName:
                        item.setData(1, QtCore.Qt.StatusTipRole)
                    else:
                        item.setData(0, QtCore.Qt.StatusTipRole)
                else:
                    item.setData(0, QtCore.Qt.StatusTipRole)
        
        def setOptions (self, force=False):
            # if name the same do nothing
            if not force:
                name = self.currentName
                text = self.ExportOptions.nameEdit.text()
                if name:
                    if name == text: return
            # set name text
            if self.checkedName:
                name = self.checkedName
            elif self.currentName:
                name = self.currentName
            elif self.ExportOptions.nameEdit.errorVisible:
                name = self.ExportOptions.nameEdit.errorName
            else:
                name = self.ExportOptions.nameEdit.defaultName
            self.ExportOptions.nameEdit.setText(name)
            # set default options
            self.ExportOptions.versionOptions.versionCombobox.clear()
            if name in [ self.ExportOptions.nameEdit.errorName,
                         self.ExportOptions.nameEdit.defaultName ]:
                self.ExportOptions.versionOptions.versionCombobox.addItem("01")
                self.ExportOptions.infoEdit.setDefault()
            # load options
            else:
                directory = self.BrowserPath.resolve()
                name = self.ExportOptions.nameEdit.text()
                path = os.path.join(directory, name)
                info = Metadata.getInfo(path)
                if info:
                    self.ExportOptions.infoEdit.set(info)
                else:
                    self.ExportOptions.infoEdit.setDefault()
                versionList = naming.getVersionList(path)
                newItem = 0
                for version in versionList:
                    if version > newItem:
                        newItem = version
                versionList.append(newItem+1)
                lastIndex = 0
                text = None
                
                self.ExportOptions.versionOptions.versionCombobox.stealth = True
                for version in versionList:
                    text = "{:02d}".format(version)
                    self.ExportOptions.versionOptions.versionCombobox.addItem(text)
                    if version-1 > lastIndex:
                        lastIndex = version-1
                self.ExportOptions.versionOptions.versionCombobox.setCurrentIndex(lastIndex)
                self.ExportOptions.versionOptions.versionCombobox.stealth = False
                self.versionChoice(text)

        def resizeMath (self, value):
            optionWidth = super(Child, self).resizeMath(value)
            if optionWidth is not None:
                self.ExportOptions.setOptionWidth(optionWidth)

    return Child
