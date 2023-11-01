from typing import *

from uniserde import JsonDoc  # type: ignore

from .component_base import FundamentalComponent

__all__ = ["Table"]


TableValue = Union[int, float, str]


class Table(FundamentalComponent):
    data: Dict[str, List[TableValue]]

    def _custom_serialize(self) -> JsonDoc:
        data = self.data

        return {
            "data": data,  # type: ignore
        }


Table._unique_id = "Table-builtin"
