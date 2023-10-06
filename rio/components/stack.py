from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = ["Stack"]


class Stack(component_base.FundamentalComponent):
    """
    A container that stacks its children in the Z direction.

    `Stacks` are similar to rows and columns, but they stack their children in
    the Z direction instead of the X or Y direction. In other words, the stack's
    children overlap each other, with the first one at the bottom, the second
    one above that, and so on.

    Attributes:
        children: The components to place in this `Stack`.
    """

    children: List[rio.Component]

    def __init__(
        self,
        *children: rio.Component,
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


Stack._unique_id = "Stack-builtin"
