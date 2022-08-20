#!/usr/bin/env python



import math

import toolkit.core.calculate
import toolkit.core.graphics
import toolkit.core.naming
import toolkit.core.ui


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *


from . import AssetBrowser
from . import BarPath
from . import BarBottom
from . import BaseOption

from .items import PopupDelegate

from . import Settings
UIGlobals = Settings.UIGlobals

WIDTH        = UIGlobals.Options.preferWidth
MARGIN       = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight







class NameEdit (QtWidgets.QLineEdit):


    def __init__ (self):
        super(NameEdit, self).__init__()

        self.setFixedHeight(HEIGHT_THICK)

        self.defaultName = "Name"
        self.setText(self.defaultName)

        self.errorVisible = False
        self.errorName    = "{ name }"


    def showError (self, flag):

        self.errorVisible = flag

        if flag == True:
            self.setText(self.errorName)


    def setName (self, text):

        if text == self.errorName:
            pass

        elif text != self.defaultName:
            text = toolkit.core.naming.nameFilter(text)
            self.setText(text)

        return text


    def mousePressEvent (self, event):
        super(NameEdit, self).mousePressEvent(event)

        if self.text() == self.defaultName:
            self.setText("")
        elif self.text() == self.errorName:
            self.setText("")


    def leaveEvent (self, event):
        super(NameEdit, self).leaveEvent(event)

        if not self.text() and not self.errorVisible:
            self.setText(self.defaultName)
        elif not self.text() and self.errorVisible:
            self.setText(self.errorName)






class Line (QtWidgets.QWidget):


    def __init__ (self, theme):
        super(Line, self).__init__()

        self.setFixedHeight(1)
        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(
                theme.color.optionLine) )
        self.setPalette(palette)








class FlatComboBox (QtWidgets.QComboBox):

    selectionChanged = Signal(str)


    def __init__ (self, theme):
        super(FlatComboBox, self).__init__()

        self.errorVisible = False
        self.errorName    = "{ name }"

        self.underPointer = False

        self.fontValue = UIGlobals.Options.fontLabel
        toolkit.core.ui.setFont(
            self, self.fontValue)


        self.setEditable(True)
        self.setFrame(False)
        self.setMaxVisibleItems(10)
        self.setMaxCount(100)

        self.setContentsMargins(0,0,0,0)
        self.lineEdit().setContentsMargins(0,0,0,0)
        self.lineEdit().setTextMargins(-2,0,-2,0)

        self.lineEdit().cursorPositionChanged.connect(self.inputEnter)

        self.setItemDelegate(
            PopupDelegate.Delegate(
                self.view(), theme) )

        self.editTextChanged.connect(self.textFilter)

        self.stealth = False
        self.currentTextChanged.connect(self.selectionAction)


    def selectionAction (self, text):

        if not self.stealth:
            self.selectionChanged.emit(text)


    def showError (self, flag):

        self.errorVisible = flag

        if flag == True and not self.currentText():
            self.setEditText(self.errorName)


    def showPopup (self):
        super(FlatComboBox, self).showPopup()

        point = QtCore.QPoint(
            self.contentsRect().x() ,
            self.contentsRect().y() )
        point = self.mapToGlobal(point)

        popup = self.findChild(QtWidgets.QFrame)
        popup.move(popup.x(), point.y())


    def getName (self):

        name = self.currentText()
        if name == self.errorName:
            return ""
        else:
            return name


    def notSet (self):

        if self.currentText() == "":
            return True
        if self.currentText() == self.errorName:
            return True
        return False


    def changeEvent (self, event):
        super(FlatComboBox, self).changeEvent(event)

        if self.lineEdit():
            widthLalbel = 0
            widthButton = 20

            if self.lineEdit().text():
                widthLalbel = toolkit.core.calculate.stringWidth(
                    self.lineEdit().text().replace(" ", "_"),
                    self.fontValue )

            self.setMinimumWidth(widthLalbel+widthButton)

        if not self.underPointer and self.errorVisible:
            if not self.currentText():
                self.setEditText(self.errorName)


    def textFilter (self, text):

        if text != self.errorName:
            text = toolkit.core.naming.nameFilter(text)
            self.setEditText(text)


    def leaveEvent (self, event):
        super(FlatComboBox, self).leaveEvent(event)

        self.lineEdit().setCursorPosition(0)
        self.underPointer = False

        if not self.currentText() and self.errorVisible:
            self.setEditText(self.errorName)
        self.clearFocus()


    def enterEvent (self, event):
        super(FlatComboBox, self).enterEvent(event)

        self.underPointer = True


    def inputEnter (self, oldPos, newPos):

        if self.underPointer:
            if self.currentText() == self.errorName:
                self.setEditText("")






