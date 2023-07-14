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
    selected_value: Optional[T] = None
    on_change: rx.EventHandler[DropdownChangeEvent[T]] = None

    def _custom_serialize(self) -> Dict[str, Any]:
        if not self.options:
            raise ValueError("`Dropdown` must have at least one option.")

        # If no value is selected, choose the first one
        if self.selected_value is None:
            self.selected_value = next(iter(self.options.values()))

        # The value may not be serializable. Get the corresponding name instead.
        for name, value in self.options.items():
            if value == self.selected_value:
                break
        else:
            name = None

        result = {
            "optionNames": list(self.options.keys()),
            "selectedName": name,
        }

        return result

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        # The frontend works with names, not values. Get the corresponding
        # value.
        try:
            self.selected_value = self.options[msg["name"]]
        except KeyError:
            # Invalid names may be sent due to lag between the frontend and
            # backend. Ignore them.
            return

        # Refresh the session
        await self.session._refresh()


Dropdown._unique_id = "Dropdown-builtin"
