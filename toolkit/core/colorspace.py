#!/usr/bin/env python


import math







def Lab_XYZ ( Lab, white="D50" ):

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
        Z * 108.884 ]

    # CIE-L*ab (D50/2°)
    return [
        X * 96.4212,
        Y * 100.000,
        Z * 82.5219 ]




def XYZ_Lab ( XYZ, white="D50" ):

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
        500 * (X - Y) ,
        200 * (Y - Z) ]




def XYZ_lRGB ( XYZ, white="D50" ):

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

    return [ R,G,B ]




def lRGB_sRGB ( lRGB ):

    R,G,B = lRGB

    def function (t):
        
        if t > 0.0031308:
            return 1.055 * (t ** (1/2.4)) - 0.055
        else:
            return 12.92 * t

    return [
        function(R) ,
        function(G) ,
        function(B) ]




def lRGB_XYZ ( lRGB, white="D50" ):

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




def sRGB_lRGB ( sRGB ):

    R,G,B = sRGB

    def function (t):

        if t > 0.04045:
            return ((t + 0.055) / 1.055) ** 2.4
        else:
            return t / 12.92

    return [
        function(R) ,
        function(G) ,
        function(B) ]





def lRGB_ACEScg ( lRGB ):

    """
        Generated using the XYZ Scaling
        on https://www.colour-science.org/apps/
    """

    R,G,B = lRGB
    return [
        R * 0.6050374899 + G * 0.3297772590 + B * 0.0652703903 ,
        R * 0.0693938279 + G * 0.9192626515 + B * 0.0113133072 ,
        R * 0.0207546370 + G * 0.1074133069 + B * 0.8717796985 ]







def CMYK_XYZ ( CMYK, CGATS ):

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
            abs(K-Ki) ) / 4

        if value < measurement:
            measurement = value
            nearCMYK = CMYKi
            nearXYZ = XYZi



    def getDirectionVector (point, channel):



        def getNearItem (data, index):


            def findNearItem ( data, index, sign="+" ):

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
                        [str(i) for i in data] )

                    if key in CGATS:
                        item = key
                        distance = abs(value-zero)
                        break

                return (distance, item)


            distanceU, itemU = findNearItem(data, index, sign="+")
            distanceD, itemD = findNearItem(data, index, sign="-")

            if itemU == itemD == None:
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







def notZero ( data ):

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




def rangeHue (hue):

    while hue > 360: hue -= 360
    while hue < 0  : hue += 360

    return hue




def differenceLightness (Lab1, Lab2):

    lightnessMax = 100

    L1, a1, b1 = Lab1
    L2, a2, b2 = Lab2

    return abs( (L1 - L2) / lightnessMax )




def differenceChroma (Lab1, Lab2):

    chromaMax = 131.207

    L1, a1, b1 = Lab1
    L2, a2, b2 = Lab2

    chroma1 = (a1**2 + b1**2) ** 0.5
    chroma2 = (a2**2 + b2**2) ** 0.5

    return abs( (chroma1 - chroma2) / chromaMax )




def differenceHue (Lab1, Lab2):

    hueMax = 360

    L1, a1, b1 = notZero(Lab1)
    L2, a2, b2 = notZero(Lab2)

    hue1 = math.degrees( math.atan(b1/a1) )
    hue2 = math.degrees( math.atan(b2/a2) )

    if a1 > 0 > b1: hue1 += 360
    elif a1 < 0: hue1 += 180

    if a2 > 0 > b2: hue2 += 360
    elif a2 < 0: hue2 += 180

    hue = abs(hue1 - hue2)
    if hue > 180: hue = 360 - hue

    return hue / hueMax




def differenceLab (Lab1, Lab2):

    lightness = differenceLightness(Lab1, Lab2)
    chroma    = differenceChroma(Lab1, Lab2)
    hue       = differenceHue(Lab1, Lab2)

    return (lightness + chroma + hue) / 3




def getChroma (Lab):

    L,a,b = Lab

    chromaMax = 131.207
    chroma = (a**2 + b**2) ** 0.5

    return chroma / chromaMax




def setChroma (Lab, chroma):

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

    a = A * signA
    b = B * signB

    return [ L,a,b ]




def getHue (Lab):

    L,a,b = notZero(Lab)
    hue = math.degrees( math.atan(b/a) )

    if a > 0 > b: hue += 360
    elif a < 0: hue += 180

    return hue




