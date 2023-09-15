from __future__ import annotations

import reflex as rx

from . import widget_base

__all__ = [
    "MarkdownView",
]


class MarkdownView(widget_base.FundamentalWidget):
    text: str


MarkdownView._unique_id = "MarkdownView-builtin"
