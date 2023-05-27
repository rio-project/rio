from __future__ import annotations

from dataclasses import KW_ONLY

import reflex as rx

from .. import theme
from . import widget_base

__all__ = [
    "Button",
    "ButtonPressedEvent",
]


class ButtonPressedEvent(widget_base.WidgetEvent):
    pass


class Button(widget_base.Widget):
    text: str
    on_press: rx.EventHandler[ButtonPressedEvent] = None
    _: KW_ONLY
    major: bool = True
    _is_entered: bool = False
    _is_pressed: bool = False

    def on_mouse_enter(self, event: rx.MouseEnterEvent) -> None:
        self._is_entered = True

    def on_mouse_leave(self, event: rx.MouseLeaveEvent) -> None:
        self._is_entered = False

    def _on_mouse_down(self, event: rx.MouseDownEvent) -> None:
        # Only react to left mouse button
        if event.button != rx.MouseButton.LEFT:
            return

        self._is_pressed = True

    async def _on_mouse_up(self, event: rx.MouseUpEvent) -> None:
        # Only react to left mouse button
        if not self._is_pressed:
            return

        await rx.call_event_handler(
            self.on_press,
            ButtonPressedEvent(self),
        )

        self._is_pressed = False

    def build(self) -> rx.Widget:
        # Change the visuals depending on whether the button is pressed, and
        # whether it's major
        match (self._is_pressed, self.major):
            case (False, False):
                fill = theme.COLOR_NEUTRAL
                stroke_color = theme.COLOR_ACCENT
            case (False, True):
                fill = theme.COLOR_ACCENT
                stroke_color = None
            case (True, False):
                fill = theme.COLOR_ACCENT
                stroke_color = theme.COLOR_ACCENT
            case (True, True):
                fill = theme.COLOR_ACCENT.brighter(0.3)
                stroke_color = None
            case _:
                assert False, "Unreachable"

        # Give visual feedback if the mouse is over the button
        if self._is_entered and not self._is_pressed:
            fill = fill.brighter(0.15)

        # Construct the result
        return rx.MouseEventListener(
            rx.Rectangle(
                child=rx.Text(
                    self.text,
                    font_weight="bold" if self.major else "normal",
                    font_color=fill.contrasting(),
                    margin=0.3,
                ),
                fill=fill,
                stroke_color=stroke_color,
                stroke_width=theme.OUTLINE_WIDTH,
                corner_radius=theme.CORNER_RADIUS,
            ),
            on_mouse_enter=self.on_mouse_enter,
            on_mouse_leave=self.on_mouse_leave,
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )
