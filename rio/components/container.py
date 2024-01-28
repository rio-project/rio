from __future__ import annotations

from typing import *  # type: ignore

import rio

from .component import Component

__all__ = [
    "Container",
]


class Container(Component):
    """
    # Container
    A component holding a single child.

    `Container` is a simple container which holds a single child component. It
    is useful for when you receive a component as child and wish to add
    additional layout attributes such as a margin.

    ##Attributes:
    `content:` The component to place inside the container.

    ## Example:
    A container with a margin:
    ```python
    rio.Container(
        content=rio.Text("Hello World!"),
        margin=1,
    )
    ```
    """

    content: rio.Component

    def build(self) -> rio.Component:
        return self.content
