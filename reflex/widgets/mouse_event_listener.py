from __future__ import annotations

import enum
from dataclasses import KW_ONLY, dataclass
from typing import Dict, List, Literal, Optional, Tuple

from .. import messages
from ..common import Jsonable
from ..styling import *
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    Widget,
    WidgetEvent,
    call_event_handler_and_refresh,
)

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
class _MouseUpDownEvent(WidgetEvent):
    button: MouseButton
    x: float
    y: float


class MouseDownEvent(_MouseUpDownEvent):
    pass


class MouseUpEvent(_MouseUpDownEvent):
    pass


@dataclass
class _MousePositionedEvent(WidgetEvent):
    x: float
    y: float


class MouseMoveEvent(_MousePositionedEvent):
    pass


class MouseEnterEvent(_MousePositionedEvent):
    pass


class MouseLeaveEvent(_MousePositionedEvent):
    pass


class MouseEventListener(FundamentalWidget):
    child: Widget
    _: KW_ONLY
    on_mouse_down: EventHandler[MouseDownEvent] = None
    on_mouse_up: EventHandler[MouseUpEvent] = None
    on_mouse_move: EventHandler[MouseMoveEvent] = None
    on_mouse_enter: EventHandler[MouseEnterEvent] = None
    on_mouse_leave: EventHandler[MouseLeaveEvent] = None

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        return {
            "reportMouseDown": self.on_mouse_down is not None,
            "reportMouseUp": self.on_mouse_up is not None,
            "reportMouseMove": self.on_mouse_move is not None,
            "reportMouseEnter": self.on_mouse_enter is not None,
            "reportMouseLeave": self.on_mouse_leave is not None,
        }

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        if isinstance(msg, messages.MouseDownEvent):
            await call_event_handler_and_refresh(
                self,
                MouseDownEvent(
                    self,
                    x=msg.x,
                    y=msg.y,
                    button=MouseButton(msg.button),
                ),
                self.on_mouse_down,
            )

        elif isinstance(msg, messages.MouseUpEvent):
            await call_event_handler_and_refresh(
                self,
                MouseUpEvent(
                    self,
                    x=msg.x,
                    y=msg.y,
                    button=MouseButton(msg.button),
                ),
                self.on_mouse_up,
            )

        elif isinstance(msg, messages.MouseMoveEvent):
            await call_event_handler_and_refresh(
                self,
                MouseMoveEvent(
                    self,
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_move,
            )

        elif isinstance(msg, messages.MouseEnterEvent):
            await call_event_handler_and_refresh(
                self,
                MouseEnterEvent(
                    self,
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_enter,
            )

        elif isinstance(msg, messages.MouseLeaveEvent):
            await call_event_handler_and_refresh(
                self,
                MouseLeaveEvent(
                    self,
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_leave,
            )

        else:
            raise RuntimeError(
                f"MouseEventListener received unexpected message `{msg}`"
            )
