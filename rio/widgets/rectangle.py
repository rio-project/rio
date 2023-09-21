from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio as rx

from .. import cursor_style
from . import widget_base

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.FundamentalWidget):
    _: KW_ONLY
    style: rx.BoxStyle
    child: Optional[rx.Widget] = None
    hover_style: Optional[rx.BoxStyle] = None
    transition_time: float = 1.0
    cursor: rx.CursorStyle = cursor_style.CursorStyle.DEFAULT
    ripple: bool = False


Rectangle._unique_id = "Rectangle-builtin"
