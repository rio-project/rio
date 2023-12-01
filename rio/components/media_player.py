from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import *  # type: ignore

from uniserde import JsonDoc
from yarl import URL

import rio

from .. import assets, color
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
    media_type: Optional[str]
    loop: bool
    autoplay: bool
    controls: bool
    muted: bool
    volume: float
    background: rio.Fill
    on_playback_end: EventHandler[[]]
    on_error: EventHandler[[]]

    def __init__(
        self,
        media: Union[Path, URL, bytes],
        *,
        media_type: Optional[str] = None,
        loop: bool = False,
        autoplay: bool = False,
        controls: bool = True,
        muted: bool = False,
        volume: float = 1.0,
        background: rio.FillLike = color.Color.TRANSPARENT,
        on_playback_end: EventHandler[[]] = None,
        on_error: EventHandler[[]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
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
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.media = media
        self.media_type = media_type
        self.loop = loop
        self.autoplay = autoplay
        self.controls = controls
        self.muted = muted
        self.volume = volume
        self.background = rio.Fill._try_from(background)
        self.on_playback_end = on_playback_end
        self.on_error = on_error

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
