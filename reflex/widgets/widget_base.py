from __future__ import annotations

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
    ClassVar,
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

import introspection
from typing_extensions import Self, dataclass_transform

from .. import messages, session
from ..common import Jsonable
from ..styling import *
from . import event_classes

__all__ = [
    "Widget",
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
    assert widget._session_ is not None

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
    assert widget._session_ is not None, widget
    await widget._session_.refresh()


def is_widget_class(cls: Type[Any]) -> bool:
    return inspect.isclass(cls) and issubclass(cls, Widget)


@dataclass
class StateBinding:
    state_property: "StateProperty"
    widget: Optional["Widget"]


class StateProperty(Generic[T]):
    """
    StateProperties act like regular properties, with additional considerations:

    - When a state property is assigned to, the widget owning it is marked as
      dirty in the session

    - State properties have the ability to share their value with other state
      property instances. If state property `A` is assigned to state property
      `B`, then `B` creates a `StateBinding` and any future access to `B` will
      be routed to `A` instead:

    ```
    class Foo(Widget):
        foo_text = "Hello"

        def build(self) -> Widget:
            return Bar(bar_text=Foo.foo_text)  # Note `Foo` instead of `self`
    ```
    """

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
        # If accessed through the class, rather than instance, return the
        # StateProperty itself
        if instance is None:
            return self

        # Otherwise get the value assigned to the property in the widget
        # instance
        try:
            value = vars(instance)[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

        # If the value is a binding return the binding's value
        if type(value) is StateBinding:
            assert value.widget is not None
            return value.state_property.__get__(value.widget)  # type: ignore

        # Otherwise return the value
        return value

    def __set__(self, instance: Widget, value: T) -> None:
        # When assigning a StateProperty to another StateProperty, a
        # `StateBinding` is created. Otherwise just assign the value as-is.
        if type(value) is StateProperty:
            # The binding's widget isn't known yet, and is injected later by the
            # `Session`.
            new_value = StateBinding(value, None)
        else:
            new_value = value

        # If this property is part of a state binding update the parent's value
        instance_vars = vars(instance)
        local_value = instance_vars.get(self.name)

        if type(local_value) is StateBinding:
            if isinstance(new_value, StateBinding):
                # This should virtually never happen. So don't handle it, scream
                # and die
                raise RuntimeError(
                    "State bindings can only be created when the widget is constructed"
                )

            local_value.state_property.__set__(local_value.widget, new_value)  # type: ignore

        else:
            instance_vars[self.name] = new_value

        # If a session is known also notify the session that the widget is
        # dirty. If the session is not known yet, the widget will be processed
        # by the session anyway, as if dirty.
        if instance._session_ is not None:
            instance._session_.register_dirty_widget(instance)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


@dataclass_transform()
@dataclass(unsafe_hash=True)
class Widget(ABC):
    _: KW_ONLY
    key: Optional[str] = None

    # Injected by the session when the widget is refreshed
    _session_: Optional["session.Session"] = dataclasses.field(default=None, init=False)

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: Set[str] = dataclasses.field(
        default_factory=set, init=False
    )

    # Cache for the function's `__init__` parameters. This is used to determine
    # which parameters were explicitly set in the constructor.
    _init_signature_: ClassVar[introspection.Signature]

    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: ClassVar[Set["StateProperty"]]

    def __new__(cls, *args, **kwargs) -> Self:
        self = super().__new__(cls)

        # Keep track of which properties were explicitly set in the constructor.
        bound_args = cls._init_signature_.bind(None, *args, **kwargs)
        self._explicitly_set_properties_ = set(bound_args.arguments)

        return self

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # All widgets must be direct subclasses of Widget
        if cls.__base__ is not Widget and cls.__base__ is not FundamentalWidget:
            raise TypeError(
                f"Widget subclasses must be direct subclasses of Widget, not {cls.__base__!r}"
            )

        # Apply the dataclass transform
        dataclasses.dataclass(unsafe_hash=True)(cls)

        # Replace all properties with custom state properties
        cls._initialize_state_properties(Widget._state_properties_)

        # Widgets must be hashable, because sessions use weak dicts & sets to
        # keep track of them. However, unlike dataclasses, instances should only
        # be equal to themselves.
        #
        # -> Replace the dataclass implementations of `__eq__` and `__hash__`
        cls.__eq__ = lambda self, other: self._id == other._id  # type: ignore
        cls.__hash__ = lambda self: self._id  # type: ignore

        # Determine and cache the `__init__` signature
        cls._init_signature_ = introspection.Signature.for_method(cls, "__init__")

    @classmethod
    def _initialize_state_properties(
        cls, parent_state_properties: Set["StateProperty"]
    ) -> None:
        """
        Spawn `StateProperty` instances for all annotated properties in this
        class.
        """
        cls._state_properties_ = parent_state_properties.copy()

        # Placeholder function, until a better one is implemented in the
        # `introspection` package.
        def is_classvar(annotation: Any) -> bool:
            if isinstance(annotation, str):
                return annotation.startswith(("ClassVar", "typing.ClassVar"))

            return typing.get_origin(annotation) is ClassVar

        for attr_name, annotation in vars(cls).get("__annotations__", {}).items():
            # Skip `ClassVar` annotations
            if is_classvar(annotation):
                continue

            # Skip internal properties. These aren't supposed to be wrapped in
            # `StateProperty`
            if attr_name in (
                "_",
                "_session_",
                "_explicitly_set_properties_",
                "_init_signature_",
            ):
                continue

            # Create the `StateProperty`
            state_property = StateProperty(attr_name)
            setattr(cls, attr_name, state_property)

            # Add it to the set of all state properties for rapid lookup
            cls._state_properties_.add(state_property)

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


# Most classes have their state proprties initielized in
# `Widget.__init_subclass__`. However, since `Widget` isn't a subclass of
# itself this needs to be done manually.
Widget._initialize_state_properties(set())


class FundamentalWidget(Widget):
    def build(self) -> "Widget":
        raise RuntimeError(f"Attempted to call `build` on fundamental widget {self}")
