#!/usr/bin/env python

import os
path = os.path.dirname(__file__)

from toolkit.system import stream



shadertag = stream.dataread(
    os.path.join(path, "shadertag.json") )


RIB_DISPLAY_EXR = stream.fileread(
    os.path.join(path, "display-exr.rib") )

RIB_DISPLAY_PNG = stream.fileread(
    os.path.join(path, "display-png.rib") )

RIB_MESH = stream.fileread(
    os.path.join(path, "mesh.rib") )

RIB_MESH_SUBD = stream.fileread(
    os.path.join(path, "mesh-subdivision.rib") )

RIB_PREVIEW = stream.fileread(
    os.path.join(path, "preview-shader.rib") )


themedark = stream.dataread(
    os.path.join(path, "themedark.json") )

themelight = stream.dataread(
    os.path.join(path, "themelight.json") )


file = open(os.path.join(path, "stylesheet.css"), "r")
stylesheet = file.read()
file.close()


pathEnvmap = os.path.join(path, "envmap.exr")
