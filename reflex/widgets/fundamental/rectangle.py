from __future__ import annotations

from typing import *  # type: ignore

import reflex as rx

from ... import common
from . import box_style, widget_base

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    style: box_style.BoxStyle
    child: Optional[rx.Widget] = None
    hover_style: Optional[box_style.BoxStyle] = None
    transition_time: float = 1.0
    cursor: common.CursorStyle = common.CursorStyle.DEFAULT


Rectangle._unique_id = "Rectangle-builtin"
