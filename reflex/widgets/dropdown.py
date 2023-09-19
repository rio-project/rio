from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import reflex as rx

from . import widget_base

__all__ = [
    "Dropdown",
    "DropdownChangeEvent",
]

T = TypeVar("T")


@dataclass
class DropdownChangeEvent(Generic[T]):
    value: Optional[T]


class Dropdown(widget_base.FundamentalWidget, Generic[T]):
    options: Mapping[str, T]
    _: KW_ONLY
    label: str
    selected_value: T
    on_change: rx.EventHandler[DropdownChangeEvent[T]]
    is_sensitive: bool = True

    def __init__(
        self,
        options: Mapping[str, T],
        *,
        label: str = "",
        selected_value: Optional[T] = None,
        on_change: Optional[rx.EventHandler[DropdownChangeEvent[T]]] = None,
        key: Optional[str] = None,
        margin: Optional[float] = None,
        margin_x: Optional[float] = None,
        margin_y: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_right: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        width: Union[Literal["natural", "grow"], float] = "natural",
        height: Union[Literal["natural", "grow"], float] = "natural",
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        if not options:
            raise ValueError("`Dropdown` must have at least one option.")

        super().__init__(
            key=key,
            margin=margin,
            margin_x=margin_x,
            margin_y=margin_y,
            margin_left=margin_left,
            margin_top=margin_top,
            margin_right=margin_right,
            margin_bottom=margin_bottom,
            width=width,
            height=height,
            align_x=align_x,
            align_y=align_y,
        )

        self.options = options
        self.label = label
        self.selected_value = (
            next(iter(options.values())) if selected_value is None else selected_value
        )
        self.on_change = on_change
        self.is_sensitive = True

    def _custom_serialize(self) -> JsonDoc:
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
