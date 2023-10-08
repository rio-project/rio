from __future__ import annotations

from typing import *  # type: ignore

from . import component_base

__all__ = ["Container"]


class Container(component_base.Component):
    """
    A component holding a single child.

    `Container` is a simple container which holds a single child component. It
    is useful for when you receive a component as child and wish to add
    additional layout attributes such as a margin.

    Attributes:
        child: The component to place inside the container.
    """

    child: component_base.Component

    def build(self) -> component_base.Component:
        return self.child
