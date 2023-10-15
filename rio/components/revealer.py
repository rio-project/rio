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
                RevealerChangeEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Revealer._unique_id = "Revealer-builtin"
