from __future__ import annotations

import web_gui as wg

from . import fundamentals

__all__ = ["Button"]


class Button(fundamentals.Widget):
    text: str
    on_press: wg.EventHandler[[]] = None
    _is_pressed: bool = False

    def _on_mouse_down(self, event: wg.MouseDownEvent) -> None:
        self._is_pressed = True

    async def _on_mouse_up(self, event: wg.MouseUpEvent) -> None:
        await wg.call_event_handler(self.on_press)
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
