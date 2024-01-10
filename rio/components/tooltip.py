from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import component_base

__all__ = [
    "Tooltip",
]


class Tooltip(component_base.FundamentalComponent):
    anchor: component_base.Component
    label: str
    _: KW_ONLY
    position: Literal["left", "top", "right", "bottom"]


Tooltip._unique_id = "Tooltip-builtin"
