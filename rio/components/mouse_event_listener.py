from __future__ import annotations

import enum
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

from uniserde import JsonDoc

import rio

from . import component_base

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


class MouseEventListener(component_base.FundamentalComponent):
    """
    Allows you to listen for mouse events on a component.

    `MouseEventListeners` take a single child component and display it. They
    then listen for any mouse activity on the child component and report it
    through their event handlers.

    Attributes:
        child: The child component to display.

        on_mouse_down: Triggered when a mouse button is pressed down while
            the mouse is placed over the child component.

        on_mouse_up: Triggered when a mouse button is released while the
            mouse is placed over the child component.

        on_mouse_move: Triggered when the mouse is moved while located over
            the child component.

        on_mouse_enter: Triggered when the mouse previously was not located
            over the child component, but now is.

        on_mouse_leave: Triggered when the mouse previously was located over
            the child component, but now is not.
    """

    child: component_base.Component
    _: KW_ONLY
    on_mouse_down: rio.EventHandler[MouseDownEvent] = None
    on_mouse_up: rio.EventHandler[MouseUpEvent] = None
    on_mouse_move: rio.EventHandler[MouseMoveEvent] = None
    on_mouse_enter: rio.EventHandler[MouseEnterEvent] = None
    on_mouse_leave: rio.EventHandler[MouseLeaveEvent] = None

    def _custom_serialize(self) -> JsonDoc:
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
            await self.call_event_handler(
                self.on_mouse_down,
                MouseDownEvent(
                    x=msg["x"],
                    y=msg["y"],
                    button=MouseButton(msg["button"]),
                ),
            )

        elif msg_type == "mouseUp":
            await self.call_event_handler(
                self.on_mouse_up,
                MouseUpEvent(
                    x=msg["x"],
                    y=msg["y"],
                    button=MouseButton(msg["button"]),
                ),
            )

        elif msg_type == "mouseMove":
            await self.call_event_handler(
                self.on_mouse_move,
                MouseMoveEvent(
                    x=msg["x"],
                    y=msg["y"],
                ),
            )

        elif msg_type == "mouseEnter":
            await self.call_event_handler(
                self.on_mouse_enter,
                MouseEnterEvent(
                    x=msg["x"],
                    y=msg["y"],
                ),
            )

        elif msg_type == "mouseLeave":
            await self.call_event_handler(
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
