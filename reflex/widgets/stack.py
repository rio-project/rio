from __future__ import annotations

from typing import List

import reflex as rx

from . import widget_base

__all__ = [
    "Stack",
]


class Stack(widget_base.HtmlWidget):
    children: List[rx.Widget]


Stack._unique_id = "Stack-builtin"
