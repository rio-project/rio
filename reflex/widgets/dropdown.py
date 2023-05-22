from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import Dict, Generic, List, Literal, Optional, Tuple, TypeVar

from .. import messages
from ..common import Jsonable, Readonly
from ..styling import *
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    WidgetEvent,
    call_event_handler_and_refresh,
)

__all__ = [
    "Dropdown",
]

T = TypeVar("T")


@dataclass
class DropdownChangeEvent(WidgetEvent, Generic[T]):
    value: Optional[T]


class Dropdown(FundamentalWidget, Generic[T]):
    options: Mapping[str, T]
    _: KW_ONLY
    value: Readonly[Optional[T]] = None
    on_change: EventHandler[DropdownChangeEvent[T]] = None

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {
            "optionNames": list(self.options.keys()),
        }

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        if isinstance(msg, messages.DropdownChangeEvent):
            try:
                value = self.options[msg.value]
            except KeyError:
                # Probably due to client lag
                return

            await call_event_handler_and_refresh(
                self,
                DropdownChangeEvent(self, value),
                self.on_change,
            )
