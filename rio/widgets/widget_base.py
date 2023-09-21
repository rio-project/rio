from __future__ import annotations

import abc
import dataclasses
import inspect
import json
import traceback
import typing
import weakref
from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore
from typing import Any

import introspection
from typing_extensions import dataclass_transform
from uniserde import Jsonable, JsonDoc

import rio as rx

from .. import common, global_state, inspection

__all__ = ["Widget"]


JAVASCRIPT_SOURCE_TEMPLATE = """
%(js_source)s

if (%(js_class_name)s !== undefined) {
    window.widgetClasses['%(cls_unique_id)s'] = %(js_class_name)s;
    window.childAttributeNames['%(cls_unique_id)s'] = %(child_attribute_names)s;
}
"""


CSS_SOURCE_TEMPLATE = """
const style = document.createElement('style');
style.innerHTML = %(escaped_css_source)s;
document.head.appendChild(style);
"""


T = TypeVar("T")
P = ParamSpec("P")


_unique_id_counter = -1


def _make_unique_id() -> int:
    global _unique_id_counter
    _unique_id_counter += 1
    return _unique_id_counter


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
                    include_children_recursively=False,
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

        # Look up the stored value
        instance_vars = vars(instance)
        try:
            local_value = instance_vars[self.name]
        except KeyError:
            pass
        else:
            # If a value is already stored, that means this is a re-assignment.
            # Which further means it's an assignment outside of `__init__`.
            # Which is not a valid place to create a state binding.
            if isinstance(value, StateProperty):
                raise RuntimeError(
                    "State bindings can only be created when calling the widget constructor"
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
                include_children_recursively=False,
            )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


class WidgetMeta(abc.ABCMeta):
    def __call__(cls, *args, **kwargs):
        widget = super().__call__(*args, **kwargs)
        widget._create_state_bindings()
        return widget


