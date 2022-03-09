#!/usr/bin/env python



import math
from . import tools


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIGlobals = Settings.UIGlobals

WIDTH       = UIGlobals.Options.width
MARGIN      = UIGlobals.Options.margin
HIGHT_THICK = UIGlobals.Options.thickHight







class NameEdit (QtWidgets.QLineEdit):


    def __init__ (self, text):
        super(NameEdit, self).__init__()

        self.setMinimumWidth(WIDTH)
        self.setMaximumWidth(WIDTH)
        self.setMinimumHeight(HIGHT_THICK)
        self.setMaximumHeight(HIGHT_THICK)

        self.defaultName = text
        self.setText(text)


    def mousePressEvent (self, event):
        super(NameEdit, self).mousePressEvent(event)

        if self.text() == self.defaultName:
            self.setText("")


    def leaveEvent (self, event):
        super(NameEdit, self).leaveEvent(event)

        if not self.text():
            self.setText(self.defaultName)
        





class ExportButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(ExportButton, self).__init__()

        self.theme = theme

        self.setMinimumWidth(WIDTH)
        self.setMaximumWidth(WIDTH)
        self.setMinimumHeight(HIGHT_THICK)
        self.setMaximumHeight(HIGHT_THICK)
        
        self.buttonPressed = False

        self.timerAnimation = QtCore.QTimer(self)
        self.timerAnimation.timeout.connect(self.animation)

        self.offset = 0

        self.timerDelay = QtCore.QTimer(self)
        self.timerDelay.timeout.connect(self.delay)

        self.delayTime  = 35
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

        clipPath = QtGui.QPainterPath()
        clipPath.addRoundedRect(
            buttonRect.x()     , buttonRect.y()      ,
            buttonRect.width() , buttonRect.height() ,
            4, 4,
            mode=QtCore.Qt.AbsoluteSize              )

        painter.setClipPath(clipPath)

        if self.buttonPressed or self.delayValue >= 0:
            textcolor = QtGui.QColor(self.theme.white)
            if disabled or self.delayValue >= 0:
                backgroundcolor = QtGui.QColor(self.theme.exportLocked)
            else:
                backgroundcolor = QtGui.QColor(self.theme.black)
        else:
            textcolor = QtGui.QColor(self.theme.text)
            backgroundcolor = QtGui.QColor(self.theme.optionButton)

        painter.fillRect(buttonRect, backgroundcolor)

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
            "Export",
            textOption)

        painter.end()
        





class OptionComboBox (QtWidgets.QComboBox):


    def __init__ (self, theme):
        super(OptionComboBox, self).__init__()

        self.theme = theme
        self.image = QtGui.QImage(":/icons/dropdown.png")

        self.buttonPressed = False


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()

        offsetY = int((buttonRect.height() - self.image.height())/2)
        offsetX = buttonRect.width()  - self.image.width() - offsetY
        position = QtCore.QPoint(
            buttonRect.x() + offsetX ,
            buttonRect.y() + offsetY )

        color = QtGui.QColor(self.theme.optionInput)
        painter.fillRect(buttonRect, color)

        if self.buttonPressed:
            image = tools.recolor(self.image, self.theme.white)
        else:
            image = tools.recolor(self.image, self.theme.spinboxArrow)
            
        painter.drawImage(position, image)
        painter.end()


    def mousePressEvent (self, event):
        super(OptionComboBox, self).mousePressEvent(event)
        self.buttonPressed = True
        self.repaint()

    def mouseReleaseEvent (self, event):
        super(OptionComboBox, self).mousePressEvent(event)
        self.buttonPressed = False
        self.repaint()
        self.clearFocus()

    def leaveEvent (self, event):
        super(OptionComboBox, self).leaveEvent(event)
        self.buttonPressed = False
        





