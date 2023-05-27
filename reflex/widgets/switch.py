from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Dict

from typing_extensions import Self

import reflex as rx

from ..common import Jsonable
from . import widget_base

__all__ = ["Switch", "SwitchChangeEvent"]


@dataclass
class SwitchChangeEvent:
    is_on: bool


class Switch(widget_base.HtmlWidget):
    is_on: bool = False
    _: KW_ONLY
    on_change: rx.EventHandler[Self, SwitchChangeEvent] = None

    async def _on_state_update(self, delta_state: Dict[str, Jsonable]) -> None:
        # Trigger on_change event
        try:
            new_value = delta_state["is_on"]
        except KeyError:
            pass
        else:
            assert isinstance(new_value, bool), new_value
            await self._call_event_handler(
                self.on_change,
                SwitchChangeEvent(new_value),
            )

        # Chain up
        await super()._on_state_update(delta_state)


Switch._unique_id = "Switch-builtin"
