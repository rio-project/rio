from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Any

from uniserde import JsonDoc

import rio

from .. import color
from .fundamental_component import FundamentalComponent

__all__ = [
    "ColorPicker",
    "ColorChangeEvent",
]


@dataclass
class ColorChangeEvent:
    color: color.Color


class ColorPicker(FundamentalComponent):
    """
    # ColorPicker
    Allows the user to pick a RGB(A) color.

    `ColorPicker` is a component that allows the user to pick a color. It
    displays a combination of colorful areas and sliders that the user can
    interact with to pick a color, and optionally an opacity slider to pick
    opacity.

    ## Attributes:
    `color:` The color that the user has picked.

    `pick_opacity:` Whether to allow the user to pick opacity. If `False`,
            the opacity slider will be hidden and the color value will be forced
            to be fully opaque.

    `on_change:` This event is triggered whenever the user changes the color.

    ## Example:
    Simple color picker:
    ```python
    rio.ColorPicker(
        color=rio.Color.from_rgb(0.5, 0.5, 0.5),
        pick_opacity=True,
    )
    ```

    Color picker with a default color and color will be updated when user changes the color:
    ```python
    class ComponentClass(rio.Component):
        color: rio.Color = rio.Color.from_rgb(0.5, 0.5, 0.5)
        def build(self)->rio.Component:
            return rio.ColorPicker(
                        color=ComponentClass.color,
                        pick_opacity=True,
                    )
    ```

    Color picker with an event handler:
    ```python
    class ComponentClass(rio.Component):
        color: rio.Color = rio.Color.from_rgb(0.5, 0.5, 0.5)
        def on_change_color(self, event: rio.ColorChangeEvent) -> None:
            print(f"Color changed to {event.color}")
        def build(self)->rio.Component:
            return rio.Card(
                rio.ColorPicker(
                        color=ComponentClass.color,
                        pick_opacity=True,
                        on_change=self.on_change_color,
                    ),
                )
    ```

    """

    color: color.Color
    _: KW_ONLY
    pick_opacity: bool = False
    on_change: rio.EventHandler[ColorChangeEvent] = None

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        # Update the color
        self._apply_delta_state_from_frontend(
            {"color": color.Color.from_rgb(*msg["color"])}
        )

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
