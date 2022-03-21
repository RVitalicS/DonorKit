#!/usr/bin/env python



from Qt import QtWidgets, QtCore, QtGui

from .. import Settings
UIGlobals = Settings.UIGlobals







class Painter (object):



    def __init__ (self, theme):

        self.theme = theme
        self.index = QtCore.QModelIndex()

        self.pointer  = QtCore.QPoint(-1, -1)
        self.iconRect = QtCore.QRect()



    def sizeHint (self):
        
        model = self.index.model()
        raw = self.index.row()
        item = model.item(raw)

        return item.sizeHint()


    def paint (self, painter, option, index):
        
        self.painter = painter
        self.option  = option
        self.index   = index

        self.space = UIGlobals.IconDelegate.space
        self.radius = UIGlobals.IconDelegate.radius

        self.checked = self.index.data(QtCore.Qt.StatusTipRole)

        self.data = self.index.data(QtCore.Qt.EditRole).get("data")
        self.type = self.index.data(QtCore.Qt.EditRole).get("type")
        if self.type != "asset":
            self.radius = 0

        self.width  = self.option.rect.width()
        self.height = self.option.rect.height()

        self.pointX = self.option.rect.x()
        self.pointY = self.option.rect.y()

        self.iconRect = QtCore.QRect(
            self.pointX + self.space   ,
            self.pointY + self.space   ,
            self.width  - self.space*2 ,
            self.height - self.space*2 )

        self.hover = False
        if self.iconRect.contains(self.pointer):
            self.hover = True
        
        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(
            self.iconRect.x()     , self.iconRect.y()      ,
            self.iconRect.width() , self.iconRect.height() ,
            self.radius           , self.radius            ,
            mode=QtCore.Qt.AbsoluteSize                    )

        self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.painter.setClipPath(clipPath)







class Editor (QtWidgets.QWidget):


    clicked      = QtCore.Signal(QtCore.QModelIndex)
    leaveEditor  = QtCore.Signal()
    
    link         = QtCore.Signal(QtCore.QModelIndex)

    createFolderQuery = QtCore.Signal(QtCore.QModelIndex)
    createFolder      = QtCore.Signal(QtCore.QModelIndex, str)

    favoriteClicked = QtCore.Signal(QtCore.QModelIndex)



    def __init__ (self, parent, index, theme):
        super(Editor, self).__init__(parent)

        self.Item = Painter(theme)
        self.Item.index = index

        self.setMouseTracking(True)



    def sizeHint (self):

        return self.Item.sizeHint()



    def paintEvent (self, event):

        painter = QtGui.QPainter()
        painter.begin(self)

        option = QtWidgets.QStyleOptionViewItem()
        option.rect = self.rect()

        self.Item.paint(
            painter,
            option,
            self.Item.index )

        painter.end()



    def mouseMoveEvent (self, event):

        self.Item.pointer = QtCore.QPoint(
            event.x(),
            event.y())

        self.update()



    def leaveEvent (self, event):

        self.leaveEditor.emit()







class Delegate (QtWidgets.QStyledItemDelegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent)

        self.theme = theme
        self.Item = Painter(theme)



    def paint (self, painter, option, index):

        iconArea = self.parent().rectForIndex(index)

        self.Item.pointer = QtCore.QPoint(
            iconArea.x() ,
            iconArea.y() )

        self.Item.paint(painter, option, index)



    def sizeHint (self, option, index):

        self.Item.index = index
        return  self.Item.sizeHint()



    def createEditor (self, parent, option, index):

        pass



    def setModelData (self, editor, model, index):

        model.setData(
            index,
            index.data(QtCore.Qt.EditRole) )



    def editorEvent (self, event, model, option, index):

        if event.type() == QtCore.QEvent.MouseMove:

            self.parent().setCurrentIndex(index)
            self.parent().edit(index)

        return True



    def leaveAction (self):

        self.setModelData(
            self.sender(),
            self.parent().model(),
            self.sender().Item.index )

        self.closeEditor.emit(
            self.sender(),
            QtWidgets.QAbstractItemDelegate.NoHint )



    def clickAction (self, index):

        self.parent().iconClickedSignal(index)
