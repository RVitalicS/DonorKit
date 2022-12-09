#!/usr/bin/env python

"""
"""

import math
from widgets import resources
import toolkit.core.calculate as calculate
import toolkit.core.graphics as graphics
import toolkit.core.ui as uiCommand
from toolkit.core.naming import rule_Input
from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from toolkit.ensure.Signal import *
from widgets.items import PopupDelegate
from widgets import Settings

UIGlobals = Settings.UIGlobals
WIDTH = UIGlobals.Options.preferWidth
MARGIN = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight


class TextBlock (QtWidgets.QTextEdit):
    loseFocus = Signal()

    def __init__ (self, text, parent=None):
        super(TextBlock, self).__init__(parent)
        self.setCommentFont(UIGlobals.Options.fontComment)
        self.textChanged.connect(self.skinnySize)
        self.defaultName = text
        self.setPlainText(text)
        self.setPropertyTag("on")
        self.setProperty("textcolor", "dim")
    
    def setCommentFont (self, font):
        self.fontComment = font
        uiCommand.setFont(self, font)
    
    def setPropertyTag (self, tag):
        self.propertyTag = tag
    
    def get (self):
        text = self.toPlainText()
        if text == self.defaultName:
            text = ""
        return text
    
    def set (self, text):
        self.setPlainText(text)
        self.setProperty("textcolor", self.propertyTag)
        self.setStyleSheet("")
    
    def setDefault (self):
        self.setPlainText(self.defaultName)
        self.setProperty("textcolor", "dim")
        self.setStyleSheet("")
    
    def mousePressEvent (self, event):
        super(TextBlock, self).mousePressEvent(event)
        if self.toPlainText() == self.defaultName:
            self.set("")
    
    def leaveEvent (self, event):
        super(TextBlock, self).leaveEvent(event)
        if not self.toPlainText():
            self.setDefault()
    
    def focusInEvent (self, event):
        super(TextBlock, self).focusInEvent(event)
        if self.toPlainText() == self.defaultName:
            self.set("")
    
    def focusOutEvent (self, event):
        super(TextBlock, self).focusOutEvent(event)
        self.loseFocus.emit()
    
    def skinnySize (self):
        document = self.document()
        document.adjustSize()
        document.setTextWidth(self.width())
        size = document.size().toSize()
        self.setFixedHeight( size.height() )


class StatusButton (QtWidgets.QPushButton):
    statusHover = Signal(str)
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(StatusButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setCheckable(True)
        self.setText("")
        space = 4
        self.value = UIGlobals.Options.Status.buttonHeight
        self.setFixedSize(QtCore.QSize(self.value+space, self.value))
        self.underPointer = False
        self.neighbor = False
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        buttonRect = self.contentsRect()
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.underPointer:
            radius = 10
        elif self.neighbor:
            radius = 6
        else:
            radius = 4
        offset = int((self.value - radius)/2)
        if self.isChecked():
            color = QtGui.QColor(self.theme.color.optionButton)
        else:
            color = QtGui.QColor(self.theme.color.browserSocket)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(color))
        painter.drawEllipse(offset, offset, radius, radius)
        painter.end()
    
    def enterEvent (self, event):
        super(StatusButton, self).enterEvent(event)
        self.underPointer = True
        self.statusHover.emit(self.objectName())
    
    def leaveEvent (self, event):
        super(StatusButton, self).leaveEvent(event)
        self.underPointer = False