class AnimationOpions (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(AnimationOpions, self).__init__()

        self.setMinimumWidth(WIDTH)
        self.setMaximumWidth(WIDTH)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.animationNameLayout = QtWidgets.QHBoxLayout()
        self.animationNameLayout.setContentsMargins(0, 0, 0, 0)
        self.animationNameLayout.setSpacing(10)
        self.animationNameLayout.setObjectName("animationNameLayout")
        self.animationNameLabel = QtWidgets.QLabel()
        self.animationNameLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.animationNameLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.animationNameLabel.setFont(UIGlobals.Options.fontLabel)
        self.animationNameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.animationNameLabel.setObjectName("animationNameLabel")
        self.animationNameLabel.setProperty("textcolor", "on")
        self.animationNameLayout.addWidget(self.animationNameLabel)

        self.animationNameCombobox = OptionComboBox(theme)
        self.animationNameCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.animationNameCombobox.setFont(UIGlobals.Options.fontLabel)
        self.animationNameCombobox.setToolTip("")
        self.animationNameCombobox.setStatusTip("")
        self.animationNameCombobox.setWhatsThis("")
        self.animationNameCombobox.setAccessibleName("")
        self.animationNameCombobox.setAccessibleDescription("")
        self.animationNameCombobox.setEditable(True)
        self.animationNameCombobox.setMaxVisibleItems(10)
        self.animationNameCombobox.setMaxCount(100)
        self.animationNameCombobox.setFrame(False)
        self.animationNameCombobox.setObjectName("animationNameCombobox")
        self.animationNameLayout.addWidget(self.animationNameCombobox)

        self.mainLayout.addLayout(self.animationNameLayout)

        self.animationRangeLayout = QtWidgets.QHBoxLayout()
        self.animationRangeLayout.setContentsMargins(0, 0, 0, 0)
        self.animationRangeLayout.setSpacing(10)
        self.animationRangeLayout.setObjectName("animationRangeLayout")
        self.animationRangeLabel = QtWidgets.QLabel()
        self.animationRangeLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.animationRangeLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.animationRangeLabel.setFont(UIGlobals.Options.fontLabel)
        self.animationRangeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.animationRangeLabel.setObjectName("animationRangeLabel")
        self.animationRangeLabel.setProperty("textcolor", "on")
        self.animationRangeLayout.addWidget(self.animationRangeLabel)

        self.rangeGroupLayout = QtWidgets.QHBoxLayout()
        self.rangeGroupLayout.setSpacing(2)
        self.rangeGroupLayout.setObjectName("rangeGroupLayout")
        self.rangeStartSpinbox = QtWidgets.QSpinBox()
        self.rangeStartSpinbox.setMinimumSize(QtCore.QSize(50, 18))
        self.rangeStartSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.rangeStartSpinbox.setMinimum(0)
        self.rangeStartSpinbox.setMaximum(99999)
        self.rangeStartSpinbox.setFont(UIGlobals.Options.fontLabel)
        self.rangeStartSpinbox.setToolTip("")
        self.rangeStartSpinbox.setStatusTip("")
        self.rangeStartSpinbox.setWhatsThis("")
        self.rangeStartSpinbox.setAccessibleName("")
        self.rangeStartSpinbox.setAccessibleDescription("")
        self.rangeStartSpinbox.setWrapping(False)
        self.rangeStartSpinbox.setFrame(True)
        self.rangeStartSpinbox.setReadOnly(False)
        self.rangeStartSpinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.rangeStartSpinbox.setSpecialValueText("")
        self.rangeStartSpinbox.setSuffix("")
        self.rangeStartSpinbox.setPrefix("")
        self.rangeStartSpinbox.setProperty("value", 1)
        self.rangeStartSpinbox.setObjectName("rangeFromSpinbox")
        self.rangeStartSpinbox.setProperty("background", "input")
        self.rangeStartSpinbox.setProperty("border", "none")
        self.rangeStartSpinbox.setProperty("textcolor", "on")
        self.rangeGroupLayout.addWidget(self.rangeStartSpinbox)

        self.rangeEndSpinbox = QtWidgets.QSpinBox()
        self.rangeEndSpinbox.setMinimumSize(QtCore.QSize(50, 18))
        self.rangeEndSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.rangeEndSpinbox.setMinimum(0)
        self.rangeEndSpinbox.setMaximum(99999)
        self.rangeEndSpinbox.setFont(UIGlobals.Options.fontLabel)
        self.rangeEndSpinbox.setToolTip("")
        self.rangeEndSpinbox.setStatusTip("")
        self.rangeEndSpinbox.setWhatsThis("")
        self.rangeEndSpinbox.setAccessibleName("")
        self.rangeEndSpinbox.setAccessibleDescription("")
        self.rangeEndSpinbox.setWrapping(False)
        self.rangeEndSpinbox.setFrame(True)
        self.rangeEndSpinbox.setReadOnly(False)
        self.rangeEndSpinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.rangeEndSpinbox.setSpecialValueText("")
        self.rangeEndSpinbox.setSuffix("")
        self.rangeEndSpinbox.setPrefix("")
        self.rangeEndSpinbox.setProperty("value", 1)
        self.rangeEndSpinbox.setObjectName("rangeToSpinbox")
        self.rangeEndSpinbox.setProperty("background", "input")
        self.rangeEndSpinbox.setProperty("border", "none")
        self.rangeEndSpinbox.setProperty("textcolor", "on")
        self.rangeGroupLayout.addWidget(self.rangeEndSpinbox)

        rangeSpacer = QtWidgets.QSpacerItem(6, 6, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.rangeGroupLayout.addItem(rangeSpacer)
        self.rangeButton = QtWidgets.QPushButton()
        self.rangeButton.setMinimumSize(QtCore.QSize(36, 18))
        self.rangeButton.setMaximumSize(QtCore.QSize(36, 18))
        self.rangeButton.setFont(UIGlobals.Options.fontLabel)
        self.rangeButton.setFlat(False)
        self.rangeButton.setObjectName("rangeButton")
        self.rangeGroupLayout.addWidget(self.rangeButton)

        self.animationRangeLayout.addLayout(self.rangeGroupLayout)
        self.mainLayout.addLayout(self.animationRangeLayout)

        self.setLayout(self.mainLayout)

        self.animationNameLabel.setText("name")
        self.animationRangeLabel.setText("range")
        self.rangeButton.setText("get")
        





class MainOpions (QtWidgets.QWidget):

    def __init__ (self, theme):
        super(MainOpions, self).__init__()

        self.setMinimumWidth(WIDTH)
        self.setMaximumWidth(WIDTH)


        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)


        self.variantLayout = QtWidgets.QHBoxLayout()
        self.variantLayout.setContentsMargins(0, 20, 0, 0)
        self.variantLayout.setSpacing(10)
        self.variantLayout.setObjectName("variantLayout")
        self.variantLabel = QtWidgets.QLabel()
        self.variantLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.variantLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.variantLabel.setFont(UIGlobals.Options.fontLabel)
        self.variantLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.variantLabel.setObjectName("variantLabel")
        self.variantLabel.setProperty("textcolor", "on")
        self.variantLayout.addWidget(self.variantLabel)

        self.variantCombobox = OptionComboBox(theme)
        self.variantCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.variantCombobox.setFont(UIGlobals.Options.fontLabel)
        self.variantCombobox.setToolTip("")
        self.variantCombobox.setStatusTip("")
        self.variantCombobox.setWhatsThis("")
        self.variantCombobox.setAccessibleName("")
        self.variantCombobox.setAccessibleDescription("")
        self.variantCombobox.setEditable(True)
        self.variantCombobox.setCurrentText("")
        self.variantCombobox.setMaxVisibleItems(10)
        self.variantCombobox.setMaxCount(100)
        self.variantCombobox.setFrame(False)
        self.variantCombobox.setObjectName("variantCombobox")
        self.variantCombobox.setProperty("textcolor", "on")
        self.variantLayout.addWidget(self.variantCombobox)

        self.mainLayout.addLayout(self.variantLayout)
        self.versionLayout = QtWidgets.QHBoxLayout()
        self.versionLayout.setContentsMargins(0, 0, 0, 0)
        self.versionLayout.setSpacing(10)
        self.versionLayout.setObjectName("versionLayout")

        self.versionLabel = QtWidgets.QLabel()
        self.versionLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.versionLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.versionLabel.setFont(UIGlobals.Options.fontLabel)
        self.versionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setProperty("textcolor", "on")
        self.versionLayout.addWidget(self.versionLabel)

        self.linkLayout = QtWidgets.QHBoxLayout()
        self.linkLayout.setContentsMargins(0, 0, 0, 0)
        self.linkLayout.setSpacing(0)
        self.linkLayout.setObjectName("linkLayout")
        self.versionLayout.addLayout(self.linkLayout)

        self.versionCombobox = OptionComboBox(theme)
        self.versionCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.versionCombobox.setFont(UIGlobals.Options.fontLabel)
        self.versionCombobox.setToolTip("")
        self.versionCombobox.setStatusTip("")
        self.versionCombobox.setWhatsThis("")
        self.versionCombobox.setAccessibleName("")
        self.versionCombobox.setAccessibleDescription("")
        self.versionCombobox.setEditable(True)
        self.versionCombobox.setCurrentText("")
        self.versionCombobox.setMaxVisibleItems(10)
        self.versionCombobox.setMaxCount(100)
        self.versionCombobox.setFrame(False)
        self.versionCombobox.setObjectName("versionCombobox")
        self.linkLayout.addWidget(self.versionCombobox)

        self.linkButton = QtWidgets.QPushButton()
        self.linkButton.setMinimumSize(QtCore.QSize(36, 18))
        self.linkButton.setMaximumSize(QtCore.QSize(36, 18))
        self.linkButton.setFont(UIGlobals.Options.fontLabel)
        self.linkButton.setCheckable(True)
        self.linkButton.setFlat(True)
        self.linkButton.setObjectName("linkButton")
        self.linkLayout.addWidget(self.linkButton)

        self.mainLayout.addLayout(self.versionLayout)
        
        self.setLayout(self.mainLayout)

        self.variantLabel.setText("Variant")
        self.versionLabel.setText("Version")
        self.linkButton.setText("link")






class CommentEdit (QtWidgets.QTextEdit):


    def __init__ (self, text):
        super(CommentEdit, self).__init__()

        self.defaultName = text
        self.setPlainText(text)

        self.setProperty("textcolor", "dim")


    def get (self):

        text = self.toPlainText()
        if text == self.defaultName:
            text = ""
        return text


    def set (self, text):

        self.setPlainText(text)
        self.setProperty("textcolor", "on")
        self.setStyleSheet("")


    def setDefault (self):

        self.setPlainText(self.defaultName)
        self.setProperty("textcolor", "dim")
        self.setStyleSheet("")


    def mousePressEvent (self, event):
        super(CommentEdit, self).mousePressEvent(event)

        if self.toPlainText() == self.defaultName:
            self.set("")


    def leaveEvent (self, event):
        super(CommentEdit, self).leaveEvent(event)

        if not self.toPlainText():
            self.setDefault()
        





class Status (QtWidgets.QWidget):


    def __init__ (self, theme):
        super(Status, self).__init__()

        self.theme = theme

        self.setMinimumWidth(WIDTH)
        self.setMaximumWidth(WIDTH)

        self.NAME = str()

        self.setMouseTracking(True)
        self.hoverStatus = False

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(0)


        lineWidth = UIGlobals.Options.Status.lineWidth

        fontLabel = UIGlobals.IconDelegate.fontAssetLabel
        metrics = QtGui.QFontMetrics(fontLabel)
        labelHeight = metrics.capHeight()

        fontButton = UIGlobals.Options.fontLabel
        metrics = QtGui.QFontMetrics(fontButton)
        textHeight = metrics.capHeight()

        buttomMargin = MARGIN - int(
            (HIGHT_THICK - labelHeight - textHeight)/2)

        self.mainLayout.setContentsMargins(
            0, MARGIN, 0, buttomMargin)


        self.mark = QtWidgets.QWidget()
        self.mark.setMinimumWidth(lineWidth)
        self.mark.setMaximumWidth(lineWidth)
        self.mark.setMinimumHeight(HIGHT_THICK)
        self.mark.setMaximumHeight(HIGHT_THICK)

        self.mark.setAutoFillBackground(True)
        self.mainLayout.addWidget(self.mark)
        

        self.statusLayout = QtWidgets.QVBoxLayout()
        self.statusLayout.setContentsMargins(
            MARGIN-lineWidth, 0, 0, 0)
        self.statusLayout.setSpacing(0)
        self.mainLayout.addLayout(self.statusLayout)



        self.labelLayout = QtWidgets.QHBoxLayout()
        self.labelLayout.setContentsMargins(0, 0, 0, 0)
        self.labelLayout.setSpacing(0)
        self.labelLayout.setObjectName("labelLayout")
        self.statusLayout.addLayout(self.labelLayout)


        self.labelStatus = QtWidgets.QLabel("STATUS")
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setProperty("textcolor", "lock")

        self.labelStatus.setFont(fontLabel)
        self.labelStatus.setMinimumHeight(labelHeight)
        self.labelStatus.setMaximumHeight(labelHeight)
        self.labelLayout.addWidget(self.labelStatus)

        labelSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.labelLayout.addItem(labelSpacer)


        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setSpacing(0)
        self.statusLayout.addLayout(self.buttonsLayout)

        self.buttonList = []
        for name in Settings.STATUS_LIST:
            self.NAME = name

            self.button = QtWidgets.QPushButton(name)
            self.button.setProperty("button", "status")
            self.button.setFont(fontButton)
            self.button.setCheckable(True)
            self.button.setFlat(True)

            self.button.pressed.connect(self.uncheckButtons)
            self.button.released.connect(self.checkButton)

            widthButton  = tools.getStringWidth(name, fontButton)
            widthButton += UIGlobals.Options.Status.space
            self.button.setMinimumWidth(widthButton)
            self.button.setMaximumWidth(widthButton)

            self.buttonList.append(self.button)
            self.buttonsLayout.addWidget(self.button)

        self.set()


        buttonsSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(buttonsSpacer)


        statusSpacer = QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(statusSpacer)

        self.setLayout(self.mainLayout)



    def set (self, status="WIP"):
        self.uncheckButtons()
        self.NAME = status
        self.setColor()
        self.checkButton()
        self.setVisibility()



    def get (self):

        return self.NAME



    def uncheckButtons (self):

        for button in self.buttonList:
            if button.isDown():
                self.NAME = button.text()
            button.setChecked(False)

        self.setColor()



    def checkButton (self):

        for button in self.buttonList:
            if button.text() == self.NAME:
                button.setChecked(True)



    def setColor(self):
        
        color = self.theme.statusWIP
        if self.NAME == "Final":
            color = self.theme.statusFinal
        elif self.NAME == "Completed":
            color = self.theme.statusCompleted

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            color )
        self.mark.setPalette(palette)



    def mouseMoveEvent (self, event):
        super(Status, self).mouseMoveEvent(event)

        pointer = QtCore.QPoint(
            event.x(),
            event.y())

        statusArea = self.statusLayout.contentsRect()
        hover = statusArea.contains(pointer)

        if hover and not self.hoverStatus:
            self.hoverStatus = True
            for button in self.buttonList:
                button.setVisible(True)

        if not hover and self.hoverStatus:
            self.hoverStatus = False
            self.setVisibility()



    def setVisibility (self):
        for button in self.buttonList:
            if button.text() == self.NAME:
                button.setVisible(True)
            else:
                button.setVisible(False)
        





