from __future__ import annotations

from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass
from typing import Literal

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = ["Grid"]


@dataclass
class GridChildPosition:
    row: int
    column: int
    width: int = 1
    height: int = 1


class Grid(FundamentalComponent):
    """
    # Grid

    A container which arranges its children in a table-like grid.

    Grids arrange their children in a table-like grid. Each child is placed in
    one or more cells of the grid. You can add children to the grid either by
    passing them in as a list or by using the `grid_add` method.


    ## Attributes:

    `row_spacing`: The amount of space between rows of the grid.

    `column_spacing`: The amount of space between columns of the grid.


    ## Example:

    This code creates a grid layout with two rows and two columns, and adds
    children to the grid by passing them in as a list:

    ```python
    rio.Grid(
        [rio.Text("Hello"), rio.Text("World!")],  # 1. Row
        [rio.Text("Foo"), rio.Text("Bar")],  # 2. Row
    )
    ```

    Alternatively, you can use the `add_child` method to add children to the grid.
    Here's how you can do it:

    ```python
    grid = rio.Grid(row_spacing=1, column_spacing=1)
    grid.add_child(rio.Text("Hello"), row=0, column=0)
    grid.add_child(rio.Text("World!"), row=0, column=1)
    grid.add_child(rio.Text("Foo"), row=1, column=0)
    grid.add_child(rio.Text("Bar"), row=1, column=1)
    ```

    In your Component class, you can use the `add_child` method within the build function to
    add children to the grid. Here's how you can do it:

    ```python
    class MyComponent(rio.Component):
        def build(self) -> rio.Component:
            grid = rio.Grid(row_spacing=1, column_spacing=1)
            grid.add_child(rio.Text("Hello"), row=0, column=0)
            grid.add_child(rio.Text("World!"), row=0, column=1)
            grid.add_child(rio.Text("Foo"), row=1, column=0)
            grid.add_child(rio.Text("Bar"), row=1, column=1)

            return grid
    ```
    """

    _: KW_ONLY
    row_spacing: float
    column_spacing: float

    # These must be annotated, otherwise rio won't understand that grids have
    # child components and won't copy over the new values when two Grids are
    # reconciled
    _children: list[rio.Component]
    _child_positions: list[GridChildPosition]

    def __init__(
        self,
        *rows: Iterable[rio.Component],
        row_spacing: float = 0.0,
        column_spacing: float = 0.0,
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

        self.row_spacing = row_spacing
        self.column_spacing = column_spacing

        # JS can only work with lists of Components, so we'll store the
        # components and their positions separately
        _children: list[rio.Component] = []
        _child_positions: list[GridChildPosition] = []

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

        self._properties_set_by_creator_.update(["_children", "_child_positions"])

    def add_child(
        self,
        child: rio.Component,
        row: int,
        column: int,
        width: int = 1,
        height: int = 1,
    ) -> None:
        """
        Add a child to the grid at a specified position.

        ## Arguments:

        `child`: The child component to add to the grid.

        `row`: The row in which to place the child.

        `column`: The column in which to place the child.

        `width`: The number of columns the child should take up.

        `height`: The number of rows the child should take up.

        ## Example:

        ```python
        grid = rio.Grid(row_spacing=1, column_spacing=1)
        grid.add_child(rio.Text("Hello"), row=0, column=0)
        ```
        """
        if width <= 0:
            raise ValueError("Children have to take up at least one column")

        if height <= 0:
            raise ValueError("Children have to take up at least one row")

        self._children.append(child)
        self._child_positions.append(GridChildPosition(row, column, width, height))

    def _custom_serialize(self) -> JsonDoc:
        return {
            "_children": [child._id for child in self._children],
            "_child_positions": [vars(pos) for pos in self._child_positions],
        }


Grid._unique_id = "Grid-builtin"
