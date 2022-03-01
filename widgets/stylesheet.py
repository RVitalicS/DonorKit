#!/usr/bin/env python



# globals

white  = "#ffffff"
paper  = "#e4e4e4"
black  = "#060a0c"
violet = "#a37acc"
purple = "#815aa8"
red    = "#f07171"

text      = "#bbbbbb"
textoff   = "#707070"
textlock  = "#8b8b8b"

browserBackground  = "#444444"
browserSocket      = "#373737"
browserSocketHover = "#525252"
browserHandle      = "#808080"

iconBackground = "#4e5052"
iconHilight    = "#545759"
iconAnimation  = "#2a2a2a"

folderLink  = "#7a7a7a"
folderColor = "#989898"

checkedHilight = "#58a5cc"


optionBackground = "#4e5052"
optionInput      = "#464849"
optionButton     = "#606365"
optionDisable    = "#3a3c3d"

spinboxArrow     = "#bbbbbb"


statusFinal     = "#00c59b"
statusCompleted = "#f57900"
statusWIP       = "#979996"



# values
radiusScrollBar = 3
radiusButton    = 4

sliderWidth = 12
sliderRadius = int(sliderWidth/2)





# stylesheet

properties = '''
*[background="transparent"] { background: transparent; }
*[background="browser"] { background: $BROWSER_BACKGROUND; }
*[background="black"] { background: $BLACK_COLOR; }

*[background="options"] { background: $OPTION_BACKGROUND; }
*[background="input"] { background: $OPTION_INPUT; }
*[background="button"] { background: $OPTION_BUTTON; }

*[border="none"] { border: none; }
*[border="round"] { border-radius: $RADIUS_BUTTONpx; }

*[textcolor="white"] { color: $WHITE_COLOR; }
*[textcolor="light"] { color: $TEXT_ON; }
*[textcolor="off"] { color: $TEXT_OFF; }
*[textcolor="disabled"] { color: $OPTION_DISABLE; }
*[textcolor="lock"] { color: $TEXT_LOCK; }
*[textcolor="violet"] { color: $VIOLET_COLOR; }
'''


slider = '''
QSlider::groove:horizontal {
    border: none;
    height: $SLIDER_WIDTHpx;
    background: $BROWSER_SOCKET;
    margin: 0px 0;
    border-radius: $SLIDER_RADIUSpx;
    }
QSlider::handle:horizontal {
    background: $BROWSER_HANDLE;
    border: none;
    width: $SLIDER_WIDTHpx;
    margin: 0px 0;
    border-radius: $SLIDER_RADIUSpx;
    }
'''


scrollbar = '''

QScrollBar:horizontal, QScrollBar:vertical {
    background: $BROWSER_BACKGROUND;
    border: none;
    border-radius: $RADIUS_BARpx;
}

QScrollBar:vertical {
    width:12px;
    margin-right: 6px;
}

QScrollBar::handle:vertical { min-height:45px; }

QScrollBar::handle:vertical {
    background: $BROWSER_HANDLE;
    border: none;
    border-radius: $RADIUS_BARpx;
}

QScrollBar:left-arrow:vertical, QScrollBar::right-arrow:vertical  {
    background: transparent;
}

QScrollBar::add-line:vertical {
    background: transparent;
}

QScrollBar::sub-line:vertical {
    background: transparent;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

'''


rootbutton = '''
QPushButton[objectName~="pathRoot"] {
    color: $TEXT_ON;
    }
QPushButton::pressed[objectName~="pathRoot"] {
    color: $WHITE_COLOR;
    }
'''



rangebutton = '''
QPushButton[objectName~="rangeButton"] {
    color: $TEXT_ON;
    background: $OPTION_BUTTON;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
QPushButton::pressed[objectName~="rangeButton"] {
    color: $TEXT_ON;
    background: $BLACK_COLOR;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
'''



linkbutton = '''
QPushButton[objectName~="linkButton"] {
    color: $TEXT_ON;
    background: $OPTION_BUTTON;
    border: none;
    }

QPushButton:checked[objectName~="linkButton"] {
    color: $TEXT_ON;
    background: $BLACK_COLOR;
    border: none;
    }

QPushButton:checked[objectName~="linkButton"][overwrite="true"] {
    color: $WHITE_COLOR;
    background: $VIOLET_COLOR;
    border: none;
    }
'''



