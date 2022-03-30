#!/usr/bin/env python



from toolkit.ensure.QtGui import *
from toolkit.core import calculate






def makeFont (size=7, weight=QtGui.QFont.Normal):

    """
        QFont::Thin         0   0
        QFont::ExtraLight   12  12
        QFont::Light        25  25
        QFont::Normal       50  50
        QFont::Medium       57  57
        QFont::DemiBold     63  63
        QFont::Bold         75  75
        QFont::ExtraBold    81  81
        QFont::Black        87  87
    """

    font = QtGui.QFont()
    font.setFamily("Cantarell")
    font.setPointSize(size)
    font.setWeight(weight)
    font.setKerning(True)

    font.setStyleStrategy(
        QtGui.QFont.PreferAntialias)
    font.setHintingPreference(
        QtGui.QFont.PreferFullHinting)
    font.setStretch(
        QtGui.QFont.Unstretched)
    font.setLetterSpacing(
        QtGui.QFont.PercentageSpacing, 100)

    return font







def setFont (widget, font):

    widget.setFont(font)

    widget.setProperty(
            "fontsize",
            calculate.fontSizeStyle(font) )

    widget.setProperty(
        "fontfamily", "cantarell" )