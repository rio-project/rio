from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from typing import Optional

import rio

from . import component_base

__all__ = [
    "SizeTripSwitch",
]


class SizeTripSwitch(component_base.FundamentalComponent):
    child: rio.Component
    _: KW_ONLY
    width_threshold: Optional[float] = None
    height_threshold: Optional[float] = None
    is_wide: bool = False
    is_tall: bool = False


SizeTripSwitch._unique_id = "SizeTripSwitch-builtin"
