from __future__ import annotations

from typing import Any, Callable, Optional

import web_gui as wg

from . import fundamentals

__all__ = ["Button"]


class Button(fundamentals.Widget):
    text: str
    on_press: Optional[Callable[[], Any]] = None
    _is_pressed: bool = False

    def _on_mouse_down(self, event: wg.MouseDownEvent) -> None:
        self._is_pressed = True

    def _on_mouse_up(self, event: wg.MouseUpEvent) -> None:
        if self.on_press is None:
            return

        self.on_press()
        self._is_pressed = False

    def build(self) -> wg.Widget:
        return wg.MouseEventListener(
            wg.Stack(
                [
                    wg.Rectangle(
                        wg.Color.from_rgb(1, 0, 0.5)
                        if self._is_pressed
                        else wg.Color.RED
                    ),
                    wg.Margin(
                        wg.Text(self.text),
                        margin=0.3,
                    ),
                ]
            ),
            on_mouse_down=self._on_mouse_down,
            on_mouse_up=self._on_mouse_up,
        )
