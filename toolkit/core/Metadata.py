#!/usr/bin/env python



import os
import re
import tempfile

import toolkit.system.stream as stream
import toolkit.core.timing as timing

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






def getStatus (path):

    status = ""
    metadataPath = os.path.join(path, METAFILE)

    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            status = data.get("status", "")

    return status






def getID (path, filename):

    ID = None

    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)

            items = data.get("items", dict())
            itemdata = items.get(filename, dict())
            ID = itemdata.get("id", None)

    return ID






def generateID (
        libraries=None,
        asset="usdmaterial" ):
    
    if not libraries:
        libraries = os.getenv("ASSETLIBS", "")

    exists = True
    while exists:

        ID = next(tempfile._get_candidate_names())
        exists = False

        for root in libraries.split(":"):

            path = os.path.join(root, METAFILE)
            if not os.path.exists(path): continue
            if not stream.validJSON(path): continue

            data = stream.dataread(path)
            if ID in data.get(asset, {}):
                exists = True
                break

    return ID






def findMaterial (ID):

    libraries = os.getenv("ASSETLIBS", "")
    for root in libraries.split(":"):

        path = os.path.join(root, METAFILE)
        if not os.path.exists(path): continue
        if not stream.validJSON(path): continue

        data = stream.dataread(path)
        assets = data.get("usdmaterial", {})
        if ID in assets:
            asset = assets.get(ID)
            asset = f"{root}{asset}"
            
            if os.path.exists(asset):
                return asset






def buildMaterialData (library, root=None, collector=None):

    if root == None:
        root = library

    if collector == None:
        collector = dict()

    for name in os.listdir(root):

        path = os.path.join(root, name)
        itemType = getType(path)

        if itemType == "usdasset":
            continue

        elif itemType == "usdmaterial":
            directory = path.replace(library, "")

            with MetadataManager(
                path, update=False) as data:

                items = data.get("items", [])
                for file, attributes in items.items():
                    ID = attributes["id"]
                    path = "{}/{}".format(directory, file)
                    collector[ID] = path

        elif os.path.isdir(path):
            collector = buildMaterialData(
                library, root=path,
                collector=collector )

    return collector






def refreshMaterialData (library):

    with MetadataManager(library) as data:
        materialdata = buildMaterialData(library)
        
        data["usdmaterial"] = materialdata
        data["scantime"] = timing.getTimeCode()







class GenerationManager_root (object):


    def __init__ (self, path, data, echo=False):
        self.path = path
        self.data = data
        self.echo = echo


    def isCurrent (self):
        
        version = self.getGeneration()
        if version != 3:
            return False
        else:
            return True


    def getCurrent (self):

        version = self.getGeneration()

        if version == 1:
            self.toSecondGen()
            version = 2

        if version == 2:
            self.toThirdGen()
            version = 3

        return self.data


    def getGeneration (self):

        version = self.data.get("generation")
        return version


    def toSecondGen (self):
        self.data["generation"] = 2

        self.data["usdmaterial"] = dict()

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))


    def toThirdGen (self):
        self.data["generation"] = 3

        root = os.path.dirname(self.path)
        materialdata = buildMaterialData(root)
        self.data["usdmaterial"] = materialdata

        self.data["scantime"] = timing.getTimeCode()

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 3rd generation '
                + 'for "{}"'.format(self.path))







