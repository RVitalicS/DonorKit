#!/usr/bin/env python


import os
from . import tools


from Qt import QtGui






STATUS_LIST = [
    "Final",
    "Completed",
    "WIP" ]

PLACEHOLDER = (
    "Lorem ipsum dolor sit amet, " +
    "consectetur adipiscing elit, " +
    "sed do eiusmod tempor incididunt " +
    "ut labore et dolore magna aliqua.\n\n" +
    "Ut enim ad minim veniam, " +
    "quis nostrud exercitation " +
    "ullamco laboris nisi ut " +
    "aliquip ex ea commodo consequat."
)







class ExportData (object):


    def __init__ (self):

        self.defaults = dict(
            modelling=True,
            surfacing=True,
            animation=False,
            modellingOverwrite=False,
            surfacingOverwrite=False,
            animationOverwrite=False,
            rangeStart=1,
            rangeEnd=1,
            link=True,
            theme="dark" )

        self.path = os.path.join(
            os.path.dirname(__file__),
            "databank",
            ".AssetExportSettings.json")

        if not os.path.exists(self.path):
            self.defaultSettings(self.path)

        elif not tools.validJSON(self.path):
            self.defaultSettings(self.path)


    def defaultSettings (self, path):
        tools.datawrite(path, self.defaults)


    def load (self):
        return tools.dataread(self.path)


    def save (self, data):
        tools.datawrite(self.path, data)







class Export (object):


    def __init__ (self, update=True):

        self.update = update


    def __enter__(self):

        self.data = ExportData().load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            ExportData().save(self.data)







class ManagerData (object):


    def __init__ (self):

        self.defaults = dict(
            scrollPosition=0.0,
            iconSize=1,
            focusLibrary="",
            subdirLibrary="",
            bookmarks=[],
            favorites=[],
            favoriteFilter=False,
            theme="dark" )

        self.path = os.path.join(
            os.path.expanduser("~"),
            ".AssetManagerSettings.json")

        if not os.path.exists(self.path):
            self.defaultSettings(self.path)

        elif not tools.validJSON(self.path):
            self.defaultSettings(self.path)


    def defaultSettings (self, path):
        tools.datawrite(path, self.defaults)


    def load (self):
        return tools.dataread(self.path)


    def save (self, data):
        tools.datawrite(self.path, data)







class Manager (object):


    def __init__ (self, update=True):

        self.update = update


    def __enter__(self):

        self.data = ManagerData().load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            ManagerData().save(self.data)







FONT_FAMILY = os.getenv("FONT_FAMILY", "")


def makeFont (
    size   = int(),
    bold   = bool(),
    weight = int(),
    family = FONT_FAMILY ):


    font = QtGui.QFont()

    font.setPointSize(size)
    font.setBold(bold)
    font.setWeight(weight)

    if FONT_FAMILY:
        font.setFamily(FONT_FAMILY)


    return font







class DataClass: pass

UIGlobals = DataClass()


UIGlobals.Path = DataClass()
UIGlobals.Path.backIcon = 13
UIGlobals.Path.height   = 32
UIGlobals.Path.fontRoot = makeFont( size=9, bold=False, weight=50 )
UIGlobals.Path.fontPath = makeFont( size=9, bold=False, weight=50 )
UIGlobals.Path.bookmarkOffset = 1


UIGlobals.Bar = DataClass()
UIGlobals.Bar.height = 32
UIGlobals.Bar.fontPreview = makeFont( size=7, bold=False, weight=50 )
UIGlobals.Bar.fontBookmark = makeFont( size=8, bold=False, weight=50 )
UIGlobals.Bar.favoriteOffset = 2
UIGlobals.Bar.bookmarkOffset = 0


UIGlobals.AssetBrowser = DataClass()
UIGlobals.AssetBrowser.margin = 16
UIGlobals.AssetBrowser.path   = 32
UIGlobals.AssetBrowser.scrollWidth = 14


