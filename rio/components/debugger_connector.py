from typing import *  # type: ignore

from . import component_base

__all__ = [
    "DebuggerConnector",
]


class DebuggerConnector(component_base.FundamentalComponent):
    pass


DebuggerConnector._unique_id = "DebuggerConnector-builtin"
