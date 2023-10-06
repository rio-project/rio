from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Drawer",
    "DrawerOpenOrCloseEvent",
]


@dataclass
class DrawerOpenOrCloseEvent:
    is_open: bool


class Drawer(component_base.FundamentalComponent):
    anchor: rio.Component
    content: rio.Component
    _: KW_ONLY
    on_open_or_close: rio.EventHandler[DrawerOpenOrCloseEvent] = None
    side: Literal["left", "right", "top", "bottom"] = "left"
    is_modal: bool = True
    is_open: bool = False
    is_user_openable: bool = True

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
                DrawerOpenOrCloseEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Drawer._unique_id = "Drawer-builtin"
