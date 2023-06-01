from __future__ import annotations

from typing import Optional, Tuple, Union
from .. import theme
import reflex as rx

from . import widget_base
from .. import styling

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    style: styling.BoxStyle
    child: Optional[rx.Widget] = None
    hover_style: Optional[styling.BoxStyle] = None
    transition_time: float = theme.TRANSITION_MED


Rectangle._unique_id = "Rectangle-builtin"
