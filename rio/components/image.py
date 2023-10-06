from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import assets
from ..common import EventHandler, ImageLike
from . import component_base

__all__ = ["Image"]


class Image(component_base.FundamentalComponent):
    image: ImageLike
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "zoom"] = "fit"
    on_error: EventHandler[[]] = None
    corner_radius: Union[float, Tuple[float, float, float, float]] = 0

    @rio.event.on_create
    def _on_create(self) -> None:
        self._image_asset = assets.Asset.from_image(self.image)

    def _custom_serialize(self) -> JsonDoc:
        if isinstance(self.corner_radius, (int, float)):
            corner_radius = (self.corner_radius,) * 4
        else:
            corner_radius = self.corner_radius

        return {
            "imageUrl": self._image_asset._serialize(self.session),
            "reportError": self.on_error is not None,
            "corner_radius": corner_radius,
        }

    async def _on_message(self, message: JsonDoc) -> None:
        await self.call_event_handler(self.on_error)


Image._unique_id = "Image-builtin"
