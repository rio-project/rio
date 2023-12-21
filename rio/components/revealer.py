from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import text_style
from . import component_base

__all__ = [
    "Revealer",
    "RevealerChangeEvent",
]

T = TypeVar("T")


@dataclass
class RevealerChangeEvent:
    is_open: bool


class Revealer(component_base.FundamentalComponent):
    header: Optional[str]
    content: component_base.Component
    _: KW_ONLY
    header_style: Union[
        Literal["heading1", "heading2", "heading3", "text"],
        text_style.TextStyle,
    ] = "text"
    is_open: bool = False
    on_change: rio.EventHandler[RevealerChangeEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_open"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "is_open" in delta_state and self.header is None:
            raise AssertionError(
                f"Frontend tried to set `Revealer.is_open` even though it has no `header`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["is_open"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value
            await self.call_event_handler(
                self.on_change,
                RevealerChangeEvent(new_value),
            )

    def _custom_serialize(self) -> JsonDoc:
        # Serialization doesn't handle unions. Hence the custom serialization
        # here
        if isinstance(self.header_style, str):
            header_style = self.header_style
        else:
            header_style = self.header_style._serialize(self.session)

        return {
            "header_style": header_style,
        }


Revealer._unique_id = "Revealer-builtin"
