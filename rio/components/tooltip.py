from __future__ import annotations

from typing import Literal

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Tooltip",
]


class Tooltip(FundamentalComponent):
    anchor: rio.Component
    tip_text: str | None
    tip_component: rio.Component | None
    position: Literal["left", "top", "right", "bottom"]

    # Impute a Text instance if a string is passed in as the tip
    def __init__(
        self,
        anchor: rio.Component,
        tip: str | rio.Component,
        position: Literal["left", "top", "right", "bottom"],
        *,
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

        self._properties_set_by_creator_.update(("tip_text", "tip_component"))

    def __post_init__(self):
        if isinstance(self.tip_text, str):
            self.tip_component = rio.Text(self.tip_text)


Tooltip._unique_id = "Tooltip-builtin"
