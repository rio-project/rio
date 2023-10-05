from __future__ import annotations

from . import component_base

__all__ = ["Container"]


class Container(component_base.Component):
    child: component_base.Component

    def build(self) -> component_base.Component:
        return self.child
