from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import *  # type: ignore

from uniserde import JsonDoc
from yarl import URL

from .. import assets
from ..common import URL, EventHandler
from . import component_base

__all__ = ["MediaPlayer"]


class MediaPlayer(component_base.KeyboardFocusableFundamentalComponent):
    """
    Plays audio and video.

    `MediaPlayer` plays back audio and video files. It can play local files and
    URLs.

    Note that the `MediaPlayer` component doesn't reserve any space for itself,
    it simply makes do with the space it is given by its parent component.

    Attributes:
        media: The media to play. This can be a file path, URL, or bytes.

        media_type: The mime type of the media file. May help the browser to
            play the file correctly.

        loop: Whether to automatically restart from the beginning when the
            playback ends.

        autoplay: Whether to start playing the media automatically, without
            requiring the user to press "Play".

        controls: Whether to display controls like a Play/Pause button, volume
            slider, etc.

        muted: Whether to mute the audio.

        volume: The volume to play the audio at. 1.0 is the native volume;
            larger numbers increase the volume, smaller numbers decrease it.

        on_playback_end: An event handler to call when the media finishes
            playing.

        on_error: An event handler to call when an error occurs, for example if
            the file format isn't supported.
    """

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

    def _custom_serialize(self) -> JsonDoc:
        media_asset = assets.Asset.new(self.media, self.media_type)
        return {
            "mediaUrl": media_asset._serialize(self.session),
            "reportError": self.on_error is not None,
            "reportPlaybackEnd": self.on_playback_end is not None,
        }

    async def _on_message(self, message: JsonDoc) -> None:
        if message["type"] == "playbackEnd":
            await self.call_event_handler(self.on_playback_end)
        elif message["type"] == "error":
            await self.call_event_handler(self.on_error)


MediaPlayer._unique_id = "MediaPlayer-builtin"
