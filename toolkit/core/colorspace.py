#!/usr/bin/env python

"""
Colorspace

Convert color data in different color spaces.
"""

import math
from typing import Union


def Lab_XYZ (Lab: list, white: str = "D50") -> list:
    """Convert values from CIE Lab color space to CIE XYZ

    Arguments:
        Lab: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        CIE XYZ color data array
    """
    L,a,b = Lab
    Y = (L + 16) / 116
    X = a / 500 + Y
    Z = Y - b / 200

    def function (t):
        if t ** 3  > 0.008856:
            return t ** 3
        else:
            return (t - 16/116) / 7.787
    X = function(X)
    Y = function(Y)
    Z = function(Z)

    # CIE-L*ab (D65/2°)
    if white == "D65": return [
        X * 95.0489,
        Y * 100.000,
        Z * 108.884]
    # CIE-L*ab (D50/2°)
    return [
        X * 96.4212,
        Y * 100.000,
        Z * 82.5219]


def XYZ_Lab (XYZ: list, white: str = "D50") -> list:
    """Convert values from CIE XYZ color space to CIE Lab

    Arguments:
        XYZ: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        CIE Lab color data array
    """
    X,Y,Z = XYZ
    # D65/2°
    if white == "D65":
        X /= 95.0489
        Y /= 100.000
        Z /= 108.884
    # D50/2°
    else:
        X /= 96.4212
        Y /= 100.000
        Z /= 82.5219

    def function (t):
        if t > 0.008856:
            return t ** (1/3)
        else:
            return (7.787 * t) + 16/116

    X = function(X)
    Y = function(Y)
    Z = function(Z)
    return [
        (116 * Y) - 16,
        500 * (X - Y),
        200 * (Y - Z)]


def XYZ_lRGB (XYZ: list, white: str = "D50") -> list:
    """Convert values from CIE XYZ color space to linear RGB

    Arguments:
        XYZ: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        Linear RGB color data array
    """
    X,Y,Z = XYZ
    X /= 100
    Y /= 100
    Z /= 100
    # D65/2°
    if white == "D65":
        R = X *  3.2404542 + Y * -1.5371385 + Z * -0.4985314
        G = X * -0.9692660 + Y *  1.8760108 + Z *  0.0415560
        B = X *  0.0556434 + Y * -0.2040259 + Z *  1.0572252
    # D50/2°
    else:
        R = X *  3.1338561 + Y * -1.6168667 + Z * -0.4906146
        G = X * -0.9787684 + Y *  1.9161415 + Z *  0.0334540
        B = X *  0.0719453 + Y * -0.2289914 + Z *  1.4052427

    return [R,G,B]


def lRGB_sRGB (lRGB: list) -> list:
    """Convert values from linear RGB color space to sRGB

    Arguments:
        lRGB: The three-element color data array
    Returns:
        sRGB color data array
    """
    def function (t):
        if t > 0.0031308:
            return 1.055 * (t ** (1/2.4)) - 0.055
        else:
            return 12.92 * t

    R,G,B = lRGB
    return [
        function(R),
        function(G),
        function(B)]


def lRGB_XYZ (lRGB: list, white: str = "D50") -> list:
    """Convert values from linear RGB color space to CIE XYZ

    Arguments:
        lRGB: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        CIE XYZ color data array
    """
    R,G,B = lRGB
    R = R * 100
    G = G * 100
    B = B * 100
    # D65
    if white == "D65": return [
        R * 0.4124564 + G * 0.3575761 + B * 0.1804375 ,
        R * 0.2126729 + G * 0.7151522 + B * 0.0721750 ,
        R * 0.0193339 + G * 0.1191920 + B * 0.9503041 ]
    # D50
    return [
        R * 0.4360747 + G * 0.3850649 + B * 0.1430804 ,
        R * 0.2225045 + G * 0.7168786 + B * 0.0606169 ,
        R * 0.0139322 + G * 0.0971045 + B * 0.7141733 ]


def sRGB_lRGB (sRGB: list) -> list:
    """Convert values from sRGB color space to linear RGB

    Arguments:
        sRGB: The three-element color data array
    Returns:
        linear RGB color data array
    """
    def function (t):
        if t > 0.04045:
            return ((t + 0.055) / 1.055) ** 2.4
        else:
            return t / 12.92

    R,G,B = sRGB
    return [
        function(R),
        function(G),
        function(B)]


