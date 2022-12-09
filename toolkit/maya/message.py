#!/usr/bin/env python

"""
Message

This module defines functions to display Maya messages.
"""

import maya.OpenMaya as OpenMaya


def viewport (text: str) -> None:
    """Display a message in current viewport
    
    Arguments:
        text: The text to display
    """
    command = ' '.join([
        'inViewMessage',
        '-fade',
        '-position "botCenter"',
        '-assistMessage "{}"'.format(text) ])
    OpenMaya.MGlobal.executeCommand(command)


def warning (text: str) -> None:
    """Display a warning in the script editor
    
    Arguments:
        text: The text to display
    """
    OpenMaya.MGlobal.displayWarning(text)


def info (text: str) -> None:
    """Display an informational message in the script editor
    
    Arguments:
        text: The text to display
    """
    OpenMaya.MGlobal.displayInfo(text)
