from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from . import component_base

__all__ = [
    "ProgressBar",
]


class ProgressBar(component_base.FundamentalComponent):
    progress: Optional[float] = None


ProgressBar._unique_id = "ProgressBar-builtin"
