#!/usr/bin/env python



import sys
import json
import subprocess


from toolkit.ensure.QtCore import *






def dataread (path):

    with open(path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def datawrite (path, data):

    with open(path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def validJSON (path):

    try: 
        data = dataread(path)
        if not data:
            return False
    except:
        return False
    
    return True






def readCGATS ():

    CGATS = dict()

    file = QtCore.QFile(":/data/cgats")
    file.open(QtCore.QIODevice.ReadOnly)

    ByteArray = file.readAll()
    data = ByteArray.data().decode("utf-8")
    file.close()

    data = data.split("\n")
    data = [line.split(" ") for line in data]
    for pair in data:

        key = pair[0]
        value = [float(i) for i in pair[1].split(",") ]

        CGATS[key] = value

    return CGATS






def terminal (command, echo=False):

    """Run the specified command in a subprocess"""


    if type(command) == list:
        command = " ".join(command)


    if echo:
        subprocess.run(
            command,
            shell=True,
            stdout=None, 
            stderr=None)

    else:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL)






def openFolder (path):

    command = ["nautilus", path]
    terminal(command)






def openUsd (path):

    command = ["usdview", path]
    terminal(command)
