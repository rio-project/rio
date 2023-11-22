from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = ["Grid"]


@dataclass
class GridChildPosition:
    row: int
    column: int
    width: int = 1
    height: int = 1


class Grid(component_base.FundamentalComponent):
    """
    A container which arranges its children in a table-like grid.

    Grids arrange their children in a table-like grid. Each child is placed in
    one or more cells of the grid.

    Example:
    ```python
    # TODO
    ```

    Attributes:
        row_spacing: The amount of space between rows of the grid.

        column_spacing: The amount of space between columns of the grid.
    """

    _: KW_ONLY
    row_spacing: float
    column_spacing: float

    # These must be annotated, otherwise rio won't understand that grids have
    # child components and won't copy over the new values when two Grids are
    # reconciled
    _children: List[rio.Component]
    _child_positions: List[GridChildPosition]

    def __init__(
        self,
        *rows: Iterable[rio.Component],
        row_spacing: float = 0.0,
        column_spacing: float = 0.0,
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

        self.row_spacing = row_spacing
        self.column_spacing = column_spacing

        # JS can only work with lists of Components, so we'll store the
        # components and their positions separately
        _children: List[rio.Component] = []
        _child_positions: List[GridChildPosition] = []

        for row_nr, row_components in enumerate(rows):
            for col_nr, component in enumerate(row_components):
                _children.append(component)
                _child_positions.append(
                    GridChildPosition(
                        row=row_nr,
                        column=col_nr,
                    )
                )

        self._children = _children
        self._child_positions = _child_positions

        self._explicitly_set_properties_.update(["_children", "_child_positions"])

    def add_child(
        self,
        child: rio.Component,
        row: int,
        column: int,
        width: int = 1,
        height: int = 1,
    ) -> None:
        self._children.append(child)
        self._child_positions.append(GridChildPosition(row, column, width, height))

    def _custom_serialize(self) -> JsonDoc:
        return {
            "_children": [child._id for child in self._children],
            "_child_positions": [vars(pos) for pos in self._child_positions],
        }


Grid._unique_id = "Grid-builtin"
