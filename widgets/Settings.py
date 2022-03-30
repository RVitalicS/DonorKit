#!/usr/bin/env python


import os

import toolkit.system.stream
import toolkit.core.ui


from toolkit.ensure.QtGui import *





STATUS_LIST = [
    "Final",
    "Completed",
    "Revise",
    "Pending Review",
    "WIP" ]






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
            ".UsdExportSettings.json")

        if not os.path.exists(self.path):
            self.defaultSettings(self.path)

        elif not toolkit.system.stream.validJSON(self.path):
            self.defaultSettings(self.path)


    def defaultSettings (self, path):
        toolkit.system.stream.datawrite(path, self.defaults)


    def load (self):
        return toolkit.system.stream.dataread(self.path)


    def save (self, data):
        toolkit.system.stream.datawrite(self.path, data)







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
            os.path.dirname(__file__),
            "databank",
            ".AssetDonorSettings.json")

        if not os.path.exists(self.path):
            self.defaultSettings(self.path)

        elif not toolkit.system.stream.validJSON(self.path):
            self.defaultSettings(self.path)


    def defaultSettings (self, path):
        toolkit.system.stream.datawrite(path, self.defaults)


    def load (self):
        return toolkit.system.stream.dataread(self.path)


    def save (self, data):
        toolkit.system.stream.datawrite(self.path, data)







class Manager (object):


    def __init__ (self, update=True):

        self.update = update


    def __enter__(self):

        self.data = ManagerData().load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            ManagerData().save(self.data)







class DataClass: pass

UIGlobals = DataClass()


UIGlobals.Path = DataClass()
UIGlobals.Path.backIcon = 13
UIGlobals.Path.height   = 32
UIGlobals.Path.fontRoot = toolkit.core.ui.makeFont(size=9)
UIGlobals.Path.fontPath = toolkit.core.ui.makeFont(size=9)
UIGlobals.Path.bookmarkOffset = 1


UIGlobals.Bar = DataClass()
UIGlobals.Bar.height = 32
UIGlobals.Bar.fontPreview  = toolkit.core.ui.makeFont(size=7)
UIGlobals.Bar.fontBookmark = toolkit.core.ui.makeFont(size=8)
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

UIGlobals.AssetBrowser.Icon.Asset.infoHeight = 26
UIGlobals.AssetBrowser.Icon.Asset.infoLabel  = 10

UIGlobals.AssetBrowser.Icon.Preview = DataClass()
UIGlobals.AssetBrowser.Icon.Preview.width  = 480
UIGlobals.AssetBrowser.Icon.Preview.height = 270


UIGlobals.IconDelegate = DataClass()
UIGlobals.IconDelegate.space  = 6
UIGlobals.IconDelegate.radius = 6
UIGlobals.IconDelegate.radiusStatus = 2

UIGlobals.IconDelegate.offsetLink = 9

UIGlobals.IconDelegate.fontLibraries   = toolkit.core.ui.makeFont(size=11)
UIGlobals.IconDelegate.fontLibraryName = toolkit.core.ui.makeFont(size=10)

UIGlobals.IconDelegate.fontCategory    = toolkit.core.ui.makeFont(size=8)
UIGlobals.IconDelegate.fontFolderName  = toolkit.core.ui.makeFont(size=9)
UIGlobals.IconDelegate.fontFolderItems = toolkit.core.ui.makeFont(size=7)

UIGlobals.IconDelegate.fontAssetName    = toolkit.core.ui.makeFont(size=8)
UIGlobals.IconDelegate.fontAssetVersion = toolkit.core.ui.makeFont(size=7)
UIGlobals.IconDelegate.fontAssetLabel   = toolkit.core.ui.makeFont(size=6)
UIGlobals.IconDelegate.fontAssetStatus  = toolkit.core.ui.makeFont(size=7)
UIGlobals.IconDelegate.fontAssetSize    = toolkit.core.ui.makeFont(size=7)

UIGlobals.IconDelegate.Animation = DataClass()
UIGlobals.IconDelegate.Animation.space  = 10
UIGlobals.IconDelegate.Animation.offset = 6
UIGlobals.IconDelegate.Animation.height = 14
UIGlobals.IconDelegate.Animation.font   = toolkit.core.ui.makeFont(size=7, weight=QtGui.QFont.Bold)


UIGlobals.Options = DataClass()

UIGlobals.Options.minimumWidth = 134
UIGlobals.Options.preferWidth  = 170
UIGlobals.Options.maximumWidth = 400
UIGlobals.Options.margin       = 30
UIGlobals.Options.thickHeight  = 32
UIGlobals.Options.buttonHeight = 12
UIGlobals.Options.rawHeight    = 16
UIGlobals.Options.labelWidth   = 52

UIGlobals.Options.fontName      = toolkit.core.ui.makeFont(size=12, weight=QtGui.QFont.Bold)
UIGlobals.Options.fontLabel     = toolkit.core.ui.makeFont(size=9)
UIGlobals.Options.fontInfo      = toolkit.core.ui.makeFont(size=9)
UIGlobals.Options.fontComment   = toolkit.core.ui.makeFont(size=9)
UIGlobals.Options.fontOverwrite = toolkit.core.ui.makeFont(size=7)
UIGlobals.Options.fontLink      = toolkit.core.ui.makeFont(size=9)

UIGlobals.Options.Export = DataClass()
UIGlobals.Options.Export.patternThickness = 11
UIGlobals.Options.Export.delayTime = 35
UIGlobals.Options.Export.font = toolkit.core.ui.makeFont(size=10)


UIGlobals.Options.Status = DataClass()
UIGlobals.Options.Status.lineWidth    = 4
UIGlobals.Options.Status.space        = 6
UIGlobals.Options.Status.buttonHeight = 10
UIGlobals.Options.Status.fontLabel    = toolkit.core.ui.makeFont(size=6)
UIGlobals.Options.Status.fontButton   = toolkit.core.ui.makeFont(size=9)
