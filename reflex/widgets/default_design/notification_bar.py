from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore
from . import text
from . import theme
from .. import fundamental

import reflex as rx


__all__ = [
    "NotificationBar",
]


class NotificationBar(fundamental.widget_base.Widget):
    text: Optional[str]
    level: Literal["success", "info", "warning", "error"]

    _: KW_ONLY

    multiline: bool = False

    def build(self) -> rx.Widget:
        # Early out: Nothing to show
        if self.text is None:
            return fundamental.Column()

        # Determine the color
        thm = self.session.attachments[theme.Theme]

        if self.level == "success":
            color = thm.success_color
        elif self.level == "info":
            color = thm.accent_color
        elif self.level == "warning":
            color = thm.warning_color
        elif self.level == "error":
            color = thm.danger_color
        else:
            raise ValueError(f"Invalid level: {self.level!r}")

        # Build the result
        return fundamental.Rectangle(
            child=text.Text(
                self.text,
                margin=thm.base_spacing,
                multiline=self.multiline,
                style=thm.text_style.replace(
                    font_color=color.contrasting(0.9),
                ),
            ),
            style=fundamental.BoxStyle(
                fill=color,
                corner_radius=thm.corner_radius,
            ),
        )