def lRGB_ACEScg (lRGB: list) -> list:
    """Convert values from linear RGB color space to ACEScg

    Generated using the XYZ Scaling
    on https://www.colour-science.org/apps/

    Arguments:
        lRGB: The three-element color data array
    Returns:
        ACEScg color data array
    """
    R,G,B = lRGB
    return [
        R * 0.6050374899 + G * 0.3297772590 + B * 0.0652703903,
        R * 0.0693938279 + G * 0.9192626515 + B * 0.0113133072,
        R * 0.0207546370 + G * 0.1074133069 + B * 0.8717796985]


def CMYK_XYZ (CMYK: list, CGATS: dict) -> list:
    """Convert values from CMYK color space to CIE XYZ

    Arguments:
        CMYK: The four-element color data array
        CGATS: The dictionary as colorimetric table
    Returns:
        CIE XYZ color data array
    """
    C,M,Y,K = CMYK
    measurement = 100.0
    nearCMYK = [0,0,0,0]
    nearXYZ = [0.0,0.0,0.0]

    for key, value in CGATS.items():
        CMYKi = [int(i) for i in key.split(",") ]
        XYZi  = value
        if CMYK == CMYKi:
            return XYZi
        Ci,Mi,Yi,Ki = CMYKi
        value = (
            abs(C-Ci) +
            abs(M-Mi) +
            abs(Y-Yi) +
            abs(K-Ki)) / 4
        if value < measurement:
            measurement = value
            nearCMYK = CMYKi
            nearXYZ = XYZi

    def getDirectionVector (point, channel):

        def getNearItem (data, index):

            def findNearItem (data, index, sign="+"):
                zero = data[index]
                data = data.copy()
                value = data[index]
                item  = None
                distance = 100
                for i in range(distance):
                    if sign == "+": value += 1
                    else: value -= 1
                    data[index] = value
                    key = ",".join(
                        [str(i) for i in data])
                    if key in CGATS:
                        item = key
                        distance = abs(value-zero)
                        break
                return (distance, item)

            distanceU, itemU = findNearItem(data, index, sign="+")
            distanceD, itemD = findNearItem(data, index, sign="-")
            if itemU is None and itemD is None:
                return (None, None)
            item = itemU
            distance = distanceU
            if distanceD < distanceU:
                item = itemD
                distance = distanceD

            return (distance, item)

        def getNewPair (data, index):
            data = data.copy()
            for i, value in enumerate(data):
                if i != index:
                    data[i] = 0
            key = ",".join([str(i) for i in data])
            if key in CGATS:
                return (data, CGATS.get(key))
            x, key = getNearItem(data, index)
            if not key: key = "0,0,0,0"
            data = [int(i) for i in key.split(",")]
            return (data, CGATS.get(key))

        zero = nearXYZ.copy()
        distance, item = getNearItem(point, channel)
        if item is None:
            point, zero = getNewPair(point, channel)
            distance, item = getNearItem(point, channel)
        near = CGATS.get(item)
        return [
            (near[0]-zero[0])/distance ,
            (near[1]-zero[1])/distance ,
            (near[2]-zero[2])/distance ]

    XYZ = nearXYZ.copy()
    for channel, value in enumerate(nearCMYK):
        distance = value - CMYK[channel]
        if abs(distance) > 0:
            direction = getDirectionVector(nearCMYK, channel)
            XYZ = [
                XYZ[0] + direction[0] * distance ,
                XYZ[1] + direction[1] * distance ,
                XYZ[2] + direction[2] * distance ]

    return XYZ


def notZero (data: Union[list, float]) -> Union[list, float]:
    """Replace zero values with a value close to zero

    Arguments:
        data: Color data array or single color channel
    Returns:
        Changed array or value
    """
    zero = 0.0000001
    if type(data) is list:
        for index, value in enumerate(data):
            if value == 0.0:
                data[index] = zero
        return data
    elif type(data) is float:
        if data == 0.0:
            data = zero
        return data


