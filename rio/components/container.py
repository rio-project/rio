from __future__ import annotations

import rio

from .component import Component

__all__ = ["Container"]


class Container(Component):
    """
    A component holding a single child.

    `Container` is a simple container which holds a single child component. It
    is useful for when you receive a component as child and wish to add
    additional layout attributes such as a margin.

    Attributes:
        child: The component to place inside the container.
    """

    child: rio.Component

    def build(self) -> rio.Component:
        return self.child
