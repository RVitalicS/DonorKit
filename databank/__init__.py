#!/usr/bin/env python

import os
bank = os.path.dirname(__file__)

from toolkit.system import stream



shadertag = stream.dataread(
    os.path.join(bank, "shadertag.json") )
