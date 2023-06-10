from __future__ import annotations

import enum
from dataclasses import KW_ONLY, dataclass
from typing import Any, Dict

import reflex as rx

from ..common import Jsonable
from ..styling import *
from . import widget_base

__all__ = [
    "MouseEventListener",
    "MouseButton",
    "MouseDownEvent",
    "MouseUpEvent",
    "MouseMoveEvent",
    "MouseEnterEvent",
    "MouseLeaveEvent",
]


class MouseButton(enum.Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


@dataclass
class _MouseUpDownEvent:
    button: MouseButton
    x: float
    y: float


class MouseDownEvent(_MouseUpDownEvent):
    pass


class MouseUpEvent(_MouseUpDownEvent):
    pass


@dataclass
class _MousePositionedEvent:
    x: float
    y: float


class MouseMoveEvent(_MousePositionedEvent):
    pass


class MouseEnterEvent(_MousePositionedEvent):
    pass


class MouseLeaveEvent(_MousePositionedEvent):
    pass


class MouseEventListener(widget_base.HtmlWidget):
    child: widget_base.Widget
    _: KW_ONLY
    on_mouse_down: rx.EventHandler[MouseDownEvent] = None
    on_mouse_up: rx.EventHandler[MouseUpEvent] = None
    on_mouse_move: rx.EventHandler[MouseMoveEvent] = None
    on_mouse_enter: rx.EventHandler[MouseEnterEvent] = None
    on_mouse_leave: rx.EventHandler[MouseLeaveEvent] = None

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {
            "reportMouseDown": self.on_mouse_down is not None,
            "reportMouseUp": self.on_mouse_up is not None,
            "reportMouseMove": self.on_mouse_move is not None,
            "reportMouseEnter": self.on_mouse_enter is not None,
            "reportMouseLeave": self.on_mouse_leave is not None,
        }

    async def _on_message(self, msg: Any) -> None:
        # Parse the message
        assert isinstance(msg, dict), msg

        msg_type = msg["type"]
        assert isinstance(msg_type, str), msg_type

        # Dispatch the correct event
        if msg_type == "mouseDown":
            await self._call_event_handler(
                self.on_mouse_down,
                MouseDownEvent(
                    x=msg["x"],
                    y=msg["y"],
                    button=MouseButton(msg["button"]),
                ),
            )

        elif msg_type == "mouseUp":
            await self._call_event_handler(
                self.on_mouse_up,
                MouseUpEvent(
                    x=msg["x"],
                    y=msg["y"],
                    button=MouseButton(msg["button"]),
                ),
            )

        elif msg_type == "mouseMove":
            await self._call_event_handler(
                self.on_mouse_move,
                MouseMoveEvent(
                    x=msg["x"],
                    y=msg["y"],
                ),
            )

        elif msg_type == "mouseEnter":
            await self._call_event_handler(
                self.on_mouse_enter,
                MouseEnterEvent(
                    x=msg["x"],
                    y=msg["y"],
                ),
            )

        elif msg_type == "mouseLeave":
            await self._call_event_handler(
                self.on_mouse_leave,
                MouseLeaveEvent(
                    x=msg["x"],
                    y=msg["y"],
                ),
            )

        else:
            raise ValueError(f"{__class__.__name__} encountered unknown message: {msg}")

        # Refresh the session
        await self.session._refresh()


MouseEventListener._unique_id = "MouseEventListener-builtin"
