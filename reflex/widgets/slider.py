from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import widget_base

__all__ = [
    "Slider",
]


class Slider(widget_base.FundamentalWidget):
    _: KW_ONLY
    min: float = 0
    max: float = 1
    value: float = 0.5
    is_sensitive: bool = True


Slider._unique_id = "Slider-builtin"
