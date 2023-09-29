from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import class_container, widget_base

__all__ = [
    "Sticky",
]


class Sticky(widget_base.Widget):
    def __init__(
        self,
        child: rio.Widget,
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
        # Passing the layout values through to `Widget` would ignore them,
        # because the HTML `Sticky` element will force itself to span the entire
        # screen.
        #
        # Instead, simply keep track of the values, then pass them on to a
        # `Container` child.
        #
        # Furthermore, another, outer `Container` is needed to ensure that the
        # layouting system doesn't apply any problematic CSS attributes to the
        # `Sticky` div.

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

    def build(self) -> rio.Widget:
        # Outer: This container absorbs any CSS attributes assigned by the
        # layouting system, so that they don't interfere with the `Sticky`
        # element.
        return rio.Container(
            # Sticky: This is the actual sticky element. It spans the entire
            # screen and doesn't scroll.
            class_container.ClassContainer(
                # Inner: This container is used to apply any layouting
                # attributes passed to the `Sticky` widget.
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
                    "rio-sticky",
                ],
            ),
        )