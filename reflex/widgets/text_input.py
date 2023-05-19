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
    "TextInput",
]


class TextInput(FundamentalWidget):
    text: str = ""
    placeholder: str = ""
    _: KW_ONLY
    secret: bool = False

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        assert self._session_ is not None

        if isinstance(msg, messages.TextInputBlurEvent):
            self.text = msg.text
            await self._session_.refresh()

        else:
            raise RuntimeError(f"TextInput received unexpected message `{msg}`")
