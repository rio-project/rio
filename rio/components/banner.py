from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import theme
from . import component_base, text

__all__ = [
    "Banner",
]


class Banner(component_base.Component):
    """
    Displays a short message to the user.

    Banners can either show a short text message to the users, or disappear
    entirely if no message is set. Use them to inform the user about the result
    of an action, to give feedback on their input, or anything else that needs
    to be communicated.

    The messages have one of four levels: success, info, warning, and error. The
    levels control the appearance of the notification bar, and allow you to
    quickly communicate the nature of the message to the user.

    Attributes:
        text: The text to display. If set to `None`, the banner will disappear
        entirely.

        level: How severe the message is. The appearance of the banner will be
        adjusted according to the level.

        multiline: Whether long text may be wrapped over multiple lines.
    """

    text: Optional[str]
    style: Literal["success", "info", "warning", "error"]

    _: KW_ONLY

    multiline: bool = False

    def build(self) -> rio.Component:
        # Early out: Nothing to show
        if self.text is None:
            return rio.Column()

        # Determine the color
        thm = self.session.attachments[rio.Theme]

        if self.style == "success":
            background_color = thm.success_color
            text_color = thm.text_color_for(background_color)
            context_name = "success"
        elif self.style == "info":
            background_color = thm.secondary_color
            text_color = thm.text_color_for(thm.secondary_color)
            context_name = "secondary"
        elif self.style == "warning":
            background_color = thm.warning_color
            text_color = thm.text_color_for(background_color)
            context_name = "warning"
        elif self.style == "error":
            background_color = thm.danger_color
            text_color = thm.text_color_for(background_color)
            context_name = "danger"
        else:
            raise ValueError(f"Invalid level: {self.style!r}")

        # Build the result
        return rio.StyleContext(
            child=rio.Rectangle(
                child=text.Text(
                    self.text,
                    margin=0.8,
                    multiline=self.multiline,
                    style=thm.text_style.replace(
                        fill=text_color,
                    ),
                ),
                style=rio.BoxStyle(
                    fill=background_color,
                    corner_radius=thm.corner_radius_small,
                ),
            ),
            context=context_name,
        )
