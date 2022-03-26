#!/usr/bin/env python



from Qt import QtGui, QtCore






def recolor (image, color, opacity=1.0):

    for x in range(image.width()):
        for y in range(image.height()):

            alpha = int(
                image.pixelColor(x,y).alpha() * opacity )

            color = QtGui.QColor(color)
            color.setAlpha(alpha)
            image.setPixelColor(x, y, color)

    return image






def multiply (image, color):

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






def lightnessAverage (image):

    if type(image) is str:
        image = QtGui.QImage(image)

    dotimage = image.scaled(1, 1, 
        QtCore.Qt.IgnoreAspectRatio,
        QtCore.Qt.FastTransformation )

    color = dotimage.pixelColor(0,0)
    if color.alpha() > 0:
        return color.lightnessF()