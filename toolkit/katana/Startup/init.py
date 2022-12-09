#!/usr/bin/env python

"""
Startup Script

Make this project visible for the interpreter
after Katana app startup.
"""

import os
import sys

katana = os.getenv("DONOR_KIT")
tool = os.path.dirname(katana)
root = os.path.dirname(tool)

if root not in sys.path:
    sys.path.append(root)
