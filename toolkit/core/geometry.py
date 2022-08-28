#!/usr/bin/env python






def createPointsLine (scale, divisions):

    count  = divisions+2
    raws   = count-1

    center = count/2
    indexCenter = int((raws)/2)

    step = scale / raws / 2
    offset = step * ((count+1) % 2)

    line = []
    for index in range(count):
        if float(index) == raws/2:
            multiplier = 0
            direction  = 1
        elif index < center:
            multiplier = (indexCenter - index)*2
            direction  = -1
        else:
            multiplier = (indexCenter - (raws-index))*2
            direction  = 1
        x = (offset + step * multiplier) * direction
        x = round(x, 8)
        line.append(x)

    return line






def applyOffset (data, offset):

    for index, coord in enumerate(data):

        summation = map(
            lambda x, y: x+y,
            coord, offset )
        data[index] = list(summation)

    return data






def createPlanePoints (scale, divisions):

    pointsLine = createPointsLine(scale, divisions)

    points = []
    for z in reversed(pointsLine):
        for x in pointsLine:
            points.append((x,0.0,z))

    return points






def createPlaneNormals (divisions):

    lineCount = divisions + 2
    pointCount = lineCount ** 2

    return [[0,1,0]] * pointCount






def createPlaneTexCoord (scale, divisions):

    pointsLine = createPointsLine(scale, divisions)

    texCoord = []
    for v in pointsLine:
        for u in pointsLine:
            texCoord.append((u,v))
    texCoord = applyOffset(texCoord, [0.5, 0.5])

    return texCoord






def createPlaneFaceCounts (divisions):

    rowCount = divisions + 1
    faceCount = rowCount ** 2

    return [4] * faceCount






def createPlaneIndices (divisions):

    indices = []
    lineCount = divisions + 2
    pointsCount = lineCount ** 2

    for i in range(pointsCount-lineCount):
        if ((i+1) % lineCount) == 0:
            continue
        indices += [i, i+1, i+lineCount+1, i+lineCount]

    return indices
