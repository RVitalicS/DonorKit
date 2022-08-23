#!/usr/bin/env python



import os

import toolkit.system.stream as stream






METAFILE = ".metadata.json"







def getType (path):

    metadataPath = os.path.join(path, METAFILE)

    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)

            return data.get("type")







def getInfo (path):

    info = ""
    metadataPath = os.path.join(path, METAFILE)

    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            info = data.get("info", "")

    return info






def getComment (path, filename):

    comment = ""

    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)

            items = data.get("items", dict())
            itemdata = items.get(filename, dict())
            comment = itemdata.get("comment", "")

    return comment