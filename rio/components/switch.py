from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .fundamental_component import FundamentalComponent

__all__ = [
    "Switch",
    "SwitchChangeEvent",
]


@dataclass
class SwitchChangeEvent:
    is_on: bool


class Switch(FundamentalComponent):
    """
    # Switch
    An input for `True` / `False` values.

    Switches allow the user to toggle between an "on" and an "off" state. They
    thus correspond to a Python `bool` value. Use them to allow the user to
    enable or disable certain features, or to select between two options.

    ## Attributes:
    `is_on:` Whether the switch is currently in the "on" state.

    `is_sensitive:` Whether the switch should respond to user input.

    `on_change:` Triggered when the user toggles the switch.

    ## Example:
    A simple switch:
    ```python
    rio.Switch(is_on=True)
    ```
    """

    is_on: bool = False
    _: KW_ONLY
    is_sensitive: bool = True
    on_change: rio.EventHandler[SwitchChangeEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_on"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "is_on" in delta_state and not self.is_sensitive:
            raise AssertionError(
                f"Frontend tried to set `Switch.is_on` even though `is_sensitive` is `False`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
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


Switch._unique_id = "Switch-builtin"
