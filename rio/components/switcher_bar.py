from __future__ import annotations

from collections.abc import Mapping
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "SwitcherBarChangeEvent",
    "SwitcherBar",
]

T = TypeVar("T")


@dataclass
class SwitcherBarChangeEvent(Generic[T]):
    value: T


class SwitcherBar(component_base.FundamentalComponent, Generic[T]):
    options: Mapping[str, T]
    _: KW_ONLY
    color: rio.ColorSet
    orientation: Literal["horizontal", "vertical"]
    spacing: float
    selected_value: T
    on_change: rio.EventHandler[SwitcherBarChangeEvent[T]]

    def __init__(
        self,
        options: Mapping[str, T],
        *,
        color: rio.ColorSet = "keep",
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        spacing: float = 1.0,
        selected_value: Optional[T] = None,
        on_change: rio.EventHandler[SwitcherBarChangeEvent[T]] = None,
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
            raise ValueError("`SwitcherBar` must have at least one option.")

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
        self.color = color
        self.orientation = orientation
        self.spacing = spacing
        self.on_change = on_change

        # This is an unsafe assignment, because the value could be `None`. This
        # will be fixed in `on_create`, once the state bindings have been
        # initialized.
        self.selected_value = selected_value  # type: ignore

    @rio.event.on_create
    def _on_create(self) -> None:
        # Make sure a value is selected
        if self.selected_value is None:
            self.selected_value = next(iter(self.options.values()))

    def _fetch_selected_name(self) -> str:
        # The frontend works with names, not values. Get the corresponding
        # name.

        # Avoid hammering a potential state binding
        selected_value = self.selected_value

        # Fetch the name
        for name, value in self.options.items():
            if value == selected_value:
                return name
        else:
            raise ValueError(
                f"There is no option with value `{self.selected_value!r}`."
            )

    def _custom_serialize(self) -> JsonDoc:
        thm = self.session.theme
        result = {
            "optionNames": list(self.options.keys()),
            "selectedName": self._fetch_selected_name(),
            "color": thm._serialize_colorset(self.color),
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

        # Trigger the event
        await self.call_event_handler(
            self.on_change, SwitcherBarChangeEvent(self.selected_value)
        )

        # Refresh the session
        await self.session._refresh()


SwitcherBar._unique_id = "SwitcherBar-builtin"
