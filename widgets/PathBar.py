#!/usr/bin/env python


import os
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







class PathBar (QtWidgets.QWidget):

    bookmarkClicked = QtCore.Signal(bool)
    pathChanged  = QtCore.Signal(str)


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
        self.mainLayout.setSpacing(UIsettings.IconDelegate.space*2)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.rootLayout = QtWidgets.QHBoxLayout()
        self.rootLayout.setContentsMargins(
            UIsettings.AssetBrowser.margin + UIsettings.IconDelegate.space,
            UIsettings.AssetBrowser.margin,
            UIsettings.IconDelegate.space, 0 )
        self.rootLayout.setSpacing(UIsettings.IconDelegate.space*2)
        self.mainLayout.addLayout(self.rootLayout)


        self.subdirLayout = QtWidgets.QVBoxLayout()
        self.subdirLayout.setContentsMargins( 0, 0,
            UIsettings.AssetBrowser.margin + UIsettings.IconDelegate.space, 0 )
        self.subdirLayout.setSpacing(0)
        self.mainLayout.addLayout(self.subdirLayout)


        self.bookmarkButton = QtWidgets.QPushButton()
        self.bookmarkButton.setProperty("bookmark", "true")
        self.bookmarkButton.setMaximumHeight(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMinimumHeight(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMaximumWidth(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setMinimumWidth(UIsettings.AssetBrowser.margin)
        self.bookmarkButton.setCheckable(True)
        self.bookmarkButton.setFlat(True)
        self.bookmarkButton.clicked.connect(self.actionBookmark)
        self.subdirLayout.addWidget(self.bookmarkButton)


        self.backButton = QtWidgets.QPushButton()
        self.backButton.setObjectName("backButton")
        self.backButton.setProperty("background", "browser")
        self.backButton.setProperty("border", "none")
        self.backButton.setFlat(True)
        self.backButton.setFixedSize(
            UIsettings.Path.backIcon,
            UIsettings.Path.height  )
        self.rootLayout.addWidget(self.backButton)
        self.backButton.clicked.connect(self.moveBack)


        self.pathRoot = QtWidgets.QPushButton()
        self.pathRoot.setObjectName("pathRoot")
        self.pathRoot.setProperty("background", "browser")
        self.pathRoot.setProperty("border", "none")
        self.pathRoot.setFont(UIsettings.Path.fontRoot)
        self.pathRoot.setFixedHeight(UIsettings.Path.height)
        self.pathRoot.setMinimumWidth(0)
        self.pathRoot.setFlat(True)
        self.rootLayout.addWidget(self.pathRoot)
        self.pathRoot.clicked.connect(self.resetRoot)


        self.pathLine = QtWidgets.QLineEdit()
        self.pathLine.setObjectName("pathLine")
        self.pathLine.setProperty("background", "browser")
        self.pathLine.setProperty("border", "none")
        self.pathLine.setFont(UIsettings.Path.fontPath)
        self.pathLine.setFixedHeight(UIsettings.Path.height)
        self.pathLine.setObjectName("pathLine")
        self.subdirLayout.addWidget(self.pathLine)
        self.pathLine.editingFinished.connect(self.changeSubdir)

        self.setLayout(self.mainLayout)



    def actionBookmark (self):
        flag = self.bookmarkButton.isChecked()
        self.bookmarkClicked.emit(flag)



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

        if not self.pathLine.text():
            with Settings.UIManager(update=True) as uiSettings:
                uiSettings["focusLibrary"] = ""
                
            self.pathChanged.emit("")
            return

        subdir = os.path.dirname(self.pathLine.text())
        path   = os.path.join(self.root, subdir)

        if os.path.exists(path):
            with Settings.UIManager(update=True) as uiSettings:

                uiSettings["subdirLibrary"] = subdir
                self.pathLine.setText(subdir)
            
            self.pathChanged.emit(path)



    def changeSubdir (self, text=None):

        if not text is None:
            self.pathLine.setText(text)
        else:
            text = self.pathLine.text()

        with Settings.UIManager(update=True) as uiSettings:

                path = os.path.join(self.root, text)
                if os.path.exists(path):

                    uiSettings["subdirLibrary"] = text
                    self.pathChanged.emit(path)

                else:
                    subdir = uiSettings["subdirLibrary"]
                    self.pathLine.setText(subdir)
                    uiSettings["subdirLibrary"] = subdir



    def get (self):

        return os.path.join(
            self.root,
            self.pathLine.text() )
