#!/usr/bin/env python



import os
import re

import toolbox.system.stream
import toolbox.core.timing






NAME = ".metadata.json"







class Metadata (object):


    def __init__ (self, path, metatype):

        self.default_data=dict()

        if metatype == "root":
            self.default_data = dict(
                type="root",
                info="",
                name=os.path.basename(path) )

        elif metatype == "usdasset":
            self.default_data = dict(
                generation=4,
                type="usdasset",
                info="",
                tags=[],
                items=dict(),
                status="WIP" )


        self.path = os.path.join(
            path, NAME)

        if not os.path.exists(self.path):
            self.default_settings(self.path)

        elif not toolbox.system.stream.validJSON(self.path):
            self.default_settings(self.path)



    def default_settings (self, path):
        toolbox.system.stream.datawrite(path, self.default_data)



    def load (self):

        data = toolbox.system.stream.dataread(self.path)
        data = self.restructure(data)

        return data



    def save (self, data):
        toolbox.system.stream.datawrite(self.path, data)



    def getGeneration (self, data):

        if data.get("generation"):
            generation = data.get("generation")
        elif type(data.get("tags", None)) is list:
            generation = 3
        elif type(data.get("comments", None)) is dict:
            generation = 2
        else:
            generation = 1

        return generation



    def restructure (self, data):

        generation = self.getGeneration(data)
        toNextGen = False

        if generation == 1:
            data = self.toSecondGen(data)
            toNextGen = True
            generation = 2

        if generation == 2:
            data = self.toThirdGen(data)
            toNextGen = True
            generation = 3

        if generation == 3:
            data = self.toFourthGen(data)
            toNextGen = True
            generation = 4

        if toNextGen:
            self.save(data)

        return data



    def toSecondGen (self, data):

        if data.get("type") == "usdasset":
            if not data.get("comments", None):
                data["comments"] = dict()
        return data



    def toThirdGen (self, data):

        if data.get("type") == "usdasset":
            if not data.get("tags", None):
                data["tags"] = []
        return data



    def toFourthGen (self, data):
        
        data["generation"] = 4

        if data.get("type") == "usdasset":

            items = dict()
            path = os.path.dirname(self.path)
            for name in os.listdir(path):
                if re.search(r"\.usd[ac]*$", name):
                    if not re.search(r"\.Final[-\.]{1}", name):
                        item = dict()
                        comment = data.get(
                            "comments", dict()).get(name, "")
                        timecode = data.get(
                            "published", toolbox.core.timing.getTimeCode())
                        item["comment"] = comment
                        item["published"] = timecode
                        items[name] = item
            data["items"] = items

            data.pop("published")
            data.pop("comments")

        return data







class MetadataManager (object):


    def __init__ (self, path, metatype):

        self.path = path
        self.metatype = metatype


    def __enter__(self):

        self.data = Metadata(self.path, self.metatype).load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        Metadata(self.path, self.metatype).save(self.data)
