from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import theme
from . import widget_base

__all__ = [
    "Card",
]


def calculate_shadow_for_height(
    thm: rio.Theme, hover_height: float
) -> Tuple[rio.Color, float]:
    """
    Given a hover height, calculate the shadow color and radius.
    """

    # Avoid a division by zero
    if hover_height == 0:
        return thm.shadow_color, 0

    shadow_opacity = min(thm.shadow_color.opacity / hover_height, 0.9)

    return (
        thm.shadow_color.replace(opacity=shadow_opacity),
        thm.shadow_radius * hover_height,
    )


class Card(widget_base.Widget):
    child: rio.Widget
    _: KW_ONLY
    corner_radius: Union[None, float, Tuple[float, float, float, float]] = None
    hover_height: float = 1.0
    elevate_on_hover: float = 0.0
    _is_hovered: bool = False

    def _on_mouse_enter(self, event: rio.MouseEnterEvent) -> None:
        self._is_hovered = True

    def _on_mouse_leave(self, event: rio.MouseLeaveEvent) -> None:
        self._is_hovered = False

    def build(self) -> rio.Widget:
        thm = self.session.attachments[theme.Theme]

        # Prepare the regular style
        corner_radius = (
            thm.corner_radius_medium
            if self.corner_radius is None
            else self.corner_radius
        )

        shadow_color, shadow_radius = calculate_shadow_for_height(
            thm,
            self.hover_height,
        )

        style = rio.BoxStyle(
            fill=thm.surface_color,
            corner_radius=corner_radius,
            shadow_color=shadow_color,
            shadow_radius=shadow_radius,
        )

        # Prepare the hover style
        shadow_color, shadow_radius = calculate_shadow_for_height(
            thm,
            self.hover_height + self.elevate_on_hover,
        )

        hover_style = style.replace(
            shadow_color=shadow_color,
            shadow_radius=shadow_radius,
        )

        # Build the card
        return rio.Rectangle(
            child=rio.Container(
                self.child,
                margin=thm.base_spacing * 1.7,
            ),
            style=style,
            hover_style=hover_style,
            transition_time=0.3,
        )