UIGlobals.AssetBrowser.Icon = DataClass()

UIGlobals.AssetBrowser.Icon.Folder = DataClass()
UIGlobals.AssetBrowser.Icon.Folder.width  = 130
UIGlobals.AssetBrowser.Icon.Folder.height = 50


UIGlobals.AssetBrowser.Icon.Asset = DataClass()

UIGlobals.AssetBrowser.Icon.Asset.min = DataClass()
UIGlobals.AssetBrowser.Icon.Asset.min.width = 130
UIGlobals.AssetBrowser.Icon.Asset.min.height = 152
UIGlobals.AssetBrowser.Icon.Asset.min.label = 74

UIGlobals.AssetBrowser.Icon.Asset.mid = DataClass()
UIGlobals.AssetBrowser.Icon.Asset.mid.width = 260
UIGlobals.AssetBrowser.Icon.Asset.mid.height = 187
UIGlobals.AssetBrowser.Icon.Asset.mid.label = 36

UIGlobals.AssetBrowser.Icon.Asset.max = DataClass()
UIGlobals.AssetBrowser.Icon.Asset.max.width = 390
UIGlobals.AssetBrowser.Icon.Asset.max.height = 260
UIGlobals.AssetBrowser.Icon.Asset.max.label = 36

UIGlobals.AssetBrowser.Icon.Asset.statusHeight = 26

UIGlobals.AssetBrowser.Icon.Preview = DataClass()
UIGlobals.AssetBrowser.Icon.Preview.width  = 480
UIGlobals.AssetBrowser.Icon.Preview.height = 270


UIGlobals.IconDelegate = DataClass()
UIGlobals.IconDelegate.space  = 6
UIGlobals.IconDelegate.radius = 6
UIGlobals.IconDelegate.radiusStatus = 2

UIGlobals.IconDelegate.offsetLink = 9

UIGlobals.IconDelegate.fontLibraries   = makeFont( size=11, bold=False, weight=50 )
UIGlobals.IconDelegate.fontCategory    = makeFont( size=8, bold=False, weight=50 )
UIGlobals.IconDelegate.fontFolderName  = makeFont( size=9, bold=False, weight=50 )
UIGlobals.IconDelegate.fontFolderItems = makeFont( size=7, bold=False, weight=20 )

UIGlobals.IconDelegate.fontAssetName    = makeFont( size=8, bold=False, weight=50 )
UIGlobals.IconDelegate.fontAssetVersion = makeFont( size=7, bold=False, weight=50 )
UIGlobals.IconDelegate.fontAssetLabel   = makeFont( size=6, bold=False, weight=50 )
UIGlobals.IconDelegate.fontAssetStatus  = makeFont( size=7, bold=False, weight=50 )

UIGlobals.IconDelegate.Animation = DataClass()
UIGlobals.IconDelegate.Animation.space  = 10
UIGlobals.IconDelegate.Animation.offset = 6
UIGlobals.IconDelegate.Animation.height = 14
UIGlobals.IconDelegate.Animation.font   = makeFont( size=7, bold=False, weight=90 )


UIGlobals.Options = DataClass()

UIGlobals.Options.width      = 210
UIGlobals.Options.margin     = 30
UIGlobals.Options.thickHight = 32

UIGlobals.Options.fontLabel = makeFont( size=9, bold=False, weight=50 )
UIGlobals.Options.fontOverwrite = makeFont( size=7, bold=False, weight=50 )
UIGlobals.Options.fontComment = makeFont( size=9, bold=False, weight=50 )

UIGlobals.Options.Export = DataClass()
UIGlobals.Options.Export.patternThickness = 11
UIGlobals.Options.Export.font = makeFont( size=9, bold=False, weight=50 )


UIGlobals.Options.Status = DataClass()
UIGlobals.Options.Status.lineWidth = 4
UIGlobals.Options.Status.space     = 6
