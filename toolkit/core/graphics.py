#!/usr/bin/env python

"""
Graphics

Direct pixel access and manipulation.
"""

from toolkit.ensure.QtCore import *
from toolkit.ensure.QtGui import *
from typing import Union


def recolor (
        image: QtGui.QImage,
        color: Union[str, QtGui.QColor],
        opacity: float = 1.0 ) -> QtGui.QImage:
    """Fill the image with solid color
    and set opacity by multiplying alpha value for each pixel

    Arguments:
        image: The image to change
        color: Hex color code
    Keyword Arguments:
        opacity: Alpha multiplier
    Returns:
        Edited image
    """
    for x in range(image.width()):
        for y in range(image.height()):
            alpha = int(
                image.pixelColor(x,y).alpha() * opacity )
            color = QtGui.QColor(color)
            color.setAlpha(alpha)
            image.setPixelColor(x, y, color)
    return image


def alphaMultiply (
        image: QtGui.QImage,
        opacity: float = 1.0 ) -> QtGui.QImage:
    """Set opacity by multiplying alpha value for each pixel

    Arguments:
        image: The image to change
    Keyword Arguments:
        opacity: Alpha multiplier
    Returns:
        Edited image
    """
    for x in range(image.width()):
        for y in range(image.height()):
            color = image.pixelColor(x,y)
            alpha = int(color.alpha() * opacity)
            color.setAlpha(alpha)
            image.setPixelColor(x, y, color)
    return image


def multiply (
        image: QtGui.QImage,
        color: Union[str, QtGui.QColor] ) -> QtGui.QImage:
    """Multiply the image colors by solid color

    Arguments:
        image: The image to change
        color: Hex color code
    Returns:
        Edited image
    """
    colorMultiply = QtGui.QColor(color)
    for x in range(image.width()):
        for y in range(image.height()):
            colorInput = image.pixelColor(x,y)
            redOutput   = colorInput.redF() * colorMultiply.redF()
            greenOutput = colorInput.greenF() * colorMultiply.greenF()
            blueOutput  = colorInput.blueF() * colorMultiply.blueF()
            colorOutput = QtGui.QColor(
                int(redOutput * 255.0)   ,
                int(greenOutput * 255.0) ,
                int(blueOutput * 255.0)  )
            image.setPixelColor(x, y, colorOutput)
    return image


def lightnessAverage (image: Union[str, QtGui.QImage]) -> float:
    """Get average lightness value of the image

    Arguments:
        image: The image to change
    Returns:
        Edited image
    """
    if type(image) is str:
        image = QtGui.QImage(image)
    dotImage = image.scaled(
        1, 1, QtCore.Qt.IgnoreAspectRatio,
        QtCore.Qt.FastTransformation)
    color = dotImage.pixelColor(0,0)
    return color.lightnessF()
