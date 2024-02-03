from __future__ import annotations

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Overlay",
]


class Overlay(FundamentalComponent):
    """
    # Overlay
    Displays its child above all other components.

    The overlay component takes a single child component, and displays it above
    all other components on the page. The child will not scroll with the rest of
    the page and is exempt from layouting.

    Components inside of overlays are allocated the entire screen, and are
    themselves responsible for positioning themselves as required. You can
    easily achieve this using the child's `align_x` and `align_y` properties.

    ## Attributes:
    `content:` The component to display in the overlay. It will take up the
        entire size of the screen, so make sure to use properties such as
        `align_x` and `align_y` to position it as needed.

    ## Example:
    An overlay containing a `Text` component will be shown on the middle of your screen:
    ```python
    rio.Overlay(
        rio.Text("Hello, world!"),
        align_x=0.5,
        align_y=0.5,
    )
    """

    content: rio.Component

    def __init__(
        self,
        content: rio.Component,
        *,
        key: str | None = None,
    ):
        # This component intentionally doesn't accept the typical layouting
        # parameters, as the underlying HTML `Overlay` element will force itself
        # to span the entire screen, ignoring them.

        super().__init__(key=key)

        self.content = content


Overlay._unique_id = "Overlay-builtin"
