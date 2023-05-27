from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import Dict, Generic, Optional, TypeVar

from typing_extensions import Self

import reflex as rx

from .. import messages
from ..common import Jsonable, Readonly
from ..styling import *
from . import widget_base

__all__ = [
    "Dropdown",
]

T = TypeVar("T")


@dataclass
class DropdownChangeEvent(Generic[T]):
    value: Optional[T]


class Dropdown(widget_base.HtmlWidget, Generic[T]):
    options: Mapping[str, T]
    _: KW_ONLY
    value: Optional[T] = None
    on_change: rx.EventHandler[Self, DropdownChangeEvent[T]] = None

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {
            "optionNames": list(self.options.keys()),
        }

    async def _on_message(self, msg: Jsonable) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        msg_value = msg["value"]
        assert isinstance(msg_value, str), msg_value

        # Get the server-side value for this selection
        try:
            self.value = self.options[msg_value]
        except KeyError:
            # Probably due to client lag
            return

        # Trigger on_change event
        await self._call_event_handler(
            self.on_change,
            DropdownChangeEvent(self.value),
        )

        # Update the widget's state
        await self.session.refresh()


Dropdown._unique_id = "Dropdown-builtin"
