


# globals

white = "#ffffff"
black = "#060a0c"

text      = "#bbbbbb"
textoff   = "#505050"
textgrey  = "#8a9199"

blackBrowser = "#444444"

iconBackground = "#4e5052"
iconHilight    = "#545759"

folderHilight  = "#545759"
checkedHilight = "#58a5cc"

greyHandle = "#808080"


optionBackground = "#4e5052"
optionInput      = "#464849"
optionButton     = "#606365"
optionDisable    = "#3a3c3d"


statusFinal     = "#00c59b"
statusCompleted = "#f57900"
statusWIP       = "#979996"



# values
radiusScrollBar = 3
radiusButton    = 4





# stylesheet

properties = '''
*[background="browser"] { background: $BLACK_BROWSER; }
*[background="black"] { background: $BLACK_COLOR; }

*[background="options"] { background: $OPTION_BACKGROUND; }
*[background="input"] { background: $OPTION_INPUT; }
*[background="button"] { background: $OPTION_BUTTON; }

*[border="none"] { border: none; }
*[border="round"] { border-radius: $RADIUS_BUTTONpx; }

*[textcolor="light"] { color: $TEXT; }
'''


slider = '''

QScrollBar:horizontal, QScrollBar:vertical {
    background: $BLACK_BROWSER;
    border: none;
    border-radius: $RADIUS_BARpx;
}

QScrollBar:horizontal {
    height:6px;
}

QScrollBar:vertical {
    width:6px;
}

QScrollBar::handle:horizontal { min-width:45px; }
QScrollBar::handle:vertical { min-height:45px; }

QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
    background: $GREY_HANDLE;
    border: none;
    border-radius: $RADIUS_BARpx;
}

QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal,
QScrollBar:left-arrow:vertical, QScrollBar::right-arrow:vertical  {
    background: transparent;
}

QScrollBar::add-line:horizontal,      QScrollBar::add-line:vertical {
    background: transparent;
}

QScrollBar::sub-line:horizontal,      QScrollBar::sub-line:vertical {
    background: transparent;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

'''


backbutton = '''
QPushButton[objectName~="backButton"] {
    background-image: url(":/icons/back.png");
    background-repeat: repeat-n;
    background-position: center left;
    }
QPushButton::pressed[objectName~="backButton"] {
    background-image: url(":/icons/backwhite.png");
    background-repeat: repeat-n;
    background-position: center left;
    }
QPushButton[objectName~="pathRoot"] {
    color: $TEXT;
    }
QPushButton::pressed[objectName~="pathRoot"] {
    color: $WHITE_COLOR;
    }
'''



exportbutton = '''
QPushButton[objectName~="exportButton"] {
    color: $TEXT;
    background: $OPTION_BUTTON;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
QPushButton::pressed[objectName~="exportButton"] {
    color: $TEXT;
    background: $BLACK_COLOR;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
'''



rangebutton = '''
QPushButton[objectName~="rangeButton"] {
    color: $TEXT;
    background: $OPTION_BUTTON;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
QPushButton::pressed[objectName~="rangeButton"] {
    color: $TEXT;
    background: $BLACK_COLOR;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    }
'''



finalbutton = '''
QPushButton[objectName~="finalButton"] {
    color: $TEXT;
    background: $OPTION_BUTTON;
    border: none;
    }
QPushButton:hover[objectName~="finalButton"] {
    color: $TEXT;
    background: $BLACK_COLOR;
    border: none;
    }
QPushButton:checked[objectName~="finalButton"] {
    color: $TEXT;
    background: $BLACK_COLOR;
    border: none;
    }
'''



checkbutton = '''
QPushButton:checked[objectName~="modelingSwitch"],
QPushButton:checked[objectName~="surfacingSwitch"],
QPushButton:checked[objectName~="animationSwitch"] {
    border: none;
    background-image: url(":/icons/checked.png");
    background-repeat: repeat-n;
    background-position: center left;
    }
QPushButton[objectName~="modelingSwitch"],
QPushButton[objectName~="surfacingSwitch"],
QPushButton[objectName~="animationSwitch"] {
    border: none;
    background-image: url(":/icons/unchecked.png");
    background-repeat: repeat-n;
    background-position: center left;
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
QPushButton[objectName~="animationOverwrite"] {
    color: $OPTION_BUTTON;
    background: $OPTION_DISABLE;
    border-radius: 8px;
    border: none;
    }
'''



versionCombobox = '''
QComboBox:editable {
    color: $TEXT;
    background: $OPTION_INPUT;
    border-radius: $RADIUS_BUTTONpx;
    border: none;
    font-size: 9pt;
}
QComboBox::drop-down {
    width: 20px;
    background: $OPTION_INPUT;
}
QComboBox::down-arrow {
    image: url(":/icons/dropdown.png");
}
QComboBox QAbstractItemView {
    border: none;
    color: $TEXT;
    background: $OPTION_INPUT;
    selection-background-color: $BLACK_COLOR;
}
'''


pathline = '''
QLineEdit[objectName~="pathLine"] {
    color: $TEXT;
    }
'''





# merge & replace

UI = "".join([
    properties,
    slider,
    backbutton,
    exportbutton,
    rangebutton,
    finalbutton,
    checkbutton,
    overridebutton,
    versionCombobox,
    pathline ])


UI = UI.replace("$WHITE_COLOR", white)
UI = UI.replace("$BLACK_COLOR", black)
UI = UI.replace("$TEXT", text)

UI = UI.replace("$OPTION_BACKGROUND", optionBackground)
UI = UI.replace("$OPTION_INPUT", optionInput)
UI = UI.replace("$OPTION_BUTTON", optionButton)
UI = UI.replace("$OPTION_DISABLE", optionDisable)

UI = UI.replace("$HILIGHT_CHECKED", checkedHilight)

UI = UI.replace("$BLACK_BROWSER", blackBrowser)
UI = UI.replace("$GREY_HANDLE", greyHandle)

UI = UI.replace("$RADIUS_BAR",    str(radiusScrollBar) )
UI = UI.replace("$RADIUS_BUTTON", str(radiusButton) )
