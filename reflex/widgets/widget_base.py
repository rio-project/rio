from __future__ import annotations

import dataclasses
import inspect
import json
import traceback
import typing
import weakref
from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import introspection
from typing_extensions import dataclass_transform

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


def _get_annotated_instance_attributes(cls):
    attrs = set()

    for cls in cls.__mro__:
        annotations = vars(cls).get("__annotations__", {})
        attrs.update(annotations.keys())

    return attrs


def is_widget_class(cls: Type[Any]) -> bool:
    return inspect.isclass(cls) and issubclass(cls, Widget)


def make_default_factory_for_value(value: T) -> Callable[[], T]:
    def default_factory() -> T:
        return value

    default_factory.__name__ = default_factory.__qualname__ = f"return_{value!r}"

    return default_factory


@dataclass(eq=False)
class StateBinding:
    # Weak reference to the widget containing this binding
    owning_widget_weak: Callable[[], Optional[Widget]]

    # The state property whose value this binding is
    owning_property: StateProperty

    # Each binding is either the root-most binding, or a child of another
    # binding. This value is True if this binding is the root.
    is_root: bool

    parent: Optional[StateBinding]
    value: Optional[object]

    children: weakref.WeakSet[StateBinding] = dataclasses.field(
        default_factory=weakref.WeakSet
    )

    def get_value(self) -> object:
        if self.is_root:
            return self.value

        assert self.parent is not None
        return self.parent.get_value()

    def set_value(self, value: object) -> None:
        # Delegate to the parent, if any
        if self.parent is not None:
            self.parent.set_value(value)
            return

        # Otherwise this is the root-most binding. Set the value
        self.value = value

        # Then recursively mark all children as dirty
        self.recursively_mark_children_as_dirty()

    def recursively_mark_children_as_dirty(self) -> None:
        to_do = [self]

        while to_do:
            cur = to_do.pop()
            owning_widget = cur.owning_widget_weak()

            # The widget's session may be `None`, if this widget has never
            # entered the widget tree. e.g. `build` returns a widget, which
            # doesn't make it through reconciliation and is thus never even
            # marked as dirty -> No session is injected.
            if owning_widget is not None and owning_widget._session_ is not None:
                owning_widget._session_._register_dirty_widget(
                    owning_widget,
                    include_fundamental_children_recursively=False,
                )

            to_do.extend(cur.children)


class StateProperty:
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

    def __get__(
        self,
        instance: Optional[Widget],
        owner: Optional[type] = None,
    ) -> object:
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
        if isinstance(value, StateBinding):
            return value.get_value()

        # Otherwise return the value
        return value

    def __set__(self, instance: Widget, value: object) -> None:
        if self.readonly:
            cls_name = type(instance).__name__
            raise AttributeError(
                f"Cannot assign to readonly property {cls_name}.{self.name}"
            )

        # If this property is part of a state binding delegate to the binding
        # instead
        instance_vars = vars(instance)
        try:
            local_value = instance_vars[self.name]

        # No value was assigned yet, i.e. this function was called by the
        # widget's `__init__`. If this is a plain value assign it. Even if it is
        # a `StateProperty` the binding will be created by the `Session`, so
        # just keep track of the value in that case as well.
        except KeyError:
            assert instance._session_ is None
            instance_vars[self.name] = value
            return

        # A value has already been assigned. This is mutation of an existing
        # widget

        # State bindings may only be created when the widget is constructed
        if isinstance(value, StateProperty):
            raise RuntimeError(
                "State bindings can only be created when the widget is constructed"
            )

        # Delegate to the binding if it exists
        if isinstance(local_value, StateBinding):
            local_value.set_value(value)
            return

        # Otherwise set the value directly and mark the widget as dirty
        instance_vars[self.name] = value

        if instance._session_ is not None:
            instance._session_._register_dirty_widget(
                instance,
                include_fundamental_children_recursively=False,
            )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


