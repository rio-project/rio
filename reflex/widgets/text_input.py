from __future__ import annotations

from dataclasses import KW_ONLY, dataclass

from .. import messages
from .widget_base import (
    EventHandler,
    FundamentalWidget,
    WidgetEvent,
    call_event_handler_and_refresh,
)

__all__ = ["TextInput", "TextInputChangeEvent"]


@dataclass
class TextInputChangeEvent(WidgetEvent):
    text: str


class TextInput(FundamentalWidget):
    text: str = ""
    placeholder: str = ""
    _: KW_ONLY
    secret: bool = False
    on_change: EventHandler[TextInputChangeEvent] = None

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        assert self._session_ is not None

        if isinstance(msg, messages.TextInputBlurEvent):
            self.text = msg.text

            await call_event_handler_and_refresh(
                self,
                TextInputChangeEvent(self, msg.text),
                self.on_change,
            )
        else:
            raise RuntimeError(f"TextInput received unexpected message `{msg}`")
