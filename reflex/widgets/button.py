from __future__ import annotations

import reflex as rx

from . import widget_base

__all__ = ["Button"]


class Button(widget_base.Widget):
    text: str
    on_press: rx.EventHandler[[]] = None
    _is_pressed: bool = False

    def _on_mouse_down(self, event: rx.MouseDownEvent) -> None:
        self._is_pressed = True

    async def _on_mouse_up(self, event: rx.MouseUpEvent) -> None:
        await rx.call_event_handler(self.on_press)
        self._is_pressed = False

    def build(self) -> rx.Widget:
        return rx.MouseEventListener(
            rx.Rectangle(
                rx.Color.from_rgb(1, 0, 0.5) if self._is_pressed else rx.Color.RED,
                rx.Margin(
                    rx.Text(self.text),
                    margin=0.3,
                ),
            ),
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )
