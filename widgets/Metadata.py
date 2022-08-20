#!/usr/bin/env python



import os
import re

import toolkit.system.stream
import toolkit.core.timing






NAME = ".metadata.json"







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

        if not self.data.get("comments", None):
            self.data["comments"] = dict()

        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))


    def toThirdGen (self):

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
                        "published", toolkit.core.timing.getTimeCode())
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







class Metadata (object):


    def __init__ (self, path, metatype):

        self.default_data=dict()

        if metatype == "root":
            self.default_data = dict(
                generation=1,
                type="root",
                name=os.path.basename(path),
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
                generation=1,
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


        self.path = os.path.join(
            path, NAME)

        if not os.path.exists(self.path):
            self.default_settings(self.path)

        elif not toolkit.system.stream.validJSON(self.path):
            self.default_settings(self.path)



    def default_settings (self, path):
        toolkit.system.stream.datawrite(path, self.default_data)



    def load (self):

        data = toolkit.system.stream.dataread(self.path)
        
        if data.get("type") == "usdasset":
            generation = GenerationManager_usdasset(
                self.path, data, echo=False)
            if not generation.isCurrent():
                data = generation.getCurrent()

        return data



    def save (self, data):
        toolkit.system.stream.datawrite(self.path, data)







class MetadataManager (object):


    def __init__ (self, path, metatype):

        self.path = path
        self.metatype = metatype


    def __enter__(self):

        self.data = Metadata(self.path, self.metatype).load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        Metadata(self.path, self.metatype).save(self.data)