def rangeHue (hue: Union[int, float]) -> Union[int, float]:
    """Set the hue value to standard range

    Arguments:
        hue: The value of the hue channel
    Returns:
        Changed hue channel value
    """
    while hue > 360: hue -= 360
    while hue < 0  : hue += 360
    return hue


def differenceLightness (Lab1: list, Lab2: list) -> float:
    """Get the lightness difference of two CIE Lab colors

    Arguments:
        Lab1: The three-element color data array
        Lab2: The three-element color data array
    Returns:
        A difference as value
    """
    lightnessMax = 100
    L1, a1, b1 = Lab1
    L2, a2, b2 = Lab2
    return round(abs((L1-L2)/lightnessMax), 6)


def differenceChroma (Lab1: list, Lab2: list) -> float:
    """Get the chroma difference of two CIE Lab colors

    Arguments:
        Lab1: The three-element color data array
        Lab2: The three-element color data array
    Returns:
        A difference as value
    """
    chromaMax = 131.207
    L1, a1, b1 = Lab1
    L2, a2, b2 = Lab2
    chroma1 = (a1**2 + b1**2) ** 0.5
    chroma2 = (a2**2 + b2**2) ** 0.5
    return round(abs((chroma1-chroma2)/chromaMax), 6)


def differenceHue (Lab1: list, Lab2: list) -> float:
    """Get the hue difference of two CIE Lab colors

    Arguments:
        Lab1: The three-element color data array
        Lab2: The three-element color data array
    Returns:
        A difference as value
    """
    hueMax = 360
    L1, a1, b1 = notZero(Lab1)
    L2, a2, b2 = notZero(Lab2)
    hue1 = math.degrees(math.atan(b1/a1))
    hue2 = math.degrees(math.atan(b2/a2))

    if a1 > 0 > b1: hue1 += 360
    elif a1 < 0: hue1 += 180

    if a2 > 0 > b2: hue2 += 360
    elif a2 < 0: hue2 += 180

    hue = abs(hue1 - hue2)
    if hue > 180: hue = 360 - hue

    return round(hue/hueMax, 6)


def differenceLab (Lab1: list, Lab2: list) -> float:
    """Get the similarity of two CIE Lab colors

    Arguments:
        Lab1: The three-element color data array
        Lab2: The three-element color data array
    Returns:
        A similarity as value
    """
    lightness = differenceLightness(Lab1, Lab2)
    chroma    = differenceChroma(Lab1, Lab2)
    hue       = differenceHue(Lab1, Lab2)
    return round((lightness+chroma+hue)/3, 6)


def getChroma (Lab: list) -> float:
    """Get chroma attribute from the CIE Lab color

    Arguments:
        Lab: The three-element color data array
    Returns:
       A chroma attribute value
    """
    L,a,b = Lab
    chromaMax = 131.207
    chroma = (a**2 + b**2) ** 0.5
    return round(chroma / chromaMax, 4)


def setChroma (Lab: list, chroma: float) -> list:
    """Set chroma attribute to the CIE Lab color

    Arguments:
        Lab: The three-element color data array
        chroma: The chroma attribute value
    Returns:
        CIE Lab color data array
    """
    L,a,b = notZero(Lab)
    signA = a / abs(a)
    signB = b / abs(b)
    A = abs(a)
    B = abs(b)
    chromaMax = 131.207
    C = chroma * chromaMax
    angle = math.atan(B/A)
    A = C * math.cos(angle)
    B = C * math.sin(angle)
    a = round(A * signA, 4)
    b = round(B * signB, 4)

    return [L,a,b]


def getHue (Lab: list) -> float:
    """Get hue from the CIE Lab color

    Arguments:
        Lab: The three-element color data array
    Returns:
        A hue value
    """
    L,a,b = notZero(Lab)
    hue = math.degrees(math.atan(b/a))
    if a > 0 > b: hue += 360
    elif a < 0: hue += 180
    return hue


