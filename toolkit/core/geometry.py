#!/usr/bin/env python

"""
Geometry

Generate 3D mesh data.
"""


def createPointsLine (scale: float, divisions: int) -> list:
    """Create an array of coordinates for one axis
    that describes line divided into equal parts

    Arguments:
        scale: The length of a line in meter units
        divisions: The number of divisions to cut a line
    Returns:
        An array of coordinates for one axis
    """
    count  = divisions+2
    rows   = count-1
    center = count/2
    indexCenter = int(rows/2)
    step = scale / rows / 2
    offset = step * ((count+1) % 2)

    line = []
    for index in range(count):
        if float(index) == rows/2:
            multiplier = 0
            direction  = 1
        elif index < center:
            multiplier = (indexCenter - index)*2
            direction  = -1
        else:
            multiplier = (indexCenter - (rows-index))*2
            direction  = 1
        x = (offset + step * multiplier) * direction
        x = round(x, 8)
        line.append(x)

    return line


def applyOffset (data: list, offset: list) -> list:
    """A single iteration to sum values in two-element arrays

    Arguments:
        data: The array of two-dimensional arrays
        offset: The array with two values for addition
    Returns:
        A changed array
    """
    for index, coord in enumerate(data):
        summation = map(
            lambda x, y: x+y,
            coord, offset )
        data[index] = list(summation)
    return data


def createPlanePoints (scale: float, divisions: int) -> list:
    """Create an array of coordinates that describes a plane
    in three-dimensional space with equal length and breadth

    Arguments:
        scale: The length/breadth of a plane in meter units
        divisions: The number of subdivisions for a plane
    Returns:
        An array of three-dimensional coordinates
    """
    pointsLine = createPointsLine(scale, divisions)
    points = []
    for z in reversed(pointsLine):
        for x in pointsLine:
            points.append((x,0.0,z))
    return points


def createPlaneNormals (divisions: int) -> list:
    """Create an array of three-element arrays
    that is a 'Normal' attribute for a plane

    Arguments:
        divisions: The number of subdivisions for a plane
    Returns:
        An array of 'Normals' for each point of a plane
    """
    lineCount = divisions + 2
    pointCount = lineCount ** 2
    return [[0,1,0]] * pointCount


def createPlaneTexCoord (scale: float, divisions: int) -> list:
    """Create an array of two-element arrays
    that is texture coordinates for a plane

    Arguments:
        scale: The length/breadth of a plane in UV coordinates
        divisions: The number of subdivisions for a plane
    Returns:
        An array of texture coordinates
    """
    pointsLine = createPointsLine(scale, divisions)
    texCoord = []
    for v in pointsLine:
        for u in pointsLine:
            texCoord.append((u,v))
    texCoord = applyOffset(texCoord, [0.5, 0.5])
    return texCoord


def createPlaneFaceCounts (divisions: int) -> list:
    """Create an array of integers that is the number of points
    within each polygon for a plane

    Arguments:
        divisions: The number of subdivisions for a plane
    Returns:
        An array of counts of consecutive indices
        that define the polygon of a plane
    """
    rowCount = divisions + 1
    faceCount = rowCount ** 2
    return [4] * faceCount


def createPlaneIndices (divisions: int) -> list:
    """Create an array of the indices
    of each vertex of each face in a plane

    Arguments:
        divisions: The number of subdivisions for a plane
    Returns:
        An array of vertex indices
    """
    indices = []
    lineCount = divisions + 2
    pointsCount = lineCount ** 2
    for i in range(pointsCount-lineCount):
        if ((i+1) % lineCount) == 0:
            continue
        indices += [i, i+1, i+lineCount+1, i+lineCount]
    return indices
