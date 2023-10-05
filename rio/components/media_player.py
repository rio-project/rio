from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import Optional, Union

from uniserde import JsonDoc
from yarl import URL

from .. import assets
from ..common import URL, EventHandler
from . import component_base

__all__ = ["MediaPlayer"]


class MediaPlayer(component_base.FundamentalComponent):
    media: Union[Path, URL, bytes]
    media_type: Optional[str] = None
    _: KW_ONLY
    loop: bool = True
    autoplay: bool = True
    controls: bool = True
    muted: bool = False
    volume: float = 1.0
    on_playback_end: EventHandler[[]] = None
    on_error: EventHandler[[]] = None

    def __post_init__(self):
        self._media_asset = assets.Asset.new(self.media, self.media_type)

    def _custom_serialize(self) -> JsonDoc:
        return {
            "mediaUrl": self._media_asset._serialize(self.session),
            "reportError": self.on_error is not None,
            "reportPlaybackEnd": self.on_playback_end is not None,
        }

    async def _on_message(self, message: JsonDoc) -> None:
        if message["type"] == "playbackEnd":
            await self.call_event_handler(self.on_playback_end)
        elif message["type"] == "error":
            await self.call_event_handler(self.on_error)


MediaPlayer._unique_id = "MediaPlayer-builtin"
