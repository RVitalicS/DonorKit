#!/usr/bin/env python

"""
UI Tools

This module defines functions to manage UI parts.
"""

from toolkit.ensure.QtWidgets import *
from toolkit.ensure.QtGui import *
from toolkit.core import calculate


def makeFont (
        size: int = 7,
        weight: QtGui.QFont.Weight = QtGui.QFont.Normal,
        tracking: float = 1.0 ) -> QtGui.QFont:
    """Create and adjust the font object from the specified attributes

    Keyword Arguments:
        size: The point size of the font
        weight: The weight of the font
        tracking: The letter spacing for the font
    Returns:
        The font object
    """
    font = QtGui.QFont()
    font.setFamily("Cantarell")
    font.setPointSize(size)
    font.setWeight(weight)
    font.setKerning(True)

    font.setStyleStrategy(QtGui.QFont.PreferAntialias)
    font.setHintingPreference(QtGui.QFont.PreferFullHinting)
    font.setStretch(QtGui.QFont.Unstretched)
    font.setLetterSpacing(QtGui.QFont.PercentageSpacing, tracking * 100)

    return font


def setFont (widget: QtWidgets.QWidget, font: QtGui.QFont) -> None:
    """Changes the widget font to the specified one

    Arguments:
        widget: The user interface object
        font: The font object
    """
    widget.setFont(font)
    widget.setProperty("fontsize", calculate.fontSizeStyle(font) )
    widget.setProperty("fontfamily", "Cantarell" )
