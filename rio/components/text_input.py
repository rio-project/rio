from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "TextInput",
    "TextInputChangeEvent",
    "TextInputConfirmEvent",
]


@dataclass
class TextInputChangeEvent:
    text: str


@dataclass
class TextInputConfirmEvent:
    text: str


class TextInput(component_base.KeyboardFocusableFundamentalComponent):
    """
    A user-editable text field.

    `TextInput` allows the user to enter a short text. The text can either be
    shown in plain text, or hidden when used for passwords or other sensitive
    information.

    Attributes:
        text: The text currently entered by the user.

        label: A short text to display next to the text input.

        prefix_text: A short text to display before the text input. Useful for
            displaying currency symbols or other prefixed units.

        suffix_text: A short text to display after the text input. Useful for
            displaying units, parts of e-mail addresses, and similar.

        is_secret: Whether the text should be hidden. Use this to hide sensitive
            information such as passwords.

        is_sensitive: Whether the text input should respond to user input.

        is_valid: Visually displays to the user whether the current text is
            valid. You can use this to signal to the user that their input needs
            to be changed.

        on_change: Triggered when the user changes the text.

        on_confirm: Triggered when the user explicitly confirms their input,
            such as by pressing the "Enter" key. You can use this to trigger
            followup actions, such as logging in or submitting a form.
    """

    text: str = ""
    _: KW_ONLY
    label: str = ""
    prefix_text: str = ""
    suffix_text: str = ""
    is_secret: bool = False
    is_sensitive: bool = True
    is_valid: bool = True
    on_change: rio.EventHandler[TextInputChangeEvent] = None
    on_confirm: rio.EventHandler[TextInputConfirmEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"text"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "text" in delta_state and not self.is_sensitive:
            raise AssertionError(
                f"Frontend tried to set `TextInput.text` even though `is_sensitive` is `False`"
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
                TextInputChangeEvent(new_value),
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
            TextInputChangeEvent(self.text),
        )

        await self.call_event_handler(
            self.on_confirm,
            TextInputConfirmEvent(self.text),
        )

        # Refresh the session
        await self.session._refresh()


TextInput._unique_id = "TextInput-builtin"
