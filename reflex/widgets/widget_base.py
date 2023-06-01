from __future__ import annotations

import dataclasses
import functools
import inspect
import json
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
    Optional,
    ParamSpec,
    Set,
    Type,
    TypeVar,
    Union,
    dataclass_transform,
    overload,
)

import introspection
from typing_extensions import Self

from .. import common, messages, session
from ..common import Jsonable

__all__ = [
    "EventHandler",
    "Widget",
    "HtmlWidget",
]


JAVASCRIPT_SOURCE_TEMPLATE = """
%(js_source)s

if (%(js_class_name)s !== undefined) {
    window.widgetClasses['%(cls_unique_id)s'] = %(js_class_name)s;
}
"""


CSS_SOURCE_TEMPLATE = """
const style = document.createElement('style');
style.innerHTML = %(escaped_css_source)s;
document.head.appendChild(style);
"""


T = TypeVar("T")
P = ParamSpec("P")


EventHandler = Optional[Callable[P, Any | Awaitable[Any]]]


_unique_id_counter = -1


def _make_unique_id() -> int:
    global _unique_id_counter
    _unique_id_counter += 1
    return _unique_id_counter


def is_widget_class(cls: Type[Any]) -> bool:
    return inspect.isclass(cls) and issubclass(cls, Widget)


@dataclass
class StateBinding:
    state_property: StateProperty
    widget: Optional[Widget]


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

    def __init__(self, name: str, readonly: bool):
        self.name = name
        self.readonly = readonly

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

    def set_value(self, instance: Widget, value: T, mark_dirty: bool) -> None:
        if self.readonly:
            cls_name = type(instance).__name__
            raise AttributeError(
                f"Cannot assign to readonly property {cls_name}.{self.name}"
            )

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

        if isinstance(local_value, StateBinding):
            if isinstance(new_value, StateBinding):
                # This should virtually never happen. So don't handle it, scream
                # and die
                raise RuntimeError(
                    "State bindings can only be created when the widget is constructed"
                )

            local_value.state_property.set_value(local_value.widget, new_value, mark_dirty)  # type: ignore

        else:
            instance_vars[self.name] = new_value

        # If a session is known also notify the session that the widget is
        # dirty. If the session is not known yet, the widget will be processed
        # by the session anyway, as if dirty.
        if instance._session_ is not None and mark_dirty:
            instance._session_.register_dirty_widget(
                instance,
                include_fundamental_children_recursively=False,
            )

    def __set__(self, instance: Widget, value: T) -> None:
        self.set_value(instance, value, mark_dirty=True)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


@dataclass_transform()
@dataclass(unsafe_hash=True)
class Widget(ABC):
    _: KW_ONLY
    key: Optional[str] = None

    margin: Optional[float] = None
    margin_x: Optional[float] = None
    margin_y: Optional[float] = None

    margin_left: Optional[float] = None
    margin_top: Optional[float] = None
    margin_right: Optional[float] = None
    margin_bottom: Optional[float] = None

    width: Optional[float] = None
    height: Optional[float] = None

    align_x: Optional[float] = None
    align_y: Optional[float] = None

    # Injected by the session when the widget is refreshed
    _session_: Optional["session.Session"] = dataclasses.field(default=None, init=False)

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: Set[str] = dataclasses.field(init=False)

    # Cache for the function's `__init__` parameters. This is used to determine
    # which parameters were explicitly set in the constructor.
    _init_signature_: ClassVar[introspection.Signature]

    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: ClassVar[Set["StateProperty"]]

    def __new__(cls, *args, **kwargs) -> Self:
        self = super().__new__(cls)

        # Keep track of which properties were explicitly set in the constructor.
        bound_args = cls._init_signature_.bind(*args, **kwargs)
        self._explicitly_set_properties_ = set(bound_args.arguments)

        return self

    def _custom_init(self):
        def elvis(*args):
            for arg in args:
                if arg is not None:
                    return arg

            assert False

        self.margin_left = elvis(self.margin_left, self.margin_x, self.margin, 0)
        self.margin_top = elvis(self.margin_top, self.margin_y, self.margin, 0)
        self.margin_right = elvis(self.margin_right, self.margin_x, self.margin, 0)
        self.margin_bottom = elvis(self.margin_bottom, self.margin_y, self.margin, 0)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # All widgets must be direct subclasses of Widget
        if cls.__base__ is not Widget and cls.__base__ is not HtmlWidget:
            raise TypeError(
                f"Widget subclasses must be direct subclasses of Widget, not {cls.__base__!r}"
            )

        # Apply the dataclass transform
        dataclasses.dataclass(unsafe_hash=True, repr=False)(cls)

        # Widgets need to run custom code in in `__init__`, but dataclasses
        # don't chain up. `__init__` is replaced with a custom function, which
        # first calls the original one, then runs the custom code.
        #
        # Take care to only do this for the leaf class, so that the custom code
        # isn't run multiple times.
        if cls.__module__ != __name__ or cls.__name__ != "HtmlWidget":
            original_init = cls.__init__

            @functools.wraps(original_init)
            def replacement_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                self._custom_init()

            cls.__init__ = replacement_init

        # Replace all properties with custom state properties
        cls._initialize_state_properties(Widget._state_properties_)

        # Widgets must be hashable, because sessions use weak dicts & sets to
        # keep track of them. However, unlike dataclasses, instances should only
        # be equal to themselves.
        #
        # -> Replace the dataclass implementations of `__eq__` and `__hash__`
        cls.__eq__ = lambda self, other: self is other  # type: ignore
        cls.__hash__ = lambda self: id(self)  # type: ignore

        # Determine and cache the `__init__` signature
        #
        # Make sure to strip `self`
        cls._init_signature_ = introspection.Signature.for_method(
            cls, "__init__"
        ).without_parameters(0)

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
                "margin",
                "margin_x",
                "margin_y",
            ):
                continue

            # Create the `StateProperty`
            # readonly = introspection.typing.has_annotation(annotation, Readonly
            readonly = False  # FIXME
            state_property = StateProperty(attr_name, readonly)
            setattr(cls, attr_name, state_property)

            # Add it to the set of all state properties for rapid lookup
            cls._state_properties_.add(state_property)

    @property
    def session(self) -> "session.Session":
        """
        Return the session this widget is part of.

        The session is accessible after the build method which constructed this
        widget has returned.
        """
        if self._session_ is None:
            raise RuntimeError(
                "The session is only accessible once the build method which constructed this widget has returned."
            )

        return self._session_

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

    @typing.overload
    async def _call_event_handler(
        self,
        handler: EventHandler[[]],
    ) -> None:
        ...

    @typing.overload
    async def _call_event_handler(
        self,
        handler: EventHandler[[T]],
        event_data: T,
    ) -> None:
        ...

    async def _call_event_handler(  # type: ignore
        self,
        handler: EventHandler[P],
        *event_data: T,  # type: ignore
    ) -> None:
        """
        Call an event handler, if one is present. Await it if necessary. Log and
        discard any exceptions.
        """

        # Event handlers are optional
        if handler is None:
            return

        # If the handler is available, call it and await it if necessary
        try:
            result = handler(*event_data)  # type: ignore

            if inspect.isawaitable(result):
                await result

        # Display and discard exceptions
        except Exception:
            print("Exception in event handler:")
            traceback.print_exc()

    def __repr__(self) -> str:
        result = f"<{type(self).__name__} id:{self._id} -"

        for child in self._iter_direct_children():
            result += f" {type(child).__name__}:{child._id}"

        return result + ">"


