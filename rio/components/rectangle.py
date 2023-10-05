from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import cursor_style
from . import component_base

__all__ = [
    "Rectangle",
]


class Rectangle(component_base.FundamentalComponent):
    _: KW_ONLY
    style: rio.BoxStyle
    child: Optional[rio.Component] = None
    hover_style: Optional[rio.BoxStyle] = None
    transition_time: float = 1.0
    cursor: rio.CursorStyle = cursor_style.CursorStyle.DEFAULT
    ripple: bool = False


Rectangle._unique_id = "Rectangle-builtin"
