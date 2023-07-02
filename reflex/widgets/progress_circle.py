from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import reflex as rx

from .. import styling, theme
from . import widget_base

__all__ = [
    "ProgressCircle",
]


class ProgressCircle(widget_base.HtmlWidget):
    _: KW_ONLY
    color: styling.Color = theme.COLOR_ACCENT
    background_color: styling.Color = theme.COLOR_NEUTRAL
    progress: Optional[float] = None

    def __init__(
        self,
        *,
        color: rx.Color = theme.COLOR_ACCENT,
        background_color: rx.Color = theme.COLOR_NEUTRAL,
        progress: Optional[float] = None,
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

        self.color = color
        self.background_color = background_color
        self.progress = progress


ProgressCircle._unique_id = "ProgressCircle-builtin"
