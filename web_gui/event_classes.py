import enum
from dataclasses import dataclass


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
class MouseMoveEvent:
    x: float
    y: float


@dataclass
class _MouseEnterLeaveEvent:
    pass


class MouseEnterEvent(_MouseEnterLeaveEvent):
    pass


class MouseLeaveEvent(_MouseEnterLeaveEvent):
    pass
