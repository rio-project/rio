from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import cursor_style
from . import component_base

__all__ = [
    "Rectangle",
]


class Rectangle(component_base.FundamentalComponent):
    """
    A customizable rectangle shape.

    Rectangles are versatile components that can be used to build up more
    complex elements. While not particularly interesting on their own, combining
    a rectangle with other components allows you to quickly create custom
    buttons, cards, or anything els you may need in your app.

    Rectangles also act as a simple source of animations. They accept two
    styles: A default style for when the user isn't interacting with them, and a
    hover style for when the mouse hovers above them. This, along with their
    `transition_time` attribute allows you to make your app feel dynamic and
    alive.

    Attributes:
        style: How the rectangle should appear when the user isn't interacting
            with it.

        child: The component to display inside the rectangle.

        hover_style: The style of the rectangle when the mouse hovers above it.
            If set to `None`, the rectangle will not change its appearance when
            hovered.

        transition_time: How many seconds it should take for the rectangle to
            transition between its styles.

        cursor: The cursor to display when the mouse hovers above the rectangle.

        ripple: Whether to display a Material Design ripple effect when the
            rectangle is hovered or clicked.
    """

    _: KW_ONLY
    style: rio.BoxStyle
    child: Optional[rio.Component] = None
    hover_style: Optional[rio.BoxStyle] = None
    transition_time: float = 1.0
    cursor: rio.CursorStyle = cursor_style.CursorStyle.DEFAULT
    ripple: bool = False


Rectangle._unique_id = "Rectangle-builtin"
