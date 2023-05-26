from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Dict, List, Literal, Optional, Tuple, Union

from .. import messages
from ..common import Jsonable
from ..styling import *
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    Widget,
    call_event_handler_and_refresh,
)

__all__ = [
    "Rectangle",
]


class Rectangle(FundamentalWidget):
    fill: FillLike
    child: Optional[Widget]
    corner_radius: Tuple[float, float, float, float]
    stroke_width: float
    stroke_color: Optional[Color]

    def __init__(
        self,
        fill: FillLike,
        child: Optional[Widget] = None,
        *,
        corner_radius: Union[float, Tuple[float, float, float, float]] = 0.0,
        stroke_width: float = 0.0,
        stroke_color: Optional[Color] = None,
    ):
        super().__init__()
        self.fill = fill
        self.child = child
        self.corner_radius = (
            (corner_radius,) * 4 if isinstance(corner_radius, float) else corner_radius
        )
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
