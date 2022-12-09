#!/usr/bin/env python

"""
Reporter

Functions to get some information about a USD file.
"""

import os
from toolkit.usd import read
from typing import Union


def getUsdReferences (path: str, container: Union[None, list] = None) -> list:
    """Find the paths of all layers referred to by reference, payload,
    and sublayer fields in this layer and in all referenced layers.

    Arguments:
        path: The path to the USD file
    Keyword Arguments:
        container: The exchange data object for the iterations
    Returns:
        The paths of all dependent assets
    """
    if container is None:
        container = []
    root = os.path.dirname(path)
    if path not in container:
        container.append(path)
    for reference in read.asReferences(path):
        container = getUsdReferences(
            reference, container=container)

    cleaned = []
    for item in container:
        if item not in cleaned:
            cleaned.append(item)
    return container


def getResolvedSize (path: str) -> str:
    """Get size of the USD file with its dependencies

    Arguments:
        path: The path to the USD file
    Returns:
        The formatted size in Megabytes
    """
    sizeMegabytes = 0
    for reference in getUsdReferences(path):
        sizeBytes = os.path.getsize(reference)
        sizeMegabytes += (sizeBytes/1000000)
    return f"{sizeMegabytes:0.2f}"
