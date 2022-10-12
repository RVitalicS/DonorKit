#!/usr/bin/env python


import os

thisDir = os.path.dirname(__file__)
rootDir = os.path.dirname(thisDir)


import toolkit.system.stream
import toolkit.core.ui


from toolkit.ensure.QtGui import *





STATUS_LIST = [
    "Final",
    "Completed",
    "Revise",
    "Pending Review",
    "WIP" ]






class ManagerData (object):


    def __init__ (self, app):

        filename = ".Settings_Manager.json"
        self.defaults = dict(
            scrollPosition=0.0,
            size=[820, 590],
            iconSize=1,
            location="",
            hidden=True,
            bookmarks=[],
            favorites=[],
            favoriteFilter=False,
            theme="dark" )

        if app == "AssetExport":

            filename = ".Settings_AssetExport.json"
            self.defaults.update( dict(
                modelling=True,
                surfacing=True,
                animation=False,
                modellingOverwrite=False,
                surfacingOverwrite=False,
                animationOverwrite=False,
                rangeStart=1,
                rangeEnd=1,
                link=True,
                maya=False ))

        elif app == "MaterialExport":

            filename = ".Settings_MaterialExport.json"
            self.defaults.update( dict(
                link=True,
                prman=False,
                hydra=False,
                maya=False,
                resub=["_*SG$", ""] ))

        elif app == "ExternalTools":

            filename = ".Settings_ExternalTools.json"
            self.defaults = dict(
                folder="nautilus",
                usd="usdview" )

        self.path = os.path.join(
            rootDir, "databank", filename )


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


    def __init__ (self, app="Manager", update=True):

        self.update = update
        self.app = app


    def __enter__(self):

        self.data = ManagerData(self.app).load()
        return self.data


    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.update:
            ManagerData(self.app).save(self.data)







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


UIGlobals.Browser = DataClass()
UIGlobals.Browser.margin = 16
UIGlobals.Browser.path   = 32
UIGlobals.Browser.scrollWidth = 14


UIGlobals.Browser.fontMessage = toolkit.core.ui.makeFont(size=10)


UIGlobals.Browser.Icon = DataClass()

UIGlobals.Browser.Icon.Folder = DataClass()
UIGlobals.Browser.Icon.Folder.width  = 130
UIGlobals.Browser.Icon.Folder.height = 50


UIGlobals.Browser.Icon.Asset = DataClass()

UIGlobals.Browser.Icon.Asset.min = DataClass()
UIGlobals.Browser.Icon.Asset.min.width = 130
UIGlobals.Browser.Icon.Asset.min.height = 152
UIGlobals.Browser.Icon.Asset.min.label = 74

UIGlobals.Browser.Icon.Asset.mid = DataClass()
UIGlobals.Browser.Icon.Asset.mid.width = 260
UIGlobals.Browser.Icon.Asset.mid.height = 187
UIGlobals.Browser.Icon.Asset.mid.label = 36

UIGlobals.Browser.Icon.Asset.max = DataClass()
UIGlobals.Browser.Icon.Asset.max.width = 390
UIGlobals.Browser.Icon.Asset.max.height = 260
UIGlobals.Browser.Icon.Asset.max.label = 36

UIGlobals.Browser.Icon.Asset.infoHeight = 26
UIGlobals.Browser.Icon.Asset.infoLabel  = 10

UIGlobals.Browser.Icon.Preview = DataClass()
UIGlobals.Browser.Icon.Preview.width  = 480
UIGlobals.Browser.Icon.Preview.height = 270


UIGlobals.IconDelegate = DataClass()
UIGlobals.IconDelegate.space  = 6
UIGlobals.IconDelegate.radius = 6
UIGlobals.IconDelegate.radiusStatus = 2

UIGlobals.IconDelegate.offsetLink = 7

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

UIGlobals.IconDelegate.fontColorTitle   = toolkit.core.ui.makeFont(size=8, weight=QtGui.QFont.Bold)
UIGlobals.IconDelegate.fontColorName    = toolkit.core.ui.makeFont(size=7)

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

UIGlobals.Options.Maya = DataClass()
UIGlobals.Options.Maya.width  = 13
UIGlobals.Options.Maya.height = 12
UIGlobals.Options.Maya.offset = 12

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
