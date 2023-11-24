from typing import *

from uniserde import JsonDoc  # type: ignore

from .component_base import FundamentalComponent

__all__ = ["Table"]


TableValue = Union[int, float, str]


class Table(FundamentalComponent):
    data: Union[Mapping[str, Sequence[TableValue]], Sequence[Sequence[TableValue]]]
    show_row_numbers: bool = True

    def _custom_serialize(self) -> JsonDoc:
        data = self.data

        if isinstance(data, list):
            data = {header: column for header, *column in zip(*data)}

        return {
            "data": data,  # type: ignore
        }


Table._unique_id = "Table-builtin"
