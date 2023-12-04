from __future__ import annotations

from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from . import component_base

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
        text: The text to display. If empty, the banner will disappear entirely.

        style: Controls the appearance of the banner. The style is one of
            `info`, `success`, `warning` and `danger`. Depending on the value
            the banner may change its colors and icon.

        multiline: Whether long text may be wrapped over multiple lines.
            Multiline banners are also styled slightly differently to make the
            icon fit their larger size.
    """

    text: str
    style: Literal["info", "success", "warning", "danger"]

    _: KW_ONLY
    markup: bool = False
    multiline: bool = False

    def build(self) -> rio.Component:
        # Early out: Nothing to show
        if not self.text:
            return rio.Spacer(width=0, height=0)

        # Prepare the style
        if self.style == "info":
            style_name = "secondary"
            icon = "info"
        elif self.style == "success":
            style_name = "success"
            icon = "check-circle"
        elif self.style == "warning":
            style_name = "warning"
            icon = "warning"
        elif self.style == "danger":
            style_name = "danger"
            icon = "error"
        else:
            raise ValueError(f"Invalid style: {self.style}")

        # Prepare the text child
        if self.markup:
            text_child = rio.MarkdownView(
                self.text,
                width="grow",
            )
        else:
            text_child = rio.Text(
                self.text,
                width="grow",
                multiline=self.multiline,
            )

        # Build the result
        if self.multiline:
            return rio.Card(
                child=rio.Row(
                    rio.Icon(
                        icon,
                        width=2.5,
                        height=2.5,
                        align_y=0,
                    ),
                    text_child,
                    spacing=1.5,
                    margin=0.5,
                ),
                color=style_name,
            )

        return rio.Card(
            child=rio.Row(
                rio.Icon(icon),
                text_child,
                spacing=0.8,
                align_x=0.5,
            ),
            color=style_name,
            corner_radius=self.session.theme.corner_radius_small,
        )
