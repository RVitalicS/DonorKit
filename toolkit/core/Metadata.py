#!/usr/bin/env python

"""
Metadata

Implement a central metadata manager with utility functions.
"""

import os
import re
import tempfile
import toolkit.system.stream as stream
import toolkit.core.timing as timing
from typing import Optional
from typing import Union

# name for hidden files that describe library items
METAFILE = ".metadata.json"


def getType (path: str) -> Union[str, None]:
    """Get a type name of the specified library item
    (root, usdasset, usdmaterial, foldercolors, etc.)

    Arguments:
        path: The directory that is library item
    Returns:
        A type name of library item
    """
    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            return data.get("type")


def getInfo (path: str) -> str:
    """Get an informational text of the specified library item

    Arguments:
        path: The directory that is library item
    Returns:
        An informational text
    """
    info = ""
    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            info = data.get("info", "")
    return info


def getComment (path: str, filename: str) -> str:
    """Get a commentary of the specified asset item

    Arguments:
        path: The root directory where the asset's items lie
        filename: The name of the file
    Returns:
        A commentary
    """
    comment = ""
    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)

            items = data.get("items", dict())
            itemdata = items.get(filename, dict())
            comment = itemdata.get("comment", "")
    return comment


def getStatus (path: str) -> str:
    """Get a status name for the specified asset

    Arguments:
        path: The root directory where the asset's items lie
    Returns:
        A status name
    """
    status = ""
    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            status = data.get("status", "")
    return status


def getID (path: str, filename: str) -> Union[str, None]:
    """Get an ID of the specified asset item

    Arguments:
        path: The root directory where the asset's items lie
        filename: The name of the file
    Returns:
        An ID string
    """
    metadataPath = os.path.join(path, METAFILE)
    if os.path.exists(metadataPath):
        if stream.validJSON(metadataPath):
            data = stream.dataread(metadataPath)
            items = data.get("items", dict())
            itemdata = items.get(filename, dict())
            return itemdata.get("id", None)


def generateID (
        libraries: Optional[str] = None,
        asset: str = "usdmaterial" ) -> Union[str, None]:
    """Generate a unique ID string.
    Check that libraries doesn't already have that ID

    Keyword Arguments:
        libraries: The root directories of the libraries
                   (':' separated list of paths)
        asset: The type name to check in libraries
    Returns:
        An ID string
    """
    if not libraries:
        libraries = os.getenv("ASSETLIBS", None)
        if libraries is None:
            return
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


def findMaterial (ID: str) -> Union[str, None]:
    """Find a material file in libraries using the ID

    Arguments:
        ID: The ID string
    Returns:
        A path to a material file
    """
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


def buildMaterialData (
        library: str,
        root: Optional[str] = None,
        collector: Optional[dict] = None) -> dict:
    """Scan hard drive locations and create a dictionary
    where key is an ID and value is a relative path

    Arguments:
        library: The root directory of the library
    Keyword Arguments:
        root: The point (path) of the current iteration
        collector: The exchange data object for the iterations
    Returns:
        A dictionary of library items
    """
    if root is None:
        root = library
    if collector is None:
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


def refreshMaterialData (library: str) -> None:
    """Renew material locations in a library description file

    Arguments:
        library: The root directory of the library
    """
    with MetadataManager(library) as data:
        materialdata = buildMaterialData(library)
        data["usdmaterial"] = materialdata
        data["scantime"] = timing.getTimeCode()


