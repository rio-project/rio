from __future__ import annotations

from dataclasses import KW_ONLY
from typing import List

from . import widget_base

__all__ = ["Column"]


class Column(widget_base.HtmlWidget):
    children: List[widget_base.Widget]
    _: KW_ONLY
    spacing: float = 0.0


Column._unique_id = "Column-builtin"
