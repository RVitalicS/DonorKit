#!/usr/bin/env python



import math
from . import stylesheet


from Qt import QtWidgets, QtCore, QtGui

from . import Settings
UIsettings = Settings.UIsettings







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

        self.finalLayout = QtWidgets.QHBoxLayout()
        self.finalLayout.setContentsMargins(0, 0, 0, 0)
        self.finalLayout.setSpacing(0)
        self.finalLayout.setObjectName("finalLayout")
        self.versionLayout.addLayout(self.finalLayout)

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
        self.finalLayout.addWidget(self.versionCombobox)

        self.finalButton = QtWidgets.QPushButton()
        self.finalButton.setMinimumSize(QtCore.QSize(36, 18))
        self.finalButton.setMaximumSize(QtCore.QSize(36, 18))
        self.finalButton.setFont(UIsettings.Options.fontLabel)
        self.finalButton.setCheckable(True)
        self.finalButton.setFlat(True)
        self.finalButton.setObjectName("finalButton")
        self.finalLayout.addWidget(self.finalButton)

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
        self.mainLayout.addLayout(self.unitGroupLayout)

        self.setLayout(self.mainLayout)

        self.variantLabel.setText("Variant")
        self.versionLabel.setText("Version")
        self.finalButton.setText("final")
        self.unitLabel.setText("unit multiplier")
        





