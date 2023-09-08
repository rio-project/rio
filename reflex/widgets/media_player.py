from __future__ import annotations

import mimetypes
from dataclasses import KW_ONLY
from pathlib import Path
from typing import Union, Optional, cast

from uniserde import JsonDoc

from . import widget_base
from ..session import Session
from ..assets import HostedAsset

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

    def __post_init__(self):
        if self.media_type is None:
            self.media_type, _ = mimetypes.guess_type(self.media)

            if self.media_type is None:
                raise ValueError(f"Could not guess MIME type for `{self.media}`")
        
        if isinstance(self.media, str):
            self._media_asset = None
        else:
            self._media_asset = HostedAsset(self.media_type, self.media)
    
    def _custom_serialize(self, app_server: object) -> JsonDoc:
        if self._media_asset is None:
            media_url = cast(str, self.media)
        else:
            self.session._app_server.weakly_host_asset(self._media_asset)
            media_url = self._media_asset.url()

        return {
            'mediaUrl': media_url,
        }
    

MediaPlayer._unique_id = "MediaPlayer-builtin"
