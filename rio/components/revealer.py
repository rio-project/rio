from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Revealer",
    "RevealerChangeEvent",
]

T = TypeVar("T")


@dataclass
class RevealerChangeEvent:
    is_expanded: bool


class Revealer(component_base.FundamentalComponent):
    header: Optional[str]
    content: component_base.Component
    _: KW_ONLY
    is_expanded: bool = False
    on_change: rio.EventHandler[RevealerChangeEvent] = None

    def _validate_delta_state_from_frontend(self, delta_state: JsonDoc) -> None:
        if not set(delta_state) <= {"is_expanded"}:
            raise AssertionError(
                f"Frontend tried to change `{type(self).__name__}` state: {delta_state}"
            )

        if "is_expanded" in delta_state and self.header is None:
            raise AssertionError(
                f"Frontend tried to set `Revealer.is_expanded` even though it has no `header`"
            )

    async def _call_event_handlers_for_delta_state(self, delta_state: JsonDoc) -> None:
        # Trigger on_change event
        try:
            is_expanded = delta_state["is_expanded"]
        except KeyError:
            pass
        else:
            assert isinstance(is_expanded, bool), is_expanded
            await self.call_event_handler(
                self.on_change,
                RevealerChangeEvent(is_expanded),
            )


Revealer._unique_id = "Revealer-builtin"
