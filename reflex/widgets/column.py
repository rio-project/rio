from __future__ import annotations

from dataclasses import KW_ONLY
from typing import List

from .widget_base import FundamentalWidget, Widget

__all__ = ["Column"]


class Column(FundamentalWidget):
    children: List[Widget]
    _: KW_ONLY
    spacing: float = 0.0
