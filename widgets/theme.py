#!/usr/bin/env python


import os
from . import tools

from Qt import QtGui

from . import Settings
UIGlobals = Settings.UIGlobals







class Theme (object):


    def __init__ (self, application="manager"):
        self.application = application

        self.name = "dark"
        filename = "themedark.json"

        if self.application == "export":
            with Settings.Export(update=False) as settings:
                self.name = settings.get("theme", "")
        else:
            with Settings.Manager(update=False) as settings:
                self.name = settings.get("theme", "")

        if self.name == "light":
            filename = "themelight.json"


        self.variables = {
            "kicker": "$KICKER",
            "white": "$WHITE_COLOR",
            "black": "$BLACK_COLOR",
            "violet": "$VIOLET_COLOR",
            "text": "$TEXT_ON",
            "textoff": "$TEXT_OFF",
            "textdim": "$TEXT_DIM",
            "textlock": "$TEXT_LOCK",
            "textover": "$TEXT_OVER",
            "texterror": "$TEXT_ERROR",
            "selectionColor": "$SELECTION_COLOR",
            "selectionBackground": "$SELECTION_BACKGROUND",
            "optionBackground": "$OPTION_BACKGROUND",
            "optionDisable": "$OPTION_DISABLE",
            "optionLine": "$OPTION_LINE",
            "browserBackground": "$BROWSER_BACKGROUND",
            "browserSocket": "$BROWSER_SOCKET",
            "browserHandleSocket": "$HANDLE_SOCKET",
            "browserHandle": "$BROWSER_HANDLE"
            }


        path = os.path.join(
            os.path.dirname(__file__),
            "databank", filename)
        self.values = tools.dataread(path)

        class Group: pass
        self.color = Group()

        for attribute, variable in self.values.items():
            value = self.values.get(attribute, "#00ff00")
            setattr(self.color, attribute, value)


        database = QtGui.QFontDatabase()
        for font in [
            ":/fonts/Cantarell-Regular.otf" ,
            ":/fonts/Cantarell-Bold.otf"    ]:
            database.addApplicationFont(font)



    def getStyleSheet (self):

        path = os.path.join(
            os.path.dirname(__file__),
            "databank",
            "stylesheet.css")

        stylesheet = ""
        with open(path, "r") as file:
            stylesheet = file.read()

        for key, variable in self.variables.items():
            value = self.values.get(key, "#00ff00")
            stylesheet = stylesheet.replace(variable, value)

        return stylesheet
