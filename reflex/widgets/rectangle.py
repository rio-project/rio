from __future__ import annotations

from typing import *  # type: ignore

import reflex as rx

from .. import cursor_style
from . import widget_base

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    style: rx.BoxStyle
    child: Optional[rx.Widget] = None
    hover_style: Optional[rx.BoxStyle] = None
    transition_time: float = 1.0
    cursor: rx.CursorStyle = cursor_style.CursorStyle.DEFAULT


Rectangle._unique_id = "Rectangle-builtin"
