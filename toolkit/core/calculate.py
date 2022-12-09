#!/usr/bin/env python

"""
Calculations

Collect common calculations.
"""

from toolkit.ensure.QtGui import *


def stringWidth (string: str, font: QtGui.QFont) -> int:
    """Calculates the string width in pixels for the specified font

    Arguments:
        string: The text to find out width
        font: The font for calculation
    Returns:
        Width in pixels
    """

    # scale font for accuracy
    scale = 1000
    font = QtGui.QFont(font)
    font.setPointSize(
        font.pointSize() * scale )
    metrics = QtGui.QFontMetrics(font)
    # get width and scale back
    width = metrics.horizontalAdvance(string)
    width = int(round(width/scale))

    return width


def fontSizeStyle (font: QtGui.QFont) -> int:
    """Calculates height in pixels for the specified font
    to match 'pointSize' attribute with 'font-size' in styleSheet

    Arguments:
        font: The font for calculation
    Returns:
        Height in pixels
    """

    # scale font for accuracy
    scale = 1000
    font = QtGui.QFont(font)
    font.setPointSize(
        font.pointSize() * scale )
    metrics = QtGui.QFontMetrics(font)
    # get height and scale back
    height = metrics.ascent()
    height = int(round(height/scale))

    return height
