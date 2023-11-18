from dataclasses import field
from typing import List, Literal, Mapping, Optional, Union

import rio

from .component_base import Component

__all__ = ["LabeledColumn"]


class LabeledColumn(Component):
    _child_list: List[Component] = field(init=False)

    def __init__(
        self,
        children: Mapping[str, Component],
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
