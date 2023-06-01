from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore


import reflex as rx

from ..styling import *
from . import widget_base

__all__ = [
    "Dropdown",
    "DropdownChangeEvent",
]

T = TypeVar("T")


@dataclass
class DropdownChangeEvent(Generic[T]):
    value: Optional[T]


class Dropdown(widget_base.HtmlWidget, Generic[T]):
    options: Mapping[str, T]
    _: KW_ONLY
    value: Optional[T] = None
    on_change: rx.EventHandler[DropdownChangeEvent[T]] = None
    _selected_name: Optional[str] = None

    def _custom_serialize(self) -> Dict[str, Any]:
        return {
            "optionNames": list(self.options.keys()),
            "selectedName": self._selected_name,
        }

    async def _on_state_update(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        self._selected_name = msg["value"]
        assert isinstance(self._selected_name, str), self._selected_name

        # Get the server-side value for this selection
        try:
            self.value = self.options[self._selected_name]
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
