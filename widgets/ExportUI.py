#!/usr/bin/env python



import math
from . import stylesheet
from . import tools


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings

MARGIN      = UIsettings.Options.margin
HIGHT_THICK = UIsettings.Options.thickHight






class NameLine (QtWidgets.QLineEdit):


    def __init__ (self, parent, text):
        super(NameLine, self).__init__(parent)

        self.defaultName = text
        self.setText(text)


    def mousePressEvent (self, event):
        super(NameLine, self).mousePressEvent(event)

        if self.text() == self.defaultName:
            self.setText("")
        





class ExportButton (QtWidgets.QPushButton):


    def __init__ (self, parent):
        super(ExportButton, self).__init__(parent)

        self.setMinimumWidth(210)
        self.setMaximumWidth(210)
        
        self.buttonPressed = False

        self.timerAnimation = QtCore.QTimer(self)
        self.timerAnimation.timeout.connect(self.animation)

        self.offset = 0

        self.timerDelay = QtCore.QTimer(self)
        self.timerDelay.timeout.connect(self.delay)

        self.delayTime  = 35
        self.delayValue = -1

        self.patternThickness = UIsettings.Options.Export.patternThickness
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
            stylesheet.radiusButton,
            stylesheet.radiusButton,
            mode=QtCore.Qt.AbsoluteSize              )

        painter.setClipPath(clipPath)

        if self.buttonPressed or self.delayValue >= 0:
            textcolor = QtGui.QColor(stylesheet.white)
            if disabled or self.delayValue >= 0:
                backgroundcolor = QtGui.QColor(stylesheet.red)
            else:
                backgroundcolor = QtGui.QColor(stylesheet.black)
        else:
            textcolor = QtGui.QColor(stylesheet.text)
            backgroundcolor = QtGui.QColor(stylesheet.optionButton)

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

        painter.setFont( UIsettings.Options.Export.font )

        textOption = QtGui.QTextOption()
        textOption.setWrapMode(QtGui.QTextOption.NoWrap)
        textOption.setAlignment(
            QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
        painter.drawText(
            QtCore.QRectF(buttonRect),
            "Export",
            textOption)

        painter.end()
        





class AnimationOpions (QtWidgets.QWidget):

    def __init__ (self, parent):
        super(AnimationOpions, self).__init__(parent)

        self.setMinimumWidth(210)
        self.setMaximumWidth(210)


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
        self.animationNameLabel.setFont(UIsettings.Options.fontLabel)
        self.animationNameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.animationNameLabel.setObjectName("animationNameLabel")
        self.animationNameLabel.setProperty("textcolor", "light")
        self.animationNameLayout.addWidget(self.animationNameLabel)

        self.animationNameCombobox = QtWidgets.QComboBox()
        self.animationNameCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.animationNameCombobox.setFont(UIsettings.Options.fontLabel)
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
        self.animationRangeLabel.setFont(UIsettings.Options.fontLabel)
        self.animationRangeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.animationRangeLabel.setObjectName("animationRangeLabel")
        self.animationRangeLabel.setProperty("textcolor", "light")
        self.animationRangeLayout.addWidget(self.animationRangeLabel)

        self.rangeGroupLayout = QtWidgets.QHBoxLayout()
        self.rangeGroupLayout.setSpacing(2)
        self.rangeGroupLayout.setObjectName("rangeGroupLayout")
        self.rangeStartSpinbox = QtWidgets.QSpinBox()
        self.rangeStartSpinbox.setMinimumSize(QtCore.QSize(50, 18))
        self.rangeStartSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.rangeStartSpinbox.setMinimum(0)
        self.rangeStartSpinbox.setMaximum(99999)
        self.rangeStartSpinbox.setFont(UIsettings.Options.fontLabel)
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
        self.rangeStartSpinbox.setProperty("textcolor", "light")
        self.rangeGroupLayout.addWidget(self.rangeStartSpinbox)

        self.rangeEndSpinbox = QtWidgets.QSpinBox()
        self.rangeEndSpinbox.setMinimumSize(QtCore.QSize(50, 18))
        self.rangeEndSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.rangeEndSpinbox.setMinimum(0)
        self.rangeEndSpinbox.setMaximum(99999)
        self.rangeEndSpinbox.setFont(UIsettings.Options.fontLabel)
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
        self.rangeEndSpinbox.setProperty("textcolor", "light")
        self.rangeGroupLayout.addWidget(self.rangeEndSpinbox)

        rangeSpacer = QtWidgets.QSpacerItem(6, 6, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.rangeGroupLayout.addItem(rangeSpacer)
        self.rangeButton = QtWidgets.QPushButton()
        self.rangeButton.setMinimumSize(QtCore.QSize(36, 18))
        self.rangeButton.setMaximumSize(QtCore.QSize(36, 18))
        self.rangeButton.setFont(UIsettings.Options.fontLabel)
        self.rangeButton.setFlat(False)
        self.rangeButton.setObjectName("rangeButton")
        self.rangeGroupLayout.addWidget(self.rangeButton)

        self.animationRangeLayout.addLayout(self.rangeGroupLayout)
        self.mainLayout.addLayout(self.animationRangeLayout)

        self.fpsLayout = QtWidgets.QHBoxLayout()
        self.fpsLayout.setContentsMargins(0, 0, 0, 0)
        self.fpsLayout.setSpacing(10)
        self.fpsLayout.setObjectName("fpsLayout")
        self.fpsLabel = QtWidgets.QLabel()
        self.fpsLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.fpsLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.fpsLabel.setFont(UIsettings.Options.fontLabel)
        self.fpsLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fpsLabel.setObjectName("fpsLabel")
        self.fpsLabel.setProperty("textcolor", "lock")
        self.fpsLabel.setEnabled(False)
        self.fpsLayout.addWidget(self.fpsLabel)

        self.fpsSpinbox = QtWidgets.QSpinBox()
        self.fpsSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.fpsSpinbox.setFont(UIsettings.Options.fontLabel)
        self.fpsSpinbox.setToolTip("")
        self.fpsSpinbox.setStatusTip("")
        self.fpsSpinbox.setWhatsThis("")
        self.fpsSpinbox.setAccessibleName("")
        self.fpsSpinbox.setAccessibleDescription("")
        self.fpsSpinbox.setWrapping(False)
        self.fpsSpinbox.setFrame(True)
        self.fpsSpinbox.setReadOnly(False)
        self.fpsSpinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.fpsSpinbox.setSpecialValueText("")
        self.fpsSpinbox.setSuffix("")
        self.fpsSpinbox.setPrefix("")
        self.fpsSpinbox.setProperty("value", 30)
        self.fpsSpinbox.setObjectName("fpsSpinbox")
        self.fpsSpinbox.setProperty("background", "options")
        self.fpsSpinbox.setProperty("border", "none")
        self.fpsSpinbox.setProperty("textcolor", "lock")
        self.fpsSpinbox.setEnabled(False)
        self.fpsLayout.addWidget(self.fpsSpinbox)

        fpsSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.fpsLayout.addItem(fpsSpacer)
        # self.mainLayout.addLayout(self.fpsLayout)

        self.setLayout(self.mainLayout)

        self.animationNameLabel.setText("name")
        self.animationRangeLabel.setText("range")
        self.rangeButton.setText("get")
        self.fpsLabel.setText("fps")
        





class MainOpions (QtWidgets.QWidget):

    def __init__ (self, parent):
        super(MainOpions, self).__init__(parent)

        self.setMinimumWidth(210)
        self.setMaximumWidth(210)


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
        self.variantLabel.setFont(UIsettings.Options.fontLabel)
        self.variantLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.variantLabel.setObjectName("variantLabel")
        self.variantLabel.setProperty("textcolor", "light")
        self.variantLayout.addWidget(self.variantLabel)

        self.variantCombobox = QtWidgets.QComboBox()
        self.variantCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.variantCombobox.setFont(UIsettings.Options.fontLabel)
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
        self.variantCombobox.setProperty("textcolor", "light")
        self.variantLayout.addWidget(self.variantCombobox)

        self.mainLayout.addLayout(self.variantLayout)
        self.versionLayout = QtWidgets.QHBoxLayout()
        self.versionLayout.setContentsMargins(0, 0, 0, 0)
        self.versionLayout.setSpacing(10)
        self.versionLayout.setObjectName("versionLayout")

        self.versionLabel = QtWidgets.QLabel()
        self.versionLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.versionLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.versionLabel.setFont(UIsettings.Options.fontLabel)
        self.versionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setProperty("textcolor", "light")
        self.versionLayout.addWidget(self.versionLabel)

        self.linkLayout = QtWidgets.QHBoxLayout()
        self.linkLayout.setContentsMargins(0, 0, 0, 0)
        self.linkLayout.setSpacing(0)
        self.linkLayout.setObjectName("linkLayout")
        self.versionLayout.addLayout(self.linkLayout)

        self.versionCombobox = QtWidgets.QComboBox()
        self.versionCombobox.setMaximumSize(QtCore.QSize(16777215, 18))
        self.versionCombobox.setFont(UIsettings.Options.fontLabel)
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
        self.linkButton.setFont(UIsettings.Options.fontLabel)
        self.linkButton.setCheckable(True)
        self.linkButton.setFlat(True)
        self.linkButton.setObjectName("linkButton")
        self.linkLayout.addWidget(self.linkButton)

        self.mainLayout.addLayout(self.versionLayout)

        self.unitGroupLayout = QtWidgets.QHBoxLayout()
        self.unitGroupLayout.setContentsMargins(0, 20, 0, 0)
        self.unitGroupLayout.setSpacing(10)
        self.unitGroupLayout.setObjectName("unitGroupLayout")
        self.unitGroupLabel = QtWidgets.QLabel()
        self.unitGroupLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.unitGroupLabel.setMaximumSize(QtCore.QSize(55, 24))
        self.unitGroupLabel.setFont(UIsettings.Options.fontLabel)
        self.unitGroupLabel.setText("")
        self.unitGroupLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.unitGroupLabel.setObjectName("unitGroupLabel")
        self.unitGroupLayout.addWidget(self.unitGroupLabel)

        self.unitLayout = QtWidgets.QHBoxLayout()
        self.unitLayout.setContentsMargins(0, 0, 0, 0)
        self.unitLayout.setSpacing(10)
        self.unitLayout.setObjectName("unitLayout")
        self.unitLabel = QtWidgets.QLabel()
        self.unitLabel.setMinimumSize(QtCore.QSize(55, 24))
        self.unitLabel.setMaximumSize(QtCore.QSize(200, 24))
        self.unitLabel.setFont(UIsettings.Options.fontLabel)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.unitLabel.setObjectName("unitLabel")
        self.unitLabel.setProperty("textcolor", "light")
        self.unitLayout.addWidget(self.unitLabel)

        self.unitSpinbox = QtWidgets.QDoubleSpinBox()
        self.unitSpinbox.setMinimumSize(QtCore.QSize(50, 18))
        self.unitSpinbox.setMaximumSize(QtCore.QSize(50, 18))
        self.unitSpinbox.setFont(UIsettings.Options.fontLabel)
        self.unitSpinbox.setToolTip("")
        self.unitSpinbox.setStatusTip("")
        self.unitSpinbox.setWhatsThis("")
        self.unitSpinbox.setAccessibleName("")
        self.unitSpinbox.setAccessibleDescription("")
        self.unitSpinbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.unitSpinbox.setWrapping(False)
        self.unitSpinbox.setFrame(True)
        self.unitSpinbox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.unitSpinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.unitSpinbox.setSpecialValueText("")
        self.unitSpinbox.setAccelerated(False)
        self.unitSpinbox.setSuffix("")
        self.unitSpinbox.setDecimals(2)
        self.unitSpinbox.setMaximum(1000.0)
        self.unitSpinbox.setProperty("value", 1.0)
        self.unitSpinbox.setObjectName("unitSpinbox")
        self.unitSpinbox.setProperty("background", "options")
        self.unitSpinbox.setProperty("border", "none")
        self.unitSpinbox.setProperty("textcolor", "light")
        self.unitLayout.addWidget(self.unitSpinbox)

        self.unitGroupLayout.addLayout(self.unitLayout)
        # self.mainLayout.addLayout(self.unitGroupLayout)

        self.setLayout(self.mainLayout)

        self.variantLabel.setText("Variant")
        self.versionLabel.setText("Version")
        self.linkButton.setText("link")
        self.unitLabel.setText("unit multiplier")
        





class Status (QtWidgets.QWidget):


    def __init__ (self):
        super(Status, self).__init__()

        self.NAME = str()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(0)


        lineWidth = UIsettings.Options.Status.lineWidth

        fontLabel = UIsettings.IconDelegate.fontAssetLabel
        metrics = QtGui.QFontMetrics(fontLabel)
        labelHeight = metrics.capHeight()

        fontButton = UIsettings.Options.fontLabel
        metrics = QtGui.QFontMetrics(fontButton)
        textHeight = metrics.capHeight()

        buttomMargin = MARGIN - int(
            (HIGHT_THICK - labelHeight - textHeight)/2)

        self.mainLayout.setContentsMargins(
            0, 0, 0, buttomMargin)


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
            widthButton += UIsettings.Options.Status.space
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
        
        color = stylesheet.statusWIP
        if self.NAME == "Final":
            color = stylesheet.statusFinal
        elif self.NAME == "Completed":
            color = stylesheet.statusCompleted

        palette = QtGui.QPalette()
        palette.setColor(
            QtGui.QPalette.Background,
            color )
        self.mark.setPalette(palette)



    def enterEvent (self, event):
        super(Status, self).enterEvent(event)

        for button in self.buttonList:
            button.setVisible(True)



    def leaveEvent (self, event):
        super(Status, self).leaveEvent(event)
        self.setVisibility()



    def setVisibility (self):
        for button in self.buttonList:
            if button.text() == self.NAME:
                button.setVisible(True)
            else:
                button.setVisible(False)


        





def setupUi (parent, ListViewLayout):


    parent.defaultName = "Name"
    parent.currentName = ""
    parent.checkedName = ""


    parent.setProperty("background", "options")
    parent.setProperty("border", "none")

    parent.verticalLayout = QtWidgets.QVBoxLayout(parent)
    parent.verticalLayout.setContentsMargins(0, 0, 0, 0)
    parent.verticalLayout.setSpacing(0)
    parent.verticalLayout.setObjectName("verticalLayout")
    parent.mainLayout = QtWidgets.QHBoxLayout()
    parent.mainLayout.setSpacing(0)
    parent.mainLayout.setObjectName("mainLayout")
    parent.mainLayout.addItem(ListViewLayout)

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
    parent.nameLineEdit = NameLine(parent, parent.defaultName)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(parent.nameLineEdit.sizePolicy().hasHeightForWidth())
    parent.nameLineEdit.setSizePolicy(sizePolicy)
    parent.nameLineEdit.setMinimumSize(QtCore.QSize(0, HIGHT_THICK))
    parent.nameLineEdit.setMaximumSize(QtCore.QSize(16777215, HIGHT_THICK))
    parent.nameLineEdit.setSizeIncrement(QtCore.QSize(0, 0))
    parent.nameLineEdit.setBaseSize(QtCore.QSize(0, 0))
    parent.nameLineEdit.setFont(UIsettings.Options.fontLabel)
    parent.nameLineEdit.setObjectName("nameLineEdit")
    parent.nameLineEdit.setProperty("background", "input")
    parent.nameLineEdit.setProperty("border", "none")
    parent.nameLineEdit.setProperty("border", "round")
    parent.nameLineEdit.setProperty("textcolor", "off")
    parent.nameLineEdit.setTextMargins(10, 0, 0, 0)
    parent.nameLayout.addWidget(parent.nameLineEdit)
    parent.optionLayout.addLayout(parent.nameLayout)

    parent.modelingLayout = QtWidgets.QHBoxLayout()
    parent.modelingLayout.setContentsMargins(0, 0, 0, 4)
    parent.modelingLayout.setSpacing(10)
    parent.modelingLayout.setObjectName("modelingLayout")
    parent.modelingLabel = QtWidgets.QLabel(parent)
    parent.modelingLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.modelingLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.modelingLabel.setFont(UIsettings.Options.fontLabel)
    parent.modelingLabel.setObjectName("modelingLabel")
    parent.modelingLabel.setProperty("textcolor", "light")
    parent.modelingLayout.addWidget(parent.modelingLabel)

    parent.modelingSwitch = QtWidgets.QPushButton(parent)
    parent.modelingSwitch.setMinimumSize(QtCore.QSize(16, 16))
    parent.modelingSwitch.setMaximumSize(QtCore.QSize(16, 16))
    parent.modelingSwitch.setText("")
    parent.modelingSwitch.setCheckable(True)
    parent.modelingSwitch.setFlat(True)
    parent.modelingSwitch.setObjectName("modelingSwitch")
    parent.modelingLayout.addWidget(parent.modelingSwitch)
    parent.modelingOverwrite = QtWidgets.QPushButton(parent)
    parent.modelingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.modelingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.modelingOverwrite.setFont(UIsettings.Options.fontOverwrite)
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
    parent.surfacingLabel = QtWidgets.QLabel(parent)
    parent.surfacingLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.surfacingLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.surfacingLabel.setFont(UIsettings.Options.fontLabel)
    parent.surfacingLabel.setObjectName("surfacingLabel")
    parent.surfacingLabel.setProperty("textcolor", "light")
    parent.surfacingLayout.addWidget(parent.surfacingLabel)

    parent.surfacingSwitch = QtWidgets.QPushButton(parent)
    parent.surfacingSwitch.setMinimumSize(QtCore.QSize(16, 16))
    parent.surfacingSwitch.setMaximumSize(QtCore.QSize(16, 16))
    parent.surfacingSwitch.setText("")
    parent.surfacingSwitch.setCheckable(True)
    parent.surfacingSwitch.setObjectName("surfacingSwitch")
    parent.surfacingLayout.addWidget(parent.surfacingSwitch)

    parent.surfacingOverwrite = QtWidgets.QPushButton(parent)
    parent.surfacingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.surfacingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.surfacingOverwrite.setFont(UIsettings.Options.fontOverwrite)
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
    parent.animationLabel = QtWidgets.QLabel(parent)
    parent.animationLabel.setMinimumSize(QtCore.QSize(55, 18))
    parent.animationLabel.setMaximumSize(QtCore.QSize(55, 18))
    parent.animationLabel.setFont(UIsettings.Options.fontLabel)
    parent.animationLabel.setObjectName("animationLabel")
    parent.animationLabel.setProperty("textcolor", "light")
    parent.animationLayout.addWidget(parent.animationLabel)

    parent.animationSwitch = QtWidgets.QPushButton(parent)
    parent.animationSwitch.setMinimumSize(QtCore.QSize(16, 16))
    parent.animationSwitch.setMaximumSize(QtCore.QSize(16, 16))
    parent.animationSwitch.setText("")
    parent.animationSwitch.setCheckable(True)
    parent.animationSwitch.setFlat(True)
    parent.animationSwitch.setObjectName("animationSwitch")
    parent.animationLayout.addWidget(parent.animationSwitch)

    parent.animationOverwrite = QtWidgets.QPushButton(parent)
    parent.animationOverwrite.setMinimumSize(QtCore.QSize(50, 16))
    parent.animationOverwrite.setMaximumSize(QtCore.QSize(50, 16))
    parent.animationOverwrite.setFont(UIsettings.Options.fontOverwrite)
    parent.animationOverwrite.setCheckable(True)
    parent.animationOverwrite.setFlat(True)
    parent.animationOverwrite.setObjectName("animationOverwrite")
    parent.animationLayout.addWidget(parent.animationOverwrite)

    animationSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    parent.animationLayout.addItem(animationSpacer)
    parent.optionLayout.addLayout(parent.animationLayout)


    parent.animationOpions = AnimationOpions(parent)
    parent.optionLayout.addWidget(parent.animationOpions)


    parent.mainOpions = MainOpions(parent)
    parent.optionLayout.addWidget(parent.mainOpions)


    optionSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    parent.optionLayout.addItem(optionSpacer)


    parent.status = Status()
    parent.wrappLayout.addWidget(parent.status)


    parent.exportLayout = QtWidgets.QHBoxLayout()
    parent.exportLayout.setContentsMargins(MARGIN, 0, MARGIN, MARGIN)
    parent.exportLayout.setSpacing(10)
    parent.exportLayout.setObjectName("exportLayout")

    parent.exportButton = ExportButton(parent)
    parent.exportButton.setMinimumHeight(HIGHT_THICK)
    parent.exportButton.setFont(UIsettings.Options.fontLabel)
    parent.exportButton.setFlat(True)
    parent.exportButton.setObjectName("exportButton")
    parent.exportButton.setProperty("state", "disabled")
    parent.exportLayout.addWidget(parent.exportButton)

    parent.wrappLayout.addLayout(parent.exportLayout)
    parent.mainLayout.addLayout(parent.wrappLayout)

    parent.mainLayout.setStretch(0, 1)
    parent.verticalLayout.addLayout(parent.mainLayout)

    parent.modelingLabel.setText("Modeling")
    parent.modelingOverwrite.setText("overwrite")
    parent.surfacingLabel.setText("Surfacing")
    parent.surfacingOverwrite.setText("overwrite")
    parent.animationLabel.setText("Animation")
    parent.animationOverwrite.setText("overwrite")
