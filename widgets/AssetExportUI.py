#!/usr/bin/env python

"""
"""

from widgets import resources
import toolkit.core.calculate as calculate
import toolkit.core.graphics as graphics
import toolkit.core.ui as uiCommand
from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets import Browser
from widgets import BarTop
from widgets import BarBottom
from widgets import BaseOption
from widgets import Settings

UIGlobals = Settings.UIGlobals
WIDTH = UIGlobals.Options.preferWidth
MARGIN = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight


class SpinBoxLabel (QtWidgets.QSpinBox):
    
    def __init__ (self, parent=None):
        super(SpinBoxLabel, self).__init__(parent)
        self.setProperty("background", "transparent")
        self.setProperty("textcolor", "on")
        self.setProperty("border", "none")
        self.fontValue = UIGlobals.Options.fontLabel
        uiCommand.setFont(self, self.fontValue)
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
            width = calculate.stringWidth(
                str(value), self.fontValue)
            self.setFixedWidth(width+2)
    
    def leaveEvent (self, event):
        super(SpinBoxLabel, self).leaveEvent(event)
        self.clearFocus()


class DoubleSpinBoxLabel (QtWidgets.QDoubleSpinBox):
    
    def __init__ (self, parent=None):
        super(DoubleSpinBoxLabel, self).__init__(parent)
        self.setProperty("background", "transparent")
        self.setProperty("border", "none")
        self.fontValue = UIGlobals.Options.fontLabel
        uiCommand.setFont(self, self.fontValue)
        self.setMinimum(0.0)
        self.setMaximum(1.0)
        self.setSingleStep(0.05)
        self.setFrame(False)
        self.setContentsMargins(0,0,0,0)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    
    def leaveEvent (self, event):
        super(DoubleSpinBoxLabel, self).leaveEvent(event)
        self.clearFocus()
    
    def setEditable (self, flag):
        self.setEnabled(flag)
        if flag:
            self.setProperty("textcolor", "on")
        else:
            self.setProperty("textcolor", "weak")
        self.setStyleSheet("")


class RangeOption (QtWidgets.QWidget):
    
    def __init__ (self, parent=None):
        super(RangeOption, self).__init__(parent)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(4)
        self.start = SpinBoxLabel()
        self.mainLayout.addWidget(self.start)
        self.dash = QtWidgets.QLabel("-")
        self.dash.setProperty("background", "transparent")
        self.dash.setProperty("textcolor", "on")
        self.dash.setProperty("border", "none")
        uiCommand.setFont(self.dash, UIGlobals.Options.fontLabel)
        self.dash.setContentsMargins(0,0,0,0)
        self.mainLayout.addWidget(self.dash)
        self.end = SpinBoxLabel()
        self.mainLayout.addWidget(self.end)
        rangeSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(rangeSpacer)
        self.setLayout(self.mainLayout)


class SwitchButton (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(SwitchButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setCheckable(True)
        self.setText("")
        self.check = QtGui.QImage(":/icons/check.png")
        self.uncheck = QtGui.QImage(":/icons/uncheck.png")
        value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(value, value))
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.isChecked():
            image = graphics.recolor(self.check, self.theme.color.green )
        else:
            image = graphics.recolor(self.uncheck, self.theme.color.optionDisable )
        painter.drawImage(position, image)
        painter.end()


class RefreshButton (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(RefreshButton, self).__init__(icon, text, parent)
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
            image = graphics.recolor(self.image, self.theme.color.white )
        else:
            image = graphics.recolor(self.image, self.theme.color.optionButton )
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


class ProxyButton (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(ProxyButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setCheckable(True)
        self.setText("")
        self.radius = 3
        self.value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(self.value, self.value))
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        buttonRect = self.contentsRect()
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.isChecked():
            color = QtGui.QColor(self.theme.color.optionButton)
        else:
            color = QtGui.QColor(self.theme.color.optionDisable)
        offset = int(self.value/2) - self.radius
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(color))
        painter.drawEllipse(offset, offset, self.radius*2, self.radius*2)
        painter.end()


class ProxyOptions (QtWidgets.QWidget):
    
    def __init__ (self, theme, parent=None):
        super(ProxyOptions, self).__init__(parent)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 3)
        self.mainLayout.setSpacing(10)
        self.proxyLabel = QtWidgets.QLabel("PROXY")
        self.proxyLabel.setObjectName("proxyLabel")
        self.proxyLabel.setProperty("textcolor", "weak")
        self.proxyLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, UIGlobals.Options.rawHeight) )
        uiCommand.setFont(self.proxyLabel, UIGlobals.IconDelegate.fontAssetLabel)
        self.proxyLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter )
        self.mainLayout.addWidget(self.proxyLabel)
        self.switch = ProxyButton(theme)
        self.switch.released.connect(self.updateUI)
        self.mainLayout.addWidget(self.switch)
        self.factor = DoubleSpinBoxLabel()
        self.mainLayout.addWidget(self.factor)
        spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)
        self.setLayout(self.mainLayout)
    
    def updateUI (self):
        if self.switch.isChecked():
            self.factor.setEditable(True)
        else:
            self.factor.setEditable(False)


