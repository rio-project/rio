from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "Switcher",
]


class Switcher(component_base.FundamentalComponent):
    child: rio.Component


Switcher._unique_id = "Switcher-builtin"
