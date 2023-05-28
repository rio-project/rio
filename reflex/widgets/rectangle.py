from __future__ import annotations

from typing import Optional, Tuple, Union

import reflex as rx

from . import widget_base
from .. import styling

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    style: styling.BoxStyle
    child: Optional[rx.Widget]


Rectangle._unique_id = "Rectangle-builtin"
