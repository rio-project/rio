from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Dict

from typing_extensions import Self

import reflex as rx

from .. import messages
from ..common import Jsonable
from . import widget_base

__all__ = ["TextInput", "TextInputChangeEvent"]


@dataclass
class TextInputChangeEvent:
    text: str


class TextInput(widget_base.HtmlWidget):
    text: str = ""
    placeholder: str = ""
    _: KW_ONLY
    secret: bool = False
    on_change: widget_base.EventHandler[TextInputChangeEvent] = None

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


TextInput._unique_id = "TextInput-builtin"
