#!/usr/bin/env python


import os

import toolkit.core.calculate
import toolkit.core.graphics
import toolkit.core.ui


from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *

from . import Settings
UIGlobals = Settings.UIGlobals

SPACE  = UIGlobals.IconDelegate.space
MARGIN = UIGlobals.AssetBrowser.margin







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

        color = QtGui.QColor(self.theme.color.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.kicker )
        else:
            image = toolkit.core.graphics.recolor(
                self.image, self.theme.color.text )

        painter.drawImage(position, image)
        painter.end()



    def mousePressEvent (self, event):
        super(BackButton, self).mousePressEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(BackButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()
        self.clearFocus()

    def enterEvent (self, event):
        super(BackButton, self).enterEvent(event)
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(BackButton, self).leaveEvent(event)
        self.buttonPressed = False
        self.clearFocus()






class BookmarkButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(BookmarkButton, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/bookmark.png")

        self.offset = UIGlobals.Path.bookmarkOffset

        self.setFixedSize(
            self.image.width() + self.offset,
            MARGIN )

        self.buttonHover = False



    def paintEvent (self, event):

        if self.isEnabled():

            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

            buttonRect = self.contentsRect()
            position = QtCore.QPoint( buttonRect.x()+self.offset, buttonRect.y())

            color = QtGui.QColor(self.theme.color.browserBackground)
            painter.fillRect(buttonRect, color)

            if self.isChecked():
                image = toolkit.core.graphics.recolor(
                    self.image, self.theme.color.browserBookmark)
            elif self.buttonHover:
                image = toolkit.core.graphics.recolor(
                    self.image, self.theme.color.browserSocketHover)
            else:
                image = toolkit.core.graphics.recolor(
                    self.image, self.theme.color.browserSocket)

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







class Bar (QtWidgets.QWidget):

    bookmarkClicked = Signal()
    pathChanged  = Signal(str)


    def __init__ (self, theme):
        super(Bar, self).__init__()

        self.root   = str()
        self.group  = str()


        height  = MARGIN
        height += UIGlobals.Path.height

        self.setFixedHeight( height )


        self.setAutoFillBackground(True)

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(
                theme.color.browserBackground) )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(SPACE*2)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.rootLayout = QtWidgets.QHBoxLayout()
        self.rootLayout.setContentsMargins(
            MARGIN + SPACE,
            MARGIN, SPACE, 0 )
        self.rootLayout.setSpacing(SPACE*2)
        self.mainLayout.addLayout(self.rootLayout)

        
        self.backButton = BackButton(theme)
        self.rootLayout.addWidget(self.backButton)
        self.backButton.released.connect(self.moveBack)


        self.pathRoot = QtWidgets.QPushButton()
        self.pathRoot.setObjectName("pathRoot")
        self.pathRoot.setProperty("background", "browser")
        self.pathRoot.setProperty("border", "none")
        toolkit.core.ui.setFont(
            self.pathRoot,
            UIGlobals.Path.fontRoot)
        self.pathRoot.setFixedHeight(UIGlobals.Path.height)
        self.pathRoot.setMinimumWidth(0)
        self.pathRoot.setFlat(True)
        self.rootLayout.addWidget(self.pathRoot)
        self.pathRoot.clicked.connect(self.resetRoot)


        self.subdirLayout = QtWidgets.QVBoxLayout()
        self.subdirLayout.setContentsMargins( 0, 0,
            MARGIN + SPACE, 0 )
        self.subdirLayout.setSpacing(0)
        self.mainLayout.addLayout(self.subdirLayout)


        self.bookmarkButton = BookmarkButton(theme)
        self.bookmarkButton.setCheckable(True)
        self.bookmarkButton.clicked.connect(self.actionBookmark)
        self.subdirLayout.addWidget(self.bookmarkButton)


        self.pathLine = QtWidgets.QLineEdit()
        self.pathLine.setObjectName("pathLine")
        self.pathLine.setProperty("background", "browser")
        self.pathLine.setProperty("border", "none")
        toolkit.core.ui.setFont(
            self.pathLine,
            UIGlobals.Path.fontPath)
        self.pathLine.setFixedHeight(UIGlobals.Path.height)
        self.pathLine.setObjectName("pathLine")
        self.subdirLayout.addWidget(self.pathLine)
        self.pathLine.editingFinished.connect(self.changeSubdir)

        self.mainLayout.setStretch(0, 0)
        self.mainLayout.setStretch(1, 1)
        self.setLayout(self.mainLayout)



    def resizeEvent (self, event):
        super(Bar, self).resizeEvent(event)
        self.uiVisibility()



    def uiVisibility (self):

        width = self.width() - MARGIN * 2 - SPACE * 2

        font = UIGlobals.Path.fontPath
        text = self.pathLine.text()
        textWidth  = toolkit.core.calculate.stringWidth(text, font)
        textWidth += SPACE

        sumwidth = (
            self.backButton.width()
            + self.pathRoot.width()
            + SPACE * 3
            + textWidth )

        if width > sumwidth:
            self.bookmarkButton.show()
            self.pathLine.show()
            
        else:
            self.pathLine.hide()
            self.bookmarkButton.hide()



    def actionBookmark (self):
        
        self.bookmarkClicked.emit()



    def setRoot (self, name, path, finish=True):

        self.pathRoot.setText(name)
        self.root = path

        with Settings.Manager(update=True) as settings:
            subdirLibrary = settings["subdirLibrary"]

            if os.path.exists(os.path.join(path, subdirLibrary)):
                self.pathLine.setText(subdirLibrary)
            else:
                settings["subdirLibrary"] = ""
                self.pathLine.setText("")

        if finish:
            path = os.path.join(self.root, self.pathLine.text())
            self.pathChanged.emit(path)



    def resetRoot (self):

        if self.group:
            self.group = str()

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

        if self.group:
            self.group = str()

            path = os.path.join(
                self.root, self.pathLine.text())
            self.pathChanged.emit(path)
            return


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

        if text is not None:
            self.pathLine.setText(text)
        else:
            text = self.pathLine.text()

        with Settings.Manager(update=True) as settings:

            path = os.path.join(self.root, text)
            if os.path.exists(path):
                
                if self.group:
                    self.group = str()

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
