#!/usr/bin/env python



from toolbox.ensure.QtCore import *
from toolbox.ensure.QtGui import *




def clear (function):
    def wrapped (self):

        function(self)

        self.painter.fillRect(
            self.option.rect,
            QtGui.QColor(self.theme.color.browserBackground)
        )

    return wrapped





def label (font):
    def decorated (function):
        def wrapped (self):

            function(self)

            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.setPen(
                QtGui.QPen(
                    QtGui.QBrush( QtGui.QColor(self.theme.color.text) ),
                    0,
                    QtCore.Qt.SolidLine,
                    QtCore.Qt.RoundCap,
                    QtCore.Qt.RoundJoin) )

            self.painter.setFont(font)

            text = self.data.get("text")

            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

            self.painter.drawText(
                QtCore.QRectF(self.iconRect),
                text,
                textOption)

        return wrapped
    return decorated
