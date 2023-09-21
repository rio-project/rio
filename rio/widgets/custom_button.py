from __future__ import annotations

from dataclasses import KW_ONLY, field
from typing import *  # type: ignore

import rio as rx

from . import button, widget_base

__all__ = [
    "CustomButton",
]


class CustomButton(widget_base.Widget):
    text: str
    on_press: rx.EventHandler[button.ButtonPressEvent] = None
    _: KW_ONLY
    is_sensitive: bool = True
    style_default: rx.BoxStyle
    style_hover: rx.BoxStyle
    style_press: rx.BoxStyle
    style_insensitive: rx.BoxStyle
    text_style_default: rx.TextStyle
    text_style_hover: rx.TextStyle
    text_style_press: rx.TextStyle
    text_style_insensitive: rx.TextStyle
    transition_speed: float
    ripple: bool = True

    # Internals
    _is_pressed: bool = field(init=False, default=False)
    _is_entered: bool = field(init=False, default=False)

    def _on_mouse_enter(self, event: rx.MouseEnterEvent) -> None:
        self._is_entered = True

    def _on_mouse_leave(self, event: rx.MouseLeaveEvent) -> None:
        self._is_entered = False

    def _on_mouse_down(self, event: rx.MouseDownEvent) -> None:
        # Only react to left mouse button
        if event.button != rx.MouseButton.LEFT:
            return

        self._is_pressed = True

    async def _on_mouse_up(self, event: rx.MouseUpEvent) -> None:
        # Only react to left mouse button, and only if sensitive
        if event.button != rx.MouseButton.LEFT or not self.is_sensitive:
            return

        await self._call_event_handler(
            self.on_press,
            button.ButtonPressEvent(),
        )

        self._is_pressed = False

    def build(self) -> rx.Widget:
        # If not sensitive, use the insensitive style
        if not self.is_sensitive:
            style = self.style_insensitive
            text_style = self.text_style_insensitive
            hover_style = None

        # If pressed use the press style
        elif self._is_pressed:
            style = self.style_press
            text_style = self.text_style_press
            hover_style = None

        # Otherwise use the regular styles
        else:
            style = self.style_default
            hover_style = self.style_hover
            text_style = (
                self.text_style_hover if self._is_entered else self.text_style_default
            )

        # Prepare the child
        child = rx.Text(
            self.text,
            style=text_style,
            margin=0.3,
        )

        return rx.MouseEventListener(
            rx.Rectangle(
                child=child,
                style=style,
                hover_style=hover_style,
                transition_time=self.transition_speed,
                cursor=rx.CursorStyle.POINTER
                if self.is_sensitive
                else rx.CursorStyle.DEFAULT,
            ),
            on_mouse_enter=self._on_mouse_enter,
            on_mouse_leave=self._on_mouse_leave,
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )
