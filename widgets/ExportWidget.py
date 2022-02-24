#!/usr/bin/env python



import os

from . import resources
from . import stylesheet
from . import tools


from Qt import QtWidgets, QtCore, QtGui

from . import AssetBrowser
from . import IconDelegate
from . import PathBar
from . import BottomBar

from . import ExportUI

from . import Settings
UIsettings = Settings.UIsettings









class ExportWidget (QtWidgets.QDialog):


    def __init__(self, parent=None):
        super(ExportWidget, self).__init__(parent)

        self.setStyleSheet( stylesheet.UI )

        self.browserLayout = QtWidgets.QVBoxLayout()
        self.browserLayout.setContentsMargins(0, 0, 0, 0)
        self.browserLayout.setSpacing(0)

        self.assetPath = PathBar.PathBar()
        self.browserLayout.addWidget(self.assetPath)

        self.AssetBrowser = AssetBrowser.AssetBrowser()
        self.browserLayout.addWidget(self.AssetBrowser)

        self.BottomBar = BottomBar.BottomBar()
        self.browserLayout.addWidget(self.BottomBar)

        ExportUI.setupUi(self, self.browserLayout)
        self.connectUi()
        self.applySettings()

        self.metadata  = ".metadata.json"
        self.libraries = self.getAssetRoots()
        self.setLibrary()

        self.setWindowTitle("Asset Export")
        self.setObjectName("ExportWidget")
        self.resize(820, 580)


        self.AssetBrowser.setFocus(QtCore.Qt.MouseFocusReason)

        self.exported = False



    def connectUi (self):

        self.AssetBrowser.iconClicked.connect(self.iconClicked)
        self.assetPath.pathChanged.connect(self.drawBrowserItems)
        self.BottomBar.previewSlider.valueChanged.connect(self.sliderAction)

        self.nameLineEdit.textChanged.connect(self.setName)

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

        self.animationOpions.animationNameCombobox.currentTextChanged.connect(self.hilightTags)
        self.animationOpions.rangeStartSpinbox.valueChanged.connect(self.setRangeStart)
        self.animationOpions.rangeEndSpinbox.valueChanged.connect(self.setRangeEnd)
        self.animationOpions.fpsSpinbox.valueChanged.connect(self.fpsSetting)

        self.animationOpions.rangeButton.released.connect(self.getRange)

        self.mainOpions.variantCombobox.currentTextChanged.connect(self.hilightTags)
        self.mainOpions.versionCombobox.currentTextChanged.connect(self.versionChoice)
        self.mainOpions.unitSpinbox.valueChanged.connect(self.unitSetting)

        self.mainOpions.linkButton.released.connect(self.linkWrap)

        self.exportButton.pressed.connect(self.exportQuery)
        self.exportButton.released.connect(self.exportAction)



    def setRangeStart (self, valueStart):

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["rangeStart"] = valueStart

        valueEnd = self.animationOpions.rangeEndSpinbox.value()
        if valueStart > valueEnd:
            self.animationOpions.rangeEndSpinbox.setValue(valueStart)



    def setRangeEnd (self, valueEnd):

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["rangeEnd"] = valueEnd

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

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["link"] = self.mainOpions.linkButton.isChecked()

        self.hilightTags("")



    def hilightTags (self, choice):

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


        if hilight:
            self.animationOpions.animationNameCombobox.setProperty("textcolor", "violet")
            self.animationOpions.animationNameCombobox.setStyleSheet("")
            self.mainOpions.variantCombobox.setProperty("textcolor", "violet")
            self.mainOpions.variantCombobox.setStyleSheet("")
            self.mainOpions.linkButton.setProperty("overwrite", "true")
        else:
            self.animationOpions.animationNameCombobox.setProperty("textcolor", "light")
            self.animationOpions.animationNameCombobox.setStyleSheet("")
            self.mainOpions.variantCombobox.setProperty("textcolor", "light")
            self.mainOpions.variantCombobox.setStyleSheet("")
            self.mainOpions.linkButton.setProperty("overwrite", "false")

        self.mainOpions.linkButton.setStyleSheet("")



    def versionChoice (self, text):

        if text:
            directory = self.assetPath.get()
            name = self.nameLineEdit.text()
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
                self.mainOpions.versionCombobox.setProperty("textcolor", "light")
            else:
                self.mainOpions.versionCombobox.setProperty("textcolor", "violet")

            self.mainOpions.versionCombobox.setStyleSheet("")

            self.hilightTags("")



    def sliderAction (self, value):

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["iconSize"] = value

        self.AssetBrowser.setGrid()



    def getAssetPath (self):

        return os.path.join(
            self.assetPath.get(),
            self.nameLineEdit.text() )



    def getAssetName (self, final=True, extension="usda"):

        name = self.nameLineEdit.text()

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

        with Settings.UIManager(update=True) as uiSettings:

            uiSettings["modelling"] = self.modelingSwitch.isChecked()
            uiSettings["surfacing"] = self.surfacingSwitch.isChecked()
            uiSettings["animation"] = self.animationSwitch.isChecked()

        self.applySettings()



    def iconClicked (self, index):

        data = index.data(QtCore.Qt.EditRole)

        if data:
            dataType = data["type"]

            if dataType == "folder":
                name = data["data"]["name"]
                self.assetPath.moveForward(name)
                self.checkedName = ""

            elif dataType == "asset":
                assetdata = data["data"]
                assetType = assetdata["type"]

                if assetType == "usdasset":
                    name = assetdata["name"]

                    if self.checkedName == name:
                        self.checkedName = ""
                    else:
                        self.checkedName = name

                else:
                    self.checkedName = ""
        else:
            self.checkedName = ""

        self.setOptions()



    def loadStatus (self):

        directory = self.assetPath.get()
        name = self.nameLineEdit.text()
        path = os.path.join(directory, name)

        metadataPath = os.path.join(path, self.metadata)
        data = tools.dataread(metadataPath)
        self.status.set(
            data.get("status", "") )



    def setName (self, text):

        for char in [
            " ", "+", "=", "*"
            ".", ",",
            ":", ";",
            "'", '"',
            "\\", "/", "|" ]:

            text = text.replace(char, "")

        self.nameLineEdit.setText(text)


        if text == self.defaultName:
            self.nameLineEdit.setProperty("textcolor", "off")
            self.currentName = ""
            self.checkedName = ""
            self.status.set()

        elif text in self.assetsNames:
            self.nameLineEdit.setProperty("textcolor", "violet")
            
            inputMatch = False
            if not text == self.checkedName:
                inputMatch = True

            self.currentName = ""
            self.checkedName = text

            self.loadStatus()
            if inputMatch:
                self.setOptions()

        else:
            self.nameLineEdit.setProperty("textcolor", "white")

            inputMatchBreak = False
            if not self.checkedName == "":
                inputMatchBreak = True

            self.currentName = text
            self.checkedName = ""

            if inputMatchBreak:
                self.status.set()
                self.setOptions(force=True)


        self.nameLineEdit.setStyleSheet("")


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
            text = self.nameLineEdit.text()
            if name:
                if name == text: return


        # set asset name text
        if self.checkedName:
            name = self.checkedName
        elif self.currentName:
            name = self.currentName
        else:
            name = self.defaultName

        self.nameLineEdit.setText(name)


        # set default options
        self.mainOpions.versionCombobox.clear()

        if name == self.defaultName:
            self.mainOpions.versionCombobox.addItem("01")


        # load asset options
        else:
            directory = self.assetPath.get()
            name = self.nameLineEdit.text()
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

            # options.fps = self.animationOpions.fpsSpinbox.value()
            # options.unitsMultiplier = self.mainOpions.unitSpinbox.value()

            options.assetPath    = self.getAssetPath()
            options.assetName    = self.getAssetName(final=False)
            options.assetFinal   = self.getAssetName(final=True )

            options.version = int(self.mainOpions.versionCombobox.currentText())
            options.link = self.mainOpions.linkButton.isChecked()

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



    def setLibrary (self, name=None):

        if name:

            path = self.libraries.get(name, None)
            if not path is None:

                with Settings.UIManager(update=True) as uiSettings:

                    uiSettings["subdirLibrary"] = ""
                    uiSettings["focusLibrary"]  = name
                    self.assetPath.setRoot(name, path)
                    return


        with Settings.UIManager(update=False) as uiSettings:

            name = uiSettings["focusLibrary"]
            
            path = self.libraries.get(name, None)
            if not path is None:

                self.assetPath.setRoot(name, path)
                return


        for name, path in self.libraries.items():
            with Settings.UIManager(update=True) as uiSettings:

                uiSettings["subdirLibrary"] = ""
                uiSettings["focusLibrary"]  = name
            
            self.assetPath.setRoot(name, path)
            return


        self.assetPath.setRoot("", "")



    def getDirItems (self, path):

        if not path:
            return []
    
        library = []
        self.assetsNames = []

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
                            status=data["status"] )) )
                    self.assetsNames.append(name)


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


        self.checkedName = ""
        self.setOptions()



    def modelingOverwriteSetting (self):
        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["modellingOverwrite"] = self.modelingOverwrite.isChecked()

    def surfacingOverwriteSetting (self):
        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["surfacingOverwrite"] = self.surfacingOverwrite.isChecked()

    def animationOverwriteSetting (self):
        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["animationOverwrite"] = self.animationOverwrite.isChecked()

    def fpsSetting (self, value):
        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["fps"] = value

    def unitSetting (self, value):
        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["unitsMultiplier"] = value

    def applySettings (self):
        with Settings.UIManager(update=False) as uiSettings:

            self.animationOpions.rangeStartSpinbox.setValue(uiSettings["rangeStart"])
            self.animationOpions.rangeEndSpinbox.setValue(uiSettings["rangeEnd"])
            self.animationOpions.fpsSpinbox.setValue(uiSettings["fps"])
            self.mainOpions.unitSpinbox.setValue(uiSettings["unitsMultiplier"])

            modelingOn  = uiSettings["modelling"]
            surfacingOn = uiSettings["surfacing"]
            animationOn = uiSettings["animation"]

            if modelingOn:
                self.modelingSwitch.setChecked(True)
                self.modelingOverwrite.setEnabled(True)
            else:
                self.modelingSwitch.setChecked(False)
                self.modelingOverwrite.setEnabled(False)
            
            if uiSettings["modellingOverwrite"]:
                self.modelingOverwrite.setChecked(True)
            else:
                self.modelingOverwrite.setChecked(False)
            
            if surfacingOn:
                self.surfacingSwitch.setChecked(True)
                self.surfacingOverwrite.setEnabled(True)
            else:
                self.surfacingSwitch.setChecked(False)
                self.surfacingOverwrite.setEnabled(False)
            
            if uiSettings["surfacingOverwrite"]:
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
            
            if uiSettings["animationOverwrite"]:
                self.animationOverwrite.setChecked(True)
            else:
                self.animationOverwrite.setChecked(False)

            if modelingOn or surfacingOn or animationOn:
                self.mainOpions.setVisible(True)
            else:
                self.mainOpions.setVisible(False)

            if uiSettings["link"]:
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
        elif self.nameLineEdit.text() == self.defaultName:
            pass
        else:
            self.exportButton.setProperty("state", "enabled")

        self.exportButton.setStyleSheet("")



    def exportAction (self):

        if self.exportButton.property("state") == "enabled":
            self.exported = True
            self.close()
