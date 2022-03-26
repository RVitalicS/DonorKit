#!/usr/bin/env python


import os





def defaultDefinition (name, module, mode="katana"):

    thisdir  = os.path.dirname(module)

    message  = ""
    if mode == "katana":
        message += "[INFO actions.{}]: "
        message += 'function is not defined in directory: "{}"'

    elif mode == "maya":
        message += "# [actions.{}] INFO: "
        message += 'function is not defined in directory: "{}"'

    else:
        message += "INFO <actions.{}>: "
        message += 'function is not defined in directory: "{}"'

    print( message.format(name, thisdir) )
