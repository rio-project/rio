from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "ThemeContextSwitcher",
]


class ThemeContextSwitcher(FundamentalComponent):
    """
    # ThemeContextSwitcher

    A container which can switch between different components.

    A `ThemeContextSwitcher` is a container which can switch between different
    components. It is commonly used to switch between different themes. The
    `content` attribute can be used to change the currently displayed component.


    ## Attributes:

    `content`: The currently displayed component.

    `color`: The color of the switcher bar.


    ## Example:

    A minimal example of a `ThemeContextSwitcher` will be shown:
    TODO: check if this is the correct example

    ```python
    rio.ThemeContextSwitcher(content=rio.Button("Button"), color="secondary")
    ```
    """

    content: rio.Component
    color: rio.ColorSet

    def _custom_serialize(self) -> JsonDoc:
        return {
            "color": self.session.theme._serialize_colorset(self.color),
        }


ThemeContextSwitcher._unique_id = "ThemeContextSwitcher-builtin"
