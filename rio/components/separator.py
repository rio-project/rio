from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Separator",
]


class Separator(FundamentalComponent):
    _: KW_ONLY
    color: rio.Color | None = None


Separator._unique_id = "Separator-builtin"
