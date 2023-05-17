from dataclasses import dataclass
from typing import Any, Literal

import uniserde

from .common import Jsonable


@uniserde.as_child
class OutgoingMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class ReplaceWidgets(OutgoingMessage):
    """
    Replace all widgets in the UI with the given one.
    """

    widget: Any  # The already serialized widget


@uniserde.as_child
class IncomingMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class ButtonPressedEvent(IncomingMessage):
    widget_id: int


@dataclass
class MouseDownEvent(IncomingMessage):
    widget_id: int
    button: Literal["left", "middle", "right"]
    x: float
    y: float


@dataclass
class MouseUpEvent(IncomingMessage):
    widget_id: int
    button: Literal["left", "middle", "right"]
    x: float
    y: float


@dataclass
class TextInputBlurEvent(IncomingMessage):
    widget_id: int
    text: str
