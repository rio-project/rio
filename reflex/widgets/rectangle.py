from __future__ import annotations

from typing import Optional, Tuple, Union

import reflex as rx

from ..styling import *
from . import widget_base

__all__ = [
    "Rectangle",
]


class Rectangle(widget_base.HtmlWidget):
    fill: FillLike
    child: Optional[rx.Widget]
    corner_radius: Tuple[float, float, float, float]
    stroke_width: float
    stroke_color: Optional[Color]

    def __init__(
        self,
        fill: FillLike,
        child: Optional[rx.Widget] = None,
        *,
        corner_radius: Union[float, Tuple[float, float, float, float]] = 0.0,
        stroke_width: float = 0.0,
        stroke_color: Optional[Color] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.fill = fill
        self.child = child
        self.corner_radius = (
            (corner_radius,) * 4 if isinstance(corner_radius, float) else corner_radius
        )
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color


Rectangle._unique_id = "Rectangle-builtin"
