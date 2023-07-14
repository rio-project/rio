from __future__ import annotations

from dataclasses import KW_ONLY
from pathlib import Path
from typing import Union

from . import widget_base

__all__ = ["MediaPlayer"]


class MediaPlayer(widget_base.HtmlWidget):
    media: Union[Path, str]
    _: KW_ONLY
    loop: bool = True
    autoplay: bool = True
    controls: bool = True
    muted: bool = False
    volume: float = 1.0

    def __post_init__(self):
        self._media_url = (
            self.media if isinstance(self.media, str) else self.media.FIXME
        )


MediaPlayer._unique_id = "MediaPlayer-builtin"
