import dataclasses
import inspect
import typing
from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Self, dataclass_transform

from web_gui import messages
from web_gui.common import Jsonable
from web_gui.styling import Dict, Jsonable

from . import event_classes, messages
from .common import Jsonable
from .styling import *

T = TypeVar("T")
EventHandler = Optional[Callable[[T], Any | Awaitable[Any]]]


_unique_id_counter = -1


def _make_unique_id() -> int:
    global _unique_id_counter
    _unique_id_counter += 1
    return _unique_id_counter


async def call_event_handler(
    event_data: T,
    handler: EventHandler[T],
) -> None:
    """
    Call an event handler, if one is present. Await it if necessary
    """
    if handler is None:
        return

    result = handler(event_data)

    if inspect.isawaitable(result):
        await result


@dataclass_transform()
@dataclass(unsafe_hash=True)
class Widget(ABC):
    _: KW_ONLY
    width_override: Optional[float] = None
    height_override: Optional[float] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Apply the dataclass transform
        dataclasses.dataclass(unsafe_hash=True)(cls)

        # Replace all properties with custom state properties
        for attr in vars(cls).get("__annotations__", ()):
            setattr(cls, attr, StateProperty(attr))

        # Widgets must be hashable, because sessions use weak dicts & sets to
        # keep track of them. However, unlike dataclasses, instances should only
        # be equal to themselves.
        #
        # -> Replace the dataclass implementations of `__eq__` and `__hash__`
        cls.__eq__ = lambda self, other: self._id == other._id  # type: ignore
        cls.__hash__ = lambda self: self._id  # type: ignore

    @property
    def _id(self) -> int:
        """
        Return an unchanging, unique ID for this widget, so it can be identified
        over the API.
        """
        try:
            return vars(self)["_id"]
        except KeyError:
            _id = _make_unique_id()
            vars(self)["_id"] = _id
            return _id

    def _custom_serialize(self) -> Dict[str, Jsonable]:
        """
        Return any additional properties to be serialized, which cannot be
        deduced automatically from the type annotations.
        """
        return {}

    @abstractmethod
    def build(self) -> "Widget":
        raise NotImplementedError()

    def _map_direct_children(self, callback: Callable[["Widget"], "Widget"]):
        for name, typ in typing.get_type_hints(self.__class__).items():
            origin, args = typing.get_origin(typ), typing.get_args(typ)

            # Remap directly contained widgets
            if origin is Widget:
                child = getattr(self, name)
                setattr(self, name, callback(child))

            # Iterate over lists of widgets, remapping their values
            elif origin is list and args[0] is Widget:
                children = getattr(self, name)
                setattr(self, name, [callback(child) for child in children])

            # TODO: What about other containers

    def _iter_direct_children(self) -> Iterable["Widget"]:
        for name, typ in typing.get_type_hints(self.__class__).items():
            origin, args = typing.get_origin(typ), typing.get_args(typ)

            # Remap directly contained widgets
            if origin is Widget:
                child = getattr(self, name)
                yield child

            # Iterate over lists of widgets, remapping their values
            elif origin is list and args[0] is Widget:
                children = getattr(self, name)
                yield from children

            # TODO: What about other containers

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        raise RuntimeError(f"{type(self).__name__} received unexpected message `{msg}`")


class FundamentalWidget(Widget):
    def build(self) -> "Widget":
        raise RuntimeError(f"Attempted to call `build` on fundamental widget {self}")


class StateProperty(Generic[T]):
    def __init__(self, name: str):
        self.name = name

    @overload
    def __get__(self, instance: Widget, owner: Optional[type] = None) -> T:
        ...

    @overload
    def __get__(self, instance: None, owner: Optional[type] = None) -> Self:
        ...

    def __get__(
        self,
        instance: Optional[Widget],
        owner: Optional[type] = None,
    ) -> Union[T, Self]:
        if instance is None:
            return self

        return vars(instance)[self.name]

    def __set__(self, instance: Widget, value: T) -> None:
        vars(instance)[self.name] = value


