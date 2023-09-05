from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from .. import app_server, text_style
from . import widget_base

__all__ = [
    "Text",
]


class Text(widget_base.HtmlWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    style: Optional[text_style.TextStyle] = None

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        # If a custom style is set, there is nothing to do
        if self.style is not None:
            return {}

        # Otherwise fetch and serialize the style from the theme
        thm = self.session.attachments[rx.Theme]
        return {
            "style": thm.text_on_surface_style._serialize(server),
        }


Text._unique_id = "Text-builtin"
