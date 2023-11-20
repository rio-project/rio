from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

__all__ = [
    "Card",
]


class Card(component_base.FundamentalComponent):
    """
    A container that visually encompasses its child components.

    Cards are used to group related components together, and to visually
    separate them from other components, allowing you to display them in a
    structured way.

    Cards are also often used as large buttons. They can be configured to
    elevate slightly when the mouse hovers over them, indicating to the user
    that they support interaction.

    Attributes:
        child: The component to display inside the card.

        corner_radius: The radius of the card's corners. If set to `None`, it
            is picked from the active theme.

        on_press: An event handler that is called when the card is clicked.
            Note that attaching an even handler will also modify the appearance
            of the card, to signal the possible interaction to the user. See
            `elevate_on_hover` and `colorize_on_hover` for details.

        elevate_on_hover: Whether the card should elevate slightly when the
            mouse hovers over it. If set to `None` the card will elevate if
            an `on_press` event handler is attached.

        colorize_on_hover: Whether the card should change its color when the
            mouse hovers over it. If set to `None` the card will change its
            color if an `on_press` event handler is attached.
    """

    child: rio.Component
    _: KW_ONLY
    corner_radius: Union[None, float, Tuple[float, float, float, float]] = None
    on_press: rio.EventHandler[[]] = None
    elevate_on_hover: Optional[bool] = None
    colorize_on_hover: Optional[bool] = None
    inner_margin: bool = True
    color: rio.ColorSet = "neutral"

    async def _on_message(self, msg: Any) -> None:
        # Trigger the press event
        await self.call_event_handler(self.on_press)

        # Refresh the session
        await self.session._refresh()

    def _custom_serialize(self) -> JsonDoc:
        thm = self.session.theme
        color = thm._serialize_colorset(self.color)

        report_press = self.on_press is not None

        return {
            "corner_radius": self.corner_radius,
            "reportPress": report_press,
            "elevate_on_hover": (
                report_press if self.elevate_on_hover is None else self.elevate_on_hover
            ),
            "colorize_on_hover": (
                report_press
                if self.colorize_on_hover is None
                else self.colorize_on_hover
            ),
            "color": color,
        }


Card._unique_id = "Card-builtin"