class Text(FundamentalWidget):
    text: str
    _: KW_ONLY
    multiline: bool = False
    font: Optional[str] = None
    font_color: Color = Color.from_rgb(0, 0, 0)
    font_size: float = 1.0
    font_weight: Literal["normal", "bold"] = "normal"
    italic: bool = False
    underlined: bool = False


class Row(FundamentalWidget):
    children: List[Widget]


class Column(FundamentalWidget):
    children: List[Widget]


class Rectangle(FundamentalWidget):
    fill: FillLike
    _: KW_ONLY
    corner_radius: Tuple[float, float, float, float] = (0, 0, 0, 0)


class Stack(FundamentalWidget):
    children: List[Widget]


class Margin(FundamentalWidget):
    child: Widget
    margin_left: float
    margin_top: float
    margin_right: float
    margin_bottom: float

    def __init__(
        self,
        child: Widget,
        *,
        margin: float = 0,
        margin_horizontal: float = 0,
        margin_vertical: float = 0,
        margin_left: float = 0,
        margin_top: float = 0,
        margin_right: float = 0,
        margin_bottom: float = 0,
    ):
        super().__init__()

        self.child = child

        if margin != 0:
            self.margin_left = margin
            self.margin_top = margin
            self.margin_right = margin
            self.margin_bottom = margin

        elif margin_horizontal != 0:
            self.margin_left = margin_horizontal
            self.margin_top = 0
            self.margin_right = margin_horizontal
            self.margin_bottom = 0

        elif margin_vertical != 0:
            self.margin_left = 0
            self.margin_top = margin_vertical
            self.margin_right = 0
            self.margin_bottom = margin_vertical

        else:
            self.margin_left = margin_left
            self.margin_top = margin_top
            self.margin_right = margin_right
            self.margin_bottom = margin_bottom


class Align(FundamentalWidget):
    child: Widget
    align_x: Optional[float]
    align_y: Optional[float]

    def __init__(
        self,
        child: Widget,
        *,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__()
        self.child = child
        self.align_x = align_x
        self.align_y = align_y

    @classmethod
    def top(cls, child: Widget):
        return cls(child, align_y=0)

    @classmethod
    def bottom(cls, child: Widget):
        return cls(child, align_y=1)

    @classmethod
    def left(cls, child: Widget):
        return cls(child, align_x=0)

    @classmethod
    def right(cls, child: Widget):
        return cls(child, align_x=1)

    @classmethod
    def top_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0)

    @classmethod
    def top_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0)

    @classmethod
    def top_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0)

    @classmethod
    def center_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=0.5)

    @classmethod
    def center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=0.5)

    @classmethod
    def center_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=0.5)

    @classmethod
    def bottom_left(cls, child: Widget):
        return cls(child, align_x=0, align_y=1)

    @classmethod
    def bottom_center(cls, child: Widget):
        return cls(child, align_x=0.5, align_y=1)

    @classmethod
    def bottom_right(cls, child: Widget):
        return cls(child, align_x=1, align_y=1)


class Button(FundamentalWidget):
    text: str
    on_click: Optional[Callable[[], Any]]

    def __init__(self, text: str, *, on_click: Optional[Callable[[], Any]] = None):
        super().__init__()
        self.text = text
        self.on_click = on_click


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
            await call_event_handler(
                event_classes.MouseDownEvent(
                    x=msg.x,
                    y=msg.y,
                    button=event_classes.MouseButton(msg.button),
                ),
                self.on_mouse_down,
            )

        elif isinstance(msg, messages.MouseUpEvent):
            await call_event_handler(
                event_classes.MouseUpEvent(
                    x=msg.x,
                    y=msg.y,
                    button=event_classes.MouseButton(msg.button),
                ),
                self.on_mouse_up,
            )

        else:
            raise RuntimeError(
                f"MouseEventListener received unexpected message `{msg}`"
            )
