#!/usr/bin/env python

"""
"""

from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from widgets import Settings

UIGlobals = Settings.UIGlobals


def clear (function):
    def wrapped (self):
        function(self)
        self.painter.fillRect(
            self.option.rect,
            QtGui.QColor(self.theme.color.browserBackground))
    return wrapped


def label (font):
    def decorated (function):
        def wrapped (self):
            function(self)
            self.painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            self.painter.setPen(QtGui.QPen(
                QtGui.QBrush(QtGui.QColor(self.theme.color.text)),
                0, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            self.painter.setFont(font)
            text = self.data.get("text")
            textOption = QtGui.QTextOption()
            textOption.setWrapMode(QtGui.QTextOption.NoWrap)
            textOption.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.painter.drawText(QtCore.QRectF(self.iconRect), text, textOption)
        return wrapped
    return decorated


def initialize (function):
    def wrapped (self):
        function(self)
        self.iconSize = 1
        with Settings.Manager(self.theme.app, update=False) as settings:
            self.iconSize = settings["iconSize"]
        IconSettings = UIGlobals.Browser.Icon
        labelHeight = IconSettings.Asset.min.label
        if self.iconSize == 2:
            labelHeight = IconSettings.Asset.mid.label
        elif self.iconSize == 3:
            labelHeight = IconSettings.Asset.max.label
        self.previewHeight = self.height - labelHeight - self.space*2
        self.labelArea = QtCore.QRect(
            self.pointX + self.space*2,
            self.pointY + self.height - labelHeight,
            self.width - self.space*4,
            labelHeight - self.space*2)
        self.spaceName = self.labelArea.width()
        self.shiftName = 0
    return wrapped


def checked (function):
    def wrapped (self):
        function(self)
        if self.checked == 1:
            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                QtCore.QRectF(self.iconRect), self.radius, self.radius)
            color = QtGui.QColor(self.theme.color.checkedHighlight)
            pen = QtGui.QPen(
                QtGui.QBrush(color), 4,
                QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            self.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            self.painter.strokePath(outlinePath, pen)
    return wrapped
