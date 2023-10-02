from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import theme
from . import widget_base

__all__ = [
    "Card",
]


class Card(widget_base.Widget):
    child: rio.Widget
    _: KW_ONLY
    corner_radius: Union[None, float, Tuple[float, float, float, float]] = None
    on_press: rio.EventHandler[[]] = None
    elevate_on_hover: Optional[bool] = None
    _is_hovered: bool = False

    def _on_mouse_enter(self, event: rio.MouseEnterEvent) -> None:
        self._is_hovered = True

    def _on_mouse_leave(self, event: rio.MouseLeaveEvent) -> None:
        self._is_hovered = False

    async def _on_press(self, event: rio.MouseUpEvent) -> None:
        await self.call_event_handler(self.on_press)

    def build(self) -> rio.Widget:
        thm = self.session.attachments[theme.Theme]

        # Does this card act as a button?
        act_as_button = self.on_press is not None
        elevate_on_hover = (
            act_as_button if self.elevate_on_hover is None else self.elevate_on_hover
        )

        # Prepare the regular style
        corner_radius = (
            thm.corner_radius_medium
            if self.corner_radius is None
            else self.corner_radius
        )

        style = rio.BoxStyle(
            fill=thm.surface_color,
            corner_radius=corner_radius,
            shadow_color=thm.shadow_color,
        )

        # Prepare the hover style
        hover_style = style.replace(
            fill=thm.surface_active_color if act_as_button else thm.surface_color,
            shadow_radius=0.2 if elevate_on_hover else None,
            shadow_offset_y=0.12 if elevate_on_hover else None,
        )

        # Build the card
        result = rio.Rectangle(
            child=rio.Container(
                self.child,
                margin=thm.base_spacing * 1.7,
            ),
            style=style,
            hover_style=hover_style,
            transition_time=0.2,
            cursor=rio.CursorStyle.POINTER
            if act_as_button
            else rio.CursorStyle.DEFAULT,
        )

        # Wrap it in a mouse event listener, if needed
        if act_as_button:
            result = rio.MouseEventListener(
                result,
                on_mouse_up=self._on_press,
            )

        return result
