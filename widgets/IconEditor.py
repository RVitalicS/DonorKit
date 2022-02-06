#!/bin/python


from Qt import QtWidgets, QtCore, QtGui

from . import IconPainter












class Editor (QtWidgets.QWidget):

    clicked      = QtCore.Signal(QtCore.QModelIndex)
    leaveEditor  = QtCore.Signal()


    def __init__ (self, option, index, parent=None):
        super(Editor, self).__init__(parent)

        self.Icon = IconPainter.Icon()
        self.Icon.index = index

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
            self.Icon.index,
            editing=True)

        painter.end()



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

            if self.Icon.iconRect.contains(pointer):
                self.clicked.emit(self.Icon.index)  



    def leaveEvent (self, event):

        self.leaveEditor.emit()
