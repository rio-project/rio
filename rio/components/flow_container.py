from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Literal

import rio

from .fundamental_component import FundamentalComponent

__all__ = ["FlowContainer"]


class FlowContainer(FundamentalComponent):
    children: list[rio.Component]
    _: KW_ONLY
    spacing_x: float
    spacing_y: float

    def __init__(
        self,
        *children: rio.Component,
        spacing_x: float = 0.0,
        spacing_y: float = 0.0,
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
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y


FlowContainer._unique_id = "FlowContainer-builtin"
