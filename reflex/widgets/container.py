from __future__ import annotations

from . import widget_base

__all__ = ["Container"]


class Container(widget_base.Widget):
    child: widget_base.Widget

    def build(self) -> widget_base.Widget:
        return self.child
