#!/usr/bin/env python



import toolbox.core.graphics
import toolbox.core.ui

from Qt import QtWidgets, QtCore, QtGui
from .items import PopupDelegate

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

        color = QtGui.QColor(self.theme.color.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocketPressed )
        elif self.buttonHover:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocketHover )
        else:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocket )

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

        color = QtGui.QColor(self.theme.color.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocketPressed )
        elif self.buttonHover:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocketHover )
        else:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.browserSocket )

        painter.drawImage(position, image)
        painter.end()


    def mousePressEvent (self, event):
        super(BookmarkButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(BookmarkButton, self).mouseReleaseEvent(event)
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

        if theme.name == "dark":
            self.dark = True
        else:
            self.dark = False

        self.moon = QtGui.QImage(":/icons/thememoon.png")
        self.sun  = QtGui.QImage(":/icons/themesun.png")

        self.setMinimumWidth( self.moon.width() )
        self.setMaximumWidth( self.moon.width() )

        offset = UIGlobals.Bar.bookmarkOffset
        self.setMinimumHeight( self.moon.height() + offset )
        self.setMaximumHeight( self.moon.height() + offset )

        self.buttonPressed = False
        self.buttonHover = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(self.theme.color.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.dark:
            image = self.moon
        else:
            image = self.sun

        if self.buttonPressed:
            image = toolbox.core.graphics.recolor(
                image, self.theme.color.browserSocketPressed )
        elif self.buttonHover:
            image = toolbox.core.graphics.recolor(
                image, self.theme.color.browserSocketHover )
        else:
            image = toolbox.core.graphics.recolor(
                image, self.theme.color.browserSocket )

        painter.drawImage(position, image)
        painter.end()


    def mousePressEvent (self, event):
        super(ThemeButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(ThemeButton, self).mouseReleaseEvent(event)
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
        toolbox.core.ui.setFont(
            self.label,
            UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "on")

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
        toolbox.core.ui.setFont(
            self.label,
            UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "on")

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
        toolbox.core.ui.setFont(
            self.label,
            UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "on")

        self.button = ThemeButton(theme)
        self.button.released.connect(self.change)

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.button)
        self.setLayout(self.mainLayout)



    def change (self):

        if self.current == "dark":
            self.current = "light"
            self.button.dark = False
            self.button.repaint()
        else:
            self.current = "dark"
            self.button.dark = True
            self.button.repaint()

        if self.theme.application == "export":
            with Settings.Export(update=True) as settings:
                settings["theme"] = self.current
        else:
            with Settings.Manager(update=True) as settings:
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

        self.label  = QtWidgets.QLabel("PREVIEW")
        toolbox.core.ui.setFont(
            self.label,
            UIGlobals.Bar.fontPreview)
        self.label.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setProperty("textcolor", "on")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setFixedWidth(35)
        self.slider.setRange(1, 3)
        self.slider.setTickInterval(1)

        with Settings.Manager(update=False) as settings:
            self.slider.setValue(settings["iconSize"])

        self.mainLayout.addWidget(self.label)
        self.mainLayout.addWidget(self.slider)
        self.setLayout(self.mainLayout)






class ComboBox (QtWidgets.QComboBox):

    def __init__ (self, theme):
        super(ComboBox, self).__init__()

        self.view().window().setAttribute(
            QtCore.Qt.WA_TranslucentBackground )

        self.setEditable(False)
        self.setFrame(False)
        self.setVisible(False)
        self.setFixedHeight(0)


    def showPopup (self):
        super(ComboBox, self).showPopup()

        popup = self.findChild(QtWidgets.QFrame)
        popup.move(
            popup.x(),
            popup.y() - popup.height())






class Bar (QtWidgets.QWidget):

    bookmarkChosen = QtCore.Signal(str)


    def __init__ (self, theme):
        super(Bar, self).__init__()

        height = UIGlobals.Bar.height


        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(
                theme.color.browserBackground) )
        self.setPalette(palette)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)


        self.bookmarkLayout = QtWidgets.QVBoxLayout()
        self.bookmarkLayout.setContentsMargins(
            int(SPACE/2),0,
            int(SPACE/2),0)
        self.bookmarkLayout.setSpacing(0)
        self.mainLayout.addLayout(self.bookmarkLayout)

        self.bookmarkCombobox = ComboBox(theme)
        self.bookmarkCombobox.setItemDelegate(
            PopupDelegate.Delegate(self.bookmarkCombobox.view(), theme) )
        self.bookmarkCombobox.activated.connect(self.getData)
        self.bookmarkLayout.addWidget(self.bookmarkCombobox)


        self.groupsLayout = QtWidgets.QHBoxLayout()
        self.groupsLayout.setContentsMargins(
            MARGIN + int(SPACE/2), 0,
            MARGIN + int(SPACE/2), 0)
        self.groupsLayout.setSpacing(0)
        self.mainLayout.addLayout(self.groupsLayout)


        self.favoriteHideForce = False
        self.favorite = FavoriteGroup(theme)
        self.favorite.setFixedHeight(height)
        self.groupsLayout.addWidget(self.favorite)

        self.bookmarkHideForce = False
        self.bookmark = BookmarkGroup(theme)
        self.bookmark.setFixedHeight(height)
        self.bookmark.button.pressed.connect(self.showBookmarks)
        self.groupsLayout.addWidget(self.bookmark)


        self.spacerCenter = QtWidgets.QSpacerItem(0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.groupsLayout.addItem(self.spacerCenter)


        self.themeHideForce = False
        self.theme = ThemeGroup(theme)
        self.theme.setFixedHeight(height)
        self.groupsLayout.addWidget(self.theme)

        self.previewHideForce = False
        self.preview = PreviewGroup(theme)
        self.preview.setFixedHeight(height)
        self.groupsLayout.addWidget(self.preview)


        self.spacerRight = QtWidgets.QSpacerItem(0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.groupsLayout.addItem(self.spacerRight)


        self.groupsLayout.setStretch(0, 0)
        self.groupsLayout.setStretch(1, 0)
        self.groupsLayout.setStretch(2, 1)
        self.groupsLayout.setStretch(3, 0)
        self.groupsLayout.setStretch(4, 0)
        self.groupsLayout.setStretch(5, 0)

        self.setLayout(self.mainLayout)


    def showBookmarks (self):
        self.bookmarkCombobox.setCurrentIndex(-1)
        self.bookmarkCombobox.setVisible(True)
        self.bookmarkCombobox.showPopup()


    def getData (self, index):
        data = self.bookmarkCombobox.itemData(index)
        self.bookmarkChosen.emit(data)
        self.bookmarkCombobox.setVisible(False)



    def resizeEvent (self, event):
        super(Bar, self).resizeEvent(event)
        self.uiVisibility()



    def uiVisibility (self):

        self.favorite.hide()
        self.bookmark.hide()
        self.preview.hide()
        self.theme.hide()

        width = self.width() - MARGIN * 2 - SPACE
        sumwidth = 0


        if not self.favoriteHideForce:
            sumwidth += self.favorite.width()
        if width > sumwidth:
            if not self.favoriteHideForce:
                self.favorite.show()


            if not self.bookmarkHideForce:
                sumwidth += self.bookmark.width()
            if width > sumwidth:
                if not self.bookmarkHideForce:
                    self.bookmark.show()


                if not self.previewHideForce:
                    sumwidth += self.preview.width()
                if width > sumwidth:
                    if not self.previewHideForce:
                        self.preview.show()


                    if not self.themeHideForce:
                        sumwidth += self.theme.width()
                    if width > sumwidth:
                        if not self.themeHideForce:
                            self.theme.show()
