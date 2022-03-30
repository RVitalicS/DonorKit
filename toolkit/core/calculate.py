#!/usr/bin/env python



from toolkit.ensure.QtGui import *






def stringWidth (string, font):

    """
        Calculates string width in pixels
        for the specific font

        :type  string: str
        :param string: name to find out width

        :type    font: QFont
        :param   font: font for calculation

        :rtype : int
        :return: width in pixels
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






def fontSizeStyle (font):

    """
        Calculates font height in pixels
        to match pointPize attibute
        with font-size in styleSheet

        :type    font: QFont
        :param   font: font for calculation

        :rtype : int
        :return: height in pixels
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
