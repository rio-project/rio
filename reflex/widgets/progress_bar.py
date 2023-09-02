from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import widget_base

__all__ = [
    "ProgressBar",
]


class ProgressBar(widget_base.HtmlWidget):
    progress: Optional[float] = None


ProgressBar._unique_id = "ProgressBar-builtin"
