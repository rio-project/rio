from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Dict

from typing_extensions import Self
from uniserde import Jsonable, JsonDoc

import reflex as rx

from .. import app_server, theme
from . import widget_base

__all__ = [
    "Switch",
    "SwitchChangeEvent",
]


@dataclass
class SwitchChangeEvent:
    is_on: bool


class Switch(widget_base.HtmlWidget):
    is_on: bool = False
    _: KW_ONLY
    on_change: rx.EventHandler[SwitchChangeEvent] = None

    def _custom_serialize(self, server: app_server.AppServer) -> JsonDoc:
        thm = self.session.attachments[rx.Theme]
        knob_color_on = thm.accent_color
        background_color_on = thm.accent_color.brighter(0.3).desaturated(0.4)

        return {
            "knobColorOn": knob_color_on.rgba,
            "knobColorOff": knob_color_on.darker(0.3).desaturated(1.0).rgba,
            "backgroundColorOn": background_color_on.rgba,
            "backgroundColorOff": background_color_on.darker(0.2).desaturated(1.0).rgba,
        }

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
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
