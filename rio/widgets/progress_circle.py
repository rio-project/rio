from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio as rx

from . import widget_base

__all__ = [
    "ProgressCircle",
]


class ProgressCircle(widget_base.FundamentalWidget):
    _: KW_ONLY
    progress: Optional[float]
    color: rx.ColorSet

    def __init__(
        self,
        *,
        progress: Optional[float] = None,
        color: rx.ColorSet = "primary",
        size: Union[Literal["grow"], float] = 3.5,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
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
            width=size,
            height=size,
            align_x=align_x,
            align_y=align_y,
        )

        self.progress = progress
        self.color = color


ProgressCircle._unique_id = "ProgressCircle-builtin"
