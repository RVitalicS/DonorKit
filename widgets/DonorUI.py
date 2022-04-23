#!/usr/bin/env python



from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtGui import *

import toolkit.core.ui

from . import AssetBrowser
from . import BarPath
from . import BarBottom
from . import BaseOption

from . import Settings
UIGlobals = Settings.UIGlobals

WIDTH        = UIGlobals.Options.preferWidth
MARGIN       = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight






class UsdLoadOptions (QtWidgets.QWidget):


    def __init__ (self, theme):
        super(UsdLoadOptions, self).__init__()
        self.setObjectName("UsdLoadOptions")


        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(
                theme.color.optionBackground) )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("optionLayout")


        self.status = BaseOption.Status(theme)
        self.mainLayout.addWidget(self.status)


        self.infoLayout = QtWidgets.QHBoxLayout()
        self.infoLayout.setContentsMargins(MARGIN, 0, MARGIN, 0)
        self.infoLayout.setSpacing(0)
        self.infoLayout.setObjectName("infoLayout")
        self.mainLayout.addLayout(self.infoLayout)


        self.infoEdit = BaseOption.TextBlock("description")
        self.infoEdit.setCommentFont(UIGlobals.Options.fontInfo)
        self.infoEdit.setPropertyTag("kicker")
        self.infoEdit.setFixedWidth(WIDTH)
        self.infoEdit.setProperty("background", "options")
        self.infoEdit.setProperty("border", "none")
        self.infoEdit.setObjectName("infoEdit")
        self.infoEdit.setViewportMargins(-4, 0, 0, 0)
        self.infoLayout.addWidget(self.infoEdit)


        self.commentLabelLayout = QtWidgets.QHBoxLayout()
        self.commentLabelLayout.setContentsMargins(MARGIN, MARGIN*2, MARGIN, 0)
        self.commentLabelLayout.setSpacing(0)
        self.commentLabelLayout.setObjectName("commentLabelLayout")
        self.mainLayout.addLayout(self.commentLabelLayout)

        self.labelComment = QtWidgets.QLabel("COMMENT")
        self.labelComment.setObjectName("labelComment")
        self.labelComment.setProperty("textcolor", "weak")
        toolkit.core.ui.setFont(
            self.labelComment,
            UIGlobals.IconDelegate.fontAssetLabel)
        self.commentLabelLayout.addWidget(self.labelComment)

        labelSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.commentLabelLayout.addItem(labelSpacer)


        self.commentLayout = QtWidgets.QHBoxLayout()
        self.commentLayout.setContentsMargins(MARGIN, 0, MARGIN, MARGIN)
        self.commentLayout.setSpacing(0)
        self.commentLayout.setObjectName("commentLayout")
        self.mainLayout.addLayout(self.commentLayout)


        self.commentEdit = BaseOption.TextBlock("text")
        self.commentEdit.setCommentFont(UIGlobals.Options.fontComment)
        self.commentEdit.setFixedWidth(WIDTH)
        self.commentEdit.setProperty("background", "options")
        self.commentEdit.setProperty("border", "none")
        self.commentEdit.setObjectName("commentEdit")
        self.commentEdit.setViewportMargins(-4,0,0,0)
        self.commentLayout.addWidget(self.commentEdit)


        optionSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(optionSpacer)


        self.linkLayout = QtWidgets.QHBoxLayout()
        self.linkLayout.setContentsMargins(
            MARGIN, 0, MARGIN, MARGIN)
        self.linkLayout.setSpacing(0)
        self.linkLayout.setObjectName("linkLayout")
        self.mainLayout.addLayout(self.linkLayout)

        self.link = BaseOption.SymbolicLink(theme)
        self.linkLayout.addWidget(self.link)

        linkSpacer = QtWidgets.QSpacerItem(
            0, self.link.height(),
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.linkLayout.addItem(linkSpacer)


        self.loadLayout = QtWidgets.QHBoxLayout()
        self.loadLayout.setContentsMargins(MARGIN, 0, MARGIN, MARGIN)
        self.loadLayout.setSpacing(0)
        self.loadLayout.setObjectName("loadLayout")
        self.mainLayout.addLayout(self.loadLayout)

        self.loadButton = BaseOption.ExportButton(theme)
        self.loadButton.setText("Load")
        toolkit.core.ui.setFont(
            self.loadButton,
            UIGlobals.Options.fontLabel)
        self.loadButton.setFlat(True)
        self.loadButton.setProperty("state", "disabled")
        self.loadLayout.addWidget(self.loadButton)


        self.setLayout(self.mainLayout)



    def setOptionWidth (self, value):

        self.infoEdit.setFixedWidth(value)
        self.infoEdit.skinnySize()
        self.commentEdit.setFixedWidth(value)
        self.commentEdit.skinnySize()
        self.loadButton.setFixedWidth(value)






def setupUi (self, theme):

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
    self.ResizeButton.hide()

    self.UsdLoadOptions = UsdLoadOptions(theme)
    self.mainLayout.addWidget(self.UsdLoadOptions)
    self.UsdLoadOptions.hide()

    self.mainLayout.setStretch(0, 1)
    self.setLayout(self.mainLayout)