class GenerationManager_usdasset (object):


    def __init__ (self, path, data, echo=False):
        self.path = path
        self.data = data
        self.echo = echo


    def isCurrent (self):
        
        version = self.getGeneration()
        if version != 4:
            return False
        else:
            return True


    def getCurrent (self):

        version = self.getGeneration()

        if version == 1:
            self.toSecondGen()
            version = 2

        if version == 2:
            self.toThirdGen()
            version = 3

        if version == 3:
            self.toFourthGen()
            version = 4

        return self.data


    def getGeneration (self):

        if self.data.get("generation"):
            version = self.data.get("generation")
        elif type(self.data.get("tags", None)) is list:
            version = 3
        elif type(self.data.get("comments", None)) is dict:
            version = 2
        else:
            version = 1

        return version


    def toSecondGen (self):
        self.data["generation"] = 2

        if not self.data.get("comments", None):
            self.data["comments"] = dict()

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))


    def toThirdGen (self):
        self.data["generation"] = 3

        if not self.data.get("tags", None):
            self.data["tags"] = []

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 3rd generation '
                + 'for "{}"'.format(self.path))


    def toFourthGen (self):
        self.data["generation"] = 4

        items = dict()
        path = os.path.dirname(self.path)
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]*$", name):
                if not re.search(r"\.Final[-\.]{1}", name):
                    item = dict()
                    comment = self.data.get(
                        "comments", dict()).get(name, "")
                    timecode = self.data.get(
                        "published", timing.getTimeCode())
                    item["comment"] = comment
                    item["published"] = timecode
                    items[name] = item
        self.data["items"] = items

        self.data.pop("published")
        self.data.pop("comments")

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 4th generation '
                + 'for "{}"'.format(self.path))







class GenerationManager_usdmaterial (object):


    def __init__ (self, path, data, echo=False):
        self.path = path
        self.data = data
        self.echo = echo


    def isCurrent (self):
        
        version = self.getGeneration()
        if version != 2:
            return False
        else:
            return True


    def getCurrent (self):

        version = self.getGeneration()

        if version == 1:
            self.toSecondGen()
            version = 2

        return self.data


    def getGeneration (self):

        version = self.data.get("generation")
        return version


    def toSecondGen (self):
        self.data["generation"] = 2

        items = self.data.get("items", [])
        for file, attributes in items.items():
            attributes["id"] = generateID()
        
        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))







class Metadata (object):


    def __init__ (self, path, metatype=None):

        self.default_data=dict()

        if not metatype:
            metatype = getType(path)

        if metatype == "root":
            self.default_data = dict(
                generation=3,
                type="root",
                name=os.path.basename(path),
                scantime=timing.getTimeCode(),
                usdmaterial=dict(),
                info="" )

        elif metatype == "usdasset":
            self.default_data = dict(
                generation=4,
                type="usdasset",
                info="",
                tags=[],
                items=dict(),
                status="WIP" )

        elif metatype == "usdmaterial":
            self.default_data = dict(
                generation=2,
                type="usdmaterial",
                info="",
                tags=[],
                items=dict(),
                status="WIP" )

        elif metatype == "foldercolors":
            self.default_data = dict(
                generation=1,
                type="foldercolors",
                info="" )

        else: return


        self.path = os.path.join(
            path, METAFILE)

        if not os.path.exists(self.path):
            self.default_settings(self.path)

        elif not stream.validJSON(self.path):
            self.default_settings(self.path)



    def default_settings (self, path):
        stream.datawrite(path, self.default_data)



    def load (self):

        data = stream.dataread(self.path)
        dataType = data.get("type")
        
        if dataType == "root":
            generation = GenerationManager_root(
                self.path, data, echo=False)
            if not generation.isCurrent():
                data = generation.getCurrent()
                self.save(data)

        elif dataType == "usdasset":
            generation = GenerationManager_usdasset(
                self.path, data, echo=False)
            if not generation.isCurrent():
                data = generation.getCurrent()
                self.save(data)

        elif dataType == "usdmaterial":
            generation = GenerationManager_usdmaterial(
                self.path, data, echo=False)
            if not generation.isCurrent():
                data = generation.getCurrent()
                self.save(data)

        return data



    def save (self, data):
        stream.datawrite(self.path, data)







class MetadataManager (object):


    def __init__ (self, path, metatype=None, update=True):

        self.path = path
        self.metatype = metatype

        self.update = update


    def __enter__(self):

        self.data = Metadata( self.path,
            metatype=self.metatype ).load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            Metadata( self.path,
                metatype=self.metatype ).save(self.data)