class GenerationManager_root (object):
    """A class for 'library root' items,
    to update structure of data to actually used one.

    Arguments:
        path: The directory that is 'library root' item
        data: The dictionary with 'library root' item description
    Keyword Arguments:
        echo: A flag used to print changes of the data
    """

    def __init__ (self, path: str, data: dict, echo: bool = False) -> None:
        self.path = path
        self.data = data
        self.echo = echo

    def isCurrent (self) -> bool:
        """Check if the generation
        of the data is the last one

        Returns:
            A result of the check
        """
        version = self.getGeneration()
        if version != 3:
            return False
        else:
            return True

    def getCurrent (self) -> dict:
        """Get data in an expected (updated) form 

        Returns:
            A library item description data
        """
        version = self.getGeneration()
        if version == 1:
            self.toSecondGen()
            version = 2
        if version == 2:
            self.toThirdGen()
            version = 3
        return self.data

    def getGeneration (self) -> int:
        """Get the current generation of the data 

        Returns:
            The generation number
        """
        version = self.data.get("generation")
        return version

    def toSecondGen (self) -> None:
        """Update data to the second generation"""
        self.data["generation"] = 2
        self.data["usdmaterial"] = dict()
        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))

    def toThirdGen (self) -> None:
        """Update data to the third generation"""
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
    """A class for 'usd asset' items,
    to update structure of data to actually used one.

    Arguments:
        path: The directory that is 'usd asset' item
        data: The dictionary with 'usd asset' item description
    Keyword Arguments:
        echo: A flag used to print changes of the data
    """

    def __init__ (self, path: str, data: dict, echo: bool = False) -> None:
        self.path = path
        self.data = data
        self.echo = echo

    def isCurrent (self) -> bool:
        """Check if the generation
        of the data is the last one

        Returns:
            A result of the check
        """
        version = self.getGeneration()
        if version != 4:
            return False
        else:
            return True

    def getCurrent (self) -> dict:
        """Get data in an expected (updated) form 

        Returns:
            A library item description data
        """
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

    def getGeneration (self) -> int:
        """Get the current generation of the data 

        Returns:
            The generation number
        """
        if self.data.get("generation"):
            version = self.data.get("generation")
        elif type(self.data.get("tags", None)) is list:
            version = 3
        elif type(self.data.get("comments", None)) is dict:
            version = 2
        else:
            version = 1
        return version

    def toSecondGen (self) -> None:
        """Update data to the second generation"""
        self.data["generation"] = 2
        if not self.data.get("comments", None):
            self.data["comments"] = dict()
        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))

    def toThirdGen (self) -> None:
        """Update data to the third generation"""
        self.data["generation"] = 3
        if not self.data.get("tags", None):
            self.data["tags"] = []
        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 3rd generation '
                + 'for "{}"'.format(self.path))

    def toFourthGen (self) -> None:
        """Update data to the fourth generation"""
        self.data["generation"] = 4
        items = dict()
        path = os.path.dirname(self.path)
        for name in os.listdir(path):
            if re.search(r"\.usd[ac]*$", name):
                if not re.search(r"\.Final[-.]", name):
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
    """A class for 'usd material' items,
    to update structure of data to actually used one.

    Arguments:
        path: The directory that is 'usd material' item
        data: The dictionary with 'usd material' item description
    Keyword Arguments:
        echo: A flag used to print changes of the data
    """

    def __init__ (self, path: str, data: dict, echo: bool = False) -> None:
        self.path = path
        self.data = data
        self.echo = echo

    def isCurrent (self) -> bool:
        """Check if the generation
        of the data is the last one

        Returns:
            A result of the check
        """
        version = self.getGeneration()
        if version != 2:
            return False
        else:
            return True

    def getCurrent (self) -> dict:
        """Get data in an expected (updated) form 

        Returns:
            A library item description data
        """
        version = self.getGeneration()
        if version == 1:
            self.toSecondGen()
            version = 2
        return self.data

    def getGeneration (self) -> int:
        """Get the current generation of the data 

        Returns:
            The generation number
        """
        version = self.data.get("generation")
        return version

    def toSecondGen (self) -> None:
        """Update data to the second generation"""
        self.data["generation"] = 2
        items = self.data.get("items", [])
        for file, attributes in items.items():
            attributes["id"] = generateID()
        if self.echo:
            print('INFO <Metadata>: '
                + 'changed to 2nd generation '
                + 'for "{}"'.format(self.path))


class Metadata (object):
    """A class to read and write metadata file,
    to create new one with default values
    and to control the right configuration.

    Arguments:
        path: The directory that is the library item
    Keyword Arguments:
        metatype: The type name of the library item
    """

    def __init__ (
            self, path: str,
            metatype: Optional[str] = None) -> None:
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

    def default_settings (self, path: str) -> None:
        """Create a metadata file with default values

        Arguments:
            path: The path to the metadata file
        """
        stream.datawrite(path, self.default_data)

    def load (self) -> dict:
        """Read a data from the metadata file
        and update if it's needed

        Returns:
            A library item description data
        """
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

    def save (self, data: dict) -> None:
        """Write the data to the metadata file

        Arguments:
            data: The library item description data
        """
        stream.datawrite(self.path, data)


class MetadataManager (object):
    """A context manager to work with metadata file

    Arguments:
        path: The directory that is the library item
    Keyword Arguments:
        metatype: The type name of the library item
        update: A flag used to write changes
    """

    def __init__ (
            self, path: str,
            metatype: Optional[str] = None,
            update: bool = True) -> None:
        self.path = path
        self.metatype = metatype
        self.update = update

    def __enter__(self) -> dict:
        """Get a data to work with

        Returns:
            The library item description data
        """
        self.data = Metadata(
            self.path,
            metatype=self.metatype).load()
        return self.data

    def __exit__(self, *args) -> None:
        """Optionally write the data"""
        if self.update:
            Metadata(
                self.path,
                metatype=self.metatype).save(self.data)
