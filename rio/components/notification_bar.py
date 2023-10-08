from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import theme
from . import component_base, text

__all__ = [
    "NotificationBar",
]


class NotificationBar(component_base.Component):
    """
    Displays a short message to the user.

    Notification bars can either show a short text message to the users, or
    disappear entirely if no message is set. Use them to inform the user about
    the result of an action, to give feedback on their input, or anything else
    that needs to be communicated.

    The notifications have one of four levels: success, info, warning, and
    error. The levels control the appearance of the notification bar, and allow
    you to quickly communicate the nature of the message to the user.

    Attributes:
        text: The text to display. If set to `None`, the notification bar will
            disappear entirely.

        level: How severe the message is. The appearance of the notification
            bar will be adjusted according to the level.

        multiline: Whether long text may be wrapped to multiple lines.
    """

    text: Optional[str]
    level: Literal["success", "info", "warning", "error"]

    _: KW_ONLY

    multiline: bool = False

    def build(self) -> rio.Component:
        # Early out: Nothing to show
        if self.text is None:
            return rio.Column()

        # Determine the color
        thm = self.session.attachments[rio.Theme]

        if self.level == "success":
            background_color = thm.success_color
            text_color = thm.text_color_for(background_color)
        elif self.level == "info":
            background_color = thm.secondary_color
            text_color = thm.text_color_for(thm.secondary_color)
        elif self.level == "warning":
            background_color = thm.warning_color
            text_color = thm.text_color_for(background_color)
        elif self.level == "error":
            background_color = thm.danger_color
            text_color = thm.text_color_for(background_color)
        else:
            raise ValueError(f"Invalid level: {self.level!r}")

        # Build the result
        return rio.Rectangle(
            child=text.Text(
                self.text,
                margin=thm.base_spacing,
                multiline=self.multiline,
                style=thm.text_style.replace(
                    fill=text_color,
                ),
            ),
            style=rio.BoxStyle(
                fill=background_color,
                corner_radius=thm.corner_radius_small,
            ),
        )