def setHue (Lab: list, hue: Union[int, float]) -> list:
    """Set hue to the CIE Lab color

    Arguments:
        Lab: The three-element color data array
        hue: The hue value
    Returns:
        CIE Lab color data array
    """
    L,a,b = Lab
    chroma = getChroma(Lab)
    hue = rangeHue(hue)
    signA = 1
    signB = 1
    if hue > 270:
        hue -= 360
        signB *= -1
    elif hue > 180:
        hue -= 180
        signA *= -1
        signB *= -1
    elif hue > 90:
        hue -= 180
        signA *= -1
    radians = math.radians(hue)
    tangent = math.tan(radians)
    A = abs(b / notZero(tangent))
    B = abs(a * tangent)
    a = A * signA
    b = B * signB
    Lab = [L,a,b]

    return setChroma(Lab, chroma)


def clampBlack (ABC: list) -> list:
    """Set value of the channel
    to 0.0 if it's negative one

    Arguments:
        ABC: The three-element color data array
    Returns:
        A changed color data array
    """
    A,B,C = ABC
    def cut (value):
        if value < 0.0:
            return 0.0
        return value
    return [cut(A), cut(B), cut(C)]


def clampWhite (ABC: list) -> list:
    """Set value of the channel
    to 1.0 if it's bigger one

    Arguments:
        ABC: The three-element color data array
    Returns:
        A changed color data array
    """
    A,B,C = ABC
    def cut (value):
        if value > 1.0:
            return 1.0
        return value
    return [cut(A), cut(B), cut(C)]


def clamp (ABC: list) -> list:
    """Set values of channels
    to a closed unit interval

    Arguments:
        ABC: The three-element color data array
    Returns:
        A changed color data array
    """
    ABC = clampBlack(ABC)
    ABC = clampWhite(ABC)
    return ABC


def sRGB_iRGB (sRGB: list) -> list:
    """Convert RGB values from floats to integers

    Arguments:
        sRGB: The three-element color data array
    Returns:
        A color data array
    """
    R,G,B = clamp(sRGB)
    return [int(R*255), int(G*255), int(B*255)]


def iRGB_sRGB (iRGB: list) -> list:
    """Convert RGB values from integers to floats

    Arguments:
        iRGB: The three-element color data array
    Returns:
        A color data array
    """
    R,G,B = iRGB
    return [R/255, G/255, B/255]


def iRGB_HEX (iRGB: list) -> str:
    """Convert integer RGB values to HEX color code

    Arguments:
        iRGB: The three-element color data array
    Returns:
        A HEX color code
    """
    R,G,B = iRGB
    return f"#{R:02X}{G:02X}{B:02X}"


def HEX_iRGB (string: str) -> list:
    """Convert HEX color code to integer RGB values

    Arguments:
        string: The HEX color code
    Returns:
        A color data array
    """
    string = string.replace("#", "")
    R = string[:2]
    G = string[2:4]
    B = string[4:]
    return [int(R,16), int(G,16), int(B,16)]


def sRGB_XYZ (sRGB: list, white: str = "D50") -> list:
    """Convert values from sRGB color space to CIE XYZ

    Arguments:
        sRGB: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        CIE XYZ color data array
    """
    lRGB = sRGB_lRGB(sRGB)
    return lRGB_XYZ(lRGB, white=white)


def sRGB_HEX (sRGB: list) -> str:
    """Convert values from sRGB color space to HEX color code

    Arguments:
        sRGB: The three-element color data array
    Returns:
        A HEX color code
    """
    iRGB = sRGB_iRGB(sRGB)
    return iRGB_HEX(iRGB)


def lRGB_Lab (lRGB: list) -> list:
    """Convert values from linear RGB color space to CIE Lab

    Arguments:
        lRGB: The three-element color data array
    Returns:
        CIE Lab color data array
    """
    XYZ = lRGB_XYZ(lRGB)
    return XYZ_Lab(XYZ)


def lRGB_HEX (lRGB: list) -> str:
    """Convert values from linear RGB color space to HEX color code

    Arguments:
        lRGB: The three-element color data array
    Returns:
        A HEX color code
    """
    sRGB = lRGB_sRGB(lRGB)
    return sRGB_HEX(sRGB)


def iRGB_XYZ (iRGB: list, white: str = "D50") -> list:
    """Convert integer RGB values to CIE XYZ color space

    Arguments:
        iRGB: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        CIE XYZ color data array
    """
    sRGB = iRGB_sRGB(iRGB)
    return sRGB_XYZ(sRGB, white=white)


