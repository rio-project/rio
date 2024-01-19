from __future__ import annotations

from collections.abc import Mapping
from dataclasses import field
from typing import Literal

import rio

from .component import Component

__all__ = ["LabeledColumn"]


class LabeledColumn(Component):
    _child_list: list[Component] = field(init=False)

    def __init__(
        self,
        children: Mapping[str, rio.Component],
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

        self.children = children

    @property
    def children(self) -> Mapping[str, Component]:
        return self._children

    @children.setter
    def children(self, children: Mapping[str, Component]) -> None:
        self._children = children
        self._child_list = list(children.values())

    def build(self) -> Component:
        rows = []

        for label, child in self.children.items():
            rows.append(
                [
                    rio.Text(label, align_x=1),
                    child,
                ]
            )

        return rio.Grid(*rows, row_spacing=0.1, column_spacing=0.2)
