from __future__ import annotations

from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import color
from . import component_base

__all__ = [
    "CodeExplorer",
]


class CodeExplorer(component_base.FundamentalComponent):
    source_code: str
    build_result: rio.Component


CodeExplorer._unique_id = "CodeExplorer-builtin"
