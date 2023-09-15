from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import reflex as rx

from .. import theme
from . import text, widget_base

__all__ = [
    "NotificationBar",
]


class NotificationBar(widget_base.Widget):
    text: Optional[str]
    level: Literal["success", "info", "warning", "error"]

    _: KW_ONLY

    multiline: bool = False

    def build(self) -> rx.Widget:
        # Early out: Nothing to show
        if self.text is None:
            return rx.Column()

        # Determine the color
        thm = self.session.attachments[rx.Theme]

        if self.level == "success":
            background_color = thm.success_color
            text_color = thm.text_color_for(background_color)
        elif self.level == "info":
            background_color = thm.secondary_color
            text_color = thm.text_on_secondary_color
        elif self.level == "warning":
            background_color = thm.warning_color
            text_color = thm.text_color_for(background_color)
        elif self.level == "error":
            background_color = thm.danger_color
            text_color = thm.text_color_for(background_color)
        else:
            raise ValueError(f"Invalid level: {self.level!r}")

        # Build the result
        return rx.Rectangle(
            child=text.Text(
                self.text,
                margin=thm.base_spacing,
                multiline=self.multiline,
                style=thm.text_style.replace(
                    font_color=text_color,
                ),
            ),
            style=rx.BoxStyle(
                fill=background_color,
                corner_radius=thm.corner_radius_small,
            ),
        )
