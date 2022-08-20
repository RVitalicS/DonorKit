#!/usr/bin/env python



import sys
import json
import subprocess


from toolkit.ensure.QtCore import *






def fileread (path):

    data = ""
    with open(path, "r") as file:
        data = file.read()

    return data


def filewrite (path, data):

    with open(path, "w") as file:
        file.write(data)







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

    command = ["nautilus", path]
    terminal(command)






def openUsd (path):

    command = ["usdview", path]
    terminal(command)
