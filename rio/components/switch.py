from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Switch",
    "SwitchChangeEvent",
]


@dataclass
class SwitchChangeEvent:
    is_on: bool


class Switch(component_base.FundamentalComponent):
    """
    An input for `True` / `False` values.

    Switches allow the user to toggle between an "on" and an "off" state. They
    thus correspond to a Python `bool` value. Use them to allow the user to
    enable or disable certain features, or to select between two options.

    Attributes:
        is_on: Whether the switch is currently in the "on" state.

        is_sensitive: Whether the switch should respond to user input.

        on_change: Triggered when the user toggles the switch.
    """

    is_on: bool = False
    _: KW_ONLY
    is_sensitive: bool = True
    on_change: rio.EventHandler[SwitchChangeEvent] = None

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["is_on"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value
            await self.call_event_handler(
                self.on_change,
                SwitchChangeEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Switch._unique_id = "Switch-builtin"
