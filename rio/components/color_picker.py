from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from .. import color
from . import component_base

__all__ = [
    "ColorPicker",
    "ColorChangeEvent",
]


@dataclass
class ColorChangeEvent:
    color: color.Color


class ColorPicker(component_base.FundamentalComponent):
    """
    Allows the user to pick a RGB(A) color.

    `ColorPicker` is a component that allows the user to pick a color. It
    displays a combination of colorful areas and sliders that the user can
    interact with to pick a color, and optionally an opacity slider to pick
    opacity.

    Attributes:
        color: The color that the user has picked.

        pick_opacity: Whether to allow the user to pick opacity. If `False`,
            the opacity slider will be hidden and the color value will be forced
            to be fully opaque.

        on_change: This event is triggered whenever the user changes the color.
    """

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
        await self.call_event_handler(
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
