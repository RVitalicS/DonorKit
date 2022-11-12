#!/usr/bin/env python



import os

from . import theme

import toolkit.core.naming
from toolkit.core import Metadata


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *

from . import BaseWidget
from . import BaseExport
from . import AssetExportUI

from . import Settings
UIGlobals = Settings.UIGlobals










class BaseMain (QtWidgets.QDialog):


    def __init__(self, parent=None):
        super(BaseMain, self).__init__(parent)

        self.theme = theme.Theme("AssetExport")
        self.setStyleSheet( self.theme.getStyleSheet() )

        self.setWindowTitle("USD Asset Export")
        self.setObjectName("UsdAssetExport")

        self.exit = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        self.exit.activated.connect(self.close)








class Dialog (
        BaseMain,
        BaseWidget.Browser,
        BaseWidget.Bookmark,
        BaseWidget.Favorite,
        BaseWidget.Slider,
        BaseWidget.Folder,
        BaseWidget.State,
        BaseExport.UI,
        BaseExport.Navigation,
        BaseExport.NameLogic ):



    def __init__(self, initname=None, parent=None):
        super(Dialog, self).__init__(parent)
        BaseWidget.Browser.__init__(self)

        AssetExportUI.setupUi(self, self.theme)
        self.connectUi()
        
        self.wantedType = "usdasset"
        self.exported = False

        self.setUiPath()
        self.applyUiSettings()

        self.Browser.setFocus(QtCore.Qt.MouseFocusReason)

        if initname:
            self.setName(initname)



    def connectUi (self):
        super(Dialog, self).connectUi()

        self.ExportOptions.modelingSwitch.released.connect(self.partitionExport)
        self.ExportOptions.surfacingSwitch.released.connect(self.partitionExport)
        self.ExportOptions.animationSwitch.released.connect(self.partitionExport)

        self.ExportOptions.modelingOverwrite.released.connect(self.overwriteState)
        self.ExportOptions.surfacingOverwrite.released.connect(self.overwriteState)
        self.ExportOptions.animationOverwrite.released.connect(self.overwriteState)

        self.ExportOptions.modelingOverwrite.released.connect(
            self.modelingOverwriteSetting )
        self.ExportOptions.surfacingOverwrite.released.connect(
            self.surfacingOverwriteSetting )
        self.ExportOptions.animationOverwrite.released.connect(
            self.animationOverwriteSetting )

        self.ExportOptions.animationOptions.animationNameCombobox.selectionChanged.connect(self.interpretTags)
        self.ExportOptions.animationOptions.range.start.valueChanged.connect(self.setRangeStart)
        self.ExportOptions.animationOptions.range.end.valueChanged.connect(self.setRangeEnd)

        self.ExportOptions.animationOptions.rangeButton.released.connect(self.getRange)



    def getDirItems (self, path, filterFavorites=False):

        return super(Dialog, self).getDirItems(path,
            filterFavorites=filterFavorites,
            showTypes=[self.wantedType] )



    def drawBrowserItems (self, path,
            filterFavorites=False):
    
        super(Dialog, self).drawBrowserItems(path,
            filterFavorites=filterFavorites)

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



    def setRangeStart (self, valueStart):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["rangeStart"] = valueStart

        valueEnd = self.ExportOptions.animationOptions.range.end.value()
        if valueStart > valueEnd:
            self.ExportOptions.animationOptions.range.end.setValue(valueStart)



    def setRangeEnd (self, valueEnd):

        with Settings.Manager(self.theme.app, True) as settings:
            settings["rangeEnd"] = valueEnd

        valueStart =  self.ExportOptions.animationOptions.range.start.value()
        if valueStart > valueEnd:
            self.ExportOptions.animationOptions.range.start.setValue(valueEnd)



    def getRange (self):

        from maya.OpenMayaAnim import MAnimControl

        valueStart = MAnimControl.minTime().value()
        valueEnd   = MAnimControl.maxTime().value()
        
        self.ExportOptions.animationOptions.range.start.setValue(valueStart)
        self.ExportOptions.animationOptions.range.end.setValue(valueEnd)



    def overwriteState (self):

        lockVersion = True
        if self.ExportOptions.modelingOverwrite.isEnabled():
            if self.ExportOptions.modelingOverwrite.isChecked():
                lockVersion = False

        if self.ExportOptions.surfacingOverwrite.isEnabled():
            if self.ExportOptions.surfacingOverwrite.isChecked():
                lockVersion = False

        if self.ExportOptions.animationOverwrite.isEnabled():
            if self.ExportOptions.animationOverwrite.isChecked():
                lockVersion = False

        if lockVersion:
            itemCount = self.ExportOptions.versionOptions.versionCombobox.count()

            lastVersion = 0
            for index in range(itemCount):
                version = self.ExportOptions.versionOptions.versionCombobox.itemText(index)
                version = int(version)

                if version > lastVersion:
                    lastVersion = version
                    self.ExportOptions.versionOptions.versionCombobox.setCurrentIndex(index)

            self.ExportOptions.animationOptions.nameDropdown.setEnabled(False)
            self.ExportOptions.versionOptions.variantDropdown.setEnabled(False)
            self.ExportOptions.versionOptions.versionDropdown.setEnabled(False)
            self.ExportOptions.versionOptions.versionCombobox.setEnabled(False)
        else:
            self.ExportOptions.animationOptions.nameDropdown.setEnabled(True)
            self.ExportOptions.versionOptions.variantDropdown.setEnabled(True)
            self.ExportOptions.versionOptions.versionDropdown.setEnabled(True)
            self.ExportOptions.versionOptions.versionCombobox.setEnabled(True)



    def interpretTags (self, choice):

        highlightAnimation = False
        highlightVariant   = False
        highlightLink      = False


        assetpath = self.getBrowserPath()
        assetname = self.getAssetName()

        self.ExportOptions.commentEdit.hide()
        comment = Metadata.getComment(assetpath, assetname)
        if not comment:
            self.ExportOptions.commentEdit.setDefault()
        else:
            self.ExportOptions.commentEdit.set(comment)
        self.ExportOptions.commentEdit.show()


        path = os.path.join(assetpath, assetname)
        if os.path.exists(path):

            animationPart = toolkit.core.naming.getAnimationName(assetname)
            animationName = self.ExportOptions.animationOptions.animationNameCombobox.getName()
            if animationPart == animationName != "":
                highlightAnimation = True

            variantPart = toolkit.core.naming.getVariantName(assetname)
            variantName = self.ExportOptions.versionOptions.variantCombobox.getName()
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
            if self.ExportOptions.animationOptions.animationNameCombobox.notSet():
                self.ExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "error")
            else:
                self.ExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "violet")
        else:
            if self.ExportOptions.animationOptions.animationNameCombobox.notSet():
                self.ExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "error")
            else:
                self.ExportOptions.animationOptions.animationNameCombobox.setProperty("textcolor", "on")

        if highlightVariant:
            self.ExportOptions.versionOptions.variantCombobox.setProperty("textcolor", "violet")
        else:
            self.ExportOptions.versionOptions.variantCombobox.setProperty("textcolor", "on")

        if highlightLink:
            self.ExportOptions.versionOptions.linkButton.setProperty("overwrite", "true")
        else:
            self.ExportOptions.versionOptions.linkButton.setProperty("overwrite", "false")

        self.ExportOptions.animationOptions.animationNameCombobox.setStyleSheet("")
        self.ExportOptions.versionOptions.variantCombobox.setStyleSheet("")
        self.ExportOptions.versionOptions.linkButton.repaint()



    def versionChoice (self, text):

        if text:
            directory = self.BrowserPath.resolve()
            if not directory: return
            
            name = self.ExportOptions.nameEdit.text()
            path = os.path.join(directory, name)

            version = int(text)


            self.ExportOptions.animationOptions.animationNameCombobox.stealth = True
            self.ExportOptions.animationOptions.animationNameCombobox.clear()
            animationList = toolkit.core.naming.getAnimationList(path, version=version)
            for animation in animationList:
                self.ExportOptions.animationOptions.animationNameCombobox.addItem(
                     animation )
            self.ExportOptions.animationOptions.animationNameCombobox.setCurrentIndex(-1)
            self.ExportOptions.animationOptions.animationNameCombobox.stealth = False


            self.ExportOptions.versionOptions.variantCombobox.stealth = True
            self.ExportOptions.versionOptions.variantCombobox.clear()
            variantList = toolkit.core.naming.getVariantList(path, version=version)
            for variant in variantList:
                self.ExportOptions.versionOptions.variantCombobox.addItem(
                     variant )
            self.ExportOptions.versionOptions.variantCombobox.setCurrentIndex(-1)
            self.ExportOptions.versionOptions.variantCombobox.stealth = False


            versionList = toolkit.core.naming.getVersionList(path)
            if version not in versionList:
                self.ExportOptions.versionOptions.versionCombobox.setProperty("textcolor", "on")
            else:
                self.ExportOptions.versionOptions.versionCombobox.setProperty("textcolor", "violet")

            self.ExportOptions.versionOptions.versionCombobox.setStyleSheet("")

            self.interpretTags("")



    def getBrowserPath (self):

        return os.path.join(
            self.BrowserPath.resolve(),
            self.ExportOptions.nameEdit.text() )



    def getAssetName (self, final=False, extension="usda"):

        name = self.ExportOptions.nameEdit.text()

        version = self.ExportOptions.versionOptions.versionCombobox.getName()
        version = int(version)

        variant = self.ExportOptions.versionOptions.variantCombobox.getName()
        animation = self.ExportOptions.animationOptions.animationNameCombobox.getName()

        if final:
            final = self.ExportOptions.versionOptions.linkButton.isChecked()

        return toolkit.core.naming.createAssetName(
            name=name,
            version=version,
            variant=variant,
            animation=animation,
            final=final,
            extension=extension )



    def partitionExport (self):

        animationSwitchChanged = False

        with Settings.Manager(self.theme.app, True) as settings:

            animationSwitchBefore = settings["animation"]
            animationSwitchAfter = self.ExportOptions.animationSwitch.isChecked()
            if animationSwitchBefore != animationSwitchAfter:
                animationSwitchChanged = True

            settings["modelling"] = self.ExportOptions.modelingSwitch.isChecked()
            settings["surfacing"] = self.ExportOptions.surfacingSwitch.isChecked()
            settings["animation"] = self.ExportOptions.animationSwitch.isChecked()

        self.applyUiSettings()

        if animationSwitchChanged:
            version = self.ExportOptions.versionOptions.versionCombobox.currentText()
            self.versionChoice(version)



    def modelingOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["modellingOverwrite"] = self.ExportOptions.modelingOverwrite.isChecked()

    def surfacingOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["surfacingOverwrite"] = self.ExportOptions.surfacingOverwrite.isChecked()

    def animationOverwriteSetting (self):
        with Settings.Manager(self.theme.app, True) as settings:
            settings["animationOverwrite"] = self.ExportOptions.animationOverwrite.isChecked()



    def applyUiSettings (self):
        super(Dialog, self).applyUiSettings()

        with Settings.Manager(self.theme.app, False) as settings:

            self.ExportOptions.animationOptions.range.start.setValue(settings.get("rangeStart"))
            self.ExportOptions.animationOptions.range.end.setValue(settings.get("rangeEnd"))

            modelingOn  = settings.get("modelling")
            surfacingOn = settings.get("surfacing")
            animationOn = settings.get("animation")

            if modelingOn:
                self.ExportOptions.modelingSwitch.setChecked(True)
                self.ExportOptions.modelingOverwrite.setEnabled(True)
            else:
                self.ExportOptions.modelingSwitch.setChecked(False)
                self.ExportOptions.modelingOverwrite.setEnabled(False)
            
            if settings.get("modellingOverwrite"):
                self.ExportOptions.modelingOverwrite.setChecked(True)
            else:
                self.ExportOptions.modelingOverwrite.setChecked(False)
            
            if surfacingOn:
                self.ExportOptions.surfacingSwitch.setChecked(True)
                self.ExportOptions.surfacingOverwrite.setEnabled(True)
            else:
                self.ExportOptions.surfacingSwitch.setChecked(False)
                self.ExportOptions.surfacingOverwrite.setEnabled(False)
            
            if settings.get("surfacingOverwrite"):
                self.ExportOptions.surfacingOverwrite.setChecked(True)
            else:
                self.ExportOptions.surfacingOverwrite.setChecked(False)

            if animationOn:
                self.ExportOptions.animationOptions.setVisible(True)
                self.ExportOptions.animationSwitch.setChecked(True)
                self.ExportOptions.animationOverwrite.setEnabled(True)
            else:
                self.ExportOptions.animationOptions.setVisible(False)
                self.ExportOptions.animationSwitch.setChecked(False)
                self.ExportOptions.animationOverwrite.setEnabled(False)
            
            if settings.get("animationOverwrite"):
                self.ExportOptions.animationOverwrite.setChecked(True)
            else:
                self.ExportOptions.animationOverwrite.setChecked(False)

            if modelingOn or surfacingOn or animationOn:
                self.ExportOptions.versionOptions.setVisible(True)
            else:
                self.ExportOptions.versionOptions.setVisible(False)

            if settings.get("link"):
                self.ExportOptions.versionOptions.linkButton.setChecked(True)
            else:
                self.ExportOptions.versionOptions.linkButton.setChecked(False)

            if settings.get("maya"):
                self.ExportOptions.mayaButton.checked = True
            else:
                self.ExportOptions.mayaButton.checked = False

        self.overwriteState()



    def exportQuery (self):

        state = "enabled"

        modelingOn  = self.ExportOptions.modelingSwitch.isChecked()
        surfacingOn = self.ExportOptions.surfacingSwitch.isChecked()
        animationOn = self.ExportOptions.animationSwitch.isChecked()

        if self.ExportOptions.nameEdit.text() == self.ExportOptions.nameEdit.defaultName:
            self.ExportOptions.nameEdit.showError(True)
            state = "disabled"

        elif self.ExportOptions.nameEdit.text() == self.ExportOptions.nameEdit.errorName:
            state = "disabled"

        if animationOn and self.ExportOptions.animationOptions.animationNameCombobox.notSet():
            self.ExportOptions.animationOptions.animationNameCombobox.showError(True)
            state = "disabled"

        elif not modelingOn and not surfacingOn and not animationOn:
            state = "disabled"
        elif self.BrowserPath.isHidden():
            state = "disabled"

        self.ExportOptions.exportButton.setProperty("state", state)
        self.ExportOptions.exportButton.setStyleSheet("")



    def getOptions (self):

        if self.exported:

            class DataClass: pass
            options = DataClass()

            options.modelling = self.ExportOptions.modelingSwitch.isChecked()
            options.modellingOverride = self.ExportOptions.modelingOverwrite.isChecked()

            options.surfacing = self.ExportOptions.surfacingSwitch.isChecked()
            options.surfacingOverride = self.ExportOptions.surfacingOverwrite.isChecked()

            options.animation = self.ExportOptions.animationSwitch.isChecked()
            options.animationOverride = self.ExportOptions.animationOverwrite.isChecked()

            options.animationName = self.ExportOptions.animationOptions.animationNameCombobox.getName()

            options.minTime = self.ExportOptions.animationOptions.range.start.value()
            options.maxTime = self.ExportOptions.animationOptions.range.end.value()

            options.assetPath = self.getBrowserPath()
            options.assetName = self.getAssetName()

            options.version = int(self.ExportOptions.versionOptions.versionCombobox.getName())
            options.variant = self.ExportOptions.versionOptions.variantCombobox.getName()
            options.link = self.ExportOptions.versionOptions.linkButton.isChecked()

            options.maya = self.ExportOptions.mayaButton.checked

            options.info = self.ExportOptions.infoEdit.get()
            options.comment = self.ExportOptions.commentEdit.get()
            options.status = self.ExportOptions.status.get()

            return options
