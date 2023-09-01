from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal

import reflex as rx

from . import widget_base

__all__ = [
    "Image",
]


class Image(widget_base.Widget):
    image: rx.ImageLike
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"

    def build(self) -> rx.Widget:
        fill = rx.ImageFill(
            image=self.image,
            fill_mode=self.fill_mode,
        )
        style = rx.BoxStyle(fill=fill)
        return rx.Rectangle(style)
