#!/usr/bin/env python


import os
from . import tools

from . import Settings
UIsettings = Settings.UIsettings







class Theme (object):


    def __init__ (self):


        self.name = "dark"
        filename = "themedark.json"

        with Settings.UIManager(update=False) as uiSettings:
            self.name = uiSettings.get("theme", "")

        if self.name == "light":
            filename = "themelight.json"


        path = os.path.join(
            os.path.dirname(__file__),
            "databank", filename)
        self.values = tools.dataread(path)

        self.variables = {
            "kicker": "$KICKER",
            "white": "$WHITE_COLOR",
            "black": "$BLACK_COLOR",
            "violet": "$VIOLET_COLOR",
            "text": "$TEXT_ON",
            "textoff": "$TEXT_OFF",
            "textlock": "$TEXT_LOCK",
            "optionBackground": "$OPTION_BACKGROUND",
            "optionInput": "$OPTION_INPUT",
            "optionButton": "$OPTION_BUTTON",
            "optionDisable": "$OPTION_DISABLE",
            "statusButton" : "$STATUS_BUTTON",
            "checkedHilight": "$HILIGHT_CHECKED",
            "browserBackground": "$BROWSER_BACKGROUND",
            "browserSocket": "$BROWSER_SOCKET",
            "browserHandleSocket": "$HANDLE_SOCKET",
            "browserHandle": "$BROWSER_HANDLE"
            }


        for attribute, variable in self.values.items():
            value = self.values.get(attribute, "#00ff00")
            setattr(self, attribute, value)



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
