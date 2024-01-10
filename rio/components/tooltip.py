from __future__ import annotations

from typing import *  # type: ignore

import rio

from . import component_base

__all__ = [
    "Tooltip",
]


class Tooltip(component_base.FundamentalComponent):
    anchor: component_base.Component
    tip_text: Optional[str]
    tip_component: Optional[component_base.Component]
    position: Literal["left", "top", "right", "bottom"]

    # Impute a Text instance if a string is passed in as the tip
    def __init__(
        self,
        anchor: component_base.Component,
        tip: Union[str, component_base.Component],
        position: Literal["left", "top", "right", "bottom"],
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

        self.anchor = anchor

        if isinstance(tip, str):
            self.tip_text = tip
            self.tip_component = None
        else:
            self.tip_text = None
            self.tip_component = tip

        self.position = position

        self._explicitly_set_properties_.update(("tip_text", "tip_component"))

    def __post_init__(self):
        if isinstance(self.tip_text, str):
            self.tip_component = rio.Text(self.tip_text)


Tooltip._unique_id = "Tooltip-builtin"
