from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

import uniserde


@uniserde.as_child
class OutgoingMessage(uniserde.Serde):
    """
    Base class for socket messages.
    """


@dataclass
class UpdateWidgetStates(OutgoingMessage):
    """
    Replace all widgets in the UI with the given one.
    """

    # Maps widget ids to serialized widgets. The widgets may be partial, i.e.
    # any property may be missing.
    delta_states: Dict[int, Any]

    # Tells the client to make the given widget the new root widget.
    root_widget_id: Optional[int]


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
class MouseMoveEvent(IncomingMessage):
    widget_id: int
    x: float
    y: float


@dataclass
class MouseEnterEvent(IncomingMessage):
    widget_id: int
    x: float
    y: float


@dataclass
class MouseLeaveEvent(IncomingMessage):
    widget_id: int
    x: float
    y: float


@dataclass
class TextInputBlurEvent(IncomingMessage):
    widget_id: int
    text: str


@dataclass
class DropdownChangeEvent(IncomingMessage):
    widget_id: int
    value: str


@dataclass
class SwitchChangeEvent(IncomingMessage):
    widget_id: int
    is_on: bool
