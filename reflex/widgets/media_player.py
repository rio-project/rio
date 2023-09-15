from __future__ import annotations

import mimetypes
from dataclasses import KW_ONLY
from pathlib import Path
from typing import Optional, Union

from ..assets import Asset
from ..common import URL
from . import widget_base

__all__ = ["MediaPlayer"]


class MediaPlayer(widget_base.FundamentalWidget):
    media: Union[Path, URL, bytes]
    media_type: Optional[str] = None
    _: KW_ONLY
    loop: bool = True
    autoplay: bool = True
    controls: bool = True
    muted: bool = False
    volume: float = 1.0
    _media_asset: Optional[Asset] = None

    def __post_init__(self):
        if self.media_type is None and not isinstance(self.media, bytes):
            self.media_type, _ = mimetypes.guess_type(str(self.media))

        self._media_asset = Asset.new(self.media, self.media_type)


MediaPlayer._unique_id = "MediaPlayer-builtin"
