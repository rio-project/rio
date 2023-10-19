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
    """
    A container which floats above other components.

    Popups are containers which float above the page when open. This allows you
    to keep your app clean by default, but present additional information or
    controls when needed.

    They take two children: The `anchor` is always visible and positions the
    popup. The `content` is located inside the popup and is only visible when
    the popup is open.

    The location popups appear at can be customized using the `direction`,
    `alignment` and `gap` attributes. Popups wil do their best to honor those
    settings, but deviate if necessary to ensure they don't go off-screen.

    Attributes:
        anchor: A component which is always visible and positions the popup.

        content: A component which is only visible when the popup is open.

        direction: The direction into which the popup opens.

        alignment: The alignment of the popup within the anchor. If the popup
            opens to the left or right, this is the vertical alignment, with `0`
            being the top and `1` being the bottom. If the popup opens to the
            top or bottom, this is the horizontal alignment, with `0` being the
            left and `1` being the right. Has no effect if the popup opens
            centered.

        gap: How much space to leave between the popup and the anchor. Has no
            effect popup opens centered.

        is_open: Whether the popup is currently open.
    """

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
