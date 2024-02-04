from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import *  # type: ignore

from uniserde import JsonDoc

from .. import maybes
from .fundamental_component import FundamentalComponent

if TYPE_CHECKING:
    import numpy
    import pandas
    import polars


__all__ = ["Table"]


TableValue = int | float | str


class Table(FundamentalComponent):
    """
    # Table
    A table of data.

    Tables are a way to display data in a grid, with rows and columns. They are
    very useful for displaying data that is naturally tabular, such as
    spreadsheets, databases, or CSV files. Tables can be sorted by clicking on
    the column headers.

    ## Attributes:
    `data:` The data to display.

    `show_row_numbers:` Whether to show row numbers on the left side of the table.

    ## Example:
    A simple table with some data:
    ```python
    rio.Table(
        data={
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "City": ["New York", "San Francisco", "Los Angeles"],
        }
    )
    ```


    """

    data: (
        pandas.DataFrame
        | polars.DataFrame
        | Mapping[str, Iterable[TableValue]]
        | Iterable[Iterable[TableValue]]
        # | numpy.ndarray
    )
    show_row_numbers: bool = True

    def _custom_serialize(self) -> JsonDoc:
        data = self.data
        jsonable_data: dict[str, list[TableValue]]

        maybes.initialize()

        # Convert the data to a dict of lists so it can be serialized as json
        if isinstance(data, Mapping):
            # For some reason Pyright infers that `data` can be a
            # `Mapping[Iterable[TableValue], Unknown]`. WTF.
            data = cast(Mapping[str, Iterable[TableValue]], data)

            jsonable_data = {
                key: (column if isinstance(column, list) else list(column))
                for key, column in data.items()
            }
        elif isinstance(data, maybes.PANDAS_DATAFRAME_TYPES):
            jsonable_data = {
                str(title): column
                for title, column in data.to_dict(orient="list").items()
            }
        elif isinstance(data, maybes.POLARS_DATAFRAME_TYPES):
            jsonable_data = {
                str(title): column
                for title, column in data.to_dict(as_series=False).items()
            }
        else:
            jsonable_data = {header: column for header, *column in zip(*data)}

        return {
            "data": jsonable_data,  # type: ignore[variance]
        }


Table._unique_id = "Table-builtin"
