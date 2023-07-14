from __future__ import annotations

from typing import Literal, Optional

import reflex as rx

from .. import common, styling, theme
from . import widget_base

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    style: styling.BoxStyle
    child: Optional[rx.Widget] = None
    hover_style: Optional[styling.BoxStyle] = None
    transition_time: float = theme.TRANSITION_MED
    cursor: common.CursorStyle = common.CursorStyle.DEFAULT


Rectangle._unique_id = "Rectangle-builtin"
