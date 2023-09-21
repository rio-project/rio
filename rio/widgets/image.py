from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal

import rio

from ..common import ImageLike
from . import widget_base

__all__ = ["Image"]


class Image(widget_base.Widget):
    image: ImageLike
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"

    def build(self) -> rio.Widget:
        fill = rio.ImageFill(
            image=self.image,
            fill_mode=self.fill_mode,
        )
        style = rio.BoxStyle(fill=fill)
        return rio.Rectangle(style=style)
