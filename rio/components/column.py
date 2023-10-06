from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = ["Column"]


class Column(component_base.FundamentalComponent):
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

    children: List[component_base.Component]
    spacing: float

    def __init__(
        self,
        *children: rio.Component,
        spacing: float = 0.0,
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
        assert isinstance(children, tuple), children
        for child in children:
            assert isinstance(child, component_base.Component), child

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
