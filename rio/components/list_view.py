from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = ["ListView"]


class ListView(component_base.FundamentalComponent):
    children: List[rio.Component]

    def __init__(
        self,
        *children: Union[rio.CustomListItem, rio.HeadingListItem, rio.SimpleListItem],
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
            assert isinstance(
                child,
                (
                    rio.HeadingListItem,
                    rio.SimpleListItem,
                    rio.CustomListItem,
                ),
            ), child

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


ListView._unique_id = "ListView-builtin"
