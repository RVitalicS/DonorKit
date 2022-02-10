#!/usr/bin/env python



import os
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







class BottomBar (QtWidgets.QWidget):


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


        self.previewLabel = QtWidgets.QLabel("PREVIEW")
        self.previewLabel.setObjectName("previewLabel")
        self.previewLabel.setFixedWidth(50)
        self.previewLabel.setFont(UIsettings.Bar.fontPreview)
        self.previewLabel.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.previewLabel.setProperty("textcolor", "light")


        self.previewSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.previewSlider.setObjectName("previewSlider")
        self.previewSlider.setFixedWidth(35)
        self.previewSlider.setRange(1, 3)
        self.previewSlider.setTickInterval(1)

        with Settings.UIManager(update=False) as uiSettings:
            self.previewSlider.setValue(uiSettings["iconSize"])


        spacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)


        self.mainLayout.addWidget(self.previewLabel)
        self.mainLayout.addWidget(self.previewSlider)
        self.mainLayout.addItem(spacer)
        self.setLayout(self.mainLayout)

