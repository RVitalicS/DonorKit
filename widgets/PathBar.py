#!/usr/bin/env python


import os
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







class PathBar (QtWidgets.QWidget):

    pathChanged  = QtCore.Signal( type(str) )


    def __init__ (self):
        super(PathBar, self).__init__()

        self.root = str()


        height  = UIsettings.AssetBrowser.margin
        height += UIsettings.Path.height

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
            UIsettings.AssetBrowser.margin,
            UIsettings.AssetBrowser.margin + UIsettings.IconDelegate.space, 0 )
        self.mainLayout.setSpacing(UIsettings.IconDelegate.space*2)


        self.pathLayout = QtWidgets.QHBoxLayout()
        self.pathLayout.setContentsMargins( 0, 0, 0, 0 )
        self.pathLayout.setSpacing(UIsettings.IconDelegate.space)


        self.backButton = QtWidgets.QPushButton()
        self.backButton.setObjectName("backButton")
        self.backButton.setProperty("background", "browser")
        self.backButton.setProperty("border", "none")
        self.backButton.setFlat(True)
        self.backButton.setFixedSize(
            UIsettings.Path.backIcon,
            UIsettings.Path.height  )
        self.backButton.clicked.connect(self.moveBack)


        self.pathRoot = QtWidgets.QPushButton()
        self.pathRoot.setObjectName("pathRoot")
        self.pathRoot.setProperty("background", "browser")
        self.pathRoot.setProperty("border", "none")
        self.pathRoot.setFont(UIsettings.Path.fontRoot)
        self.pathRoot.setFixedHeight(UIsettings.Path.height)
        self.pathRoot.setMinimumWidth(0)
        self.pathRoot.setFlat(True)
        self.pathRoot.clicked.connect(self.resetRoot)


        self.pathLine = QtWidgets.QLineEdit()
        self.pathLine.setObjectName("pathLine")
        self.pathLine.setProperty("background", "browser")
        self.pathLine.setProperty("border", "none")
        self.pathLine.setFont(UIsettings.Path.fontPath)
        self.pathLine.setFixedHeight(UIsettings.Path.height)
        self.pathLine.setObjectName("pathLine")
        self.pathLine.editingFinished.connect(self.changeSubdir)


        self.mainLayout.addWidget(self.backButton)
        self.mainLayout.addItem(self.pathLayout)
        self.pathLayout.addWidget(self.pathRoot)
        self.pathLayout.addWidget(self.pathLine)

        self.setLayout(self.mainLayout)



    def setRoot (self, name, path):

        self.pathRoot.setText(name)
        self.root = path

        with Settings.UIManager(update=True) as uiSettings:
            subdirLibrary = uiSettings["subdirLibrary"]

            if os.path.exists(os.path.join(path, subdirLibrary)):
                self.pathLine.setText(subdirLibrary)
            else:
                uiSettings["subdirLibrary"] = ""
                self.pathLine.setText("")

        path = os.path.join(self.root, self.pathLine.text())
        self.pathChanged.emit(path)



    def resetRoot (self):

        with Settings.UIManager(update=True) as uiSettings:
            uiSettings["subdirLibrary"] = ""
            self.pathLine.setText("")

        self.pathChanged.emit(self.root)



    def moveForward (self, name):

        subdir = os.path.join(self.pathLine.text(), name)
        path   = os.path.join(self.root, subdir)

        if os.path.exists(path):
            with Settings.UIManager(update=True) as uiSettings:

                uiSettings["subdirLibrary"] = subdir
                self.pathLine.setText(subdir)
            
            self.pathChanged.emit(path)



    def moveBack (self):

        subdir = os.path.dirname(self.pathLine.text())
        path   = os.path.join(self.root, subdir)

        if os.path.exists(path):
            with Settings.UIManager(update=True) as uiSettings:

                uiSettings["subdirLibrary"] = subdir
                self.pathLine.setText(subdir)
            
            self.pathChanged.emit(path)



    def changeSubdir (self):

        text = self.pathLine.text()
        
        with Settings.UIManager(update=True) as uiSettings:

                subdir = uiSettings["subdirLibrary"]
                if text != subdir:

                    path = os.path.join(self.root, text)
                    if os.path.exists(path):

                        uiSettings["subdirLibrary"] = text
                        self.pathChanged.emit(path)


                    else:
                        self.pathLine.setText(subdir)
                        uiSettings["subdirLibrary"] = subdir



    def get (self):

        return os.path.join(
            self.root,
            self.pathLine.text() )