class AnimationOptions (QtWidgets.QWidget):
    
    def __init__ (self, theme, parent=None):
        super(AnimationOptions, self).__init__(parent)
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
        uiCommand.setFont(self.nameLabel, UIGlobals.IconDelegate.fontAssetLabel)
        self.nameLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter )
        self.animationNameLayout.addWidget(self.nameLabel)

        self.nameDropdown = BaseOption.DropdownButton(theme)
        self.nameDropdown.pressed.connect(self.showNames)
        self.animationNameLayout.addWidget(self.nameDropdown)

        self.animationNameCombobox = BaseOption.FlatComboBox(theme)
        self.animationNameLayout.addWidget(self.animationNameCombobox)
        nameSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
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
        uiCommand.setFont(self.rangeLabel, UIGlobals.IconDelegate.fontAssetLabel)
        self.rangeLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter )
        self.animationRangeLayout.addWidget(self.rangeLabel)

        self.rangeButton = RefreshButton(theme)
        self.animationRangeLayout.addWidget(self.rangeButton)

        self.range = RangeOption()
        self.animationRangeLayout.addWidget(self.range)
        rangeSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.animationRangeLayout.addItem(rangeSpacer)
        self.setLayout(self.mainLayout)
    
    def showNames (self):
        self.animationNameCombobox.showPopup()


