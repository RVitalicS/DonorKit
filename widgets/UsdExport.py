#!/usr/bin/env python



import os
import re

from . import resources
from . import theme

import toolkit.core.metadata
import toolkit.core.naming

from toolkit.system import stream


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from . import BaseWidget
from . import UsdExportUI

from . import Metadata
from . import Settings
UIGlobals = Settings.UIGlobals










class ExportBase (QtWidgets.QDialog):


    def __init__(self, parent=None):
        super(ExportBase, self).__init__(parent)

        self.theme = theme.Theme("export")
        self.setStyleSheet( self.theme.getStyleSheet() )

        self.setWindowTitle("USD Asset Export")
        self.setObjectName("UsdExport")








class Dialog (
        ExportBase,
        BaseWidget.Browser,
        BaseWidget.Bookmark,
        BaseWidget.Favorite,
        BaseWidget.Slider,
        BaseWidget.Folder,
        BaseWidget.State ):



    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        BaseWidget.Browser.__init__(self)

        UsdExportUI.setupUi(self, self.theme)
        self.connectUi()
        
        self.exported = False

        self.setUiPath()
        self.applyUiSettings()

        self.AssetBrowser.setFocus(QtCore.Qt.MouseFocusReason)



    def connectUi (self):

        self.AssetBrowser.iconClicked.connect(self.iconClicked)
        self.AssetBrowser.favoriteClicked.connect(self.favoriteClicked)
        self.AssetBrowser.link.connect(self.linkAction)
        self.AssetBrowser.createFolderQuery.connect(self.createFolderQuery)
        self.AssetBrowser.createFolder.connect(self.createFolder)

        self.AssetPath.pathChanged.connect(self.drawDecision)
        self.AssetPath.pathChanged.connect(self.uiVisibility)
        self.AssetPath.bookmarkClicked.connect(self.switchBookmark)

        self.BarBottom.preview.slider.valueChanged.connect(self.sliderAction)
        self.BarBottom.favorite.button.released.connect(self.favoriteFilter)
        self.BarBottom.bookmarkChosen.connect(self.jumpBookmark)

        self.ResizeButton.moveStart.connect(self.resizeMath)

        self.UsdExportOptions.nameEdit.textChanged.connect(self.setName)

        self.UsdExportOptions.modelingSwitch.released.connect(self.partitionExport)
        self.UsdExportOptions.surfacingSwitch.released.connect(self.partitionExport)
        self.UsdExportOptions.animationSwitch.released.connect(self.partitionExport)

        self.UsdExportOptions.modelingOverwrite.released.connect(self.overwriteState)
        self.UsdExportOptions.surfacingOverwrite.released.connect(self.overwriteState)
        self.UsdExportOptions.animationOverwrite.released.connect(self.overwriteState)

        self.UsdExportOptions.modelingOverwrite.released.connect(
            self.modelingOverwriteSetting )
        self.UsdExportOptions.surfacingOverwrite.released.connect(
            self.surfacingOverwriteSetting )
        self.UsdExportOptions.animationOverwrite.released.connect(
            self.animationOverwriteSetting )

        self.UsdExportOptions.animationOptions.animationNameCombobox.selectionChanged.connect(self.interpretTags)
        self.UsdExportOptions.animationOptions.range.start.valueChanged.connect(self.setRangeStart)
        self.UsdExportOptions.animationOptions.range.end.valueChanged.connect(self.setRangeEnd)

        self.UsdExportOptions.animationOptions.rangeButton.released.connect(self.getRange)

        self.UsdExportOptions.mainOptions.variantCombobox.selectionChanged.connect(self.interpretTags)
        self.UsdExportOptions.mainOptions.versionCombobox.selectionChanged.connect(self.versionChoice)

        self.UsdExportOptions.mainOptions.linkButton.released.connect(self.linkWrap)

        self.UsdExportOptions.exportButton.pressed.connect(self.exportQuery)
        self.UsdExportOptions.exportButton.released.connect(self.exportAction)



    def uiVisibility (self, path):
        
        if self.AssetPath.isRoot(path):
            self.AssetPath.hide()
            self.BarBottom.hide()

            self.ResizeButton.hide()
            self.UsdExportOptions.hide()

        else:
            self.AssetPath.show()
            self.BarBottom.show()

            self.ResizeButton.show()
            self.UsdExportOptions.show()



    def getDirItems (self, path,
            filterFavorites=False,
            showTypes=["usdasset"] ):

        return super(Dialog, self).getDirItems(path,
            filterFavorites=filterFavorites,
            showTypes=showTypes )



    def drawBrowserItems (self, path,
            filterFavorites=False):
    
        super(Dialog, self).drawBrowserItems(path,
            filterFavorites=filterFavorites)

        hasCheckedName = False
        model = self.AssetBrowser.model()
        for index in range(model.rowCount()):

            item = model.item(index)
            data = item.data(QtCore.Qt.StatusTipRole)
            if data == 1:
                hasCheckedName = True
                break

        if not hasCheckedName:
            self.checkedName = ""
            self.setOptions()



    def setRangeStart (self, valueStart):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["rangeStart"] = valueStart

        valueEnd = self.UsdExportOptions.animationOptions.range.end.value()
        if valueStart > valueEnd:
            self.UsdExportOptions.animationOptions.range.end.setValue(valueStart)



    def setRangeEnd (self, valueEnd):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["rangeEnd"] = valueEnd

        valueStart =  self.UsdExportOptions.animationOptions.range.start.value()
        if valueStart > valueEnd:
            self.UsdExportOptions.animationOptions.range.start.setValue(valueEnd)



    def getRange (self):

        from maya.OpenMayaAnim import MAnimControl

        valueStart = MAnimControl.minTime().value()
        valueEnd   = MAnimControl.maxTime().value()
        
        self.UsdExportOptions.animationOptions.range.start.setValue(valueStart)
        self.UsdExportOptions.animationOptions.range.end.setValue(valueEnd)



    def overwriteState (self):

        lockVersion = True
        if self.UsdExportOptions.modelingOverwrite.isEnabled():
            if self.UsdExportOptions.modelingOverwrite.isChecked():
                lockVersion = False

        if self.UsdExportOptions.surfacingOverwrite.isEnabled():
            if self.UsdExportOptions.surfacingOverwrite.isChecked():
                lockVersion = False

        if self.UsdExportOptions.animationOverwrite.isEnabled():
            if self.UsdExportOptions.animationOverwrite.isChecked():
                lockVersion = False

        if lockVersion:
            itemCount = self.UsdExportOptions.mainOptions.versionCombobox.count()

            lastVersion = 0
            for index in range(itemCount):
                version = self.UsdExportOptions.mainOptions.versionCombobox.itemText(index)
                version = int(version)

                if version > lastVersion:
                    lastVersion = version
                    self.UsdExportOptions.mainOptions.versionCombobox.setCurrentIndex(index)

            self.UsdExportOptions.animationOptions.nameDropdown.setEnabled(False)
            self.UsdExportOptions.mainOptions.variantDropdown.setEnabled(False)
            self.UsdExportOptions.mainOptions.versionDropdown.setEnabled(False)
            self.UsdExportOptions.mainOptions.versionCombobox.setEnabled(False)
        else:
            self.UsdExportOptions.animationOptions.nameDropdown.setEnabled(True)
            self.UsdExportOptions.mainOptions.variantDropdown.setEnabled(True)
            self.UsdExportOptions.mainOptions.versionDropdown.setEnabled(True)
            self.UsdExportOptions.mainOptions.versionCombobox.setEnabled(True)



    def linkWrap (self):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["link"] = self.UsdExportOptions.mainOptions.linkButton.isChecked()

        self.interpretTags("")



    def interpretTags (self, choice):

        highlightAnimation = False
        highlightVariant   = False
        highlightLink      = False


        assetpath = self.getAssetPath()
        assetname = self.getAssetName()

        self.UsdExportOptions.commentEdit.hide()
        comment = toolkit.core.metadata.getComment(assetpath, assetname)
        if not comment:
            self.UsdExportOptions.commentEdit.setDefault()
        else:
            self.UsdExportOptions.commentEdit.set(comment)
        self.UsdExportOptions.commentEdit.show()


        path = os.path.join(assetpath, assetname)
        if os.path.exists(path):

            animationPart = toolkit.core.naming.getAnimationName(assetname)
            animationName = self.UsdExportOptions.animationOptions.animationNameCombobox.getName()
            if animationPart == animationName != "":
                highlightAnimation = True

            variantPart = toolkit.core.naming.getVariantName(assetname)
            variantName = self.UsdExportOptions.mainOptions.variantCombobox.getName()
            if variantPart == variantName != "":
                highlightVariant = True

            finalname = toolkit.core.naming.makeFinal(assetname)
            finalpath = os.path.join(assetpath, finalname)
            if os.path.exists(finalpath):
                realpath = os.path.realpath(finalpath)
                realname = os.path.basename(realpath)
                if realname == assetname:
                    highlightLink = True


        if highlightAnimation:
            if self.UsdExportOptions.animationOptions.animationNameCombobox.notSet():
                self.UsdExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "error")
            else:
                self.UsdExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "violet")
        else:
            if self.UsdExportOptions.animationOptions.animationNameCombobox.notSet():
                self.UsdExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "error")
            else:
                self.UsdExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "on")

        if highlightVariant:
            self.UsdExportOptions.mainOptions.variantCombobox.setProperty("textcolor", "violet")
        else:
            self.UsdExportOptions.mainOptions.variantCombobox.setProperty("textcolor", "on")

        if highlightLink:
            self.UsdExportOptions.mainOptions.linkButton.setProperty("overwrite", "true")
        else:
            self.UsdExportOptions.mainOptions.linkButton.setProperty("overwrite", "false")

        self.UsdExportOptions.animationOptions.animationNameCombobox.setStyleSheet("")
        self.UsdExportOptions.mainOptions.variantCombobox.setStyleSheet("")
        self.UsdExportOptions.mainOptions.linkButton.repaint()



    def versionChoice (self, text):

        if text:
            directory = self.AssetPath.resolve()
            if not directory: return
            
            name = self.UsdExportOptions.nameEdit.text()
            path = os.path.join(directory, name)

            version = int(text)


            self.UsdExportOptions.animationOptions.animationNameCombobox.stealth = True
            self.UsdExportOptions.animationOptions.animationNameCombobox.clear()
            animationList = toolkit.core.naming.getAnimationList(path, version=version)
            for animation in animationList:
                self.UsdExportOptions.animationOptions.animationNameCombobox.addItem(
                     animation )
            self.UsdExportOptions.animationOptions.animationNameCombobox.setCurrentIndex(-1)
            self.UsdExportOptions.animationOptions.animationNameCombobox.stealth = False


            self.UsdExportOptions.mainOptions.variantCombobox.stealth = True
            self.UsdExportOptions.mainOptions.variantCombobox.clear()
            variantList = toolkit.core.naming.getVariantList(path, version=version)
            for variant in variantList:
                self.UsdExportOptions.mainOptions.variantCombobox.addItem(
                     variant )
            self.UsdExportOptions.mainOptions.variantCombobox.setCurrentIndex(-1)
            self.UsdExportOptions.mainOptions.variantCombobox.stealth = False


            versionList = toolkit.core.naming.getVersionList(path)
            if version not in versionList:
                self.UsdExportOptions.mainOptions.versionCombobox.setProperty("textcolor", "on")
            else:
                self.UsdExportOptions.mainOptions.versionCombobox.setProperty("textcolor", "violet")

            self.UsdExportOptions.mainOptions.versionCombobox.setStyleSheet("")

            self.interpretTags("")



    def getAssetPath (self):

        return os.path.join(
            self.AssetPath.resolve(),
            self.UsdExportOptions.nameEdit.text() )



    def getAssetName (self, final=False, extension="usda"):

        name = self.UsdExportOptions.nameEdit.text()

        version = self.UsdExportOptions.mainOptions.versionCombobox.getName()
        version = int(version)

        variant = self.UsdExportOptions.mainOptions.variantCombobox.getName()
        animation = self.UsdExportOptions.animationOptions.animationNameCombobox.getName()

        if final:
            final = self.UsdExportOptions.mainOptions.linkButton.isChecked()

        return toolkit.core.naming.createAssetName(
            name, version,
            variant=variant,
            animation=animation,
            final=final,
            extension=extension )



    def partitionExport (self):

        animationSwitchChanged = False

        with Settings.Manager(self.theme.app, True) as settings:

            animationSwitchBefore = settings["animation"]
            animationSwitchAfter = self.UsdExportOptions.animationSwitch.isChecked()
            if animationSwitchBefore != animationSwitchAfter:
                animationSwitchChanged = True

            settings["modelling"] = self.UsdExportOptions.modelingSwitch.isChecked()
            settings["surfacing"] = self.UsdExportOptions.surfacingSwitch.isChecked()
            settings["animation"] = self.UsdExportOptions.animationSwitch.isChecked()

        self.applyUiSettings()

        if animationSwitchChanged:
            version = self.UsdExportOptions.mainOptions.versionCombobox.currentText()
            self.versionChoice(version)



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
                self.AssetPath.goForward(name)
                self.checkedName = ""

            elif dataType == "usdasset":
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

        directory = self.AssetPath.resolve()
        name = self.UsdExportOptions.nameEdit.text()
        path = os.path.join(directory, name)

        metadataPath = os.path.join(path, self.metafile)
        data = stream.dataread(metadataPath)
        self.UsdExportOptions.status.set(
            data.get("status", "") )



    def setName (self, text):

        text = self.UsdExportOptions.nameEdit.setName(text)

        if text == self.UsdExportOptions.nameEdit.errorName:
            self.UsdExportOptions.nameEdit.setProperty("textcolor", "error")
            self.currentName = ""
            self.checkedName = ""
            self.UsdExportOptions.status.set()

        elif text == self.UsdExportOptions.nameEdit.defaultName:
            self.UsdExportOptions.nameEdit.setProperty("textcolor", "weak")
            self.currentName = ""
            self.checkedName = ""
            self.UsdExportOptions.status.set()

        elif text in self.assetsNames:
            self.UsdExportOptions.nameEdit.setProperty("textcolor", "violet")
            
            inputMatch = False
            if not text == self.checkedName:
                inputMatch = True

            self.currentName = ""
            self.checkedName = text

            self.loadStatus()
            if inputMatch:
                self.setOptions()

        else:
            self.UsdExportOptions.nameEdit.setProperty("textcolor", "kicker")

            inputMatchBreak = False
            if not self.checkedName == "":
                inputMatchBreak = True

            self.currentName = text
            self.checkedName = ""

            if inputMatchBreak:
                self.UsdExportOptions.status.set()
                self.setOptions(force=True)


        self.UsdExportOptions.nameEdit.setStyleSheet("")


        model = self.AssetBrowser.model()
        for raw in range(model.rowCount()):
            item = model.item(raw)
            data = item.data(QtCore.Qt.EditRole)
            iconType = data["type"]

            if iconType == "usdasset":

                if data["name"] == self.checkedName:
                    item.setData(1, QtCore.Qt.StatusTipRole)
                else:
                    item.setData(0, QtCore.Qt.StatusTipRole)

            else:
                item.setData(0, QtCore.Qt.StatusTipRole)



    def setOptions (self, force=False):

        # if name the same do nothing
        if not force:
            name = self.currentName
            text = self.UsdExportOptions.nameEdit.text()
            if name:
                if name == text: return


        # set asset name text
        if self.checkedName:
            name = self.checkedName
        elif self.currentName:
            name = self.currentName
        elif self.UsdExportOptions.nameEdit.errorVisible:
            name = self.UsdExportOptions.nameEdit.errorName
        else:
            name = self.UsdExportOptions.nameEdit.defaultName

        self.UsdExportOptions.nameEdit.setText(name)

        # set default options
        self.UsdExportOptions.mainOptions.versionCombobox.clear()

        if name in [ self.UsdExportOptions.nameEdit.errorName,
                     self.UsdExportOptions.nameEdit.defaultName ]:
            self.UsdExportOptions.mainOptions.versionCombobox.addItem("01")
            self.UsdExportOptions.infoEdit.setDefault()


        # load asset options
        else:

            directory = self.AssetPath.resolve()
            name = self.UsdExportOptions.nameEdit.text()
            path = os.path.join(directory, name)

            info = toolkit.core.metadata.getInfo(path)
            if info:
                self.UsdExportOptions.infoEdit.set(info)
            else:
                self.UsdExportOptions.infoEdit.setDefault()

            versionList = toolkit.core.naming.getVersionList(path)

            newItem = 0
            for version in versionList:
                if version > newItem:
                    newItem = version
            versionList.append(newItem+1)

            lastItem = 0
            self.UsdExportOptions.mainOptions.versionCombobox.stealth = True
            for version in versionList:
                self.UsdExportOptions.mainOptions.versionCombobox.addItem(
                     "{:02d}".format(version) )
                if version > lastItem:
                    lastItem = version

            self.UsdExportOptions.mainOptions.versionCombobox.setCurrentIndex(lastItem-1)
            self.UsdExportOptions.mainOptions.versionCombobox.stealth = False




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
            self.UsdExportOptions.setOptionWidth(optionWidth)



    def resizeEvent (self, event):
        super(Dialog, self).resizeEvent(event)

        with Settings.Manager(self.theme.app, True) as settings:
            settings["size"] = [ self.width(), self.height() ]



    def modelingOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["modellingOverwrite"] = self.UsdExportOptions.modelingOverwrite.isChecked()

    def surfacingOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["surfacingOverwrite"] = self.UsdExportOptions.surfacingOverwrite.isChecked()

    def animationOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["animationOverwrite"] = self.UsdExportOptions.animationOverwrite.isChecked()



    def applyUiSettings (self):
        super(Dialog, self).applyUiSettings()

        with Settings.Manager(self.theme.app, False) as settings:

            self.UsdExportOptions.animationOptions.range.start.setValue(settings.get("rangeStart"))
            self.UsdExportOptions.animationOptions.range.end.setValue(settings.get("rangeEnd"))

            modelingOn  = settings.get("modelling")
            surfacingOn = settings.get("surfacing")
            animationOn = settings.get("animation")

            if modelingOn:
                self.UsdExportOptions.modelingSwitch.setChecked(True)
                self.UsdExportOptions.modelingOverwrite.setEnabled(True)
            else:
                self.UsdExportOptions.modelingSwitch.setChecked(False)
                self.UsdExportOptions.modelingOverwrite.setEnabled(False)
            
            if settings.get("modellingOverwrite"):
                self.UsdExportOptions.modelingOverwrite.setChecked(True)
            else:
                self.UsdExportOptions.modelingOverwrite.setChecked(False)
            
            if surfacingOn:
                self.UsdExportOptions.surfacingSwitch.setChecked(True)
                self.UsdExportOptions.surfacingOverwrite.setEnabled(True)
            else:
                self.UsdExportOptions.surfacingSwitch.setChecked(False)
                self.UsdExportOptions.surfacingOverwrite.setEnabled(False)
            
            if settings.get("surfacingOverwrite"):
                self.UsdExportOptions.surfacingOverwrite.setChecked(True)
            else:
                self.UsdExportOptions.surfacingOverwrite.setChecked(False)

            if animationOn:
                self.UsdExportOptions.animationOptions.setVisible(True)
                self.UsdExportOptions.animationSwitch.setChecked(True)
                self.UsdExportOptions.animationOverwrite.setEnabled(True)
            else:
                self.UsdExportOptions.animationOptions.setVisible(False)
                self.UsdExportOptions.animationSwitch.setChecked(False)
                self.UsdExportOptions.animationOverwrite.setEnabled(False)
            
            if settings.get("animationOverwrite"):
                self.UsdExportOptions.animationOverwrite.setChecked(True)
            else:
                self.UsdExportOptions.animationOverwrite.setChecked(False)

            if modelingOn or surfacingOn or animationOn:
                self.UsdExportOptions.mainOptions.setVisible(True)
            else:
                self.UsdExportOptions.mainOptions.setVisible(False)

            if settings.get("link"):
                self.UsdExportOptions.mainOptions.linkButton.setChecked(True)
            else:
                self.UsdExportOptions.mainOptions.linkButton.setChecked(False)

        self.overwriteState()



    def exportQuery (self):

        state = "enabled"

        modelingOn  = self.UsdExportOptions.modelingSwitch.isChecked()
        surfacingOn = self.UsdExportOptions.surfacingSwitch.isChecked()
        animationOn = self.UsdExportOptions.animationSwitch.isChecked()

        if self.UsdExportOptions.nameEdit.text() == self.UsdExportOptions.nameEdit.defaultName:
            self.UsdExportOptions.nameEdit.showError(True)
            state = "disabled"

        elif self.UsdExportOptions.nameEdit.text() == self.UsdExportOptions.nameEdit.errorName:
            state = "disabled"

        if animationOn and self.UsdExportOptions.animationOptions.animationNameCombobox.notSet():
            self.UsdExportOptions.animationOptions.animationNameCombobox.showError(True)
            state = "disabled"

        elif not modelingOn and not surfacingOn and not animationOn:
            state = "disabled"
        elif self.AssetPath.isHidden():
            state = "disabled"

        self.UsdExportOptions.exportButton.setProperty("state", state)
        self.UsdExportOptions.exportButton.setStyleSheet("")



    def exportAction (self):

        if self.UsdExportOptions.exportButton.property("state") == "enabled":
            self.exported = True
            self.close()



    def getOptions (self):

        if self.exported:

            class DataClass: pass
            options = DataClass()

            options.modelling = self.UsdExportOptions.modelingSwitch.isChecked()
            options.modellingOverride = self.UsdExportOptions.modelingOverwrite.isChecked()

            options.surfacing = self.UsdExportOptions.surfacingSwitch.isChecked()
            options.surfacingOverride = self.UsdExportOptions.surfacingOverwrite.isChecked()

            options.animation = self.UsdExportOptions.animationSwitch.isChecked()
            options.animationOverride = self.UsdExportOptions.animationOverwrite.isChecked()

            options.animationName = self.UsdExportOptions.animationOptions.animationNameCombobox.getName()

            options.minTime = self.UsdExportOptions.animationOptions.range.start.value()
            options.maxTime = self.UsdExportOptions.animationOptions.range.end.value()

            options.assetPath = self.getAssetPath()
            options.assetName = self.getAssetName()

            options.version = int(self.UsdExportOptions.mainOptions.versionCombobox.getName())
            options.variant = self.UsdExportOptions.mainOptions.variantCombobox.getName()
            options.link = self.UsdExportOptions.mainOptions.linkButton.isChecked()

            options.info = self.UsdExportOptions.infoEdit.get()
            options.comment = self.UsdExportOptions.commentEdit.get()
            options.status = self.UsdExportOptions.status.get()

            return options
