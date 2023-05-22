from __future__ import annotations

from dataclasses import KW_ONLY, dataclass

from .. import messages
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    WidgetEvent,
    call_event_handler_and_refresh,
)

__all__ = ["Switch", "SwitchChangeEvent"]


@dataclass
class SwitchChangeEvent(WidgetEvent):
    is_on: bool


class Switch(FundamentalWidget):
    is_on: bool = False
    _: KW_ONLY
    on_change: EventHandler[SwitchChangeEvent] = None

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        if isinstance(msg, messages.SwitchChangeEvent):
            self.is_on = msg.is_on
            await call_event_handler_and_refresh(
                self,
                SwitchChangeEvent(self, msg.is_on),
                self.on_change,
            )