class Status (QtWidgets.QWidget):
    clicked = Signal(str)
    
    def __init__ (self, theme, parent=None):
        super(Status, self).__init__(parent)
        self.theme = theme
        self.NAME = str()
        self.setMouseTracking(True)
        self.hoverStatus = False
        self.hoverDots = False
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.groupLayout = QtWidgets.QHBoxLayout()
        self.groupLayout.setSpacing(0)
        self.groupLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.addLayout(self.groupLayout)

        lineWidth = UIGlobals.Options.Status.lineWidth
        fontLabel = UIGlobals.Options.Status.fontLabel
        metrics = QtGui.QFontMetrics(fontLabel)
        labelHeight = metrics.capHeight() + 1
        fontButton = UIGlobals.Options.Status.fontButton
        metrics = QtGui.QFontMetrics(fontButton)
        textHeight = metrics.ascent() + metrics.descent()
        textOffset = 4
        buttonHeight = UIGlobals.Options.Status.buttonHeight
        bottomMargin = (
            MARGIN - (HEIGHT_THICK - labelHeight - textHeight) - buttonHeight)
        self.setFixedHeight(MARGIN + HEIGHT_THICK + buttonHeight + bottomMargin)
        
        self.mainLayout.setContentsMargins(0, MARGIN, 0, bottomMargin)
        self.mark = QtWidgets.QWidget()
        self.mark.setFixedWidth(lineWidth)
        self.mark.setFixedHeight(HEIGHT_THICK)
        self.mark.setAutoFillBackground(True)
        self.groupLayout.addWidget(self.mark)
        
        self.statusLayout = QtWidgets.QVBoxLayout()
        self.statusLayout.setContentsMargins(MARGIN-lineWidth, 0, 0, 0)
        self.statusLayout.setSpacing(textOffset)
        self.groupLayout.addLayout(self.statusLayout)
        self.labelLayout = QtWidgets.QHBoxLayout()
        self.labelLayout.setContentsMargins(0, 0, 0, 0)
        self.labelLayout.setSpacing(0)
        self.labelLayout.setObjectName("labelLayout")
        self.statusLayout.addLayout(self.labelLayout)

        self.labelStatus = QtWidgets.QLabel("STATUS")
        self.labelStatus.setMouseTracking(True)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setProperty("textcolor", "weak")
        uiCommand.setFont(self.labelStatus, fontLabel)
        self.labelStatus.setFixedHeight(labelHeight)
        self.labelLayout.addWidget(self.labelStatus)

        labelSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding ,
            QtWidgets.QSizePolicy.Minimum   )
        self.labelLayout.addItem(labelSpacer)
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.setContentsMargins(0, 0, 0, 0)
        self.nameLayout.setSpacing(0)
        self.statusLayout.addLayout(self.nameLayout)

        self.nameStatus = QtWidgets.QLabel(self.NAME)
        self.nameStatus.setMouseTracking(True)
        self.nameStatus.setObjectName("nameStatus")
        self.nameStatus.setProperty("textcolor", "kicker")
        uiCommand.setFont(self.nameStatus, fontButton)
        self.nameStatus.setFixedHeight(textHeight)
        self.nameLayout.addWidget(self.nameStatus)
        nameSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding ,
            QtWidgets.QSizePolicy.Minimum   )
        self.nameLayout.addItem(nameSpacer)
        labelGroupSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum   ,
            QtWidgets.QSizePolicy.Expanding )
        self.statusLayout.addItem(labelGroupSpacer)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setContentsMargins(
            MARGIN + UIGlobals.Options.Maya.width, 0, 0, 0)
        self.buttonLayout.setSpacing(0)
        self.mainLayout.addLayout(self.buttonLayout)
        buttonSpacer = QtWidgets.QSpacerItem(
            0, buttonHeight,
            QtWidgets.QSizePolicy.Expanding ,
            QtWidgets.QSizePolicy.Minimum   )
        self.buttonLayout.addItem(buttonSpacer)
        self.buttonList = []

        for name in Settings.STATUS_LIST:
            self.NAME = name
            button = StatusButton(theme)
            button.setMouseTracking(True)
            button.setObjectName(name)
            button.hide()
            button.statusHover.connect(self.statusHover)
            button.pressed.connect(self.uncheckButtons)
            button.released.connect(self.checkButton)
            self.buttonList.append(button)
            self.buttonLayout.addWidget(button)
        self.set()

        buttonSpacer = QtWidgets.QSpacerItem(
            0, buttonHeight,
            QtWidgets.QSizePolicy.Expanding ,
            QtWidgets.QSizePolicy.Minimum   )
        self.buttonLayout.addItem(buttonSpacer)
        self.setLayout(self.mainLayout)
    
    def statusHover (self, text):
        startIndex = 0
        endIndex = len(self.buttonList) -1
        neighbor = None
        for button in self.buttonList:
            index = self.buttonList.index(button)
            if index != neighbor:
                button.neighbor = False
            if button.objectName() == text:
                if index == startIndex:
                    buttonRight = self.buttonList[index+1]
                    buttonRight.neighbor = True
                    neighbor = index+1
                elif index == endIndex:
                    buttonLeft = self.buttonList[index-1]
                    buttonLeft.neighbor = True
                else:
                    buttonLeft = self.buttonList[index-1]
                    buttonRight = self.buttonList[index+1]
                    buttonLeft.neighbor = True
                    buttonRight.neighbor = True
                    neighbor = index+1
            else:
                button.underPointer = False
        self.nameStatus.setText(text)
        self.setColor(status=text)
        self.repaint()
    
    def set (self, status="WIP"):
        self.uncheckButtons()
        self.NAME = status
        self.nameStatus.setText(status)
        self.setColor()
        self.checkButton()
    
    def get (self):
        return self.NAME
    
    def uncheckButtons (self):
        for button in self.buttonList:
            if button.isDown():
                self.NAME = button.objectName()
            button.setChecked(False)
        self.setColor()
    
    def checkButton (self):
        for button in self.buttonList:
            if button.objectName() == self.NAME:
                button.setChecked(True)
                break
        if self.hoverStatus:
            self.clicked.emit(self.NAME)
    
    def setColor(self, status=""):
        if not status:
            status = self.NAME
        color = self.theme.color.statusWIP
        if status == "Final":
            color = self.theme.color.statusFinal
        elif status == "Completed":
            color = self.theme.color.statusCompleted
        elif status == "Revise":
            color = self.theme.color.statusRevise
        elif status == "Pending Review":
            color = self.theme.color.statusPendingReview
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(color) )
        self.mark.setPalette(palette)
    
    def mouseMoveEvent (self, event):
        super(Status, self).mouseMoveEvent(event)
        pointer = QtCore.QPoint(event.x(), event.y())
        statusArea = QtCore.QRect(
            self.contentsRect().x() + MARGIN,
            self.contentsRect().y() + MARGIN,
            self.contentsRect().width() - MARGIN*2,
            HEIGHT_THICK + UIGlobals.Options.Status.buttonHeight)
        hoverWidget = statusArea.contains(pointer)
        labelWidth = self.nameStatus.width()
        if labelWidth < self.labelStatus.width():
            labelWidth = self.labelStatus.width()
        labelArea = QtCore.QRect(
            statusArea.x(),
            statusArea.y(),
            labelWidth,
            HEIGHT_THICK)
        hoverLabel = labelArea.contains(pointer)
        if hoverLabel and not self.hoverStatus:
            self.hoverStatus = True
            for button in self.buttonList:
                button.show()
        elif not hoverWidget and self.hoverStatus:
            self.hoverStatus = False
            for button in self.buttonList:
                button.hide()
            self.set(status=self.NAME)
        buttonArea = QtCore.QRect(
            statusArea.x(),
            statusArea.y() + HEIGHT_THICK,
            statusArea.width(),
            UIGlobals.Options.Status.buttonHeight)
        hoverButtons = buttonArea.contains(pointer)
        if hoverButtons and not self.hoverDots:
            self.hoverDots = True
        elif not hoverButtons and self.hoverDots:
            self.hoverDots = False
            for button in self.buttonList:
                button.neighbor = False
                button.repaint()


