from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import reflex as rx

from . import widget_base

__all__ = [
    "MarkdownView",
]


class MarkdownView(widget_base.FundamentalWidget):
    text: str
    _: KW_ONLY
    default_language: Optional[str] = None


MarkdownView._unique_id = "MarkdownView-builtin"
