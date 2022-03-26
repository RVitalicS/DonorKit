#!/usr/bin/env python


import os
import sys


katanaDir  = os.getenv("ASSET_MANAGER")
toolboxDir = os.path.dirname(katanaDir)
rootDir    = os.path.dirname(toolboxDir)


if rootDir not in sys.path:
    sys.path.append(rootDir)
