from __future__ import annotations

from dataclasses import KW_ONLY
from datetime import timedelta
from typing import *  # type: ignore

import reflex as rx

from . import widget_base

__all__ = [
    "Slideshow",
]


class Slideshow(widget_base.FundamentalWidget):
    children: List[rx.Widget]
    _: KW_ONLY
    linger_time: float

    def __init__(
        self,
        *children: rx.Widget,
        linger_time: Union[float, timedelta] = timedelta(seconds=10),
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        assert isinstance(children, tuple), children
        for child in children:
            assert isinstance(child, widget_base.Widget), child

        if isinstance(linger_time, timedelta):
            linger_time = linger_time.total_seconds()

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

        self.children = list(children)
        self.linger_time = linger_time


Slideshow._unique_id = "Slideshow-builtin"
