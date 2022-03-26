#!/usr/bin/env python



import math

import toolbox.core.calculate
import toolbox.core.graphics
import toolbox.core.ui


from toolbox.ensure.QtWidgets import *
from toolbox.ensure.QtCore import *
from toolbox.ensure.QtGui import *
from toolbox.ensure.Signal import *

from . import Settings
UIGlobals = Settings.UIGlobals

WIDTH        = UIGlobals.Options.preferWidth
MARGIN       = UIGlobals.Options.margin
HEIGHT_THICK = UIGlobals.Options.thickHeight







class TextBlock (QtWidgets.QTextEdit):

    loseFocus = Signal()


    def __init__ (self, text):
        super(TextBlock, self).__init__()

        self.setCommentFont(UIGlobals.Options.fontComment)
        self.textChanged.connect(self.skinnySize)

        self.defaultName = text
        self.setPlainText(text)

        self.setPropertyTag("on")
        self.setProperty("textcolor", "dim")


    def setCommentFont (self, font):

        self.fontComment = font
        toolbox.core.ui.setFont(self, font)


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

    statusHover  = Signal(str)


    def __init__ (self, theme):
        super(StatusButton, self).__init__()

        self.theme = theme

        self.setCheckable(True)
        self.setText("")

        space = 4
        self.value = UIGlobals.Options.Status.buttonHeight
        self.setFixedSize(
            QtCore.QSize(self.value+space, self.value))

        self.underPointer  = False
        self.neighbor      = False


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


    def __init__ (self, theme):
        super(Status, self).__init__()

        self.theme = theme

        self.NAME = str()

        self.setMouseTracking(True)
        self.hoverStatus = False
        self.hoverDots   = False

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
            MARGIN
            - (HEIGHT_THICK - labelHeight - textHeight - textOffset)
            - buttonHeight )

        self.setFixedHeight(
            MARGIN
            + HEIGHT_THICK
            + buttonHeight
            + bottomMargin )
        
        self.mainLayout.setContentsMargins(
            0, MARGIN, 0, bottomMargin)

        self.mark = QtWidgets.QWidget()
        self.mark.setFixedWidth(lineWidth)
        self.mark.setFixedHeight(HEIGHT_THICK)

        self.mark.setAutoFillBackground(True)
        self.groupLayout.addWidget(self.mark)
        

        self.statusLayout = QtWidgets.QVBoxLayout()
        self.statusLayout.setContentsMargins(
            MARGIN-lineWidth, 0, MARGIN, 0)
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
        toolbox.core.ui.setFont(
            self.labelStatus,
            fontLabel)
        self.labelStatus.setFixedHeight(labelHeight)
        self.labelLayout.addWidget(self.labelStatus)

        labelSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding ,
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
        toolbox.core.ui.setFont(
            self.nameStatus, fontButton)
        self.nameStatus.setFixedHeight(textHeight)
        self.nameLayout.addWidget(self.nameStatus)

        nameSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding ,
            QtWidgets.QSizePolicy.Minimum   )
        self.nameLayout.addItem(nameSpacer)


        labelGroupSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum   ,
            QtWidgets.QSizePolicy.Expanding )
        self.statusLayout.addItem(labelGroupSpacer)


        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
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
        endIndex   = len(self.buttonList) -1

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
                    buttonLeft  = self.buttonList[index-1]
                    buttonRight = self.buttonList[index+1]
                    buttonLeft.neighbor  = True
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
            statusArea.x()                        ,
            statusArea.y()         + HEIGHT_THICK ,
            statusArea.width()                    ,
            UIGlobals.Options.Status.buttonHeight )
        hoverButtons = buttonArea.contains(pointer)

        if hoverButtons and not self.hoverDots:
            self.hoverDots = True

        elif not hoverButtons and self.hoverDots:
            self.hoverDots = False
            for button in self.buttonList:
                button.neighbor = False
                button.repaint()






class ExportButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(ExportButton, self).__init__()

        self.theme = theme
        
        self.setFixedHeight(HEIGHT_THICK)
        
        self.buttonPressed = False

        self.timerAnimation = QtCore.QTimer(self)
        self.timerAnimation.timeout.connect(self.animation)

        self.offset = 0

        self.timerDelay = QtCore.QTimer(self)
        self.timerDelay.timeout.connect(self.delay)

        self.delayTime  = UIGlobals.Options.Export.delayTime
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

        if self.buttonPressed or self.delayValue >= 0:
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
                buttonRect.x()      + thickness   ,
                buttonRect.y()      + thickness   ,
                buttonRect.width()  - thickness*2 ,
                buttonRect.height() - thickness*2 )

            outlinePath = QtGui.QPainterPath()
            outlinePath.addRoundedRect(
                QtCore.QRectF(shape), radius, radius)

            color = QtGui.QColor(self.theme.color.optionBackground)
            painter.fillPath(outlinePath, QtGui.QBrush(color))


        if self.buttonPressed and disabled or self.delayValue >= 0:

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
                buttonRect.x()      - buttonRect.height()   ,
                buttonRect.y()      - buttonRect.height()   ,
                buttonRect.width()  + buttonRect.height()*2 ,
                buttonRect.height() + buttonRect.height()*2 )

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
        painter.setPen(
            QtGui.QPen(
                QtGui.QBrush( textcolor ),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )

        painter.setFont( UIGlobals.Options.Export.font )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(
            QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
        painter.drawText(
            QtCore.QRectF(buttonRect),
            self.text(),
            textOption)

        painter.end()






class ResizeButton (QtWidgets.QPushButton):

    moveStart = Signal(int)


    def __init__ (self, theme):
        super(ResizeButton, self).__init__()

        self.theme = theme
        self.buttonPressed = False

        self.setFixedWidth(3)
        self.setMaximumHeight(2000)

        self.setCheckable(False)
        self.setText("")

        self.setCursor(
            QtGui.QCursor(QtCore.Qt.SizeHorCursor))

        self.setMouseTracking(True)


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        painter.fillRect(
            self.contentsRect() ,
            QtGui.QColor(self.theme.color.browserBackground) )

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






class SymbolicLink (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(SymbolicLink, self).__init__()

        self.theme = theme
        self.fontText = UIGlobals.Options.fontLink

        self.buttonPressed = False
        self.setCheckable(True)
        self.setText("")

        self.image = QtGui.QImage(":/icons/check.png")
        self.space = 7
        self.text  = "Symbolic Link"

        self.setFixedWidth(
            self.image.width() + self.space
            + toolbox.core.calculate.stringWidth(self.text, self.fontText) )
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
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.violet )
            color = QtGui.QColor(self.theme.color.kicker)
        else:
            image = toolbox.core.graphics.recolor(
                self.image, self.theme.color.optionDisable )
            color = QtGui.QColor(self.theme.color.optionDisable)

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawImage(position, image)


        painter.setPen(
            QtGui.QPen(
                QtGui.QBrush(color),
                0,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin) )
        painter.setFont(self.fontText)

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

        painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        painter.drawText(
            QtCore.QRectF(buttonRect),
            self.text,
            textOption)


        painter.end()
