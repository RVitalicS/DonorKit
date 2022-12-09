#!/usr/bin/env python

"""
Message

Prepare the data to be printed in a more informative form.
"""

import os
from typing import Optional


def defaultDefinition (
        name: str, module: str,
        mode: Optional[str] = None) -> None:
    """Print that this function is not defined yet

    Arguments:
        name: The function name
        module: The module path
    Keyword Arguments:
        mode: The application dependent representation (Maya, Katana, etc.)
    """
    thisdir  = os.path.dirname(module)
    if mode == "katana":
        message = (f"[INFO actions.{name}]: "
                 + f'function is not defined in directory: "{thisdir}"')
    elif mode == "maya":
        message = (f"# [actions.{name}] INFO: "
                 + f'function is not defined in directory: "{thisdir}"')
    else:
        message = (f"INFO <actions.{name}>: "
                 + f'function is not defined in directory: "{thisdir}"')
    print(message)
