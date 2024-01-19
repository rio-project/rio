from __future__ import annotations

from typing import Literal

import rio

from .fundamental_component import FundamentalComponent

__all__ = ["Column"]


class Column(FundamentalComponent):
    """
    A container that lays out its children vertically.

    `Column`s are one of the most common components in Rio. They take any number
    of children and lay them out vertically, with the first one at the top, the
    second one below that, and so on. All components in `Column`s occupy the
    full width of their parent.

    The `Column`'s horizontal counterpart is the `Row`. A similar component, but
    stacking its children in the Z direction, is the `Stack`.

    ### Undefined Space

    Like most containers in `rio`, `Column`s always attempt to allocate all
    available space to their children. In the context of a `Column` though, this
    could easily lead to unexpected results. If more space is available than
    needed, should all children grow? Only the first? Should they grow by equal
    amounts, or proportionally?

    To avoid this ambiguity, `Column`s have a concept of *undefined space*.
    Simply put, **not using all available space is considered an error and
    should be avoided.** `Column`s indicate this by highlighting the extra space
    with unmistakable animated sprites.

    Getting rid of undefined space is easy: Depending on what look you're going
    for, either add a `Spacer` somewhere into your `Column`, assign one of the
    components a `"grow"` value as its height, or set the `Column`'s vertical
    alignment.

    Attributes:
        children: The components to place in this `Column`.

        spacing: How much empty space to leave between two adjacent children. No
            spacing is added before the first child or after the last child.
    """

    children: list[rio.Component]
    spacing: float

    def __init__(
        self,
        *children: rio.Component,
        spacing: float = 0.0,
        key: str | None = None,
        margin: float | None = None,
        margin_x: float | None = None,
        margin_y: float | None = None,
        margin_left: float | None = None,
        margin_top: float | None = None,
        margin_right: float | None = None,
        margin_bottom: float | None = None,
        width: float | Literal["natural", "grow"] = "natural",
        height: float | Literal["natural", "grow"] = "natural",
        align_x: float | None = None,
        align_y: float | None = None,
    ):
        assert isinstance(children, tuple), children
        for child in children:
            assert isinstance(child, rio.Component), child

        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.children = list(children)
        self.spacing = spacing


Column._unique_id = "Column-builtin"
