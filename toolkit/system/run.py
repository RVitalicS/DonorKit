#!/usr/bin/env python

import sys
import subprocess
from widgets import Settings


def terminal (command, echo=False):
    """Run the specified command in a subprocess"""

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


def openFolder (path):

    command = []
    with Settings.Manager(
            app="ExternalTools",
            update=False ) as settings:
        command  = settings["folder"]
        command  = command.split(" ")
        command += [path]
    terminal(command)


def openUsd (path):

    command = []
    with Settings.Manager(
            app="ExternalTools",
            update=False ) as settings:
        command  = settings["usd"]
        command  = command.split(" ")
        command += [path]
    terminal(command)
