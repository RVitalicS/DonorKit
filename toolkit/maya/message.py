#!/usr/bin/env python

import maya.OpenMaya as OpenMaya





def viewport (text):

    command = ' '.join([
        'inViewMessage',
        '-fade',
        '-position "botCenter"',
        '-assistMessage "{}"'.format(text) ])

    OpenMaya.MGlobal.executeCommand(command)





def warning (text):

    OpenMaya.MGlobal.displayWarning(text)





def info (text):
    
    OpenMaya.MGlobal.displayInfo(text)
