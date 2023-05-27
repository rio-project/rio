from __future__ import annotations

from dataclasses import KW_ONLY
from typing import List

import reflex as rx

from . import widget_base

__all__ = [
    "Row",
]


class Row(widget_base.HtmlWidget):
    children: List[rx.Widget]
    _: KW_ONLY
    spacing: float = 0.0


Row._unique_id = "Row-builtin"
