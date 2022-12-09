#!/usr/bin/env python

"""
"""

import databank
from toolkit.ensure.QtGui import *
from widgets import Settings

UIGlobals = Settings.UIGlobals


class Theme (object):

    def __init__ (self, app="Manager"):
        self.app = app
        with Settings.Manager(self.app, False) as settings:
            self.name = settings.get("theme", "")
        if self.name == "dark":
            self.values = databank.themedark
        else:
            self.values = databank.themelight
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
            "browserHandle": "$BROWSER_HANDLE" }

        class Group: pass
        self.color = Group()
        for attribute, variable in self.values.items():
            value = self.values.get(attribute, "#00ff00")
            setattr(self.color, attribute, value)
        database = QtGui.QFontDatabase()
        for font in [":/fonts/Cantarell-Regular.otf", ":/fonts/Cantarell-Bold.otf"]:
            database.addApplicationFont(font)

    def getStyleSheet (self):
        stylesheet = databank.stylesheet
        for key, variable in self.variables.items():
            value = self.values.get(key, "#00ff00")
            stylesheet = stylesheet.replace(variable, value)
        return stylesheet
