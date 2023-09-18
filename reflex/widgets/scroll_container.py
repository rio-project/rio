from dataclasses import KW_ONLY
from typing import Literal

from .widget_base import FundamentalWidget, Widget

__all__ = ["ScrollContainer"]


class ScrollContainer(FundamentalWidget):
    child: Widget
    _: KW_ONLY
    scroll_x: Literal["never", "auto", "always"] = "auto"
    scroll_y: Literal["never", "auto", "always"] = "auto"


ScrollContainer._unique_id = "ScrollContainer-builtin"
