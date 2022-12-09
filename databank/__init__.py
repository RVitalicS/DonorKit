#!/usr/bin/env python

"""
Data Bank

Use variables to get a data of service files
"""

# TODO: get rid of reading
from toolkit.system import stream
import os


# root of the project
path = os.path.dirname(__file__)

# name translator
shadertag = stream.dataread(
    os.path.join(path, "shadertag.json") )

# render data blocks
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

# UI color tokens
themedark = stream.dataread(
    os.path.join(path, "themedark.json") )
themelight = stream.dataread(
    os.path.join(path, "themelight.json") )

# UI customization file
file = open(os.path.join(path, "stylesheet.css"), "r")
stylesheet = file.read()
file.close()

# lighting image
pathEnvmap = os.path.join(path, "envmap.exr")
