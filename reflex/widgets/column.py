from __future__ import annotations

from typing import List

from .widget_base import FundamentalWidget, Widget

__all__ = ["Column"]


class Column(FundamentalWidget):
    children: List[Widget]
