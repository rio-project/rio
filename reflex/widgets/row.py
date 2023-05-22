from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Dict, List, Literal, Optional, Tuple

from .. import messages
from ..common import Jsonable
from ..styling import *
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    Widget,
    call_event_handler_and_refresh,
)

__all__ = [
    "Row",
]


class Row(FundamentalWidget):
    children: List[Widget]