# Most classes have their state properties initialized in
# `Widget.__init_subclass__`. However, since `Widget` isn't a subclass of
# itself this needs to be done manually.
Widget._initialize_state_properties(set())


class HtmlWidget(Widget):
    # Unique id for identifying this class in the frontend. This is initialized
    # in `Widget.__init_subclass__`.
    _unique_id: ClassVar[str]

    def build(self) -> "Widget":
        raise RuntimeError(f"Attempted to call `build` on `HtmlWidget` {self}")

    @classmethod
    def build_javascript_source(cls, sess: session.Session) -> str:
        return ""

    @classmethod
    def build_css_source(cls, sess: session.Session) -> str:
        return ""

    def __init_subclass__(cls):
        hash_ = common.secure_string_hash(
            cls.__module__,
            cls.__qualname__,
            hash_length=12,
        )

        cls._unique_id = f"{cls.__name__}-{hash_}"

        super().__init_subclass__()

    @classmethod
    def _build_initialization_messages(
        cls, sess: session.Session
    ) -> Iterable[messages.OutgoingMessage]:
        message_source = ""

        javascript_source = cls.build_javascript_source(sess)
        if javascript_source:
            message_source += JAVASCRIPT_SOURCE_TEMPLATE % {
                "js_source": javascript_source,
                "js_class_name": cls.__name__,
                "cls_unique_id": cls._unique_id,
            }

        css_source = cls.build_css_source(sess)
        if css_source:
            escaped_css_source = json.dumps(css_source)
            message_source += CSS_SOURCE_TEMPLATE % {
                "escaped_css_source": escaped_css_source,
            }

        if message_source:
            yield messages.EvaluateJavascript(javascript_source=message_source)

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
        # The frontend has requested the widget's staet to be changed
        if isinstance(msg, messages.WidgetStateUpdate):
            await self._on_state_update(msg.delta_state)

        # A custom message was sent by the frontend
        elif isinstance(msg, messages.WidgetMessage):
            await self._on_message(msg.payload)

        # Unknown, chain up
        else:
            await super()._handle_message(msg)

    async def _on_state_update(self, delta_state: Dict[str, Jsonable]) -> None:
        """
        This function is called when the frontend sends a state update to this
        widget.
        """
        # Update all state properties to reflect the new state
        for attr_name, attr_value in delta_state.items():
            assert isinstance(attr_value, (bool, int, float, str)), attr_value
            assert hasattr(type(self), attr_name), attr_name
            assert isinstance(getattr(type(self), attr_name), StateProperty), attr_name

            setattr(self, attr_name, attr_value)

        # Trigger a refresh
        assert self._session_ is not None
        await self._session_.refresh()

    async def _on_message(self, message: Jsonable) -> None:
        """
        This function is called when the frontend sends a message to this widget
        via `sendMessage`.
        """
        pass
