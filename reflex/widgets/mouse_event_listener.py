from __future__ import annotations

from dataclasses import KW_ONLY
from typing import Dict, List, Literal, Optional, Tuple

from .. import messages
from ..common import Jsonable
from ..styling import *
from . import event_classes
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    Widget,
    call_event_handler_and_refresh,
)

__all__ = [
    "MouseEventListener",
]


class MouseEventListener(FundamentalWidget):
    child: Widget
    _: KW_ONLY
    on_mouse_down: EventHandler[event_classes.MouseDownEvent] = None
    on_mouse_up: EventHandler[event_classes.MouseUpEvent] = None
    on_mouse_move: EventHandler[event_classes.MouseMoveEvent] = None
    on_mouse_enter: EventHandler[event_classes.MouseEnterEvent] = None
    on_mouse_leave: EventHandler[event_classes.MouseLeaveEvent] = None

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
                event_classes.MouseDownEvent(
                    x=msg.x,
                    y=msg.y,
                    button=event_classes.MouseButton(msg.button),
                ),
                self.on_mouse_down,
            )

        elif isinstance(msg, messages.MouseUpEvent):
            await call_event_handler_and_refresh(
                self,
                event_classes.MouseUpEvent(
                    x=msg.x,
                    y=msg.y,
                    button=event_classes.MouseButton(msg.button),
                ),
                self.on_mouse_up,
            )

        elif isinstance(msg, messages.MouseMoveEvent):
            await call_event_handler_and_refresh(
                self,
                event_classes.MouseMoveEvent(
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_move,
            )

        elif isinstance(msg, messages.MouseEnterEvent):
            await call_event_handler_and_refresh(
                self,
                event_classes.MouseEnterEvent(
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_enter,
            )

        elif isinstance(msg, messages.MouseLeaveEvent):
            await call_event_handler_and_refresh(
                self,
                event_classes.MouseLeaveEvent(
                    x=msg.x,
                    y=msg.y,
                ),
                self.on_mouse_leave,
            )

        else:
            raise RuntimeError(
                f"MouseEventListener received unexpected message `{msg}`"
            )
