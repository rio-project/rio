from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from ..fundamental import widget_base
from . import theme

__all__ = [
    "ProgressCircle",
]


class ProgressCircle(widget_base.HtmlWidget):
    _: KW_ONLY
    progress: Optional[float] = None
    color: Optional[rx.Color] = None
    background_color: Optional[rx.Color] = None

    def __init__(
        self,
        *,
        progress: Optional[float] = None,
        color: Optional[rx.Color] = None,
        background_color: Optional[rx.Color] = None,
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
        self.background_color = background_color

    def _custom_serialize(self) -> JsonDoc:
        thm = self.session.attachments[theme.Theme]

        color = thm.accent_color if self.color is None else self.color
        background_color = (
            thm.neutral_color
            if self.background_color is None
            else self.background_color
        )

        return {
            "color": color.rgba,
            "background_color": background_color.rgba,
        }


ProgressCircle._unique_id = "ProgressCircle-builtin"