class SwitchButton (QtWidgets.QPushButton):


    def __init__ (self, theme):
        super(SwitchButton, self).__init__()

        self.theme = theme

        self.setCheckable(True)
        self.setText("")

        self.check = QtGui.QImage(":/icons/check.png")

        self.sizeValue = 16
        self.setMinimumSize(QtCore.QSize(self.sizeValue, self.sizeValue))
        self.setMaximumSize(QtCore.QSize(self.sizeValue, self.sizeValue))


    def paintEvent (self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        buttonRect = self.contentsRect()
        offset = int((self.sizeValue - self.check.width())/2)
        position = QtCore.QPoint(
            buttonRect.x()          ,
            buttonRect.y() + offset )

        color = QtGui.QColor(self.theme.optionBackground)
        painter.fillRect(buttonRect, color)

        if self.isChecked():
            image = tools.recolor(self.check, self.theme.green)
        else:
            image = tools.recolor(self.check, self.theme.optionDisable)

        painter.drawImage(position, image)
        painter.end()


        





def setupUi (parent, ListViewLayout, theme):


    parent.defaultName = "Name"
    parent.currentName = ""
    parent.checkedName = ""


    parent.setProperty("background", "options")
    parent.setProperty("border", "none")

    parent.mainLayout = QtWidgets.QHBoxLayout()
    parent.mainLayout.setContentsMargins(0, 0, 0, 0)
    parent.mainLayout.setSpacing(0)
    parent.mainLayout.setObjectName("mainLayout")
    parent.mainLayout.addLayout(ListViewLayout)

    parent.wrappLayout = QtWidgets.QVBoxLayout()
    parent.wrappLayout.setContentsMargins(0, 0, 0, 0)
    parent.wrappLayout.setSpacing(0)
    parent.wrappLayout.setObjectName("wrappLayout")

    parent.optionLayout = QtWidgets.QVBoxLayout()
    parent.optionLayout.setContentsMargins(MARGIN, 0, MARGIN, 0)
    parent.optionLayout.setSpacing(0)
    parent.optionLayout.setObjectName("optionLayout")
    parent.wrappLayout.addLayout(parent.optionLayout)


    parent.nameLayout = QtWidgets.QHBoxLayout()
    parent.nameLayout.setContentsMargins(0, 16, 0, MARGIN)
    parent.nameLayout.setSpacing(0)
    parent.nameLayout.setObjectName("nameLayout")
    parent.nameEdit = NameEdit(parent.defaultName)
    parent.nameEdit.setFont(UIGlobals.Options.fontLabel)
    parent.nameEdit.setObjectName("nameEdit")
    parent.nameEdit.setProperty("background", "input")
    parent.nameEdit.setProperty("border", "none")
    parent.nameEdit.setProperty("border", "round")
    parent.nameEdit.setProperty("textcolor", "off")
    parent.nameEdit.setTextMargins(10, 0, 0, 0)
    parent.nameLayout.addWidget(parent.nameEdit)
    parent.optionLayout.addLayout(parent.nameLayout)

    parent.modelingLayout = QtWidgets.QHBoxLayout()
    parent.modelingLayout.setContentsMargins(0, 0, 0, 4)
    parent.modelingLayout.setSpacing(10)
    parent.modelingLayout.setObjectName("modelingLayout")
    parent.modelingLabel = QtWidgets.QLabel()
    parent.modelingLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.modelingLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.modelingLabel.setFont(UIGlobals.Options.fontLabel)
    parent.modelingLabel.setObjectName("modelingLabel")
    parent.modelingLabel.setProperty("textcolor", "on")
    parent.modelingLayout.addWidget(parent.modelingLabel)

    parent.modelingSwitch = SwitchButton(theme)
    parent.modelingLayout.addWidget(parent.modelingSwitch)

    parent.modelingOverwrite = QtWidgets.QPushButton()
    parent.modelingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.modelingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.modelingOverwrite.setFont(UIGlobals.Options.fontOverwrite)
    parent.modelingOverwrite.setCheckable(True)
    parent.modelingOverwrite.setObjectName("modelingOverwrite")
    parent.modelingLayout.addWidget(parent.modelingOverwrite)
    modelingSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    parent.modelingLayout.addItem(modelingSpacer)
    parent.optionLayout.addLayout(parent.modelingLayout)

    parent.surfacingLayout = QtWidgets.QHBoxLayout()
    parent.surfacingLayout.setContentsMargins(0, 0, 0, 4)
    parent.surfacingLayout.setSpacing(10)
    parent.surfacingLayout.setObjectName("surfacingLayout")
    parent.surfacingLabel = QtWidgets.QLabel()
    parent.surfacingLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.surfacingLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.surfacingLabel.setFont(UIGlobals.Options.fontLabel)
    parent.surfacingLabel.setObjectName("surfacingLabel")
    parent.surfacingLabel.setProperty("textcolor", "on")
    parent.surfacingLayout.addWidget(parent.surfacingLabel)

    parent.surfacingSwitch = SwitchButton(theme)
    parent.surfacingLayout.addWidget(parent.surfacingSwitch)

    parent.surfacingOverwrite = QtWidgets.QPushButton()
    parent.surfacingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.surfacingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.surfacingOverwrite.setFont(UIGlobals.Options.fontOverwrite)
    parent.surfacingOverwrite.setCheckable(True)
    parent.surfacingOverwrite.setFlat(True)
    parent.surfacingOverwrite.setObjectName("surfacingOverwrite")
    parent.surfacingLayout.addWidget(parent.surfacingOverwrite)

    surfacingSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    parent.surfacingLayout.addItem(surfacingSpacer)
    parent.optionLayout.addLayout(parent.surfacingLayout)

    parent.animationLayout = QtWidgets.QHBoxLayout()
    parent.animationLayout.setContentsMargins(0, 0, 0, 4)
    parent.animationLayout.setSpacing(10)
    parent.animationLayout.setObjectName("animationLayout")
    parent.animationLabel = QtWidgets.QLabel()
    parent.animationLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.animationLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.animationLabel.setFont(UIGlobals.Options.fontLabel)
    parent.animationLabel.setObjectName("animationLabel")
    parent.animationLabel.setProperty("textcolor", "on")
    parent.animationLayout.addWidget(parent.animationLabel)

    parent.animationSwitch = SwitchButton(theme)
    parent.animationLayout.addWidget(parent.animationSwitch)

    parent.animationOverwrite = QtWidgets.QPushButton()
    parent.animationOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.animationOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.animationOverwrite.setFont(UIGlobals.Options.fontOverwrite)
    parent.animationOverwrite.setCheckable(True)
    parent.animationOverwrite.setFlat(True)
    parent.animationOverwrite.setObjectName("animationOverwrite")
    parent.animationLayout.addWidget(parent.animationOverwrite)

    animationSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    parent.animationLayout.addItem(animationSpacer)
    parent.optionLayout.addLayout(parent.animationLayout)


    parent.animationOpions = AnimationOpions(theme)
    parent.optionLayout.addWidget(parent.animationOpions)


    parent.mainOpions = MainOpions(theme)
    parent.optionLayout.addWidget(parent.mainOpions)


    parent.commentLabelLayout = QtWidgets.QVBoxLayout()
    parent.commentLabelLayout.setContentsMargins(0, MARGIN, 0, 0)
    parent.commentLabelLayout.setSpacing(0)
    parent.commentLabelLayout.setObjectName("commentLabelLayout")
    parent.optionLayout.addLayout(parent.commentLabelLayout)

    parent.labelComment = QtWidgets.QLabel("COMMENT")
    parent.labelComment.setObjectName("labelComment")
    parent.labelComment.setProperty("textcolor", "lock")
    parent.labelComment.setFont(UIGlobals.IconDelegate.fontAssetLabel)
    parent.commentLabelLayout.addWidget(parent.labelComment)


    optionSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    parent.optionLayout.addItem(optionSpacer)


    parent.commentLayout = QtWidgets.QVBoxLayout()
    parent.commentLayout.setContentsMargins(0, 0, MARGIN, 0)
    parent.commentLayout.setSpacing(0)
    parent.commentLayout.setObjectName("commentLayout")
    parent.wrappLayout.addLayout(parent.commentLayout)


    textOffset = 4
    parent.commentEdit = CommentEdit("Silent Push")
    parent.commentEdit.setMinimumWidth(WIDTH+MARGIN)
    parent.commentEdit.setMaximumWidth(WIDTH+MARGIN)
    parent.commentEdit.setMinimumHeight(HIGHT_THICK)
    parent.commentEdit.setProperty("background", "options")
    parent.commentEdit.setProperty("border", "none")
    parent.commentEdit.setObjectName("commentEdit")
    parent.commentEdit.setViewportMargins( MARGIN-textOffset, 0, 0, 0)
    parent.commentEdit.setFont(UIGlobals.Options.fontComment)
    parent.commentLayout.addWidget(parent.commentEdit)


    parent.status = Status(theme)
    parent.wrappLayout.addWidget(parent.status)


    parent.exportLayout = QtWidgets.QHBoxLayout()
    parent.exportLayout.setContentsMargins(MARGIN, 0, MARGIN, MARGIN)
    parent.exportLayout.setSpacing(10)
    parent.exportLayout.setObjectName("exportLayout")

    parent.exportButton = ExportButton(theme)
    parent.exportButton.setFont(UIGlobals.Options.fontLabel)
    parent.exportButton.setFlat(True)
    parent.exportButton.setObjectName("exportButton")
    parent.exportButton.setProperty("state", "disabled")
    parent.exportLayout.addWidget(parent.exportButton)

    parent.wrappLayout.addLayout(parent.exportLayout)
    parent.mainLayout.addLayout(parent.wrappLayout)

    parent.mainLayout.setStretch(0, 1)
    parent.setLayout(parent.mainLayout)

    parent.modelingLabel.setText("Modeling")
    parent.modelingOverwrite.setText("overwrite")
    parent.surfacingLabel.setText("Surfacing")
    parent.surfacingOverwrite.setText("overwrite")
    parent.animationLabel.setText("Animation")
    parent.animationOverwrite.setText("overwrite")
