from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "MarkdownView",
]


class MarkdownView(component_base.FundamentalComponent):
    text: str
    _: KW_ONLY
    default_language: Optional[str] = None


MarkdownView._unique_id = "MarkdownView-builtin"
