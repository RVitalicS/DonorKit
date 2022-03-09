#!/usr/bin/env python



from . import ItemBase

from . import AssetUsdPainter
from . import AssetUsdEditor







class Delegate (ItemBase.Delegate):


    def __init__ (self, parent, theme):
        super(Delegate, self).__init__(parent, theme)
        self.Item = AssetUsdPainter.Item(theme)



    def createEditor (self, parent, option, index):

        editor = AssetUsdEditor.Editor(parent, index, self.theme)
        editor.Item.controlMode = self.parent().controlMode

        editor.clicked.connect(self.clickAction)
        editor.leaveEditor.connect(self.leaveAcion)
        
        editor.link.connect(self.linkAction)
        editor.favoriteClicked.connect(self.favoriteAction)

        return editor



    def favoriteAction (self, index):

        self.parent().favoriteClickedSignal(index)



    def linkAction (self, index):
        
        self.parent().linkBridge(index)
