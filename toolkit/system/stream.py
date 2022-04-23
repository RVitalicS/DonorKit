#!/usr/bin/env python



import sys
import subprocess
import json

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

    """Run the specified command in a subprocess."""


    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT )

    except OSError as error:
        print(error)

        returncode = 1
        return returncode

    while True:

        processOutput = process.stdout.readline().decode("utf-8", "replace")
        if processOutput:
            if echo:
                sys.stdout.write(processOutput)

        elif process.poll() is not None:
            break

    return process.returncode





def openFolder (path):

    terminal("nautilus " + path)






def openUsd (path):

    terminal("usdview " + path)