class Window (object):

    def setupUi(self, parent, ListViewLayout):


        self.defaultName = "Name"
        self.currentName = ""
        self.checkedName = ""


        parent.setProperty("background", "options")
        parent.setProperty("border", "none")

        self.verticalLayout = QtWidgets.QVBoxLayout(parent)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.addItem(ListViewLayout)

        self.optionLayout = QtWidgets.QVBoxLayout()
        self.optionLayout.setContentsMargins(30, 0, 30, 30)
        self.optionLayout.setSpacing(0)
        self.optionLayout.setObjectName("optionLayout")
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.setContentsMargins(0, 16, 0, 30)
        self.nameLayout.setSpacing(0)
        self.nameLayout.setObjectName("nameLayout")
        self.nameLineEdit = QtWidgets.QLineEdit(parent)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLineEdit.sizePolicy().hasHeightForWidth())
        self.nameLineEdit.setSizePolicy(sizePolicy)
        self.nameLineEdit.setMinimumSize(QtCore.QSize(0, 32))
        self.nameLineEdit.setMaximumSize(QtCore.QSize(16777215, 32))
        self.nameLineEdit.setSizeIncrement(QtCore.QSize(0, 0))
        self.nameLineEdit.setBaseSize(QtCore.QSize(0, 0))
        self.nameLineEdit.setFont(UIsettings.Options.fontLabel)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setProperty("background", "input")
        self.nameLineEdit.setProperty("border", "none")
        self.nameLineEdit.setProperty("border", "round")
        self.nameLineEdit.setProperty("textcolor", "off")
        self.nameLineEdit.setTextMargins(10, 0, 0, 0)
        self.nameLayout.addWidget(self.nameLineEdit)

        self.optionLayout.addLayout(self.nameLayout)
        self.modelingLayout = QtWidgets.QHBoxLayout()
        self.modelingLayout.setContentsMargins(0, 0, 0, 4)
        self.modelingLayout.setSpacing(10)
        self.modelingLayout.setObjectName("modelingLayout")
        self.modelingLabel = QtWidgets.QLabel(parent)
        self.modelingLabel.setMinimumSize(QtCore.QSize(55, 18))
        self.modelingLabel.setMaximumSize(QtCore.QSize(55, 18))
        self.modelingLabel.setFont(UIsettings.Options.fontLabel)
        self.modelingLabel.setObjectName("modelingLabel")
        self.modelingLabel.setProperty("textcolor", "light")
        self.modelingLayout.addWidget(self.modelingLabel)

        self.modelingSwitch = QtWidgets.QPushButton(parent)
        self.modelingSwitch.setMinimumSize(QtCore.QSize(16, 16))
        self.modelingSwitch.setMaximumSize(QtCore.QSize(16, 16))
        self.modelingSwitch.setText("")
        self.modelingSwitch.setCheckable(True)
        self.modelingSwitch.setFlat(True)
        self.modelingSwitch.setObjectName("modelingSwitch")
        self.modelingLayout.addWidget(self.modelingSwitch)
        self.modelingOverwrite = QtWidgets.QPushButton(parent)
        self.modelingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
        self.modelingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
        self.modelingOverwrite.setFont(UIsettings.Options.fontOverwrite)
        self.modelingOverwrite.setCheckable(True)
        self.modelingOverwrite.setObjectName("modelingOverwrite")
        self.modelingLayout.addWidget(self.modelingOverwrite)
        modelingSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.modelingLayout.addItem(modelingSpacer)
        self.optionLayout.addLayout(self.modelingLayout)

        self.surfacingLayout = QtWidgets.QHBoxLayout()
        self.surfacingLayout.setContentsMargins(0, 0, 0, 4)
        self.surfacingLayout.setSpacing(10)
        self.surfacingLayout.setObjectName("surfacingLayout")
        self.surfacingLabel = QtWidgets.QLabel(parent)
        self.surfacingLabel.setMinimumSize(QtCore.QSize(55, 18))
        self.surfacingLabel.setMaximumSize(QtCore.QSize(55, 18))
        self.surfacingLabel.setFont(UIsettings.Options.fontLabel)
        self.surfacingLabel.setObjectName("surfacingLabel")
        self.surfacingLabel.setProperty("textcolor", "light")
        self.surfacingLayout.addWidget(self.surfacingLabel)

        self.surfacingSwitch = QtWidgets.QPushButton(parent)
        self.surfacingSwitch.setMinimumSize(QtCore.QSize(16, 16))
        self.surfacingSwitch.setMaximumSize(QtCore.QSize(16, 16))
        self.surfacingSwitch.setText("")
        self.surfacingSwitch.setCheckable(True)
        self.surfacingSwitch.setObjectName("surfacingSwitch")
        self.surfacingLayout.addWidget(self.surfacingSwitch)

        self.surfacingOverwrite = QtWidgets.QPushButton(parent)
        self.surfacingOverwrite.setMinimumSize(QtCore.QSize(50, 16))
        self.surfacingOverwrite.setMaximumSize(QtCore.QSize(50, 16))
        self.surfacingOverwrite.setFont(UIsettings.Options.fontOverwrite)
        self.surfacingOverwrite.setCheckable(True)
        self.surfacingOverwrite.setFlat(True)
        self.surfacingOverwrite.setObjectName("surfacingOverwrite")
        self.surfacingLayout.addWidget(self.surfacingOverwrite)

        surfacingSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.surfacingLayout.addItem(surfacingSpacer)
        self.optionLayout.addLayout(self.surfacingLayout)

        self.animationLayout = QtWidgets.QHBoxLayout()
        self.animationLayout.setContentsMargins(0, 0, 0, 4)
        self.animationLayout.setSpacing(10)
        self.animationLayout.setObjectName("animationLayout")
        self.animationLabel = QtWidgets.QLabel(parent)
        self.animationLabel.setMinimumSize(QtCore.QSize(55, 18))
        self.animationLabel.setMaximumSize(QtCore.QSize(55, 18))
        self.animationLabel.setFont(UIsettings.Options.fontLabel)
        self.animationLabel.setObjectName("animationLabel")
        self.animationLabel.setProperty("textcolor", "light")
        self.animationLayout.addWidget(self.animationLabel)

        self.animationSwitch = QtWidgets.QPushButton(parent)
        self.animationSwitch.setMinimumSize(QtCore.QSize(16, 16))
        self.animationSwitch.setMaximumSize(QtCore.QSize(16, 16))
        self.animationSwitch.setText("")
        self.animationSwitch.setCheckable(True)
        self.animationSwitch.setFlat(True)
        self.animationSwitch.setObjectName("animationSwitch")
        self.animationLayout.addWidget(self.animationSwitch)

        self.animationOverwrite = QtWidgets.QPushButton(parent)
        self.animationOverwrite.setMinimumSize(QtCore.QSize(50, 16))
        self.animationOverwrite.setMaximumSize(QtCore.QSize(50, 16))
        self.animationOverwrite.setFont(UIsettings.Options.fontOverwrite)
        self.animationOverwrite.setCheckable(True)
        self.animationOverwrite.setFlat(True)
        self.animationOverwrite.setObjectName("animationOverwrite")
        self.animationLayout.addWidget(self.animationOverwrite)

        animationSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.animationLayout.addItem(animationSpacer)
        self.optionLayout.addLayout(self.animationLayout)


        self.animationOpions = AnimationOpions(parent)
        self.optionLayout.addWidget(self.animationOpions)


        self.mainOpions = MainOpions(parent)
        self.optionLayout.addWidget(self.mainOpions)


        optionSpacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.optionLayout.addItem(optionSpacer)


        self.exportLayout = QtWidgets.QHBoxLayout()
        self.exportLayout.setContentsMargins(0, 30, 0, 0)
        self.exportLayout.setSpacing(10)
        self.exportLayout.setObjectName("exportLayout")

        self.exportButton = ExportButton(parent)
        self.exportButton.setMinimumHeight(32)
        self.exportButton.setFont(UIsettings.Options.fontLabel)
        self.exportButton.setFlat(True)
        self.exportButton.setObjectName("exportButton")
        self.exportButton.setProperty("state", "disabled")
        self.exportLayout.addWidget(self.exportButton)

        self.optionLayout.addLayout(self.exportLayout)
        self.mainLayout.addLayout(self.optionLayout)

        self.mainLayout.setStretch(0, 1)
        self.verticalLayout.addLayout(self.mainLayout)

        self.nameLineEdit.setText(self.defaultName)
        self.modelingLabel.setText("Modeling")
        self.modelingOverwrite.setText("overwrite")
        self.surfacingLabel.setText("Surfacing")
        self.surfacingOverwrite.setText("overwrite")
        self.animationLabel.setText("Animation")
        self.animationOverwrite.setText("overwrite")


        QtCore.QMetaObject.connectSlotsByName(parent)