@dataclass_transform(eq_default=False)
@dataclass(eq=False, repr=False)
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

    width: Union[Literal["natural", "grow"], float] = "natural"
    height: Union[Literal["natural", "grow"], float] = "natural"

    align_x: Optional[float] = None
    align_y: Optional[float] = None

    # Weak reference to the widget whose `build` method returned this widget.
    _weak_builder_: Callable[[], Optional[Widget]] = dataclasses.field(
        # Dataclasses seem to unintentionally turn this function into a method.
        # Make sure it works whether or not `self` is passed.
        default=lambda *args: None,
        init=False,
    )

    # Each time a widget is built the build generation in that widget's WIDGET
    # DATA is incremented. If this value no longer matches the value in its
    # parent's WIDGET DATA, the widget is dead.
    _build_generation_: int = dataclasses.field(default=-1, init=False)

    # Injected by the session when the widget is refreshed
    _session_: Optional["session.Session"] = dataclasses.field(default=None, init=False)

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: Set[str] = dataclasses.field(
        init=False, default_factory=set
    )

    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: ClassVar[Set["StateProperty"]]

    @classmethod
    def _preprocess_dataclass_fields(cls):
        # When a field has a default value (*not* default factory!), the
        # constructor actually doesn't assign the default value to the instance.
        # The default value is actually permanently stored in the class. So the
        # instance doesn't have the attribute, but the class does, and
        # everything is fine, right? Wrong. We create a `StateProperty` for each
        # field, which overrides that default value. We absolutely need every
        # attribute to be an instance attribute, which we can achieve by
        # replacing every default value with a default factory.
        cls_vars = vars(cls)

        for attr_name in cls_vars.get("__annotations__", {}):
            try:
                field_or_default = cls_vars[attr_name]
            except KeyError:
                continue

            if not isinstance(field_or_default, dataclasses.Field):
                field = dataclasses.field(
                    default_factory=make_default_factory_for_value(field_or_default)
                )
                setattr(cls, attr_name, field)
                continue

            # If it doesn't have a default value, we can ignore it
            if field_or_default.default is dataclasses.MISSING:
                continue

            field_or_default.default_factory = make_default_factory_for_value(
                field_or_default.default
            )
            field_or_default.default = dataclasses.MISSING

    @staticmethod
    def _determine_explicitly_set_properties(
        original_init,
        self: "Widget",
        *args,
        **kwargs,
    ):
        # Chain up to the original `__init__`
        original_init(self, *args, **kwargs)

        # Determine which properties were explicitly set
        bound_args = inspect.signature(original_init).bind(self, *args, **kwargs)
        self._explicitly_set_properties_.update(bound_args.arguments)

    @staticmethod
    def _post_init(
        original_init,
        self: "Widget",
        *args,
        **kwargs,
    ):
        original_init(self, *args, **kwargs)

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

        has_custom_init = "__init__" in vars(cls)

        # Apply the dataclass transform
        cls._preprocess_dataclass_fields()
        dataclasses.dataclass(eq=False, repr=False)(cls)

        # Keep track of which properties were explicitly set in the constructor.
        introspection.wrap_method(
            cls._determine_explicitly_set_properties,
            cls,
            "__init__",
        )

        # Widgets need to run custom code in in `__init__`, but dataclass
        # constructors don't chain up. So if this class's `__init__` was created
        # by the `@dataclass` decorator, wrap it with a custom `__init__` that
        # calls our initialization code.
        if not has_custom_init:
            introspection.wrap_method(
                cls._post_init,
                cls,
                "__init__",
            )

        # Replace all properties with custom state properties
        cls._initialize_state_properties(Widget._state_properties_)

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
                "_build_generation_",
                "_explicitly_set_properties_",
                "_init_signature_",
                "_session_",
                "_weak_builder_",
                "margin_x",
                "margin_y",
                "margin",
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
        for name in _get_annotated_instance_attributes(self.__class__):
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

    async def force_refresh(self) -> None:
        self.session._register_dirty_widget(
            self,
            include_fundamental_children_recursively=False,
        )

        await self.session._refresh()

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
        await self._session_._refresh()

    async def _on_message(self, message: Jsonable) -> None:
        """
        This function is called when the frontend sends a message to this widget
        via `sendMessage`.
        """
        pass
