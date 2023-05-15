from __future__ import annotations

import inspect
import traceback
import typing
from typing import Any, Awaitable, Callable, Optional, TypeVar

from typing_extensions import ParamSpec

import web_gui as wg

from . import fundamentals

__all__ = ["Button"]


T = TypeVar("T")
P = ParamSpec("P")


EventHandler = Optional[Callable[P, Any | Awaitable[Any]]]


@typing.overload
async def call_event_handler(
    handler: EventHandler[[]],
) -> None:
    ...


@typing.overload
async def call_event_handler(
    handler: EventHandler[T],
    event_data: T,
) -> None:
    ...


async def call_event_handler(  # type: ignore
    handler: EventHandler[P],
    *event_data: T,  # type: ignore
) -> None:
    """
    Call an event handler, if one is present. Await it if necessary.
    """

    # Event handlers are optional
    if handler is None:
        return

    # If the handler is available, call it and await it if necessary
    try:
        result = handler(*event_data)  # type: ignore

        if inspect.isawaitable(result):
            await result

    # Display and discard exceptions
    except Exception:
        print("Exception in event handler:")
        traceback.print_exc()


class Button(fundamentals.Widget):
    text: str
    on_press: Optional[Callable[[], Any]] = None
    _is_pressed: bool = False

    def _on_mouse_down(self, event: wg.MouseDownEvent) -> None:
        self._is_pressed = True

    async def _on_mouse_up(self, event: wg.MouseUpEvent) -> None:
        await call_event_handler(self.on_press)
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