@dataclass_transform(eq_default=False)
@dataclass(eq=False, repr=False)
class Widget(metaclass=WidgetMeta):
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

    _id: int = dataclasses.field(init=False)

    # Weak reference to the widget whose `build` method returned this widget.
    #
    # TODO: What exactly does this mean? Is the builder the widget in which
    # build() this widget was created? Or the one that has actually added this
    # child into the widget tree?
    _weak_builder_: Callable[[], Optional[Widget]] = dataclasses.field(
        # Dataclasses seem to unintentionally turn this function into a method.
        # Make sure it works whether or not `self` is passed.
        default=lambda *args: None,
        init=False,
    )

    # Each time a widget is built the build generation in that widget's WIDGET
    # DATA is incremented. If this value no longer matches the value in its
    # builder's WIDGET DATA, the widget is dead.
    _build_generation_: int = dataclasses.field(default=-1, init=False)

    # Injected by the session when the widget is refreshed
    _session_: Optional["rx.Session"] = dataclasses.field(default=None, init=False)

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: Set[str] = dataclasses.field(
        init=False, default_factory=set
    )

    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: ClassVar[Dict[str, "StateProperty"]]

    # Maps event tags to the methods that handle them. The methods aren't bound
    # to the instance yet, so make sure to pass `self` when calling them
    _rio_event_handlers_: ClassVar[Dict[str, Callable]]

    # This flag indicates whether state bindings for this widget have already
    # been initialized. Used by `__getattribute__` to check if it should throw
    # an error.
    _state_bindings_initialized_: bool = dataclasses.field(default=False, init=False)

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
    def _init_widget(
        original_init,
        self: "Widget",
        *args,
        **kwargs,
    ):
        # Create a unique ID for this widget
        self._id = _make_unique_id()

        # Fetch the session this widget is part of
        if global_state.currently_building_session is None:
            raise RuntimeError("Widgets can only be created inside of `build` methods.")

        session = global_state.currently_building_session
        self._session_ = session
        session._register_dirty_widget(
            self,
            include_children_recursively=False,
        )

        # Keep track of this widget's existence
        #
        # Widgets must be known by their id, so any messages addressed to
        # them can be passed on correctly.
        session._weak_widgets_by_id[self._id] = self

        # Some events need support from the session. Register them
        for event_tag, event_handler in self._rio_event_handlers_.items():
            if event_tag == "on_route_change":
                session._route_change_callbacks[self] = event_handler

        # Initialize the margins
        def elvis(*param_names):
            for param_name in param_names:
                value = kwargs.get(param_name)

                if value is not None:
                    return value

            return 0

        self.margin_left = elvis("margin_left", "margin_x", "margin")
        self.margin_top = elvis("margin_top", "margin_y", "margin")
        self.margin_right = elvis("margin_right", "margin_x", "margin")
        self.margin_bottom = elvis("margin_bottom", "margin_y", "margin")

        # Call the `__init__` created by `@dataclass`
        original_init(self, *args, **kwargs)

    def _create_state_bindings(self) -> None:
        self._state_bindings_initialized_ = True

        creator = global_state.currently_building_widget

        # The creator can be `None` if this widget was created by the app's
        # `build` function. It's not possible to create a state binding in that
        # case.
        if creator is None:
            return

        creator_vars = vars(creator)
        self_vars = vars(self)

        for prop_name, state_property in self._state_properties_.items():
            # The dataclass constructor doesn't actually assign default values
            # as instance attributes. In that case we get a KeyError here. But
            # default values can't be state bindings, so just skip this
            # attribute
            try:
                value = self_vars[prop_name]
            except KeyError:
                continue

            # Create a StateBinding, if requested
            if not isinstance(value, StateProperty):
                continue

            # In order to create a `StateBinding`, the creator's
            # attribute must also be a binding
            parent_binding = creator_vars[value.name]

            if not isinstance(parent_binding, StateBinding):
                parent_binding = StateBinding(
                    owning_widget_weak=weakref.ref(creator),
                    owning_property=value,
                    is_root=True,
                    parent=None,
                    value=parent_binding,
                    children=weakref.WeakSet(),
                )
                creator_vars[value.name] = parent_binding

            # Create the child binding
            child_binding = StateBinding(
                owning_widget_weak=weakref.ref(self),
                owning_property=state_property,
                is_root=False,
                parent=parent_binding,
                value=None,
                children=weakref.WeakSet(),
            )
            parent_binding.children.add(child_binding)
            self_vars[prop_name] = child_binding

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls_vars = vars(cls)
        has_custom_init = "__init__" in cls_vars

        # If it exists, rename the `__post_init__` method, so that the dataclass
        # `__init__` doesn't automatically call it. We will call it manually
        # once the widget's state bindings have been created.
        if "__post_init__" in cls_vars:
            cls._rio_post_init = cls.__post_init__  # type: ignore
            del cls.__post_init__  # type: ignore
            # FIXME

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
                cls._init_widget,
                cls,
                "__init__",
            )

        # Replace all properties with custom state properties
        all_parent_state_properties: Dict[str, StateProperty] = {}

        for base in cls.__bases__:
            if not issubclass(base, Widget):
                continue

            all_parent_state_properties.update(base._state_properties_)

        cls._initialize_state_properties(all_parent_state_properties)

        # Keep track of all event handlers. By gathering them here, the widget
        # constructor doesn't have to re-scan the entire class for each
        # instantiation.
        cls._rio_event_handlers_ = {}

        if cls.on_route_change is not Widget.on_route_change:
            cls._rio_event_handlers_["on_route_change"] = cls.on_route_change

    @classmethod
    def _initialize_state_properties(
        cls,
        parent_state_properties: Dict[str, "StateProperty"],
    ) -> None:
        """
        Spawn `StateProperty` instances for all annotated properties in this
        class.
        """
        cls._state_properties_ = parent_state_properties.copy()

        # TODO: Placeholder function, until a better one is implemented in the
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
                "_id",
                "_init_signature_",
                "_session_",
                "_weak_builder_",
                "_state_bindings_initialized_",
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
            cls._state_properties_[attr_name] = state_property

    # When running in development mode, make sure that no widget `__init__`
    # tries to read a state property. This would be incorrect because state
    # bindings are not yet initialized at that point.
    if common.RUNNING_IN_DEV_MODE:

        def __getattribute__(self, attr_name: str):
            # fmt: off
            if (
                attr_name in type(self)._state_properties_ and
                not super().__getattribute__("_state_bindings_initialized_")
            ):
                # fmt: on
                raise Exception(
                    "You have attempted to read a state property in a widget's"
                    " `__init__` method. This is not allowed because state"
                    " bindings are not yet initialized at that point. Please"
                    " move this code into the `on_create` method."
                )

            return super().__getattribute__(attr_name)

    @property
    def session(self) -> "rx.Session":
        """
        Return the session this widget is part of.

        The session is accessible after the build method which constructed this
        widget has returned.
        """
        if self._session_ is None:
            raise RuntimeError(
                "The session is only accessible once the build method which"
                " constructed this widget has returned."
            )

        return self._session_

    def _custom_serialize(self) -> JsonDoc:
        """
        Return any additional properties to be serialized, which cannot be
        deduced automatically from the type annotations.
        """
        return {}

    @abstractmethod
    def build(self) -> "Widget":
        raise NotImplementedError()

    def _iter_direct_children(self) -> Iterable["Widget"]:
        for name in inspection.get_child_widget_containing_attribute_names(type(self)):
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

    def _iter_direct_and_indirect_children(
        self,
        *,
        include_self: bool,
        cross_build_boundaries: bool,
    ) -> Iterable["Widget"]:
        # Special case the widget itself to handle `include_self`
        if include_self:
            yield self

        if not cross_build_boundaries and not isinstance(self, FundamentalWidget):
            return

        # Iteratively yield all children
        to_do = list(self._iter_direct_children())
        while to_do:
            cur = to_do.pop()
            yield cur

            if cross_build_boundaries or isinstance(cur, FundamentalWidget):
                to_do.extend(cur._iter_direct_children())

    async def _on_message(self, msg: Jsonable) -> None:
        raise RuntimeError(f"{type(self).__name__} received unexpected message `{msg}`")

    def _is_in_widget_tree(self, cache: Dict[rx.Widget, bool]) -> bool:
        """
        Returns whether this widget is directly or indirectly connected to the
        widget tree of a session.

        This operation is fast, but has to walk up the widget tree to make sure
        the widget's parent is also connected. Thus, when checking multiple
        widgets it can easily happen that the same widgets are checked over and
        over, resulting on O(n log n) runtime. To avoid this, pass a cache
        dictionary to this function, which will be used to memoize the result.

        Be careful not to reuse the cache if the widget hierarchy might have
        changed (e.g. after an async yield).
        """

        # Already cached?
        try:
            return cache[self]
        except KeyError:
            pass

        # Root widget?
        if self is self.session._root_widget:
            result = True

        # Has the builder has been garbage collected?
        else:
            builder = self._weak_builder_()
            if builder is None:
                result = False

            # Has the builder since created new build output, and this widget
            # isn't part of it anymore?
            else:
                parent_data = self.session._lookup_widget_data(builder)
                result = (
                    parent_data.build_generation == self._build_generation_
                    and builder._is_in_widget_tree(cache)
                )

        # Cache the result and return
        cache[self] = result
        return result

    @typing.overload
    async def _call_event_handler(
        self,
        handler: rx.EventHandler[[]],
    ) -> None:
        ...

    @typing.overload
    async def _call_event_handler(
        self,
        handler: rx.EventHandler[[T]],
        event_data: T,
    ) -> None:
        ...

    async def _call_event_handler(  # type: ignore
        self,
        handler: rx.EventHandler[P],
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
            include_children_recursively=False,
        )

        await self.session._refresh()

    def __repr__(self) -> str:
        result = f"<{type(self).__name__} id:{self._id}"

        child_strings = []
        for child in self._iter_direct_children():
            child_strings.append(f" {type(child).__name__}:{child._id}")

        if child_strings:
            result += " -" + "".join(child_strings)

        return result + ">"

    # Event Handler Templates
    #
    # Users may override these synchronously or asynchronously
    def on_route_change(self) -> Any:
        pass


