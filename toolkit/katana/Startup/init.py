#!/usr/bin/env python


import os
import sys


katana  = os.getenv("DONOR_KIT")
toolbox = os.path.dirname(katana)
root    = os.path.dirname(toolbox)


if root not in sys.path:
    sys.path.append(root)
