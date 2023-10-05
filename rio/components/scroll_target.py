from typing import *  # type: ignore
from typing import Optional

from .component_base import Component, FundamentalComponent

__all__ = ["ScrollTarget"]


class ScrollTarget(FundamentalComponent):
    id: str
    child: Optional[Component] = None

    def __post_init__(self):
        if self.id.startswith("rio-id-"):
            raise ValueError(
                f"Invalid ID for ScrollTarget: `{self.id}`. IDs starting with `rio-id-` are reserved for internal use."
            )


ScrollTarget._unique_id = "ScrollTarget-builtin"
