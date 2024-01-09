from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "MultiLineTextInput",
    "MultiLineTextInputChangeEvent",
    "MultiLineTextInputConfirmEvent",
]


@dataclass
class MultiLineTextInputChangeEvent:
    text: str


@dataclass
class MultiLineTextInputConfirmEvent:
    text: str


class MultiLineTextInput(component_base.KeyboardFocusableFundamentalComponent):
    text: str = ""
    _: KW_ONLY
    label: str = ""
    is_sensitive: bool = True
    is_valid: bool = True
    on_change: rio.EventHandler[MultiLineTextInputChangeEvent] = None
    on_confirm: rio.EventHandler[MultiLineTextInputConfirmEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"text"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "text" in delta_state and not self.is_sensitive:
            raise AssertionError(
                f"Frontend tried to set `MultiLineTextInput.text` even though `is_sensitive` is `False`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["text"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, str), new_value
            await self.call_event_handler(
                self.on_change,
                MultiLineTextInputChangeEvent(new_value),
            )

        self._apply_delta_state_from_frontend(delta_state)

    async def _on_message(self, msg: Any) -> None:
        # Listen for messages indicating the user has confirmed their input
        #
        # In addition to notifying the backend, these also include the input's
        # current value. This ensures any event handlers actually use the up-to
        # date value.
        assert isinstance(msg, dict), msg

        self._apply_delta_state_from_frontend({"text": msg["text"]})

        await self.call_event_handler(
            self.on_change,
            MultiLineTextInputChangeEvent(self.text),
        )

        await self.call_event_handler(
            self.on_confirm,
            MultiLineTextInputConfirmEvent(self.text),
        )

        # Refresh the session
        await self.session._refresh()


MultiLineTextInput._unique_id = "MultiLineTextInput-builtin"
