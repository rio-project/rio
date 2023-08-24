from __future__ import annotations

from typing import Literal

import reflex as rx

from ... import fills, image_source
from .. import fundamental

__all__ = [
    "Image",
]


class Image(fundamental.Widget):
    image: image_source.ImageLike
    fill_mode: Literal["fit", "stretch", "tile", "zoom"] = "fit"

    def build(self) -> rx.Widget:
        fill = fills.ImageFill(
            image=self.image,
            fill_mode=self.fill_mode,
        )
        style = fundamental.BoxStyle(fill=fill)
        return fundamental.Rectangle(style)
