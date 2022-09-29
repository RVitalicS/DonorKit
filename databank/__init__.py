#!/usr/bin/env python

import os
bank = os.path.dirname(__file__)

from toolkit.system import stream



shadertag = stream.dataread(
    os.path.join(bank, "shadertag.json") )


RIB_DISPLAY_EXR = stream.fileread(
    os.path.join(bank, "display-exr.rib") )

RIB_DISPLAY_PNG = stream.fileread(
    os.path.join(bank, "display-png.rib") )

RIB_MESH = stream.fileread(
    os.path.join(bank, "mesh.rib") )

RIB_MESH_SUBD = stream.fileread(
    os.path.join(bank, "mesh-subdivision.rib") )

RIB_PREVIEW = stream.fileread(
    os.path.join(bank, "preview-shader.rib") )
