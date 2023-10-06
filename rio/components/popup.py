from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Popup",
    "PopupOpenOrCloseEvent",
]


@dataclass
class PopupOpenOrCloseEvent:
    is_open: bool


class Popup(component_base.FundamentalComponent):
    anchor: rio.Component
    content: rio.Component
    _: KW_ONLY
    direction: Literal["left", "top", "right", "bottom", "center"] = "center"
    alignment: float = 0.5
    gap: float = 0.0
    is_open: bool = False
    on_open_or_close: rio.EventHandler[PopupOpenOrCloseEvent] = None

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
        # Trigger on_open_or_close event
        try:
            new_value = delta_state["is_open"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value
            await self.call_event_handler(
                self.on_open_or_close,
                PopupOpenOrCloseEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Popup._unique_id = "Popup-builtin"
