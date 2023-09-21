from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import app_server, color
from . import widget_base

__all__ = [
    "ColorPicker",
    "ColorChangeEvent",
]


@dataclass
class ColorChangeEvent:
    color: color.Color


class ColorPicker(widget_base.FundamentalWidget):
    color: color.Color
    _: KW_ONLY
    pick_opacity: bool = False
    on_change: rio.EventHandler[ColorChangeEvent] = None

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        # Update the color
        self.color = color.Color.from_rgb(*msg["color"])

        # Trigger the change event
        await self._call_event_handler(
            self.on_change,
            ColorChangeEvent(self.color),
        )

        # Refresh the session
        await self.session._refresh()

    def _custom_serialize(self) -> JsonDoc:
        return {
            "color": self.color.rgba,
        }


ColorPicker._unique_id = "ColorPicker-builtin"