def setHue (Lab, hue):

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


    radians = math.radians( hue )
    tangens = math.tan( radians )

    A = abs(b / notZero(tangens))
    B = abs(a * tangens)

    a = A * signA
    b = B * signB

    Lab = [ L,a,b ]

    return setChroma(Lab, chroma)







def clampBlack ( ABC ):

    A,B,C = ABC
    def cut (value):
        if value < 0.0: return 0.0
        return value
    return [ cut(A), cut(B), cut(C) ]


def clampWhite ( ABC ):

    A,B,C = ABC
    def cut (value):
        if value > 1.0: return 1.0
        return value
    return [ cut(A), cut(B), cut(C) ]


def clamp ( ABC ):

    ABC = clampBlack(ABC)
    ABC = clampWhite(ABC)
    return ABC







def sRGB_iRGB ( sRGB ):

    R,G,B = clamp(sRGB)
    return [ int(R*255), int(G*255), int(B*255)]




def iRGB_sRGB ( iRGB ):

    R,G,B = iRGB
    return [ R/255, G/255, B/255 ]







def iRGB_HEX ( iRGB ):

    R,G,B = iRGB
    return "#{:02X}{:02X}{:02X}".format( R,G,B )




def HEX_iRGB ( string ):

    string = string.replace("#", "")

    R = string[:2]
    G = string[2:4]
    B = string[4:]

    return [int(R, 16), int(G, 16), int(B, 16)]







def sRGB_XYZ ( sRGB, white="D50" ):

    lRGB = sRGB_lRGB ( sRGB )
    return lRGB_XYZ( lRGB, white=white )




def sRGB_HEX ( sRGB ):

    iRGB = sRGB_iRGB( sRGB )
    return iRGB_HEX( iRGB )







def lRGB_Lab ( lRGB ):

    XYZ = lRGB_XYZ ( lRGB )
    return XYZ_Lab ( XYZ )




def lRGB_HEX ( lRGB ):

    sRGB = lRGB_sRGB( lRGB )
    return sRGB_HEX( sRGB )







def iRGB_XYZ ( iRGB, white="D50" ):

    sRGB = iRGB_sRGB ( iRGB )
    return sRGB_XYZ( sRGB, white=white )







def XYZ_sRGB ( XYZ, white="D50" ):

    lRGB = XYZ_lRGB ( XYZ, white=white )
    return lRGB_sRGB ( lRGB )




def XYZ_ACEScg ( XYZ ):

    lRGB = XYZ_lRGB( XYZ )
    return lRGB_ACEScg( lRGB )




def XYZ_iRGB ( XYZ, white="D50" ):

    sRGB = XYZ_sRGB ( XYZ, white=white )
    return sRGB_iRGB( sRGB )




def XYZ_HEX ( XYZ ):

    lRGB = XYZ_lRGB( XYZ )
    return lRGB_HEX( lRGB )







def HEX_sRGB ( string ):

    iRGB = HEX_iRGB( string )
    return iRGB_sRGB( iRGB )




def HEX_lRGB ( string ):

    sRGB = HEX_sRGB( string )
    return sRGB_lRGB( sRGB )




def HEX_ACEScg ( string ):

    lRGB = HEX_lRGB( string )
    return lRGB_ACEScg( lRGB )




def HEX_XYZ ( string ):

    lRGB = HEX_lRGB( string )
    return lRGB_XYZ( lRGB )




def HEX_Lab ( string ):

    XYZ = HEX_XYZ( string )
    return XYZ_Lab( XYZ )






def Lab_lRGB ( Lab ):

    XYZ = Lab_XYZ( Lab )
    return XYZ_lRGB( XYZ )




def Lab_sRGB ( Lab ):

    lRGB = Lab_lRGB( Lab )
    return lRGB_sRGB( lRGB )



def Lab_ACEScg ( Lab ):

    lRGB = Lab_lRGB( Lab )
    return lRGB_ACEScg( lRGB )




def Lab_iRGB ( Lab ):

    sRGB = Lab_sRGB( Lab )
    return sRGB_iRGB( sRGB )




def Lab_HEX ( Lab ):

    lRGB = Lab_lRGB( Lab )
    return lRGB_HEX( lRGB )
