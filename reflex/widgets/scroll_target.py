from typing import Optional

from .widget_base import FundamentalWidget, Widget

__all__ = ["ScrollTarget"]


class ScrollTarget(FundamentalWidget):
    id: str
    child: Optional[Widget] = None

    def __post_init__(self):
        if self.id.startswith("reflex-id-"):
            raise ValueError(
                f"Invalid ID for ScrollTarget: `{self.id}`. IDs starting with `reflex-id-` are reserved for internal use."
            )


ScrollTarget._unique_id = "ScrollTarget-builtin"
