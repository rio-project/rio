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


Text._unique_id = "Text-builtin"
