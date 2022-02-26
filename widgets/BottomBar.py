#!/usr/bin/env python



import os
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







class BottomBar (QtWidgets.QWidget):

    bookmarkChoosed = QtCore.Signal(str)


    def __init__ (self):
        super(BottomBar, self).__init__()

        height = UIsettings.Bar.height

        self.setMaximumHeight( height )
        self.setMinimumHeight( height )


        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            stylesheet.browserBackground )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(
            UIsettings.AssetBrowser.margin + UIsettings.IconDelegate.space,
            0,
            UIsettings.AssetBrowser.margin + UIsettings.IconDelegate.space,
            0 )
        self.mainLayout.setSpacing(0)


        self.previewLayout = QtWidgets.QHBoxLayout()
        self.previewLayout.setContentsMargins(0, 0,
            UIsettings.IconDelegate.space*4, 0)
        self.previewLayout.setSpacing(UIsettings.IconDelegate.space*2)
        self.mainLayout.addLayout(self.previewLayout)


        self.previewLabel = QtWidgets.QLabel("PREVIEW")
        self.previewLabel.setObjectName("previewLabel")
        self.previewLabel.setFont(UIsettings.Bar.fontPreview)
        self.previewLabel.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.previewLabel.setProperty("textcolor", "light")
        self.previewLayout.addWidget(self.previewLabel)


        self.previewSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.previewSlider.setObjectName("previewSlider")
        self.previewSlider.setFixedWidth(35)
        self.previewSlider.setRange(1, 3)
        self.previewSlider.setTickInterval(1)
        self.previewLayout.addWidget(self.previewSlider)

        with Settings.UIManager(update=False) as uiSettings:
            self.previewSlider.setValue(uiSettings["iconSize"])


        self.bookmarksLayout = QtWidgets.QHBoxLayout()
        self.bookmarksLayout.setContentsMargins(0, 0,
            UIsettings.IconDelegate.space*4, 0)
        self.bookmarksLayout.setSpacing(UIsettings.IconDelegate.space*2)
        self.mainLayout.addLayout(self.bookmarksLayout)


        self.bookmarksLabel = QtWidgets.QLabel("BOOKMARKS")
        self.bookmarksLabel.setObjectName("bookmarksLabel")
        self.bookmarksLabel.setFont(UIsettings.Bar.fontPreview)
        self.bookmarksLabel.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.bookmarksLabel.setProperty("textcolor", "light")
        self.bookmarksLayout.addWidget(self.bookmarksLabel)


        self.bookmarkButton = QtWidgets.QPushButton()
        self.bookmarkButton.setProperty("bookmark", "true")
        self.bookmarkButton.setMaximumHeight(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMinimumHeight(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMaximumWidth(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMinimumWidth(UIsettings.AssetBrowser.margin)
        self.bookmarksLayout.addWidget(self.bookmarkButton)
        self.bookmarkButton.pressed.connect(self.showBookmarks)
        self.bookmarkButton.released.connect(self.hideBookmarks)


        self.bookmarkCombobox = QtWidgets.QComboBox()
        self.bookmarkCombobox.setFont(UIsettings.Bar.fontBookmark)
        self.bookmarkCombobox.setEditable(False)
        self.bookmarkCombobox.setFrame(False)
        self.bookmarkCombobox.setVisible(False)
        self.bookmarkCombobox.setProperty("bookmark", "true")
        self.bookmarkCombobox.activated.connect(self.bookmarkData)
        self.bookmarksLayout.addWidget(self.bookmarkCombobox)


        spacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        self.mainLayout.setStretch(0, 0)
        self.mainLayout.setStretch(1, 0)
        self.mainLayout.setStretch(2, 1)
        self.setLayout(self.mainLayout)



    def showBookmarks (self):
        self.bookmarkCombobox.setCurrentIndex(-1)
        self.bookmarkCombobox.setVisible(True)
        self.bookmarkCombobox.showPopup()



    def hideBookmarks (self):
        self.bookmarkCombobox.hidePopup()
        self.bookmarkCombobox.setVisible(False)



    def bookmarkData (self, index):
        data = self.bookmarkCombobox.itemData(index)
        self.bookmarkChoosed.emit(data)
        self.bookmarkCombobox.setVisible(False)
