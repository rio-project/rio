from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal, Optional

from .. import styling
from . import widget_base

__all__ = [
    "Text",
]


class Text(widget_base.HtmlWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    style: styling.TextStyle = styling.TextStyle()


Text._unique_id = "Text-builtin"
