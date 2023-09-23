from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal

from uniserde import JsonDoc

from .. import assets
from ..common import EventHandler, ImageLike
from . import widget_base

__all__ = ["Image"]


class Image(widget_base.FundamentalWidget):
    image: ImageLike
    _: KW_ONLY
    fill_mode: Literal["fit", "stretch", "zoom"] = "fit"
    on_error: EventHandler[[]] = None

    def on_created(self) -> None:
        self._image_asset = assets.Asset.from_image(self.image)

    def _custom_serialize(self) -> JsonDoc:
        return {
            "image_url": self._image_asset._serialize(self.session),
            "report_error": self.on_error is not None,
        }

    async def _on_message(self, message: JsonDoc) -> None:
        await self._call_event_handler(self.on_error)


Image._unique_id = "Image-builtin"
