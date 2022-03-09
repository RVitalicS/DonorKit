#!/usr/bin/env python



from Qt import QtCore, QtGui

from . import Settings
UIGlobals = Settings.UIGlobals







class Item (object):


    def __init__ (self, theme):

        self.theme = theme
        self.index = QtCore.QModelIndex()
        
        self.pointer  = QtCore.QPoint(-1, -1)



    def sizeHint (self):

        model = self.index.model()
        raw = self.index.row()
        item = model.item(raw)

        size = item.sizeHint()
        size.setHeight(24)

        return size



    def paint (self, painter, option, index):

        colorText = self.theme.text
        colorBackground = self.theme.browserHandleSocket
        if option.rect.contains(self.pointer):
            colorText = self.theme.white
            colorBackground = self.theme.black

        painter.fillRect(
            option.rect, QtGui.QColor(colorBackground) )

        space = UIGlobals.IconDelegate.space
        width  = option.rect.width()
        height = option.rect.height()
        pointX = option.rect.x()
        pointY = option.rect.y()

        nameRect = QtCore.QRect(
            pointX + space   ,
            pointY                ,
            width  - space*2 ,
            height                )

        painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( QtGui.QColor(colorText) ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        font = UIGlobals.Bar.fontBookmark
        painter.setFont(font)

        text = index.data(QtCore.Qt.EditRole)

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.drawText(
            QtCore.QRectF(nameRect),
            text,
            textOption)
