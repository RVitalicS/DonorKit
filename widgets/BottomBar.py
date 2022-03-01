#!/usr/bin/env python



import os
from . import tools
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings
        





class FavoriteButton (QtWidgets.QPushButton):


    def __init__ (self):
        super(FavoriteButton, self).__init__()
        self.setCheckable(True)

        self.image = QtGui.QImage(":/icons/star.png")

        self.setMinimumWidth( self.image.width() )
        self.setMaximumWidth( self.image.width() )

        offset = UIsettings.Bar.favoriteOffset
        self.setMinimumHeight( self.image.height() + offset )
        self.setMaximumHeight( self.image.height() + offset )

        self.buttonHover = False



    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(stylesheet.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = tools.recolor(self.image, stylesheet.browserHandle)
        elif self.buttonHover:
            image = tools.recolor(self.image, stylesheet.browserSocketHover)
        else:
            image = tools.recolor(self.image, stylesheet.browserSocket)

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


    def __init__ (self):
        super(BookmarkButton, self).__init__()

        self.image = QtGui.QImage(":/icons/bookmark.png")

        self.setMinimumWidth( self.image.width() )
        self.setMaximumWidth( self.image.width() )

        offset = UIsettings.Bar.bookmarkOffset
        self.setMinimumHeight( self.image.height() + offset )
        self.setMaximumHeight( self.image.height() + offset )

        self.buttonPressed = False
        self.buttonHover = False



    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        position = QtCore.QPoint(buttonRect.x(), buttonRect.y())

        color = QtGui.QColor(stylesheet.browserBackground)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = tools.recolor(self.image, stylesheet.browserHandle)
        elif self.buttonHover:
            image = tools.recolor(self.image, stylesheet.browserSocketHover)
        else:
            image = tools.recolor(self.image, stylesheet.browserSocket)

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


        self.favoritesLayout = QtWidgets.QHBoxLayout()
        self.favoritesLayout.setContentsMargins(0, 0,
            UIsettings.IconDelegate.space*4, 0)
        self.favoritesLayout.setSpacing(UIsettings.IconDelegate.space*2)
        self.mainLayout.addLayout(self.favoritesLayout)

        self.favoritesLabel = QtWidgets.QLabel("FAVORITES")
        self.favoritesLabel.setObjectName("favoritesLabel")
        self.favoritesLabel.setFont(UIsettings.Bar.fontPreview)
        self.favoritesLabel.setAlignment(
            QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.favoritesLabel.setProperty("textcolor", "light")
        self.favoritesLayout.addWidget(self.favoritesLabel)

        self.favoritesButton = FavoriteButton()
        self.favoritesLayout.addWidget(self.favoritesButton)


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


        self.bookmarkButton = BookmarkButton()
        self.bookmarksLayout.addWidget(self.bookmarkButton)
        self.bookmarkButton.pressed.connect(self.showBookmarks)

        self.bookmarkCombobox = QtWidgets.QComboBox()
        self.bookmarkCombobox.setFont(UIsettings.Bar.fontBookmark)
        self.bookmarkCombobox.setEditable(False)
        self.bookmarkCombobox.setFrame(False)
        self.bookmarkCombobox.setProperty("bookmark", "true")
        self.bookmarkCombobox.activated.connect(self.bookmarkData)
        self.bookmarksLayout.addWidget(self.bookmarkCombobox)


        spacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)


        self.previewLayout = QtWidgets.QHBoxLayout()
        self.previewLayout.setContentsMargins(0,0,0,0)
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


        self.mainLayout.setStretch(0, 0)
        self.mainLayout.setStretch(1, 0)
        self.mainLayout.setStretch(2, 1)
        self.mainLayout.setStretch(3, 0)
        self.setLayout(self.mainLayout)



    def showBookmarks (self):
        self.bookmarkCombobox.setCurrentIndex(-1)
        self.bookmarkCombobox.showPopup()



    def bookmarkData (self, index):
        data = self.bookmarkCombobox.itemData(index)
        self.bookmarkChoosed.emit(data)
        self.bookmarkCombobox.setVisible(False)