class SpinBoxLabel (QtWidgets.QSpinBox):


    def __init__ (self):
        super(SpinBoxLabel, self).__init__()

        self.setProperty("background", "transparent")
        self.setProperty("textcolor", "on")
        self.setProperty("border", "none")

        self.fontValue = UIGlobals.Options.fontLabel
        toolkit.core.ui.setFont(
            self, self.fontValue)

        self.setMinimum(0)
        self.setMaximum(99999)

        self.setFrame(False)
        self.setContentsMargins(0,0,0,0)
        self.lineEdit().setContentsMargins(0,0,0,0)
        self.lineEdit().setTextMargins(-2,0,-2,0)

        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.valueChanged.connect(self.skinnySize)
        self.skinnySize()


    def skinnySize (self):

        value = self.value()
        if value >= 0:
            width = toolkit.core.calculate.stringWidth(
                str(value), self.fontValue )
            
            self.setFixedWidth(width+2)


    def leaveEvent (self, event):

        super(SpinBoxLabel, self).leaveEvent(event)
        self.clearFocus()






class RangeOption (QtWidgets.QWidget):


    def __init__ (self):
        super(RangeOption, self).__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(4)

        self.start = SpinBoxLabel()
        self.mainLayout.addWidget(self.start)

        self.dash = QtWidgets.QLabel("-")
        self.dash.setProperty("background", "transparent")
        self.dash.setProperty("textcolor", "on")
        self.dash.setProperty("border", "none")
        toolkit.core.ui.setFont(
            self.dash,
            UIGlobals.Options.fontLabel)
        self.dash.setContentsMargins(0,0,0,0)
        self.mainLayout.addWidget(self.dash)

        self.end = SpinBoxLabel()
        self.mainLayout.addWidget(self.end)

        rangeSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(rangeSpacer)

        self.setLayout(self.mainLayout)






class SwitchButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(SwitchButton, self).__init__()

        self.theme = theme

        self.setCheckable(True)
        self.setText("")

        self.check   = QtGui.QImage(":/icons/check.png")
        self.uncheck = QtGui.QImage(":/icons/uncheck.png")

        value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(value, value))


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() ,
            buttonRect.y() )

        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = toolkit.core.graphics.recolor(
                self.check, self.theme.color.green )
        else:
            image = toolkit.core.graphics.recolor(
                self.uncheck, self.theme.color.optionDisable )

        painter.drawImage(position, image)
        painter.end()






class RefreshButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(RefreshButton, self).__init__()

        self.theme = theme

        self.setCheckable(False)
        self.setText("")

        self.image = QtGui.QImage(":/icons/refresh.png")

        self.value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(self.value, self.value))

        self.buttonPressed = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() + int((self.value-self.image.width() )/2) ,
            buttonRect.y() + int((self.value-self.image.height())/2) )

        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.white )
        else:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.optionButton )

        painter.drawImage(position, image)
        painter.end()



    def mousePressEvent (self, event):
        super(RefreshButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(RefreshButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()

    def enterEvent (self, event):
        super(RefreshButton, self).enterEvent(event)

    def leaveEvent (self, event):
        super(RefreshButton, self).leaveEvent(event)
        self.buttonPressed = False






class DropdownButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(DropdownButton, self).__init__()

        self.theme = theme

        self.setCheckable(False)
        self.setText("")

        self.image = QtGui.QImage(":/icons/dropdown.png")

        self.value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(self.value, self.value))

        self.buttonPressed = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() + int((self.value-self.image.width() )/2) ,
            buttonRect.y() + int((self.value-self.image.height())/2) )

        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.white )
        else:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.optionButton )

        painter.drawImage(position, image)
        painter.end()



    def mousePressEvent (self, event):
        super(DropdownButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(DropdownButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()

    def enterEvent (self, event):
        super(DropdownButton, self).enterEvent(event)

    def leaveEvent (self, event):
        super(DropdownButton, self).leaveEvent(event)
        self.buttonPressed = False






class LinkButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(LinkButton, self).__init__()

        self.theme = theme

        self.setCheckable(True)
        self.setText("")

        self.image = QtGui.QImage(":/icons/linkchain.png")

        self.setFixedSize(QtCore.QSize(
            self.image.width() ,
            UIGlobals.Options.buttonHeight ))

        self.buttonPressed = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() ,
            ( buttonRect.y() +
            int((UIGlobals.Options.buttonHeight
            - self.image.height())/2) )
        )

        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            if self.property("overwrite") == "true":
                image = toolkit.core.graphics.recolor(
                    self.image, self.theme.color.violet )
            else:
                image = toolkit.core.graphics.recolor(
                    self.image, self.theme.color.optionButton )
        else:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.browserSocket )

        painter.drawImage(position, image)
        painter.end()



    def mousePressEvent (self, event):
        super(LinkButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(LinkButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()

    def enterEvent (self, event):
        super(LinkButton, self).enterEvent(event)

    def leaveEvent (self, event):
        super(LinkButton, self).leaveEvent(event)
        self.buttonPressed = False






class AnimationOptions (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(AnimationOptions, self).__init__()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.animationNameLayout = QtWidgets.QHBoxLayout()
        self.animationNameLayout.setContentsMargins(0, 0, 0, 0)
        self.animationNameLayout.setSpacing(10)
        self.animationNameLayout.setObjectName("animationNameLayout")

        self.nameLabel = QtWidgets.QLabel("NAME")
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setProperty("textcolor", "weak")
        self.nameLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, UIGlobals.Options.rawHeight) )
        toolkit.core.ui.setFont(
            self.nameLabel,
            UIGlobals.IconDelegate.fontAssetLabel)
        self.nameLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter )
        self.animationNameLayout.addWidget(self.nameLabel)

        self.nameDropdown = DropdownButton(theme)
        self.nameDropdown.pressed.connect(self.showNames)
        self.animationNameLayout.addWidget(self.nameDropdown)

        self.animationNameCombobox = FlatComboBox(theme)
        self.animationNameLayout.addWidget(self.animationNameCombobox)

        nameSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.animationNameLayout.addItem(nameSpacer)

        self.mainLayout.addLayout(self.animationNameLayout)

        self.animationRangeLayout = QtWidgets.QHBoxLayout()
        self.animationRangeLayout.setContentsMargins(0, 0, 0, 0)
        self.animationRangeLayout.setSpacing(10)
        self.animationRangeLayout.setObjectName("animationRangeLayout")
        self.mainLayout.addLayout(self.animationRangeLayout)

        self.rangeLabel = QtWidgets.QLabel("RANGE")
        self.rangeLabel.setObjectName("rangeLabel")
        self.rangeLabel.setProperty("textcolor", "weak")
        self.rangeLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, UIGlobals.Options.rawHeight) )
        toolkit.core.ui.setFont(
            self.rangeLabel,
            UIGlobals.IconDelegate.fontAssetLabel)
        self.rangeLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter )
        self.animationRangeLayout.addWidget(self.rangeLabel)

        self.rangeButton = RefreshButton(theme)
        self.animationRangeLayout.addWidget(self.rangeButton)

        self.range = RangeOption()
        self.animationRangeLayout.addWidget(self.range)

        rangeSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.animationRangeLayout.addItem(rangeSpacer)

        self.setLayout(self.mainLayout)


    def showNames (self):

        self.animationNameCombobox.showPopup()
        





class MainOptions (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(MainOptions, self).__init__()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.variantLayout = QtWidgets.QHBoxLayout()
        self.variantLayout.setContentsMargins(0, 20, 0, 0)
        self.variantLayout.setSpacing(10)
        self.variantLayout.setObjectName("variantLayout")
        self.mainLayout.addLayout(self.variantLayout)

        self.variantLabel = QtWidgets.QLabel("Variant")
        self.variantLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 24))
        toolkit.core.ui.setFont(
            self.variantLabel,
            UIGlobals.Options.fontLabel)
        self.variantLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.variantLabel.setObjectName("variantLabel")
        self.variantLabel.setProperty("textcolor", "on")
        self.variantLayout.addWidget(self.variantLabel)

        self.variantDropdown = DropdownButton(theme)
        self.variantDropdown.pressed.connect(self.showVariant)
        self.variantLayout.addWidget(self.variantDropdown)

        self.variantCombobox = FlatComboBox(theme)
        self.variantLayout.addWidget(self.variantCombobox)

        variantSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.variantLayout.addItem(variantSpacer)

        self.versionLayout = QtWidgets.QHBoxLayout()
        self.versionLayout.setContentsMargins(0, 0, 0, 0)
        self.versionLayout.setSpacing(10)
        self.versionLayout.setObjectName("versionLayout")

        self.versionLabel = QtWidgets.QLabel("Version")
        self.versionLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 24))
        toolkit.core.ui.setFont(
            self.versionLabel,
            UIGlobals.Options.fontLabel)
        self.versionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setProperty("textcolor", "on")
        self.versionLayout.addWidget(self.versionLabel)

        self.versionDropdown = DropdownButton(theme)
        self.versionDropdown.pressed.connect(self.showVersions)
        self.versionLayout.addWidget(self.versionDropdown)

        self.versionCombobox = FlatComboBox(theme)
        self.versionLayout.addWidget(self.versionCombobox)

        versionSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.versionLayout.addItem(versionSpacer)

        self.linkButton = LinkButton(theme)
        self.versionLayout.addWidget(self.linkButton)

        self.mainLayout.addLayout(self.versionLayout)
        
        self.setLayout(self.mainLayout)


    def showVariant (self):

        self.variantCombobox.showPopup()


    def showVersions (self):

        self.versionCombobox.showPopup()





