#!/usr/bin/env python


import os
from . import tools


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIGlobals = Settings.UIGlobals







class BackButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(BackButton, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/back.png")

        self.setFixedSize(
            UIGlobals.Path.backIcon,
            UIGlobals.Path.height  )

        self.buttonPressed = False



    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        positionY = (
            buttonRect.y()
            + int((
                UIGlobals.Path.height
                - self.image.height()
            )/2) )
        position = QtCore.QPoint( buttonRect.x(), positionY)

        color = QtGui.QColor(self.theme.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = tools.recolor(self.image, self.theme.kicker)
        else:
            image = tools.recolor(self.image, self.theme.text)

        painter.drawImage(position, image)
        painter.end()



    def mousePressEvent (self, event):
        super(BackButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(BackButton, self).mousePressEvent(event)
        self.buttonPressed = False
        self.repaint()
        self.clearFocus()

    def enterEvent (self, event):
        super(BackButton, self).enterEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(BackButton, self).leaveEvent(event)
        self.buttonPressed = False






class BookmarkButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(BookmarkButton, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/bookmark.png")

        self.offset = UIGlobals.Path.bookmarkOffset

        self.setMinimumWidth( self.image.width() + self.offset )
        self.setMaximumWidth( self.image.width() + self.offset )

        self.setMinimumHeight( UIGlobals.AssetBrowser.margin )
        self.setMaximumHeight( UIGlobals.AssetBrowser.margin )

        self.buttonHover = False



    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint( buttonRect.x()+self.offset, buttonRect.y())

        color = QtGui.QColor(self.theme.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = tools.recolor(self.image, self.theme.purple)
        elif self.buttonHover:
            image = tools.recolor(self.image, self.theme.browserSocketHover)
        else:
            image = tools.recolor(self.image, self.theme.browserSocket)

        painter.drawImage(position, image)
        painter.end()



    def enterEvent (self, event):
        super(BookmarkButton, self).enterEvent(event)
        self.buttonHover = True
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(BookmarkButton, self).leaveEvent(event)
        self.buttonHover = False
        self.clearFocus()







class PathBar (QtWidgets.QWidget):

    bookmarkClicked = QtCore.Signal()
    pathChanged  = QtCore.Signal(str)


    def __init__ (self, theme):
        super(PathBar, self).__init__()

        self.root = str()


        height  = UIGlobals.AssetBrowser.margin
        height += UIGlobals.Path.height

        self.setMaximumHeight( height )
        self.setMinimumHeight( height )


        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            theme.browserBackground )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(UIGlobals.IconDelegate.space*2)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.rootLayout = QtWidgets.QHBoxLayout()
        self.rootLayout.setContentsMargins(
            UIGlobals.AssetBrowser.margin + UIGlobals.IconDelegate.space,
            UIGlobals.AssetBrowser.margin,
            UIGlobals.IconDelegate.space, 0 )
        self.rootLayout.setSpacing(UIGlobals.IconDelegate.space*2)
        self.mainLayout.addLayout(self.rootLayout)


        self.subdirLayout = QtWidgets.QVBoxLayout()
        self.subdirLayout.setContentsMargins( 0, 0,
            UIGlobals.AssetBrowser.margin + UIGlobals.IconDelegate.space, 0 )
        self.subdirLayout.setSpacing(0)
        self.mainLayout.addLayout(self.subdirLayout)


        self.bookmarkButton = BookmarkButton(theme)
        self.bookmarkButton.setCheckable(True)
        self.bookmarkButton.clicked.connect(self.actionBookmark)
        self.subdirLayout.addWidget(self.bookmarkButton)

        
        self.backButton = BackButton(theme)
        self.rootLayout.addWidget(self.backButton)
        self.backButton.released.connect(self.moveBack)


        self.pathRoot = QtWidgets.QPushButton()
        self.pathRoot.setObjectName("pathRoot")
        self.pathRoot.setProperty("background", "browser")
        self.pathRoot.setProperty("border", "none")
        self.pathRoot.setFont(UIGlobals.Path.fontRoot)
        self.pathRoot.setFixedHeight(UIGlobals.Path.height)
        self.pathRoot.setMinimumWidth(0)
        self.pathRoot.setFlat(True)
        self.rootLayout.addWidget(self.pathRoot)
        self.pathRoot.clicked.connect(self.resetRoot)


        self.pathLine = QtWidgets.QLineEdit()
        self.pathLine.setObjectName("pathLine")
        self.pathLine.setProperty("background", "browser")
        self.pathLine.setProperty("border", "none")
        self.pathLine.setFont(UIGlobals.Path.fontPath)
        self.pathLine.setFixedHeight(UIGlobals.Path.height)
        self.pathLine.setObjectName("pathLine")
        self.subdirLayout.addWidget(self.pathLine)
        self.pathLine.editingFinished.connect(self.changeSubdir)

        self.setLayout(self.mainLayout)



    def actionBookmark (self):
        
        self.bookmarkClicked.emit()



    def setRoot (self, name, path):

        self.pathRoot.setText(name)
        self.root = path

        with Settings.Manager(update=True) as settings:
            subdirLibrary = settings["subdirLibrary"]

            if os.path.exists(os.path.join(path, subdirLibrary)):
                self.pathLine.setText(subdirLibrary)
            else:
                settings["subdirLibrary"] = ""
                self.pathLine.setText("")

        path = os.path.join(self.root, self.pathLine.text())
        self.pathChanged.emit(path)



    def resetRoot (self):

        with Settings.Manager(update=True) as settings:
            settings["subdirLibrary"] = ""
            self.pathLine.setText("")

        self.pathChanged.emit(self.root)



    def moveForward (self, name):

        subdir = os.path.join(self.pathLine.text(), name)
        path   = os.path.join(self.root, subdir)

        if os.path.exists(path):
            with Settings.Manager(update=True) as settings:

                settings["subdirLibrary"] = subdir
                self.pathLine.setText(subdir)
            
            self.pathChanged.emit(path)



    def moveBack (self):

        if not self.pathLine.text():
            with Settings.Manager(update=True) as settings:
                settings["focusLibrary"] = ""
                
            self.pathChanged.emit("")
            return

        subdir = os.path.dirname(self.pathLine.text())
        path   = os.path.join(self.root, subdir)

        if os.path.exists(path):
            with Settings.Manager(update=True) as settings:

                settings["subdirLibrary"] = subdir
                self.pathLine.setText(subdir)
            
            self.pathChanged.emit(path)



    def changeSubdir (self, text=None):

        success = True

        if not text is None:
            self.pathLine.setText(text)
        else:
            text = self.pathLine.text()

        with Settings.Manager(update=True) as settings:

                path = os.path.join(self.root, text)
                if os.path.exists(path):

                    settings["subdirLibrary"] = text
                    self.pathChanged.emit(path)

                else:
                    subdir = settings["subdirLibrary"]
                    self.pathLine.setText(subdir)
                    settings["subdirLibrary"] = subdir

                    success = False

        return success



    def get (self):

        return os.path.join(
            self.root,
            self.pathLine.text() )
