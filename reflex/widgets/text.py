from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal, Optional

from ..styling import *
from .widget_base import FundamentalWidget

__all__ = [
    "Text",
]


class Text(FundamentalWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    font: Optional[str] = None
    font_color: Color = Color.from_rgb(0, 0, 0)
    font_size: float = 1.0
    font_weight: Literal["normal", "bold"] = "normal"
    italic: bool = False
    underlined: bool = False
