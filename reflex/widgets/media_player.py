from __future__ import annotations

import mimetypes
from dataclasses import KW_ONLY
from pathlib import Path
from typing import Union, Optional, cast

from uniserde import JsonDoc

from . import widget_base
from ..session import Session
from ..assets import Asset

__all__ = ["MediaPlayer"]


class MediaPlayer(widget_base.HtmlWidget):
    media: Union[Path, str]
    media_type: Optional[str] = None
    _: KW_ONLY
    loop: bool = True
    autoplay: bool = True
    controls: bool = True
    muted: bool = False
    volume: float = 1.0
    _media_asset: Optional[Asset] = None

    def __post_init__(self):
        if self.media_type is None:
            self.media_type, _ = mimetypes.guess_type(self.media)

            if self.media_type is None:
                raise ValueError(f"Could not guess MIME type for `{self.media}`")
        
        if isinstance(self.media, str):
            self._media_asset = None
        else:
            self._media_asset = Asset.new(self.media, self.media_type)
    

MediaPlayer._unique_id = "MediaPlayer-builtin"
