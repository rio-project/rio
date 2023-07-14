from __future__ import annotations

from typing import Literal

import reflex as rx

from ..image_source import ImageLike
from . import widget_base

__all__ = ["Image"]


class Image(widget_base.Widget):
    image: ImageLike
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"

    def build(self) -> rx.Widget:
        fill = rx.ImageFill(
            image=self.image,
            fill_mode=self.fill_mode,
        )
        style = rx.BoxStyle(fill=fill)
        return rx.Rectangle(style)