statusbutton = '''
QPushButton[button="status"] {
    color: $TEXT_LOCK;
    background: none;
    border: none;
    Text-align: left;
    }
QPushButton:hover[button="status"],
QPushButton:checked[button="status"] {
    color: $WHITE_COLOR;
    background: none;
    border: none;
    Text-align: left;
    }
'''



overridebutton = '''
QPushButton:checked[objectName~="modelingOverwrite"],
QPushButton:checked[objectName~="surfacingOverwrite"],
QPushButton:checked[objectName~="animationOverwrite"] {
    color: $WHITE_COLOR;
    background: $BLACK_COLOR;
    border-radius: 8px;
    border: none;
    }
QPushButton[objectName~="modelingOverwrite"],
QPushButton[objectName~="surfacingOverwrite"],
QPushButton[objectName~="animationOverwrite"],
QPushButton:disabled[objectName~="modelingOverwrite"],
QPushButton:disabled[objectName~="surfacingOverwrite"],
QPushButton:disabled[objectName~="animationOverwrite"] {
    color: $OPTION_BUTTON;
    background: $OPTION_DISABLE;
    border-radius: 8px;
    border: none;
    }
'''



versioncombobox = '''
QComboBox:editable[textcolor="violet"] {
    color: $VIOLET_COLOR;
    background: $OPTION_INPUT;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    font-size: 9pt;
}
QComboBox:editable {
    color: $TEXT_ON;
    background: $OPTION_INPUT;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    font-size: 9pt;
}
QComboBox::drop-down {
    width: 20px;
    background: $OPTION_INPUT;
}
QComboBox QAbstractItemView {
    border: none;
    color: $TEXT_ON;
    background: $OPTION_INPUT;
    selection-background-color: $BLACK_COLOR;
}
'''



bookmarkcombobox = '''
QComboBox::drop-down[bookmark="true"] {
    width: 20px;
    background: $BROWSER_BACKGROUND;
}
QComboBox::down-arrow[bookmark="true"] {
    image: none;
}
QComboBox[bookmark="true"],
QAbstractItemView[bookmark="true"] {
    border: none;
    color: $TEXT_ON;
    background: $BROWSER_BACKGROUND;
    selection-background-color: $BLACK_COLOR;
}
'''


pathline = '''
QLineEdit[objectName~="pathLine"] {
    color: $TEXT_ON;
    }
'''





# merge & replace

UI = "".join([
    properties,
    slider,
    scrollbar,
    rangebutton,
    linkbutton,
    statusbutton,
    overridebutton,
    versioncombobox,
    bookmarkcombobox,
    rootbutton,
    pathline ])


UI = UI.replace("$WHITE_COLOR", white)
UI = UI.replace("$BLACK_COLOR", black)
UI = UI.replace("$VIOLET_COLOR", violet)
UI = UI.replace("$RED_COLOR", red)

UI = UI.replace("$TEXT_ON", text)
UI = UI.replace("$TEXT_OFF", textoff)
UI = UI.replace("$TEXT_LOCK", textlock)

UI = UI.replace("$OPTION_BACKGROUND", optionBackground)
UI = UI.replace("$OPTION_INPUT", optionInput)
UI = UI.replace("$OPTION_BUTTON", optionButton)
UI = UI.replace("$OPTION_DISABLE", optionDisable)

UI = UI.replace("$HILIGHT_CHECKED", checkedHilight)

UI = UI.replace("$BROWSER_BACKGROUND", browserBackground)
UI = UI.replace("$BROWSER_SOCKET", browserSocket)
UI = UI.replace("$BROWSER_HANDLE", browserHandle)

UI = UI.replace("$SLIDER_WIDTH", str(sliderWidth) )
UI = UI.replace("$SLIDER_RADIUS", str(sliderRadius) )

UI = UI.replace("$RADIUS_BAR",    str(radiusScrollBar) )
UI = UI.replace("$RADIUS_BUTTON", str(radiusButton) )
