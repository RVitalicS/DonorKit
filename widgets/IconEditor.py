#!/usr/bin/env python



from Qt import QtWidgets, QtCore, QtGui

from . import IconPainter

from . import Settings
UIGlobals = Settings.UIGlobals







class Editor (QtWidgets.QWidget):

    createFolderQuery = QtCore.Signal(QtCore.QModelIndex)
    createFolder      = QtCore.Signal(QtCore.QModelIndex, str)
    folderLink        = QtCore.Signal(QtCore.QModelIndex)
    favoriteClicked = QtCore.Signal(QtCore.QModelIndex)
    clicked      = QtCore.Signal(QtCore.QModelIndex)
    leaveEditor  = QtCore.Signal()


    def __init__ (self, option, index, theme, parent=None):
        super(Editor, self).__init__(parent)

        self.Icon = IconPainter.Icon(theme)
        self.Icon.index = index

        self.inputFolderName = False

        self.setMouseTracking(True)



    def sizeHint (self):

        return self.Icon.sizeHint()



    def paintEvent (self, event):

        painter = QtGui.QPainter()
        painter.begin(self)

        option = QtWidgets.QStyleOptionViewItem()
        option.rect = self.rect()

        self.Icon.paint(
            painter,
            option,
            self.Icon.index )

        painter.end()

        if not self.inputFolderName:
            dataType = self.Icon.index.data(QtCore.Qt.EditRole).get("type", "")
            if dataType == "folderquery":
                self.inputFolderName = True

                self.iconName = QtWidgets.QLineEdit(self)
                self.iconName.setProperty("background", "transparent")
                self.iconName.setProperty("border", "none")
                self.iconName.setProperty("textcolor", "light")
                self.iconName.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom)
                self.iconName.setFont(UIGlobals.IconDelegate.fontFolderName)
                self.iconName.setContentsMargins( 0, 0, 0, 0)
                self.iconName.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
                self.iconName.setGeometry(self.Icon.folderNameArea)
                self.iconName.show()
                self.iconName.setFocus()



    def mouseMoveEvent (self, event):

        self.Icon.pointer = QtCore.QPoint(
            event.x(),
            event.y())

        self.update()



    def mouseReleaseEvent (self, event):

        self.dragAccept = False

        if event.button() == QtCore.Qt.LeftButton:

            pointer = QtCore.QPoint(
                event.x(),
                event.y())

            if self.Icon.favoriteArea.contains(pointer):
                self.favoriteClicked.emit(self.Icon.index)
                self.repaint()
                return

            if self.Icon.folderLinkArea.contains(pointer):
                self.folderLink.emit(self.Icon.index)
                self.repaint()
                return

            if self.Icon.createFolderArea.contains(pointer):
                self.createFolderQuery.emit(self.Icon.index)
                self.repaint()
                return

            if self.Icon.iconRect.contains(pointer):
                self.clicked.emit(self.Icon.index)
                return



    def keyPressEvent (self, event):
        super(Editor, self).keyReleaseEvent(event)

        if event.key() == QtCore.Qt.Key_Control:
            self.Icon.controlMode = True
            self.repaint()



    def keyReleaseEvent (self, event):
        super(Editor, self).keyReleaseEvent(event)
        
        if event.key() == QtCore.Qt.Key_Control:
            self.Icon.controlMode = False
            self.repaint()



    def leaveEvent (self, event):

        self.leaveEditor.emit()

        if self.inputFolderName:
            self.inputFolderName = False

            self.createFolder.emit(
                self.Icon.index,
                self.iconName.text())
