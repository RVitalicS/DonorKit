#!/usr/bin/env python


from toolbox.ensure.Usd import *
from toolbox.ensure.Ar import *

import os, re






def getUsdReferences (path, container=None):

    if container == None:
        container = []

    root = os.path.dirname(path)
    if path not in container:
        container.append(path)

    Resolver = Ar.GetResolver()
    
    stage = Usd.Stage.Open( Resolver.Resolve(path) )
    layers = stage.GetRootLayer().GetExternalReferences()

    for layer in layers:

        working = re.match(r"^\./.*",   layer)
        above   = re.match(r"^\.\./.*", layer)

        if working:
            path = re.sub(r"^\.",
                root, layer)
        elif above:
            path = re.sub(r"^\.\.",
                os.path.dirname(root), layer)
        else:
            path = layer

        container = getUsdReferences(
            Resolver.Resolve(path),
            container=container)

    return container






def getResolvedSize (path):

    sizeMegabytes = 0
    for reference in getUsdReferences(path):
        sizeBytes = os.path.getsize(reference)
        sizeMegabytes += (sizeBytes/1000000)

    return "{:0.2f}".format(sizeMegabytes)
