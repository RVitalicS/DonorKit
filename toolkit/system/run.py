#!/usr/bin/env python

"""
Run commands

This module defines functions to execute commands
in a shell of the operating system.
"""

import sys
import subprocess
from widgets import Settings
from typing import Union


def terminal (command: Union[str, list], echo: bool = False) -> None:
    """Run the specified command in a subprocess

    Arguments:
        command: The arguments used to launch the process
    Keyword Arguments:
        echo: Wait for child process to terminate
              and print data from stdout and stderr
    """
    if type(command) == list:
        command = " ".join(command)
    if echo:
        popen = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)
        popen.wait()
        for line in popen.stdout:
            sys.stdout.write(line)
        for line in popen.stderr:
            sys.stdout.write(line)
    else:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL)


def openFolder (path: str) -> None:
    """Get command from the settings
    to open directory in a file manager

    Arguments:
        path: The directory to open
    """
    command = []
    with Settings.Manager(
            app="ExternalTools",
            update=False ) as settings:
        command  = settings["folder"]
        command  = command.split(" ")
        command += [path]
    terminal(command)


def openUsd (path: str) -> None:
    """Get command from the settings
    to open file in a UsdView

    Arguments:
        path: The USD file to open
    """
    command = []
    with Settings.Manager(
            app="ExternalTools",
            update=False ) as settings:
        command  = settings["usd"]
        command  = command.split(" ")
        command += [path]
    terminal(command)