class UsdExportOptions (QtWidgets.QWidget):


    def __init__ (self, theme):
        super(UsdExportOptions, self).__init__()
        self.setObjectName("UsdExportOptions")


        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            theme.color.optionBackground )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("optionLayout")


        self.optionLayout = QtWidgets.QVBoxLayout()
        self.optionLayout.setContentsMargins(MARGIN, 0, MARGIN, 0)
        self.optionLayout.setSpacing(0)
        self.optionLayout.setObjectName("optionLayout")
        self.mainLayout.addLayout(self.optionLayout)


        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.setContentsMargins(0, 16, 0, int(MARGIN/4))
        self.nameLayout.setSpacing(0)
        self.nameLayout.setObjectName("nameLayout")

        self.nameEdit = NameEdit()
        toolkit.core.ui.setFont(
            self.nameEdit,
            UIGlobals.Options.fontName)
        self.nameEdit.setObjectName("nameEdit")
        self.nameEdit.setProperty("background", "transparent")
        self.nameEdit.setProperty("border", "none")
        self.nameEdit.setProperty("textcolor", "weak")
        self.nameEdit.setTextMargins(0, 0, 0, 0)
        self.nameLayout.addWidget(self.nameEdit)
        self.optionLayout.addLayout(self.nameLayout)


        self.infoLayout = QtWidgets.QHBoxLayout()
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(0)
        self.optionLayout.addLayout(self.infoLayout)

        self.infoEdit = BaseOption.TextBlock("description")
        self.infoEdit.setFixedWidth(WIDTH)
        self.infoEdit.setCommentFont(UIGlobals.Options.fontInfo)
        self.infoEdit.setPropertyTag("kicker")
        self.infoEdit.setProperty("background", "options")
        self.infoEdit.setProperty("border", "none")
        self.infoEdit.setObjectName("infoEdit")
        self.infoEdit.setViewportMargins(-4, 0, 0, 0)
        self.infoLayout.addWidget(self.infoEdit)

        self.lineLayout = QtWidgets.QHBoxLayout()
        self.lineLayout.setContentsMargins(0, 4, 0, MARGIN)
        self.lineLayout.setSpacing(0)
        self.optionLayout.addLayout(self.lineLayout)

        self.line = Line(theme)
        self.line.setFixedWidth(WIDTH)
        self.lineLayout.addWidget(self.line)

        self.modelingLayout = QtWidgets.QHBoxLayout()
        self.modelingLayout.setContentsMargins(0, 0, 0, 4)
        self.modelingLayout.setSpacing(10)
        self.modelingLayout.setObjectName("modelingLayout")
        self.modelingLabel = QtWidgets.QLabel("Modeling")
        self.modelingLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 18))
        toolkit.core.ui.setFont(
            self.modelingLabel,
            UIGlobals.Options.fontLabel)
        self.modelingLabel.setObjectName("modelingLabel")
        self.modelingLabel.setProperty("textcolor", "on")
        self.modelingLayout.addWidget(self.modelingLabel)

        self.modelingSwitch = SwitchButton(theme)
        self.modelingLayout.addWidget(self.modelingSwitch)

        self.modelingOverwrite = QtWidgets.QPushButton("overwrite")
        self.modelingOverwrite.setFixedSize(QtCore.QSize(50, 16))
        toolkit.core.ui.setFont(
            self.modelingOverwrite,
            UIGlobals.Options.fontOverwrite)
        self.modelingOverwrite.setCheckable(True)
        self.modelingOverwrite.setObjectName("modelingOverwrite")
        self.modelingLayout.addWidget(self.modelingOverwrite)
        modelingSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.modelingLayout.addItem(modelingSpacer)
        self.optionLayout.addLayout(self.modelingLayout)

        self.surfacingLayout = QtWidgets.QHBoxLayout()
        self.surfacingLayout.setContentsMargins(0, 0, 0, 4)
        self.surfacingLayout.setSpacing(10)
        self.surfacingLayout.setObjectName("surfacingLayout")
        self.surfacingLabel = QtWidgets.QLabel("Surfacing")
        self.surfacingLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 18))
        toolkit.core.ui.setFont(
            self.surfacingLabel,
            UIGlobals.Options.fontLabel)
        self.surfacingLabel.setObjectName("surfacingLabel")
        self.surfacingLabel.setProperty("textcolor", "on")
        self.surfacingLayout.addWidget(self.surfacingLabel)

        self.surfacingSwitch = SwitchButton(theme)
        self.surfacingLayout.addWidget(self.surfacingSwitch)

        self.surfacingOverwrite = QtWidgets.QPushButton("overwrite")
        self.surfacingOverwrite.setFixedSize(QtCore.QSize(50, 16))
        toolkit.core.ui.setFont(
            self.surfacingOverwrite,
            UIGlobals.Options.fontOverwrite)
        self.surfacingOverwrite.setCheckable(True)
        self.surfacingOverwrite.setFlat(True)
        self.surfacingOverwrite.setObjectName("surfacingOverwrite")
        self.surfacingLayout.addWidget(self.surfacingOverwrite)

        surfacingSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.surfacingLayout.addItem(surfacingSpacer)
        self.optionLayout.addLayout(self.surfacingLayout)

        self.animationLayout = QtWidgets.QHBoxLayout()
        self.animationLayout.setContentsMargins(0, 0, 0, 4)
        self.animationLayout.setSpacing(10)
        self.animationLayout.setObjectName("animationLayout")
        self.animationLabel = QtWidgets.QLabel("Animation")
        self.animationLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 18))
        toolkit.core.ui.setFont(
            self.animationLabel,
            UIGlobals.Options.fontLabel)
        self.animationLabel.setObjectName("animationLabel")
        self.animationLabel.setProperty("textcolor", "on")
        self.animationLayout.addWidget(self.animationLabel)

        self.animationSwitch = SwitchButton(theme)
        self.animationLayout.addWidget(self.animationSwitch)

        self.animationOverwrite = QtWidgets.QPushButton("overwrite")
        self.animationOverwrite.setFixedSize(QtCore.QSize(50, 16))
        toolkit.core.ui.setFont(
            self.animationOverwrite,
            UIGlobals.Options.fontOverwrite)
        self.animationOverwrite.setCheckable(True)
        self.animationOverwrite.setFlat(True)
        self.animationOverwrite.setObjectName("animationOverwrite")
        self.animationLayout.addWidget(self.animationOverwrite)

        animationSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.animationLayout.addItem(animationSpacer)
        self.optionLayout.addLayout(self.animationLayout)


        self.animationOptions = AnimationOptions(theme)
        self.animationOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.animationOptions)


        self.mainOptions = MainOptions(theme)
        self.mainOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.mainOptions)


        self.commentLabelLayout = QtWidgets.QHBoxLayout()
        self.commentLabelLayout.setContentsMargins(0, MARGIN, 0, 0)
        self.commentLabelLayout.setSpacing(0)
        self.commentLabelLayout.setObjectName("commentLabelLayout")
        self.optionLayout.addLayout(self.commentLabelLayout)

        self.labelComment = QtWidgets.QLabel("COMMENT")
        self.labelComment.setObjectName("labelComment")
        self.labelComment.setProperty("textcolor", "weak")
        toolkit.core.ui.setFont(
            self.labelComment,
            UIGlobals.IconDelegate.fontAssetLabel)
        self.commentLabelLayout.addWidget(self.labelComment)

        commentSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.commentLabelLayout.addItem(commentSpacer)


        self.commentLayout = QtWidgets.QHBoxLayout()
        self.commentLayout.setContentsMargins(
            0, 0, 0, int(MARGIN/2) )
        self.commentLayout.setSpacing(0)
        self.commentLayout.setObjectName("commentLayout")
        self.optionLayout.addLayout(self.commentLayout)


        self.commentEdit = BaseOption.TextBlock("text")
        self.commentEdit.setFixedWidth(WIDTH)
        self.commentEdit.setProperty("background", "options")
        self.commentEdit.setProperty("border", "none")
        self.commentEdit.setObjectName("commentEdit")
        self.commentEdit.setViewportMargins( -4, 0, 0, 0)
        self.commentLayout.addWidget(self.commentEdit)


        optionSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(optionSpacer)


        self.statusLayout = QtWidgets.QHBoxLayout()
        self.statusLayout.setContentsMargins(0, 0, MARGIN, 0)
        self.statusLayout.setSpacing(0)
        self.mainLayout.addLayout(self.statusLayout)

        self.status = BaseOption.Status(theme)
        self.statusLayout.addWidget(self.status)

        self.mayaLayout = QtWidgets.QVBoxLayout()
        self.mayaLayout.setContentsMargins(0, 0, 0, 
            UIGlobals.Options.Maya.offset)
        self.mayaLayout.setSpacing(0)
        self.mayaLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.statusLayout.addLayout(self.mayaLayout)

        self.mayaButton = BaseOption.MayaButton(theme)
        self.mayaLayout.addWidget(self.mayaButton)


        self.exportLayout = QtWidgets.QHBoxLayout()
        self.exportLayout.setContentsMargins(MARGIN, 0, MARGIN, MARGIN)
        self.exportLayout.setSpacing(10)
        self.exportLayout.setObjectName("exportLayout")
        self.mainLayout.addLayout(self.exportLayout)

        self.exportButton = BaseOption.ExportButton(theme)
        self.exportButton.setText("Export")
        toolkit.core.ui.setFont(
            self.exportButton,
            UIGlobals.Options.fontLabel)
        self.exportButton.setFlat(True)
        self.exportButton.setProperty("state", "disabled")
        self.exportLayout.addWidget(self.exportButton)


        self.setLayout(self.mainLayout)


    def setOptionWidth (self, value):

        self.nameEdit.setFixedWidth(value)
        self.line.setFixedWidth(value)
        self.infoEdit.setFixedWidth(value)
        self.infoEdit.skinnySize()
        self.animationOptions.setFixedWidth(value)
        self.mainOptions.setFixedWidth(value)
        self.commentEdit.setFixedWidth(value)
        self.commentEdit.skinnySize()
        self.exportButton.setFixedWidth(value)

        self.status.setFixedWidth(
            value + MARGIN - self.mayaButton.width() )



    def resizeEvent (self, event):
        super(UsdExportOptions, self).resizeEvent(event)
        self.uiVisibility()



    def uiVisibility (self):

        self.mainOptions.linkButton.hide()

        space = 10

        width = self.width() - MARGIN * 2

        sumwidth = (
            UIGlobals.Options.labelWidth
            + space
            + self.mainOptions.versionDropdown.width()
            + space
            + self.mainOptions.versionCombobox.width() )

        sumwidth += space + self.mainOptions.linkButton.width()

        if width > sumwidth:
            self.mainOptions.linkButton.show()





def setupUi (self, theme):


    self.currentName = ""
    self.checkedName = ""


    self.setProperty("background", "browser")
    self.setProperty("border", "none")

    self.mainLayout = QtWidgets.QHBoxLayout()
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.mainLayout.setSpacing(0)
    self.mainLayout.setObjectName("mainLayout")


    self.browserLayout = QtWidgets.QVBoxLayout()
    self.browserLayout.setContentsMargins(0, 0, 0, 0)
    self.browserLayout.setSpacing(0)
    self.mainLayout.addLayout(self.browserLayout)

    self.AssetPath = BarPath.Bar(theme)
    self.browserLayout.addWidget(self.AssetPath)

    self.AssetBrowser = AssetBrowser.AssetBrowser(theme)
    self.browserLayout.addWidget(self.AssetBrowser)

    self.BarBottom = BarBottom.Bar(theme)
    self.browserLayout.addWidget(self.BarBottom)

    self.ResizeButton = BaseOption.ResizeButton(theme)
    self.mainLayout.addWidget(self.ResizeButton)

    self.UsdExportOptions = UsdExportOptions(theme)
    self.mainLayout.addWidget(self.UsdExportOptions)


    self.mainLayout.setStretch(0, 1)
    self.setLayout(self.mainLayout)
