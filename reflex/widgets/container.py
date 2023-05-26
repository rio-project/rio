from __future__ import annotations

from .widget_base import FundamentalWidget, Widget

__all__ = ["Container"]


class Container(Widget):
    child: Widget

    def build(self) -> Widget:
        return self.child