# Most classes have their state properties initialized in
# `Widget.__init_subclass__`. However, since `Widget` isn't a subclass of
# itself this needs to be done manually.
Widget._initialize_state_properties({})
introspection.wrap_method(
    Widget._init_widget,
    Widget,
    "__init__",
)


class FundamentalWidget(Widget):
    # Unique id for identifying this class in the frontend. This is initialized
    # in `Widget.__init_subclass__`.
    _unique_id: ClassVar[str]

    def build(self) -> "Widget":
        raise RuntimeError(f"Attempted to call `build` on `FundamentalWidget` {self}")

    @classmethod
    def build_javascript_source(cls, sess: rx.Session) -> str:
        return ""

    @classmethod
    def build_css_source(cls, sess: rx.Session) -> str:
        return ""

    def __init_subclass__(cls):
        # Assign a unique id to this class. This allows the frontend to identify
        # widgets.
        hash_ = common.secure_string_hash(
            cls.__module__,
            cls.__qualname__,
            hash_length=12,
        )

        cls._unique_id = f"{cls.__name__}-{hash_}"

        # Chain up
        super().__init_subclass__()

    @classmethod
    async def _initialize_on_client(cls, sess: rx.Session) -> None:
        message_source = ""

        javascript_source = cls.build_javascript_source(sess)
        if javascript_source:
            message_source += JAVASCRIPT_SOURCE_TEMPLATE % {
                "js_source": javascript_source,
                "js_class_name": cls.__name__,
                "cls_unique_id": cls._unique_id,
                "child_attribute_names": json.dumps(
                    inspection.get_child_widget_containing_attribute_names(cls)
                ),
            }

        css_source = cls.build_css_source(sess)
        if css_source:
            escaped_css_source = json.dumps(css_source)
            message_source += CSS_SOURCE_TEMPLATE % {
                "escaped_css_source": escaped_css_source,
            }

        if message_source:
            await sess._evaluate_javascript(message_source)

    async def _on_state_update(self, delta_state: JsonDoc) -> None:
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
