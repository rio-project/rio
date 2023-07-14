from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from ..common import Jsonable
from . import widget_base

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


class TextInput(widget_base.HtmlWidget):
    text: str = ""
    placeholder: str = ""
    _: KW_ONLY
    secret: bool = False
    on_change: widget_base.EventHandler[TextInputChangeEvent] = None
    on_confirm: widget_base.EventHandler[TextInputConfirmEvent] = None

    async def _on_state_update(self, delta_state: Dict[str, Jsonable]) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["text"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, str), new_value
            await self._call_event_handler(
                self.on_change,
                TextInputChangeEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)

    async def _on_message(self, msg: Any) -> None:
        # Listen for messages indicating the user has confirmed their input
        #
        # In addition to notifying the backend, these also include the input's
        # current value. This ensures any event handlers actually use the up-to
        # date value.
        assert isinstance(msg, dict), msg
        self.text = msg["text"]

        await self._call_event_handler(
            self.on_change,
            TextInputChangeEvent(self.text),
        )

        await self._call_event_handler(
            self.on_confirm,
            TextInputConfirmEvent(self.text),
        )

        # Refresh the session
        await self.session._refresh()


TextInput._unique_id = "TextInput-builtin"
