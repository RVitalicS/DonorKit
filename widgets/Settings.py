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







class UI (object):


    def __init__ (self):

        self.default_data = dict(
            scrollPosition=0.0,
            iconSize=1,
            focusLibrary="",
            subdirLibrary="",
            bookmarks=[],
            favorites=[],
            favoriteFilter=False,
            modelling=True,
            surfacing=True,
            animation=False,
            modellingOverwrite=False,
            surfacingOverwrite=False,
            animationOverwrite=False,
            rangeStart=1,
            rangeEnd=1,
            fps=30,
            link=True,
            unitsMultiplier=1.0,
            theme="dark" )

        self.path = os.path.join(
            os.path.dirname(__file__),
            "databank",
            ".AssetExportSettings.json")

        if not os.path.exists(self.path):
            self.default_settings(self.path)

        elif not tools.validJSON(self.path):
            self.default_settings(self.path)


    def default_settings (self, path):
        tools.datawrite(path, self.default_data)


    def load (self):
        return tools.dataread(self.path)


    def save (self, data):
        tools.datawrite(self.path, data)







class UIManager (object):


    def __init__ (self, update=True):

        self.update = update


    def __enter__(self):

        self.data = UI().load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            UI().save(self.data)







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

UIsettings = DataClass()


UIsettings.Path = DataClass()
UIsettings.Path.backIcon = 13
UIsettings.Path.height   = 32
UIsettings.Path.fontRoot = makeFont( size=9, bold=False, weight=50 )
UIsettings.Path.fontPath = makeFont( size=9, bold=False, weight=50 )
UIsettings.Path.bookmarkOffset = 1


UIsettings.Bar = DataClass()
UIsettings.Bar.height = 32
UIsettings.Bar.fontPreview = makeFont( size=7, bold=False, weight=50 )
UIsettings.Bar.fontBookmark = makeFont( size=8, bold=False, weight=50 )
UIsettings.Bar.favoriteOffset = 2
UIsettings.Bar.bookmarkOffset = 0


UIsettings.AssetBrowser = DataClass()
UIsettings.AssetBrowser.margin = 16
UIsettings.AssetBrowser.path   = 32
UIsettings.AssetBrowser.scrollWidth = 14


UIsettings.AssetBrowser.Icon = DataClass()

UIsettings.AssetBrowser.Icon.Folder = DataClass()
UIsettings.AssetBrowser.Icon.Folder.width  = 130
UIsettings.AssetBrowser.Icon.Folder.height = 50


UIsettings.AssetBrowser.Icon.Asset = DataClass()

UIsettings.AssetBrowser.Icon.Asset.min = DataClass()
UIsettings.AssetBrowser.Icon.Asset.min.width = 130
UIsettings.AssetBrowser.Icon.Asset.min.height = 152
UIsettings.AssetBrowser.Icon.Asset.min.label = 74

UIsettings.AssetBrowser.Icon.Asset.mid = DataClass()
UIsettings.AssetBrowser.Icon.Asset.mid.width = 260
UIsettings.AssetBrowser.Icon.Asset.mid.height = 187
UIsettings.AssetBrowser.Icon.Asset.mid.label = 36

UIsettings.AssetBrowser.Icon.Asset.max = DataClass()
UIsettings.AssetBrowser.Icon.Asset.max.width = 390
UIsettings.AssetBrowser.Icon.Asset.max.height = 260
UIsettings.AssetBrowser.Icon.Asset.max.label = 36

UIsettings.AssetBrowser.Icon.Asset.statusHeight = 26

UIsettings.AssetBrowser.Icon.Preview = DataClass()
UIsettings.AssetBrowser.Icon.Preview.width  = 480
UIsettings.AssetBrowser.Icon.Preview.height = 270


UIsettings.IconDelegate = DataClass()
UIsettings.IconDelegate.space  = 6
UIsettings.IconDelegate.radius = 6
UIsettings.IconDelegate.radiusStatus = 2

UIsettings.IconDelegate.offsetLink = 9

UIsettings.IconDelegate.fontLibraries   = makeFont( size=11, bold=False, weight=50 )
UIsettings.IconDelegate.fontCategory    = makeFont( size=8, bold=False, weight=50 )
UIsettings.IconDelegate.fontFolderName  = makeFont( size=9, bold=False, weight=50 )
UIsettings.IconDelegate.fontFolderItems = makeFont( size=7, bold=False, weight=20 )

UIsettings.IconDelegate.fontAssetName    = makeFont( size=8, bold=False, weight=50 )
UIsettings.IconDelegate.fontAssetVersion = makeFont( size=7, bold=False, weight=50 )
UIsettings.IconDelegate.fontAssetLabel   = makeFont( size=6, bold=False, weight=50 )
UIsettings.IconDelegate.fontAssetStatus  = makeFont( size=7, bold=False, weight=50 )

UIsettings.IconDelegate.Animation = DataClass()
UIsettings.IconDelegate.Animation.space  = 10
UIsettings.IconDelegate.Animation.offset = 6
UIsettings.IconDelegate.Animation.height = 14
UIsettings.IconDelegate.Animation.font   = makeFont( size=7, bold=False, weight=90 )


UIsettings.Options = DataClass()

UIsettings.Options.width      = 210
UIsettings.Options.margin     = 30
UIsettings.Options.thickHight = 32

UIsettings.Options.fontLabel = makeFont( size=9, bold=False, weight=50 )
UIsettings.Options.fontOverwrite = makeFont( size=7, bold=False, weight=50 )
UIsettings.Options.fontComment = makeFont( size=9, bold=False, weight=50 )

UIsettings.Options.Export = DataClass()
UIsettings.Options.Export.patternThickness = 11
UIsettings.Options.Export.font = makeFont( size=9, bold=False, weight=50 )


UIsettings.Options.Status = DataClass()
UIsettings.Options.Status.lineWidth = 4
UIsettings.Options.Status.space     = 6
