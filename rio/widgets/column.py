from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import widget_base

__all__ = ["Column"]


class Column(widget_base.FundamentalWidget):
    """
    A container that lays out its children vertically.

    Columns are one of the most common widgets in Rio. They take any number of
    children and lay them out vertically, with the first on at the top, the
    second one below that, and so on. All widgets in columns occupy the full
    width.

    <!-- TODO: Explain undefined space -->

    Attributes:
        children: The child widgets in this column.

        spacing: How much space to leave between two adjacent children. No
            spacing is added before the first child or after the last child.
    """

    children: List[widget_base.Widget]
    spacing: float

    def __init__(
        self,
        *children: rio.Widget,
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
            assert isinstance(child, widget_base.Widget), child

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
