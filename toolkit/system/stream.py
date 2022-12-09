#!/usr/bin/env python

"""
Load and Save Data

Functions to communicate with data that is stored on a hard drive.
"""

import json
from toolkit.ensure.QtCore import *
from typing import Union


def fileread (path: str) -> str:
    """Read the file as a text data

    Arguments:
        path: The fully qualified file path
    Returns:
        The text data
    """
    data = ""
    with open(path, "r") as file:
        data = file.read()
    return data


def filewrite (path: str, data: str) -> None:
    """Write the text data to the file

    Arguments:
        path: The fully qualified file path
        data: The text data
    """
    with open(path, "w") as file:
        file.write(data)


def dataread (path: str) -> Union[dict, list, None]:
    """Load a JSON file from disk

    Arguments:
        path: The fully qualified file path
    Returns:
        The JSON data
    """
    with open(path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def datawrite (path: str, data: Union[dict, list]) -> None:
    """Save a data as a JSON file

    Arguments:
        path: The fully qualified file path
        data: The JSON data
    """
    with open(path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def validJSON (path):
    """Check if a JSON file could be read

    Arguments:
        path: The fully qualified file path
    Returns:
        A result of the check
    """
    try: 
        data = dataread(path)
        if not data:
            return False
    except:
        return False
    
    return True


def readCGATS () -> dict:
    """Create a colorimetric table data
    where key is CMYK value string
    and value is CIE XYZ color data array

    Returns:
        The colorimetric table data
    """
    CGATS = dict()

    file = QtCore.QFile(":/data/cgats")
    file.open(QtCore.QIODevice.ReadOnly)
    ByteArray = file.readAll()
    data = ByteArray.data().decode("utf-8")
    file.close()

    data = data.split("\n")
    data = [line.split(" ") for line in data]
    for pair in data:
        key = pair[0]
        value = [float(i) for i in pair[1].split(",") ]
        CGATS[key] = value

    return CGATS
