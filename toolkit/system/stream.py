#!/usr/bin/env python



import subprocess
import json






def dataread (path):

    with open(path, "r") as file:
        return json.load(file)


def datawrite (path, data):

    with open(path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def validJSON (path):

    try: 
        data = dataread(path)
        if not data:
            return False
    except:
        return False
    
    return True






def openFolder (path):

    subprocess.Popen(["nautilus", path],
        stdin  = None ,
        stdout = None ,
        stderr = None )