class MayaButton (QtWidgets.QPushButton):
    stateChanged = Signal()

    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(MayaButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setFixedSize(QtCore.QSize(
            UIGlobals.Options.Maya.width,
            UIGlobals.Options.Maya.height))
        self.icon = QtGui.QImage(":/icons/maya.png")
        self.checked = False
    
    def mousePressEvent (self, event):
        super(MayaButton, self).mousePressEvent(event)
        self.checked = not self.checked
        self.repaint()
        self.stateChanged.emit()
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() ,
            buttonRect.y() )
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.checked:
            image = self.icon
        else:
            image = graphics.recolor(
                self.icon.copy(),
                self.theme.color.optionDisable,
                opacity=0.75)
        painter.drawImage(position, image)
        painter.end()


class ExportButton (QtWidgets.QPushButton):

    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(ExportButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setFixedHeight(HEIGHT_THICK)
        self.buttonPressed = False
        self.setProperty("state", "disabled")
        self.timerAnimation = QtCore.QTimer(self)
        self.timerAnimation.timeout.connect(self.animation)
        self.offset = 0
        self.timerDelay = QtCore.QTimer(self)
        self.timerDelay.timeout.connect(self.delay)
        self.delayTime = UIGlobals.Options.Export.delayTime
        self.delayValue = -1
        self.patternThickness = UIGlobals.Options.Export.patternThickness
        self.patternStep = int(round(
            (self.patternThickness/math.cos(45))*1.5 ))
    
    def delay (self):
        self.delayValue += 1
        if self.delayValue == self.delayTime:
            self.delayValue = -1
            self.offset = 0
            self.timerAnimation.stop()
            self.timerDelay.stop()
            self.clearFocus()
        self.repaint()
    
    def animation (self):
        self.offset += 1
        if self.offset == self.patternStep:
            self.offset = 0
        self.repaint()
    
    def mousePressEvent (self, event):
        super(ExportButton, self).mousePressEvent(event)
        self.buttonPressed = True
        if self.property("state") != "enabled":
            self.timerAnimation.start(100)
        else:
            self.repaint()
    
    def mouseReleaseEvent (self, event):
        super(ExportButton, self).mousePressEvent(event)
        self.buttonPressed = False
        if self.property("state") != "enabled":
            self.delayValue = 0
            self.timerDelay.start(self.delayTime)
        else:
            self.repaint()
            self.clearFocus()
    
    def enterEvent (self, event):
        super(ExportButton, self).enterEvent(event)
        self.delayValue = -1
        self.offset = 0
        self.timerAnimation.stop()
        self.timerDelay.stop()
        self.setFocus(QtCore.Qt.MouseFocusReason)
        self.repaint()
    
    def paintEvent (self, event):
        disabled = self.property("state") != "enabled"
        exportState = (self.buttonPressed or self.delayValue >= 0)
        errorState = (self.buttonPressed and disabled or self.delayValue >= 0)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        buttonRect = self.contentsRect()
        radius = 3
        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(
            QtCore.QRectF(buttonRect),
            radius, radius,
            mode=QtCore.Qt.AbsoluteSize)
        painter.setClipPath(clipPath)
        
        if exportState:
            textcolor = QtGui.QColor(self.theme.color.white)
            if disabled or self.delayValue >= 0:
                backgroundcolor = QtGui.QColor(self.theme.color.exportLocked)
            else:
                backgroundcolor = QtGui.QColor(self.theme.color.black)
            painter.fillRect(buttonRect, backgroundcolor)
        else:
            textcolor = QtGui.QColor(self.theme.color.text)
            backgroundcolor = QtGui.QColor(self.theme.color.optionLine)
            painter.fillRect(buttonRect, backgroundcolor)
            thickness = 1
            shape = QtCore.QRect(
                buttonRect.x() + thickness,
                buttonRect.y() + thickness,
                buttonRect.width() - thickness*2,
                buttonRect.height() - thickness*2)
            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                QtCore.QRectF(shape), radius, radius)
            color = QtGui.QColor(self.theme.color.optionBackground)
            painter.fillPath(outlinePath, QtGui.QBrush(color))
        
        if errorState:
            brush = QtGui.QBrush(
                backgroundcolor.darker(108),
                QtCore.Qt.SolidPattern)
            pen = QtGui.QPen(
                brush, self.patternThickness,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin)
            painter.setBrush(brush)
            painter.setPen(pen)
            patternRect = QtCore.QRect(
                buttonRect.x() - buttonRect.height(),
                buttonRect.y() - buttonRect.height(),
                buttonRect.width() + buttonRect.height()*2,
                buttonRect.height() + buttonRect.height()*2)
            stepSum = 0
            
            while stepSum < patternRect.width():
                
                xStart = stepSum
                yStart = patternRect.y()
                xEnd = stepSum - patternRect.height()
                yEnd = yStart + patternRect.height()
                painter.drawLine(
                    self.offset + xStart, yStart,
                    self.offset + xEnd,   yEnd)
                stepSum += self.patternStep
        
        # TEXT
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.setPen(QtGui.QPen(
            QtGui.QBrush(textcolor), 0, QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setFont( UIGlobals.Options.Export.font )
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        painter.drawText(QtCore.QRectF(buttonRect), self.text(), textOption)
        painter.end()


class ResizeButton (QtWidgets.QPushButton):
    moveStart = Signal(int)
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(ResizeButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.buttonPressed = False
        self.setFixedWidth(3)
        self.setMaximumHeight(2000)
        self.setCheckable(False)
        self.setText("")
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        self.setMouseTracking(True)
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.fillRect(self.contentsRect(), QtGui.QColor(self.theme.color.browserBackground))
        painter.end()
    
    def mousePressEvent (self, event):
        super(ResizeButton, self).mousePressEvent(event)
        self.buttonPressed = True
    
    def mouseReleaseEvent (self, event):
        super(ResizeButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
    
    def mouseMoveEvent (self, event):
        super(ResizeButton, self).mouseMoveEvent(event)
        if self.buttonPressed:
            moved = self.mapToParent(QtCore.QPoint(event.x(), 0))
            self.moveStart.emit( moved.x() )
    
    def enterEvent (self, event):
        super(ResizeButton, self).enterEvent(event)
    
    def leaveEvent (self, event):
        super(ResizeButton, self).leaveEvent(event)
        self.buttonPressed = False


class LinkToken (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(LinkToken, self).__init__(icon, text, parent)
        self.theme = theme
        self.fontText = UIGlobals.Options.fontLink
        self.buttonPressed = False
        self.setCheckable(True)
        self.setText("")
        self.image = QtGui.QImage(":/icons/check.png")
        self.space = 7
        self.text = "Symbolic Link"
        self.setFixedWidth(
            self.image.width() + self.space
            + calculate.stringWidth(self.text, self.fontText) )
        self.setFixedHeight(self.image.height())
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() ,
            buttonRect.y() )
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.isChecked():
            image = graphics.recolor(
                self.image, self.theme.color.violet )
            color = QtGui.QColor(self.theme.color.kicker)
        else:
            image = graphics.recolor(self.image, self.theme.color.optionDisable)
            color = QtGui.QColor(self.theme.color.optionDisable)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawImage(position, image)
        painter.setPen(QtGui.QPen(
            QtGui.QBrush(color), 0, QtCore.Qt.SolidLine,
            QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.setFont(self.fontText)
        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.drawText(QtCore.QRectF(buttonRect), self.text, textOption)
        painter.end()


class LinkButton (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(LinkButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setCheckable(True)
        self.setText("")
        self.image = QtGui.QImage(":/icons/linkchain.png")
        self.setFixedSize(QtCore.QSize(
            self.image.width(), UIGlobals.Options.buttonHeight ))
        self.buttonPressed = False
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x(), (buttonRect.y() + int((UIGlobals.Options.buttonHeight - self.image.height())/2)) )
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.isChecked():
            if self.property("overwrite") == "true":
                image = graphics.recolor(self.image, self.theme.color.violet)
            else:
                image = graphics.recolor(self.image, self.theme.color.optionButton)
        else:
            image = graphics.recolor(self.image, self.theme.color.browserSocket)
        painter.drawImage(position, image)
        painter.end()
    
    def mousePressEvent (self, event):
        super(LinkButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()
    
    def mouseReleaseEvent (self, event):
        super(LinkButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()
    
    def enterEvent (self, event):
        super(LinkButton, self).enterEvent(event)
    
    def leaveEvent (self, event):
        super(LinkButton, self).leaveEvent(event)
        self.buttonPressed = False


class NameEdit (QtWidgets.QLineEdit):
    
    def __init__ (self, parent=None):
        super(NameEdit, self).__init__(parent)
        self.setFixedHeight(HEIGHT_THICK)
        self.defaultName = "Name"
        self.setText(self.defaultName)
        self.errorVisible = False
        self.errorName = "{ name }"
    
    def showError (self, flag):
        self.errorVisible = flag
        if flag:
            self.setText(self.errorName)
    
    def setName (self, text):
        if text == self.errorName:
            pass
        elif text != self.defaultName:
            text = rule_Input(text)
            self.setText(text)
        return text
    
    def mousePressEvent (self, event):
        super(NameEdit, self).mousePressEvent(event)
        if self.text() == self.defaultName:
            self.setText("")
        elif self.text() == self.errorName:
            self.setText("")
    
    def leaveEvent (self, event):
        super(NameEdit, self).leaveEvent(event)
        if not self.text() and not self.errorVisible:
            self.setText(self.defaultName)
        elif not self.text() and self.errorVisible:
            self.setText(self.errorName)


class Line (QtWidgets.QWidget):

    def __init__ (self, theme, parent=None):
        super(Line, self).__init__(parent)
        self.setFixedHeight(1)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            QtGui.QColor(theme.color.optionLine) )
        self.setPalette(palette)


class FlatComboBox (QtWidgets.QComboBox):
    selectionChanged = Signal(str)

    def __init__ (self, theme, parent=None):
        super(FlatComboBox, self).__init__(parent)
        self.errorVisible = False
        self.errorName = "{ name }"
        self.underPointer = False
        self.fontValue = UIGlobals.Options.fontLabel
        uiCommand.setFont(self, self.fontValue)
        self.setEditable(True)
        self.setFrame(False)
        self.setMaxVisibleItems(10)
        self.setMaxCount(100)
        self.setContentsMargins(0,0,0,0)
        self.lineEdit().setContentsMargins(0,0,0,0)
        self.lineEdit().setTextMargins(-2,0,-2,0)
        self.lineEdit().cursorPositionChanged.connect(self.inputEnter)
        self.setItemDelegate(
            PopupDelegate.Delegate(self.view(), theme) )
        self.editTextChanged.connect(self.textFilter)
        self.stealth = False
        self.currentTextChanged.connect(self.selectionAction)
    
    def selectionAction (self, text):
        if not self.stealth:
            self.selectionChanged.emit(text)
    
    def showError (self, flag):
        self.errorVisible = flag
        if flag and not self.currentText():
            self.setEditText(self.errorName)
    
    def showPopup (self):
        super(FlatComboBox, self).showPopup()
        point = QtCore.QPoint(
            self.contentsRect().x(),
            self.contentsRect().y())
        point = self.mapToGlobal(point)
        popup = self.findChild(QtWidgets.QFrame)
        popup.move(popup.x(), point.y())
    
    def getName (self):
        name = self.currentText()
        if name == self.errorName:
            return ""
        else:
            return name
    
    def notSet (self):
        if self.currentText() == "":
            return True
        if self.currentText() == self.errorName:
            return True
        return False
    
    def changeEvent (self, event):
        super(FlatComboBox, self).changeEvent(event)
        if self.lineEdit():
            widthLabel = 0
            widthButton = 20
            if self.lineEdit().text():
                widthLabel = calculate.stringWidth(
                    self.lineEdit().text().replace(" ", "_"),
                    self.fontValue )
            self.setMinimumWidth(widthLabel+widthButton)
        if not self.underPointer and self.errorVisible:
            if not self.currentText():
                self.setEditText(self.errorName)
    
    def textFilter (self, text):
        if text != self.errorName:
            text = rule_Input(text)
            self.setEditText(text)
    
    def leaveEvent (self, event):
        super(FlatComboBox, self).leaveEvent(event)
        self.lineEdit().setCursorPosition(0)
        self.underPointer = False
        if not self.currentText() and self.errorVisible:
            self.setEditText(self.errorName)
        self.clearFocus()
    
    def enterEvent (self, event):
        super(FlatComboBox, self).enterEvent(event)
        self.underPointer = True
    
    def inputEnter (self, oldPos, newPos):
        if self.underPointer:
            if self.currentText() == self.errorName:
                self.setEditText("")


class DropdownButton (QtWidgets.QPushButton):
    
    def __init__ (self, theme, icon=None, text=None, parent=None):
        super(DropdownButton, self).__init__(icon, text, parent)
        self.theme = theme
        self.setCheckable(False)
        self.setText("")
        self.image = QtGui.QImage(":/icons/dropdown.png")
        self.value = UIGlobals.Options.buttonHeight
        self.setFixedSize(QtCore.QSize(self.value, self.value))
        self.buttonPressed = False
    
    def paintEvent (self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        buttonRect = self.contentsRect()
        position = QtCore.QPoint(
            buttonRect.x() + int((self.value-self.image.width() )/2),
            buttonRect.y() + int((self.value-self.image.height())/2))
        color = QtGui.QColor(self.theme.color.optionBackground)
        painter.fillRect(buttonRect, color)
        if self.buttonPressed:
            image = graphics.recolor(self.image, self.theme.color.white)
        else:
            image = graphics.recolor(self.image, self.theme.color.optionButton)
        painter.drawImage(position, image)
        painter.end()
    
    def mousePressEvent (self, event):
        super(DropdownButton, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()
    
    def mouseReleaseEvent (self, event):
        super(DropdownButton, self).mouseReleaseEvent(event)
        self.buttonPressed = False
        self.repaint()
    
    def enterEvent (self, event):
        super(DropdownButton, self).enterEvent(event)
    
    def leaveEvent (self, event):
        super(DropdownButton, self).leaveEvent(event)
        self.buttonPressed = False


class VersionBlock (QtWidgets.QWidget):

    def __init__ (self, theme, parent=None):
        super(VersionBlock, self).__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.versionLayout = QtWidgets.QHBoxLayout()
        self.versionLayout.setContentsMargins(0, 20, 0, 0)
        self.versionLayout.setSpacing(10)
        self.versionLayout.setObjectName("versionLayout")
        self.versionLabel = QtWidgets.QLabel("Version")
        self.versionLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 24))
        uiCommand.setFont(self.versionLabel, UIGlobals.Options.fontLabel)
        self.versionLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setProperty("textcolor", "on")
        self.versionLayout.addWidget(self.versionLabel)

        self.versionDropdown = DropdownButton(theme)
        self.versionDropdown.pressed.connect(self.showVersions)
        self.versionLayout.addWidget(self.versionDropdown)

        self.versionCombobox = FlatComboBox(theme)
        self.versionLayout.addWidget(self.versionCombobox)
        versionSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.versionLayout.addItem(versionSpacer)

        self.linkButton = LinkButton(theme)
        self.versionLayout.addWidget(self.linkButton)
        self.mainLayout.addLayout(self.versionLayout)
        self.variantLayout = QtWidgets.QHBoxLayout()
        self.variantLayout.setContentsMargins(0, 0, 0, 0)
        self.variantLayout.setSpacing(10)
        self.variantLayout.setObjectName("variantLayout")
        self.mainLayout.addLayout(self.variantLayout)
        self.variantLabel = QtWidgets.QLabel("Variant")
        self.variantLabel.setFixedSize(
            QtCore.QSize(UIGlobals.Options.labelWidth, 24))
        uiCommand.setFont(self.variantLabel, UIGlobals.Options.fontLabel)
        self.variantLabel.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.variantLabel.setObjectName("variantLabel")
        self.variantLabel.setProperty("textcolor", "on")
        self.variantLayout.addWidget(self.variantLabel)

        self.variantDropdown = DropdownButton(theme)
        self.variantDropdown.pressed.connect(self.showVariant)
        self.variantLayout.addWidget(self.variantDropdown)
        
        self.variantCombobox = FlatComboBox(theme)
        self.variantLayout.addWidget(self.variantCombobox)
        variantSpacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.variantLayout.addItem(variantSpacer)
    
        self.setLayout(self.mainLayout)
    
    def showVariant (self):
        self.variantCombobox.showPopup()
    
    def showVersions (self):
        self.versionCombobox.showPopup()
