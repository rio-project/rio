import dataclasses
import inspect
import traceback
import typing
from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Self, dataclass_transform

from web_gui import messages
from web_gui.common import Jsonable
from web_gui.styling import Dict, Jsonable

from .. import event_classes, messages, session
from ..common import Jsonable
from ..styling import *

__all__ = [
    "Widget",
    "Text",
    "Row",
    "Column",
    "Rectangle",
    "Stack",
    "Margin",
    "Align",
    "MouseEventListener",
    "TextInput",
    "Override",
]


T = TypeVar("T")
EventHandler = Optional[Callable[[T], Any | Awaitable[Any]]]


_unique_id_counter = -1


def _make_unique_id() -> int:
    global _unique_id_counter
    _unique_id_counter += 1
    return _unique_id_counter


async def call_event_handler_and_refresh(
    widget: "Widget",
    event_data: T,
    handler: EventHandler[T],
) -> None:
    """
    Call an event handler, if one is present. Await it if necessary
    """
    assert widget._session is not None

    # Event handlers are optional
    if handler is None:
        return

    # If the handler is available, call it and await it if necessary
    try:
        result = handler(event_data)

        if inspect.isawaitable(result):
            await result

    # Display and discard exceptions
    except Exception:
        print("Exception in event handler:")
        traceback.print_exc()

    # Refresh the session if necessary. A rebuild might be in order
    assert widget._session is not None, widget
    await widget._session.refresh()


def is_widget_class(cls: Type[Any]) -> bool:
    return inspect.isclass(cls) and issubclass(cls, Widget)


@dataclass_transform()
@dataclass(unsafe_hash=True)
class Widget(ABC):
    _: KW_ONLY
    key: Optional[str] = None

    # Injected by the session when the widget is refreshed
    _session: Optional["session.Session"] = None

    # Keep track of all changed properties
    _dirty_properties: Set["StateProperty"] = dataclasses.field(
        default_factory=set, init=False
    )

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Apply the dataclass transform
        dataclasses.dataclass(unsafe_hash=True)(cls)

        # Replace all properties with custom state properties
        for attr in vars(cls).get("__annotations__", ()):
            if attr in (
                "_",
                "_session",
                "_dirty_properties",
            ):
                continue

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

    def _iter_direct_children(self) -> Iterable["Widget"]:
        for name in typing.get_type_hints(self.__class__):
            try:
                value = getattr(self, name)
            except AttributeError:
                continue

            if isinstance(value, Widget):
                yield value

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Widget):
                        yield item

            # TODO: What about other containers

    def _iter_direct_and_indirect_children(
        self,
        include_self: bool,
    ) -> Iterable["Widget"]:
        if include_self:
            yield self

        for child in self._iter_direct_children():
            yield from child._iter_direct_and_indirect_children(True)

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        raise RuntimeError(f"{type(self).__name__} received unexpected message `{msg}`")


class FundamentalWidget(Widget):
    def build(self) -> "Widget":
        raise RuntimeError(f"Attempted to call `build` on fundamental widget {self}")


@dataclass
class StateBinding:
    state_property: "StateProperty"
    widget: Optional["Widget"]


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

        # Get the value assigned to the property in the widget instance
        value = vars(instance)[self.name]

        # If the value is a binding return the binding's value
        if type(value) is StateBinding:
            assert value.widget is not None
            return value.state_property.__get__(value.widget)  # type: ignore

        # Otherwise return the value
        return value

    def __set__(self, instance: Widget, value: T) -> None:
        # If the value is a state property, wrap it in a binding
        if type(value) is StateProperty:
            new_value = StateBinding(value, None)
        else:
            new_value = value

        # If this property is part of a state binding update the parent's value
        instance_vars = vars(instance)
        old_value = instance_vars.get(self.name)

        if type(old_value) is StateBinding:
            if isinstance(new_value, StateBinding):
                # This should virtually never happen. So don't handle it,
                # scream and die
                raise RuntimeError(
                    "State bindings can only be created when the widget is constructed"
                )

            old_value.state_property.__set__(old_value.widget, new_value)  # type: ignore

        else:
            instance_vars[self.name] = new_value

        # Mark the widget as dirty
        instance._dirty_properties.add(self)

        # If a session is known notify the session that the widget is dirty. If
        # the session is not known yet, the widget will be processed by the
        # session anyway, as if dirty.
        if instance._session is not None:
            instance._session.register_dirty_widget(instance)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


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
    child: Optional[Widget] = None
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
        key: Optional[str] = None,
        margin: float = 0,
        margin_horizontal: float = 0,
        margin_vertical: float = 0,
        margin_left: float = 0,
        margin_top: float = 0,
        margin_right: float = 0,
        margin_bottom: float = 0,
    ):
        super().__init__(key=key)

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
        key: Optional[str] = None,
        align_x: Optional[float] = None,
        align_y: Optional[float] = None,
    ):
        super().__init__(key=key)
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

        else:
            raise RuntimeError(
                f"MouseEventListener received unexpected message `{msg}`"
            )


class TextInput(FundamentalWidget):
    text: str = ""
    placeholder: str = ""

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        assert self._session is not None

        if isinstance(msg, messages.TextInputBlurEvent):
            self.text = msg.text
            await self._session.refresh()

        else:
            raise RuntimeError(f"TextInput received unexpected message `{msg}`")


class Override(FundamentalWidget):
    child: Widget
    width: Optional[float] = None
    height: Optional[float] = None
