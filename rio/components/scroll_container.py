from dataclasses import KW_ONLY
from typing import *  # type: ignore

from .component_base import Component, FundamentalComponent

__all__ = ["ScrollContainer"]


class ScrollContainer(FundamentalComponent):
    child: Component
    _: KW_ONLY
    scroll_x: Literal["never", "auto", "always"] = "auto"
    scroll_y: Literal["never", "auto", "always"] = "auto"


ScrollContainer._unique_id = "ScrollContainer-builtin"
