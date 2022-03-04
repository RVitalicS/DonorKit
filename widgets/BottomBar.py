#!/usr/bin/env python



import os
from . import tools

from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIGlobals = Settings.UIGlobals

SPACE  = UIGlobals.IconDelegate.space * 2
MARGIN = UIGlobals.AssetBrowser.margin





class FavoriteButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(FavoriteButton, self).__init__()
        self.setCheckable(True)

        self.theme = theme
        self.image = QtGui.QImage(":/icons/star.png")

        self.setMinimumWidth( self.image.width() )
        self.setMaximumWidth( self.image.width() )

        offset = UIGlobals.Bar.favoriteOffset
        self.setMinimumHeight( self.image.height() + offset )
        self.setMaximumHeight( self.image.height() + offset )

        self.buttonHover = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(self.theme.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = tools.recolor(self.image, self.theme.browserSocketPressed)
        elif self.buttonHover:
            image = tools.recolor(self.image, self.theme.browserSocketHover)
        else:
            image = tools.recolor(self.image, self.theme.browserSocket)

        painter.drawImage(position, image)
        painter.end()


    def enterEvent (self, event):
        super(FavoriteButton, self).enterEvent(event)
        self.buttonHover = True
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(FavoriteButton, self).leaveEvent(event)
        self.buttonHover = False
        self.clearFocus()
        





class BookmarkButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(BookmarkButton, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/bookmark.png")

        self.setMinimumWidth( self.image.width() )
        self.setMaximumWidth( self.image.width() )

        offset = UIGlobals.Bar.bookmarkOffset
        self.setMinimumHeight( self.image.height() + offset )
        self.setMaximumHeight( self.image.height() + offset )

        self.buttonPressed = False
        self.buttonHover = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(self.theme.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = tools.recolor(self.image, self.theme.browserSocketPressed)
        elif self.buttonHover:
            image = tools.recolor(self.image, self.theme.browserSocketHover)
        else:
            image = tools.recolor(self.image, self.theme.browserSocket)

        painter.drawImage(position, image)
        painter.end()


    def mousePressEvent (self, event):
        super(BookmarkButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(BookmarkButton, self).mousePressEvent(event)
        self.buttonPressed = False
        self.repaint()
        self.clearFocus()

    def enterEvent (self, event):
        super(BookmarkButton, self).enterEvent(event)
        self.buttonHover = True
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(BookmarkButton, self).leaveEvent(event)
        self.buttonHover = False
        self.buttonPressed = False
        





class ThemeButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(ThemeButton, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/theme.png")

        self.setMinimumWidth( self.image.width() )
        self.setMaximumWidth( self.image.width() )

        offset = UIGlobals.Bar.bookmarkOffset
        self.setMinimumHeight( self.image.height() + offset )
        self.setMaximumHeight( self.image.height() + offset )

        self.buttonPressed = False
        self.buttonHover = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(self.theme.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = tools.recolor(self.image, self.theme.browserSocketPressed)
        elif self.buttonHover:
            image = tools.recolor(self.image, self.theme.browserSocketHover)
        else:
            image = tools.recolor(self.image, self.theme.browserSocket)

        painter.drawImage(position, image)
        painter.end()


    def mousePressEvent (self, event):
        super(ThemeButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(ThemeButton, self).mousePressEvent(event)
        self.buttonPressed = False
        self.repaint()
        self.clearFocus()

    def enterEvent (self, event):
        super(ThemeButton, self).enterEvent(event)
        self.buttonHover = True
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def leaveEvent (self, event):
        super(ThemeButton, self).leaveEvent(event)
        self.buttonHover = False
        self.buttonPressed = False
        





class FavoriteGroup (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(FavoriteGroup, self).__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0, SPACE*2 ,0)
        self.mainLayout.setSpacing(SPACE)

        self.label = QtWidgets.QLabel("FAVORITES")
        self.label.setFont(UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "light")

        self.button = FavoriteButton(theme)

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.button)
        self.setLayout(self.mainLayout)
        





class BookmarkGroup (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(BookmarkGroup, self).__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0, SPACE*2 ,0)
        self.mainLayout.setSpacing(SPACE)

        self.label = QtWidgets.QLabel("BOOKMARKS")
        self.label.setFont(UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "light")

        self.button = BookmarkButton(theme)

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.button)
        self.setLayout(self.mainLayout)
        





class ThemeGroup (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(ThemeGroup, self).__init__()

        self.theme = theme
        self.current = theme.name

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0, SPACE*2 ,0)
        self.mainLayout.setSpacing(SPACE)

        self.label = QtWidgets.QLabel("THEME")
        self.label.setFont(UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "light")

        self.button = ThemeButton(theme)
        self.button.released.connect(self.change)

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.button)
        self.setLayout(self.mainLayout)


    def change (self):

        if self.current == "dark":
            self.current = "light"
        else:
            self.current = "dark"

        with Settings.Export(update=True) as settings:
            settings["theme"] = self.current

        if self.current != self.theme.name:
            self.label.setText("RESTART")
        else:
            self.label.setText("THEME")
        





class PreviewGroup (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(PreviewGroup, self).__init__()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(SPACE)

        self.label = QtWidgets.QLabel("PREVIEW")
        self.label.setFont(UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "light")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setFixedWidth(35)
        self.slider.setRange(1, 3)
        self.slider.setTickInterval(1)

        with Settings.Manager(update=False) as settings:
            self.slider.setValue(settings["iconSize"])

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.slider)
        self.setLayout(self.mainLayout)
        





class BottomBar (QtWidgets.QWidget):

    bookmarkChoosed = QtCore.Signal(str)


    def __init__ (self, theme):
        super(BottomBar, self).__init__()

        height = UIGlobals.Bar.height


        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            theme.browserBackground )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)


        self.bookmarkCombobox = QtWidgets.QComboBox()
        self.bookmarkCombobox.setFont(UIGlobals.Bar.fontBookmark)
        self.bookmarkCombobox.setEditable(False)
        self.bookmarkCombobox.setFrame(False)
        self.bookmarkCombobox.setVisible(False)
        self.bookmarkCombobox.setFixedHeight(0)
        self.bookmarkCombobox.setProperty("bookmark", "true")
        self.bookmarkCombobox.activated.connect(self.getData)
        self.mainLayout.addWidget(self.bookmarkCombobox)


        self.groupsLayout = QtWidgets.QHBoxLayout()
        self.groupsLayout.setContentsMargins(
            MARGIN + int(SPACE/2), 0,
            MARGIN + int(SPACE/2), 0)
        self.groupsLayout.setSpacing(0)
        self.mainLayout.addLayout(self.groupsLayout)


        self.favorite = FavoriteGroup(theme)
        self.favorite.setFixedHeight(height)
        self.groupsLayout.addWidget(self.favorite)

        self.bookmark = BookmarkGroup(theme)
        self.bookmark.setFixedHeight(height)
        self.bookmark.button.pressed.connect(self.showBookmarks)
        self.groupsLayout.addWidget(self.bookmark)


        spacer = QtWidgets.QSpacerItem(0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.groupsLayout.addItem(spacer)


        self.theme = ThemeGroup(theme)
        self.theme.setFixedHeight(height)
        self.groupsLayout.addWidget(self.theme)

        self.preview = PreviewGroup(theme)
        self.preview.setFixedHeight(height)
        self.groupsLayout.addWidget(self.preview)


        self.groupsLayout.setStretch(0, 0)
        self.groupsLayout.setStretch(1, 0)
        self.groupsLayout.setStretch(2, 1)
        self.groupsLayout.setStretch(3, 0)
        self.groupsLayout.setStretch(4, 0)

        self.setLayout(self.mainLayout)


    def showBookmarks (self):
        self.bookmarkCombobox.setCurrentIndex(-1)
        self.bookmarkCombobox.setVisible(True)
        self.bookmarkCombobox.showPopup()


    def getData (self, index):
        data = self.bookmarkCombobox.itemData(index)
        self.bookmarkChoosed.emit(data)
        self.bookmarkCombobox.setVisible(False)



    def resizeEvent (self, event):
        super(BottomBar, self).resizeEvent(event)

        self.favorite.hide()
        self.bookmark.hide()
        self.preview.hide()
        self.theme.hide()

        width = self.width() - MARGIN * 2 - SPACE
        sumwidth = self.favorite.width()

        if width > sumwidth:
            self.favorite.show()

            sumwidth += self.bookmark.width()
            if width > sumwidth:
                self.bookmark.show()

                sumwidth += self.preview.width()
                if width > sumwidth:
                    self.preview.show()

                    sumwidth += self.theme.width()
                    if width > sumwidth:
                        self.theme.show()
