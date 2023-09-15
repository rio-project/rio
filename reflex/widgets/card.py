from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import reflex as rx

from .. import theme
from . import widget_base

__all__ = [
    "Card",
]


class Card(widget_base.Widget):
    child: rx.Widget
    _: KW_ONLY
    corner_radius: Optional[float] = None
    hover_height: float = 1.0
    _is_hovered: bool = False

    def _on_mouse_enter(self, event: rx.MouseEnterEvent) -> None:
        self._is_hovered = True

    def _on_mouse_leave(self, event: rx.MouseLeaveEvent) -> None:
        self._is_hovered = False

    def build(self) -> rx.Widget:
        thm = self.session.attachments[theme.Theme]

        # The higher up the card the larger, but weaker the shadow is
        hover_height = self.hover_height + self._is_hovered * 0.7

        if hover_height == 0:
            shadow_opacity = 0.9
        else:
            shadow_opacity = min(thm.shadow_color.opacity / hover_height, 0.9)

        # Build the result
        return rx.MouseEventListener(
            rx.Rectangle(
                child=rx.Container(
                    self.child,
                    margin=thm.base_spacing * 1.5,
                ),
                style=rx.BoxStyle(
                    fill=thm.surface_color,
                    corner_radius=thm.corner_radius_small
                    if self.corner_radius is None
                    else self.corner_radius,
                    shadow_color=thm.shadow_color.replace(opacity=shadow_opacity),
                    shadow_radius=thm.shadow_radius * hover_height,
                ),
                transition_time=0.3,
            ),
            on_mouse_enter=self._on_mouse_enter,
            on_mouse_leave=self._on_mouse_leave,
        )
