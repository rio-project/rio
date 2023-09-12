from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from typing import Optional

import reflex as rx

from . import widget_base

__all__ = [
    "SizeTripSwitch",
]


class SizeTripSwitch(widget_base.FundamentalWidget):
    child: rx.Widget
    _: KW_ONLY
    width_threshold: Optional[float] = None
    height_threshold: Optional[float] = None
    is_wide: bool = False
    is_tall: bool = False


SizeTripSwitch._unique_id = "SizeTripSwitch-builtin"
