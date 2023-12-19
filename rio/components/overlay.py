from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "Overlay",
]


class Overlay(component_base.FundamentalComponent):
    """
    Displays its child above all other components.

    The overlay component takes a single child widget, and displays it above all
    other components on the page. The child will not scroll with the rest of the
    page and is exempt from layouting.

    Components inside of overlays are allocated the entire screen, and are
    themselves responsible for positioning themselves as required. You can
    easily achieve this using the child's `align_x` and `align_y` properties.

    Attributes:
        child: The component to display in the overlay. It will take up the
        entire size of the screen, so make sure to use properties such as
        `align_x` and `align_y` to position it as needed.
    """

    child: rio.Component

    def __init__(
        self,
        child: rio.Component,
        *,
        key: Optional[str] = None,
    ):
        # This component intentionally doesn't accept the typical layouting
        # parameters, as the underlying HTML `Overlay` element will force itself
        # to span the entire screen, ignoring them.

        super().__init__(
            key=key,
        )

        self.child = child


Overlay._unique_id = "Overlay-builtin"
