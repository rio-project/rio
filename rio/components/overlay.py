from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import class_container, component_base

__all__ = [
    "Overlay",
]


class Overlay(component_base.Component):
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

    def __init__(
        self,
        child: rio.Component,
        *,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        # Passing the layout values through to `Component` would ignore them,
        # because the HTML `Overlay` element will force itself to span the entire
        # screen.
        #
        # Instead, simply keep track of the values, then pass them on to a
        # `Container` child.
        #
        # Furthermore, another, outer `Container` is needed to ensure that the
        # layouting system doesn't apply any problematic CSS attributes to the
        # `Overlay` div.

        super().__init__(
            key=key,
        )
        self._passthrough_margin = margin
        self._passthrough_margin_x = margin_x
        self._passthrough_margin_y = margin_y
        self._passthrough_margin_left = margin_left
        self._passthrough_margin_top = margin_top
        self._passthrough_margin_right = margin_right
        self._passthrough_margin_bottom = margin_bottom
        self._passthrough_width = width
        self._passthrough_height = height
        self._passthrough_align_x = align_x
        self._passthrough_align_y = align_y

        self.child = child

    def build(self) -> rio.Component:
        # Outer: This container absorbs any CSS attributes assigned by the
        # layouting system, so that they don't interfere with the `Overlay`
        # element.
        return rio.Container(
            # Overlay: This is the actual overlay element. It spans the entire
            # screen and doesn't scroll.
            class_container.ClassContainer(
                # Inner: This container is used to apply any layouting
                # attributes passed to the `Overlay` component.
                rio.Container(
                    margin=self._passthrough_margin,
                    margin_x=self._passthrough_margin_x,
                    margin_y=self._passthrough_margin_y,
                    margin_left=self._passthrough_margin_left,
                    margin_top=self._passthrough_margin_top,
                    margin_right=self._passthrough_margin_right,
                    margin_bottom=self._passthrough_margin_bottom,
                    width=self._passthrough_width,  # type: ignore
                    height=self._passthrough_height,  # type: ignore
                    align_x=self._passthrough_align_x,
                    align_y=self._passthrough_align_y,
                    child=rio.Container(
                        child=self.child,
                    ),
                ),
                classes=[
                    "rio-overlay",
                ],
            ),
        )
