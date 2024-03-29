#!/usr/bin/env python

"""
"""

import re
import os
import toolkit.core.calculate as calculate
import toolkit.core.graphics as graphics
import toolkit.core.ui as uiCommand
from toolkit.core import Metadata
from toolkit.core import timing
from toolkit.system import stream
from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *
from widgets import Settings

UIGlobals = Settings.UIGlobals
SPACE = UIGlobals.IconDelegate.space
MARGIN = UIGlobals.Browser.margin


class BackButton (QtWidgets.QPushButton):

    def __init__ (self, theme, parent=None):
        super(BackButton, self).__init__(parent)
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
            buttonRect.y() + int((UIGlobals.Path.height - self.image.height())/2) )
        position = QtCore.QPoint( buttonRect.x(), positionY)
        color = QtGui.QColor(self.theme.color.browserBackground)
        painter.fillRect(buttonRect, color)
        if self.buttonPressed:
            image = graphics.recolor(self.image, self.theme.color.kicker)
        else:
            image = graphics.recolor(self.image, self.theme.color.text)
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
    
    def __init__ (self, theme, parent=None):
        super(BookmarkButton, self).__init__(parent)
        self.theme = theme
        self.image = QtGui.QImage(":/icons/bookmark.png")
        self.offset = UIGlobals.Path.bookmarkOffset
        self.setFixedSize(
            self.image.width() + self.offset, MARGIN)
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
                image = graphics.recolor(self.image, self.theme.color.browserBookmark)
            elif self.buttonHover:
                image = graphics.recolor(self.image, self.theme.color.browserSocketHover)
            else:
                image = graphics.recolor(self.image, self.theme.color.browserSocket)
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
    pathChanged = Signal(str)

    def __init__ (self, theme, parent=None):
        super(Bar, self).__init__(parent)
        self.theme = theme
        self.libraries = self.getLibraries()
        height = MARGIN
        height += UIGlobals.Path.height
        self.setFixedHeight( height )
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(theme.color.browserBackground))
        self.setPalette(palette)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(SPACE*2)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.rootLayout = QtWidgets.QHBoxLayout()
        self.rootLayout.setContentsMargins(
            MARGIN + SPACE, MARGIN, SPACE, 0 )
        self.rootLayout.setSpacing(SPACE*2)
        self.mainLayout.addLayout(self.rootLayout)

        self.backButton = BackButton(theme)
        self.rootLayout.addWidget(self.backButton)
        self.backButton.released.connect(self.goBack)

        self.rootButton = QtWidgets.QPushButton()
        self.rootButton.setObjectName("rootButton")
        self.rootButton.setProperty("background", "browser")
        self.rootButton.setProperty("border", "none")
        uiCommand.setFont(self.rootButton, UIGlobals.Path.fontRoot)
        self.rootButton.setFixedHeight(UIGlobals.Path.height)
        self.rootButton.setMinimumWidth(0)
        self.rootButton.setFlat(True)
        self.rootLayout.addWidget(self.rootButton)
        self.rootButton.clicked.connect(self.goLibrary)

        self.subdirLayout = QtWidgets.QVBoxLayout()
        self.subdirLayout.setContentsMargins(0, 0, MARGIN + SPACE, 0)
        self.subdirLayout.setSpacing(0)
        self.mainLayout.addLayout(self.subdirLayout)

        self.bookmarkButton = BookmarkButton(theme)
        self.bookmarkButton.setCheckable(True)
        self.bookmarkButton.clicked.connect(self.switchBookmark)
        self.subdirLayout.addWidget(self.bookmarkButton)

        self.pathLine = QtWidgets.QLineEdit()
        self.pathLine.setObjectName("pathLine")
        self.pathLine.setProperty("textcolor", "on")
        self.pathLine.setProperty("background", "browser")
        self.pathLine.setProperty("border", "none")
        uiCommand.setFont(self.pathLine, UIGlobals.Path.fontPath)
        self.pathLine.setFixedHeight(UIGlobals.Path.height)
        self.pathLine.setObjectName("pathLine")
        self.subdirLayout.addWidget(self.pathLine)
        self.pathLine.editingFinished.connect(self.goQuery)
        self.mainLayout.setStretch(0, 0)
        self.mainLayout.setStretch(1, 1)
        self.setLayout(self.mainLayout)
    
    def getUI (self, root=False):
        pathUI = self.rootButton.text()
        subdir = self.pathLine.text()
        if subdir and not root:
            pathUI += "/"+ subdir
        return pathUI
    
    def setUI (self, pathUI):
        path = self.resolve(pathUI)
        if pathUI and not path:
            return
        if not pathUI:
            path = ""
        subdir = pathUI.split("/")
        libname = subdir[0]
        subdir.remove(libname)
        subdir = "/".join(subdir)
        self.rootButton.setText(libname)
        self.pathLine.setText(subdir)
        with Settings.Manager(self.theme.app, True) as settings:
            settings["location"] = pathUI
        self.goEmit(path)
    
    def resolve (self, pathUI=None ):
        if pathUI is None:
            pathUI = self.getUI()
        subdir = pathUI.split("/")
        libname = subdir[0]
        subdir.remove(libname)
        path = self.libraries.get(libname, "")
        for item in subdir:
            path = os.path.join(path, item)
            if os.path.exists(path):
                continue
            dirname = os.path.dirname(path)
            metadata = os.path.join(dirname, Metadata.METAFILE)
            if not os.path.exists(metadata):
                continue
            data = stream.dataread(metadata)
            dataType = data.get("type")
            if dataType == "foldercolors":
                for filename in os.listdir(dirname):
                    if not re.search(r"\.json*$", filename):
                        continue
                    elif filename == Metadata.METAFILE:
                        continue
                    filepath = os.path.join(dirname, filename)
                    data = stream.dataread(filepath)
                    if data.get("title") == item:
                        path = os.path.join(dirname, filename)
                        break
        if os.path.exists(path):
            return path
    
    def exists (self, pathUI):
        result = False
        itemUI = None
        components = pathUI.split(":")
        if len(components) == 2:
            pathUI, itemUI = components
        path = self.resolve(pathUI)
        if path and not itemUI:
            result = True
        elif path and itemUI:
            if self.isColors(path):
                data = stream.dataread(path)
                records = data.get("records", {})
                for name,color in records.items():
                    code = color.get("code")
                    if code == itemUI:
                        result = True
                        break
        return result
    
    def isRoot (self, path ):
        if path == "":
            return True
        return False
    
    def isUsdAsset (self, path=None ):
        if path is None:
            path = self.resolve()
        if os.path.isdir(path):
            dataType = Metadata.getType(path)
            if dataType == "usdasset":
                return True
        return False
    
    def isUsdMaterial (self, path=None ):
        if path is None:
            path = self.resolve()
        if os.path.isdir(path):
            dataType = Metadata.getType(path)
            if dataType == "usdmaterial":
                return True
        return False
    
    def isFolderColors (self, path=None ):
        if path is None:
            path = self.resolve()
        if os.path.isdir(path):
            dataType = Metadata.getType(path)
            if dataType == "foldercolors":
                return True
        return False
    
    def isColors (self, path=None ):
        if path is None:
            path = self.resolve()
        if os.path.isfile(path):
            path = os.path.dirname(path)
            dataType = Metadata.getType(path)
            if dataType == "foldercolors":
                return True
        return False
    
    def goEmit (self, path):
        with Settings.Manager(self.theme.app, False) as settings:
            bookmarks = settings.get("bookmarks")
        pathUI = self.getUI()
        if pathUI in bookmarks:
            self.bookmarkButton.setChecked(True)
        else:
            self.bookmarkButton.setChecked(False)
        self.pathChanged.emit(path)
    
    def goQuery (self):
        pathUI = self.getUI()
        self.setUI(pathUI)
        with Settings.Manager(self.theme.app, False) as settings:
            pathUI = settings.get("location")
        subdir = pathUI.split("/")
        libname = subdir[0]
        subdir.remove(libname)
        subdir = "/".join(subdir)
        self.pathLine.setText(subdir)
    
    def goForward (self, name):
        pathUI = os.path.join(self.getUI(), name)
        path = self.resolve(pathUI)
        if not path:
            return
        text = os.path.join(self.pathLine.text(), name)
        self.pathLine.setText(text)
        with Settings.Manager(self.theme.app, True) as settings:
            settings["location"] = pathUI
        self.goEmit(path)
    
    def goBack (self):
        pathUI = os.path.dirname(self.getUI())
        path = self.resolve(pathUI)
        if pathUI and not path:
            return
        if not pathUI:
            path = ""
        text = os.path.dirname(self.pathLine.text())
        self.pathLine.setText(text)
        with Settings.Manager(self.theme.app, True) as settings:
            settings["location"] = pathUI
        self.goEmit(path)
    
    def goLibrary (self):
        pathUI = self.getUI(root=True)
        path = self.resolve(pathUI)
        if not path:
            return
        self.pathLine.setText("")
        with Settings.Manager(self.theme.app, True) as settings:
            settings["location"] = pathUI
        self.goEmit(path)
    
    def getLibraries (self):
        libraries = dict()
        if not os.getenv("ASSETLIBS", ""):
            thisDir = os.path.dirname(__file__)
            rootDir = os.path.dirname(thisDir)
            libsDir = os.path.join(
                rootDir, "examples", "libraries" )
            os.environ["ASSETLIBS"] = "{}:{}".format(
                os.path.join(libsDir, "Colors" ) ,
                os.path.join(libsDir, "Models" ) )
        path = os.getenv("ASSETLIBS", "")
        for rootPath in path.split(":"):
            needRefresh = False
            with Metadata.MetadataManager(
                    rootPath, update=False) as data:
                if data.get("type") == "root":
                    name = data.get("name")
                    libraries[name] = rootPath
                    scantime = data.get("scantime")
                    if timing.isDayAgo(scantime):
                        needRefresh = True
            if needRefresh:
                Metadata.refreshMaterialData(rootPath)
        return libraries
    
    def getCurrentLibrary (self):
        libname = self.rootButton.text()
        path = self.libraries.get(libname, "")
        return path
    
    def switchBookmark (self):
        self.bookmarkClicked.emit()
    
    def uiVisibility (self):
        width = self.width() - MARGIN * 2 - SPACE * 2
        font = UIGlobals.Path.fontPath
        text = self.pathLine.text()
        textWidth = calculate.stringWidth(text, font)
        textWidth += SPACE
        sumwidth = (
            self.backButton.width() + self.rootButton.width()
            + SPACE * 3 + textWidth)
        if width > sumwidth:
            self.bookmarkButton.show()
            self.pathLine.show()
        else:
            self.pathLine.hide()
            self.bookmarkButton.hide()

    def resizeEvent (self, event):
        super(Bar, self).resizeEvent(event)
        self.uiVisibility()
