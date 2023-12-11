from __future__ import annotations

import collections.abc
from typing import *

if TYPE_CHECKING:
    import pandas
    import polars

from uniserde import JsonDoc  # type: ignore

from .. import maybes
from .component_base import FundamentalComponent

__all__ = ["Table"]


TableValue = Union[int, float, str]


class Table(FundamentalComponent):
    data: Union[
        pandas.DataFrame,
        polars.DataFrame,
        Mapping[str, Iterable[TableValue]],
        Iterable[Iterable[TableValue]],
    ]
    show_row_numbers: bool = True

    def _custom_serialize(self) -> JsonDoc:
        data = self.data
        jsonable_data: Dict[str, List[TableValue]]

        maybes.initialize()

        # Convert the data to a dict of lists so it can be serialized as json
        if isinstance(data, collections.abc.Mapping):
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
