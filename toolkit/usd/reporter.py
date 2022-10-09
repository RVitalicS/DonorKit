#!/usr/bin/env python


import os, re

from toolkit.usd import read






def getUsdReferences (path, container=None):

    if container == None:
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






def getResolvedSize (path):

    sizeMegabytes = 0
    for reference in getUsdReferences(path):
        sizeBytes = os.path.getsize(reference)
        sizeMegabytes += (sizeBytes/1000000)

    return "{:0.2f}".format(sizeMegabytes)
