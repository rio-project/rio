from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Dict, List, Literal, Optional, Tuple

from .. import messages
from ..common import Jsonable
from ..styling import *
from . import event_classes
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    Widget,
    call_event_handler_and_refresh,
)

__all__ = [
    "Override",
]


class Override(FundamentalWidget):
    child: Widget
    width: Optional[float] = None
    height: Optional[float] = None