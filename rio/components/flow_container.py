from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base

__all__ = ["FlowContainer"]


class FlowContainer(component_base.FundamentalComponent):
    children: List[component_base.Component]
    _: KW_ONLY
    spacing_x: float
    spacing_y: float

    def __init__(
        self,
        *children: rio.Component,
        spacing_x: float = 0.0,
        spacing_y: float = 0.0,
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
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

        self._explicitly_set_properties_.add("children")


FlowContainer._unique_id = "FlowContainer-builtin"