def XYZ_sRGB (XYZ: list, white: str = "D50") -> list:
    """Convert values from CIE XYZ color space to sRGB

    Arguments:
        XYZ: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        sRGB color data array
    """
    lRGB = XYZ_lRGB(XYZ, white=white)
    return lRGB_sRGB(lRGB)


def XYZ_ACEScg (XYZ: list) -> list:
    """Convert values from CIE XYZ color space to ACEScg

    Arguments:
        XYZ: The three-element color data array
    Returns:
        ACEScg color data array
    """
    lRGB = XYZ_lRGB(XYZ)
    return lRGB_ACEScg(lRGB)


def XYZ_iRGB (XYZ: list, white: str = "D50") -> list:
    """Convert values from CIE XYZ color space to integer RGB values

    Arguments:
        XYZ: The three-element color data array
    Keyword Arguments:
        white: Reference white (D50, D65)
    Returns:
        A color data array
    """
    sRGB = XYZ_sRGB(XYZ, white=white)
    return sRGB_iRGB(sRGB)


def XYZ_HEX (XYZ: list) -> str:
    """Convert values from CIE XYZ color space to HEX color code

    Arguments:
        XYZ: The three-element color data array
    Returns:
        A HEX color code
    """
    lRGB = XYZ_lRGB(XYZ)
    return lRGB_HEX(lRGB)


def HEX_sRGB (string: str) -> list:
    """Convert HEX color code to sRGB color space values

    Arguments:
        string: The HEX color code
    Returns:
        sRGB color data array
    """
    iRGB = HEX_iRGB(string)
    return iRGB_sRGB(iRGB)


def HEX_lRGB (string: str) -> list:
    """Convert HEX color code to linear RGB color space values

    Arguments:
        string: The HEX color code
    Returns:
        Linear RGB color data array
    """
    sRGB = HEX_sRGB(string)
    return sRGB_lRGB(sRGB)


def HEX_ACEScg (string: str) -> list:
    """Convert HEX color code to ACEScg color space values

    Arguments:
        string: The HEX color code
    Returns:
        ACEScg color data array
    """
    lRGB = HEX_lRGB(string)
    return lRGB_ACEScg(lRGB)


def HEX_XYZ (string: str) -> list:
    """Convert HEX color code to CIE XYZ color space values

    Arguments:
        string: The HEX color code
    Returns:
        CIE XYZ color data array
    """
    lRGB = HEX_lRGB(string)
    return lRGB_XYZ(lRGB)


def HEX_Lab (string: str) -> list:
    """Convert HEX color code to CIE Lab color space values

    Arguments:
        string: The HEX color code
    Returns:
        CIE Lab color data array
    """
    XYZ = HEX_XYZ(string)
    return XYZ_Lab(XYZ)


def Lab_lRGB (Lab: list) -> list:
    """Convert values from CIE Lab color space to linear RGB

    Arguments:
        Lab: The three-element color data array
    Returns:
        Linear RGB color data array
    """
    XYZ = Lab_XYZ(Lab)
    return XYZ_lRGB(XYZ)


def Lab_sRGB (Lab: list) -> list:
    """Convert values from CIE Lab color space to sRGB

    Arguments:
        Lab: The three-element color data array
    Returns:
        sRGB color data array
    """
    lRGB = Lab_lRGB(Lab)
    return lRGB_sRGB(lRGB)


def Lab_ACEScg (Lab: list) -> list:
    """Convert values from CIE Lab color space to ACEScg

    Arguments:
        Lab: The three-element color data array
    Returns:
        ACEScg color data array
    """
    lRGB = Lab_lRGB(Lab)
    return lRGB_ACEScg(lRGB)


def Lab_iRGB (Lab: list) -> list:
    """Convert values from CIE Lab color space to integer RGB values

    Arguments:
        Lab: The three-element color data array
    Returns:
        A color data array
    """
    sRGB = Lab_sRGB(Lab)
    return sRGB_iRGB(sRGB)


def Lab_HEX (Lab: list) -> str:
    """Convert values from CIE Lab color space to HEX color code

    Arguments:
        Lab: The three-element color data array
    Returns:
        A HEX color code
    """
    lRGB = Lab_lRGB(Lab)
    return lRGB_HEX(lRGB)