class ExportOptions (QtWidgets.QWidget):
    def __init__ (self, theme, parent=None):
        super(ExportOptions, self).__init__(parent)
        self.setObjectName("AssetExportOptions")
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            theme.color.optionBackground)
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

        self.nameEdit = BaseOption.NameEdit()
        uiCommand.setFont(self.nameEdit, UIGlobals.Options.fontName)
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

        self.line = BaseOption.Line(theme)
        self.line.setFixedWidth(WIDTH)
        self.lineLayout.addWidget(self.line)
        self.modelingLayout = QtWidgets.QHBoxLayout()
        self.modelingLayout.setContentsMargins(0, 0, 0, 4)
        self.modelingLayout.setSpacing(10)
        self.modelingLayout.setObjectName("modelingLayout")
        self.modelingLabel = QtWidgets.QLabel("Modeling")
        self.modelingLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 18))
        uiCommand.setFont(self.modelingLabel, UIGlobals.Options.fontLabel)
        self.modelingLabel.setObjectName("modelingLabel")
        self.modelingLabel.setProperty("textcolor", "on")
        self.modelingLayout.addWidget(self.modelingLabel)

        self.modelingSwitch = SwitchButton(theme)
        self.modelingLayout.addWidget(self.modelingSwitch)

        self.modelingOverwrite = QtWidgets.QPushButton("overwrite")
        self.modelingOverwrite.setFixedSize(QtCore.QSize(50, 16))
        uiCommand.setFont(self.modelingOverwrite, UIGlobals.Options.fontOverwrite)
        self.modelingOverwrite.setCheckable(True)
        self.modelingOverwrite.setObjectName("modelingOverwrite")
        self.modelingLayout.addWidget(self.modelingOverwrite)
        modelingSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.modelingLayout.addItem(modelingSpacer)
        self.optionLayout.addLayout(self.modelingLayout)

        self.proxyOptions = ProxyOptions(theme)
        self.proxyOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.proxyOptions)
        self.surfacingLayout = QtWidgets.QHBoxLayout()
        self.surfacingLayout.setContentsMargins(0, 0, 0, 4)
        self.surfacingLayout.setSpacing(10)
        self.surfacingLayout.setObjectName("surfacingLayout")

        self.surfacingLabel = QtWidgets.QLabel("Surfacing")
        self.surfacingLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 18))
        uiCommand.setFont(self.surfacingLabel, UIGlobals.Options.fontLabel)
        self.surfacingLabel.setObjectName("surfacingLabel")
        self.surfacingLabel.setProperty("textcolor", "on")
        self.surfacingLayout.addWidget(self.surfacingLabel)

        self.surfacingSwitch = SwitchButton(theme)
        self.surfacingLayout.addWidget(self.surfacingSwitch)
        self.surfacingOverwrite = QtWidgets.QPushButton("overwrite")
        self.surfacingOverwrite.setFixedSize(QtCore.QSize(50, 16))
        uiCommand.setFont(self.surfacingOverwrite, UIGlobals.Options.fontOverwrite)
        self.surfacingOverwrite.setCheckable(True)
        self.surfacingOverwrite.setFlat(True)
        self.surfacingOverwrite.setObjectName("surfacingOverwrite")
        self.surfacingLayout.addWidget(self.surfacingOverwrite)
        surfacingSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
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
        uiCommand.setFont(self.animationLabel, UIGlobals.Options.fontLabel)
        self.animationLabel.setObjectName("animationLabel")
        self.animationLabel.setProperty("textcolor", "on")
        self.animationLayout.addWidget(self.animationLabel)

        self.animationSwitch = SwitchButton(theme)
        self.animationLayout.addWidget(self.animationSwitch)

        self.animationOverwrite = QtWidgets.QPushButton("overwrite")
        self.animationOverwrite.setFixedSize(QtCore.QSize(50, 16))
        uiCommand.setFont(self.animationOverwrite, UIGlobals.Options.fontOverwrite)
        self.animationOverwrite.setCheckable(True)
        self.animationOverwrite.setFlat(True)
        self.animationOverwrite.setObjectName("animationOverwrite")
        self.animationLayout.addWidget(self.animationOverwrite)
        animationSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.animationLayout.addItem(animationSpacer)
        self.optionLayout.addLayout(self.animationLayout)

        self.animationOptions = AnimationOptions(theme)
        self.animationOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.animationOptions)

        self.versionOptions = BaseOption.VersionBlock(theme)
        self.versionOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.versionOptions)
        self.commentLabelLayout = QtWidgets.QHBoxLayout()
        self.commentLabelLayout.setContentsMargins(0, MARGIN, 0, 0)
        self.commentLabelLayout.setSpacing(0)
        self.commentLabelLayout.setObjectName("commentLabelLayout")
        self.optionLayout.addLayout(self.commentLabelLayout)

        self.labelComment = QtWidgets.QLabel("COMMENT")
        self.labelComment.setObjectName("labelComment")
        self.labelComment.setProperty("textcolor", "weak")
        uiCommand.setFont(self.labelComment, UIGlobals.IconDelegate.fontAssetLabel)
        self.commentLabelLayout.addWidget(self.labelComment)
        commentSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.commentLabelLayout.addItem(commentSpacer)
        self.commentLayout = QtWidgets.QHBoxLayout()
        self.commentLayout.setContentsMargins(0, 0, 0, int(MARGIN/2) )
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
            0, 0, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(optionSpacer)
        self.statusLayout = QtWidgets.QHBoxLayout()
        self.statusLayout.setContentsMargins(0, 0, MARGIN, 0)
        self.statusLayout.setSpacing(0)
        self.mainLayout.addLayout(self.statusLayout)

        self.status = BaseOption.Status(theme)
        self.statusLayout.addWidget(self.status)
        self.mayaLayout = QtWidgets.QVBoxLayout()
        self.mayaLayout.setContentsMargins(0, 0, 0, UIGlobals.Options.Maya.offset)
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
        uiCommand.setFont(self.exportButton, UIGlobals.Options.fontLabel)
        self.exportButton.setFlat(True)
        self.exportButton.setProperty("state", "disabled")
        self.exportLayout.addWidget(self.exportButton)
        self.setLayout(self.mainLayout)
    
    def setOptionWidth (self, value):
        self.nameEdit.setFixedWidth(value)
        self.line.setFixedWidth(value)
        self.infoEdit.setFixedWidth(value)
        self.infoEdit.skinnySize()
        self.proxyOptions.setFixedWidth(value)
        self.animationOptions.setFixedWidth(value)
        self.versionOptions.setFixedWidth(value)
        self.commentEdit.setFixedWidth(value)
        self.commentEdit.skinnySize()
        self.exportButton.setFixedWidth(value)
        self.status.setFixedWidth(
            value + MARGIN - self.mayaButton.width() )
    
    def resizeEvent (self, event):
        super(ExportOptions, self).resizeEvent(event)
        self.uiVisibility()
    
    def uiVisibility (self):
        self.versionOptions.linkButton.hide()
        space = 10
        width = self.width() - MARGIN * 2
        sumwidth = (
            UIGlobals.Options.labelWidth + space
            + self.versionOptions.versionDropdown.width() + space
            + self.versionOptions.versionCombobox.width() )
        sumwidth += space + self.versionOptions.linkButton.width()
        if width > sumwidth:
            self.versionOptions.linkButton.show()


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
    self.BrowserPath = BarTop.Bar(theme)
    self.browserLayout.addWidget(self.BrowserPath)
    self.Browser = Browser.Browser(theme)
    self.browserLayout.addWidget(self.Browser)
    self.BarBottom = BarBottom.Bar(theme)
    self.browserLayout.addWidget(self.BarBottom)
    self.ResizeButton = BaseOption.ResizeButton(theme)
    self.mainLayout.addWidget(self.ResizeButton)
    self.ExportOptions = ExportOptions(theme)
    self.mainLayout.addWidget(self.ExportOptions)
    self.mainLayout.setStretch(0, 1)
    self.setLayout(self.mainLayout)
