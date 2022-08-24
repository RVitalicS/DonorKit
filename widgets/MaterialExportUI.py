#!/usr/bin/env python



from . import resources

import toolkit.core.calculate
import toolkit.core.graphics
import toolkit.core.naming
import toolkit.core.ui


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *


from . import Browser
from . import BarTop
from . import BarBottom
from . import BaseOption

from . import Settings
UIGlobals = Settings.UIGlobals

WIDTH        = UIGlobals.Options.preferWidth
MARGIN       = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight








class RenderButton (QtWidgets.QPushButton):

    stateChanged = Signal()


    def __init__ (self, theme, prman=True):
        super(RenderButton, self).__init__()

        self.theme = theme

        value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(value, value))

        if prman:
            self.icon = QtGui.QImage(":/icons/prman.png")
        else:
            self.icon = QtGui.QImage(":/icons/hydra.png")

        self.checked = False


    def mousePressEvent (self, event):
        super(RenderButton, self).mousePressEvent(event)

        self.checked = not self.checked
        self.repaint()

        self.stateChanged.emit()


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() ,
            buttonRect.y() )

        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.checked:
            image = toolkit.core.graphics.recolor(
                self.icon, self.theme.color.violet )
        else:
            image = toolkit.core.graphics.recolor(
                self.icon, self.theme.color.optionDisable )

        painter.drawImage(position, image)
        painter.end()






class RenderOptions (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(RenderOptions, self).__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 20, 0, 0)
        self.mainLayout.setSpacing(12)


        self.renderLabel = QtWidgets.QLabel("Render")
        self.renderLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 24))
        toolkit.core.ui.setFont(
            self.renderLabel,
            UIGlobals.Options.fontLabel)
        self.renderLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.renderLabel.setObjectName("renderLabel")
        self.renderLabel.setProperty("textcolor", "on")
        self.mainLayout.addWidget(self.renderLabel)


        self.renderLayout = QtWidgets.QHBoxLayout()
        self.renderLayout.setContentsMargins(0, 0, 0, 0)
        self.renderLayout.setSpacing(6)
        self.renderLayout.setObjectName("renderLayout")

        self.prman = RenderButton(theme, prman=True)
        self.renderLayout.addWidget(self.prman)

        self.hydra = RenderButton(theme, prman=False)
        self.renderLayout.addWidget(self.hydra)

        self.mainLayout.addLayout(self.renderLayout)


        renderSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(renderSpacer)
        

        self.setLayout(self.mainLayout)






class ExportOptions (QtWidgets.QWidget):


    def __init__ (self, theme):
        super(ExportOptions, self).__init__()
        self.setObjectName("MaterialExportOptions")


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

        self.nameEdit = BaseOption.NameEdit()
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
        self.lineLayout.setContentsMargins(0, 4, 0, 0)
        self.lineLayout.setSpacing(0)
        self.optionLayout.addLayout(self.lineLayout)

        self.line = BaseOption.Line(theme)
        self.line.setFixedWidth(WIDTH)
        self.lineLayout.addWidget(self.line)


        self.versionOptions = BaseOption.VersionBlock(theme)
        self.versionOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.versionOptions)


        self.renderOptions = RenderOptions(theme)
        self.renderOptions.setFixedWidth(WIDTH)
        self.optionLayout.addWidget(self.renderOptions)


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
        self.versionOptions.setFixedWidth(value)
        self.renderOptions.setFixedWidth(value)
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
            UIGlobals.Options.labelWidth
            + space
            + self.versionOptions.versionDropdown.width()
            + space
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
