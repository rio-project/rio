from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from .. import app_server
from uniserde import JsonDoc


from uniserde import JsonDoc

import reflex as rx
from reflex import app_server

from .. import app_server, text_style
from . import widget_base

__all__ = [
    "Text",
]


class Text(widget_base.FundamentalWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    style: Union[
        Literal["heading1", "heading2", "heading3", "text"],
        text_style.TextStyle,
    ] = "text"

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.style, str):
            style = self.style
        else:
            style = self.style._serialize(server)

        return {
            "style": style,
        }


Text._unique_id = "Text-builtin"
