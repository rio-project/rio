from __future__ import annotations

import abc
import asyncio
import dataclasses
import inspect
import json
import typing
import weakref
from abc import abstractmethod
from collections import defaultdict
from dataclasses import KW_ONLY, dataclass
from typing import *  # type: ignore

import introspection
from typing_extensions import dataclass_transform
from uniserde import Jsonable, JsonDoc

import rio

from .. import common, event, global_state, inspection

__all__ = ["Component"]


JAVASCRIPT_SOURCE_TEMPLATE = """
%(js_source)s

if (%(js_class_name)s !== undefined) {
    window.componentClasses['%(cls_unique_id)s'] = %(js_class_name)s;
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


def make_default_factory_for_value(value: T) -> Callable[[], T]:
    def default_factory() -> T:
        return value

    default_factory.__name__ = default_factory.__qualname__ = f"return_{value!r}"

    return default_factory


async def call_component_handler_once(
    weak_component: weakref.ReferenceType[Component],
    handler: Callable,
) -> None:
    # Does the component still exist?
    component = weak_component()

    if component is None:
        return

    # Call the handler
    await component.call_event_handler(lambda: handler(component))
    await component.session._refresh()


async def _periodic_event_worker(
    weak_component: weakref.ReferenceType[Component],
    handler: Callable,
) -> None:
    while True:
        # Wait for the next tick
        await asyncio.sleep(handler._rio_event_periodic_interval_)  # type: ignore

        # Call the handler
        await call_component_handler_once(weak_component, handler)


@dataclass(eq=False)
class StateBinding:
    # Weak reference to the component containing this binding
    owning_component_weak: Callable[[], Optional[Component]]

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
        to_do: List[StateBinding] = [self]

        while to_do:
            cur = to_do.pop()
            owning_component = cur.owning_component_weak()

            # The component's session may be `None`, if this component has never
            # entered the component tree. e.g. `build` returns a component, which
            # doesn't make it through reconciliation and is thus never even
            # marked as dirty -> No session is injected.
            if owning_component is not None and owning_component._session_ is not None:
                owning_component._session_._register_dirty_component(
                    owning_component,
                    include_children_recursively=False,
                )

            to_do.extend(cur.children)


class StateProperty:
    """
    StateProperties act like regular properties, with additional considerations:

    - When a state property is assigned to, the component owning it is marked as
      dirty in the session

    - State properties have the ability to share their value with other state
      property instances. If state property `A` is assigned to state property
      `B`, then `B` creates a `StateBinding` and any future access to `B` will
      be routed to `A` instead:

    ```
    class Foo(Component):
        foo_text = "Hello"

        def build(self) -> Component:
            return Bar(bar_text=Foo.foo_text)  # Note `Foo` instead of `self`
    ```
    """

    def __init__(self, name: str, readonly: bool):
        self.name = name
        self.readonly = readonly

    def __get__(
        self,
        instance: Optional[Component],
        owner: Optional[type] = None,
    ) -> object:
        # If accessed through the class, rather than instance, return the
        # StateProperty itself
        if instance is None:
            return self

        # Otherwise get the value assigned to the property in the component
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

    def __set__(self, instance: Component, value: object) -> None:
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
                    "State bindings can only be created when calling the component constructor"
                )

            # Delegate to the binding if it exists
            if isinstance(local_value, StateBinding):
                local_value.set_value(value)
                return

        # Otherwise set the value directly and mark the component as dirty
        instance_vars[self.name] = value

        if instance._session_ is not None:
            instance._session_._register_dirty_component(
                instance,
                include_children_recursively=False,
            )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


class ComponentMeta(abc.ABCMeta):
    def __call__(cls, *args: object, **kwargs: object):
        component = super().__call__(*args, **kwargs)
        component._create_state_bindings()

        # Call `_rio_post_init` for every class in the MRO
        for base in reversed(type(component).__mro__):
            try:
                post_init = vars(base)["_rio_post_init"]
            except KeyError:
                continue

            post_init(component)

        # Call `on_create` handlers
        on_create_handlers = component._rio_event_handlers_[event.EventTag.ON_CREATE]

        for handler in on_create_handlers:
            handler(component)

        return component


@dataclass_transform(eq_default=False)
@dataclass(eq=False, repr=False)
class Component(metaclass=ComponentMeta):
    """
    Base class for all `rio` components.

    Components are the building blocks of `rio` apps. `rio` ships with many
    useful components out of the box, but you can also subclass a component to
    create your own.

    Attributes:
        key: A unique identifier for this component. If two components with the
            same key are present during reconciliation they will be considered
            the same component and their state will be preserved. If no key is
            specified, reconciliation falls back to a less precise method, by
            comparing the location of the component in the component tree.

        margin: The margin around this component. This is a shorthand for
            setting `margin_left`, `margin_top`, `margin_right` and
            `margin_bottom` to the same value. If multiple conflicting margins
            are specified the most specific one wins. If for example `margin`
            and `margin_left` are both specified, `margin_left` is used for the
            left side, while the other sides use `margin`.

        margin_x: The horizontal margin around this component. This is a
            shorthand for setting `margin_left` and `margin_right` to the same
            value. If multiple conflicting margins are specified the most
            specific one wins. If for example `margin_x` and `margin_left` are
            both specified, `margin_left` is used for the left side, while the
            other side uses `margin_x`.

        margin_y: The vertical margin around this component. This is a shorthand
            for setting `margin_top` and `margin_bottom` to the same value. If
            multiple conflicting margins are specified the most specific one
            wins. If for example `margin_y` and `margin_top` are both specified,
            `margin_top` is used for the top side, while the other side uses
            `margin_y`.

        margin_left: The left margin around this component. If multiple
            conflicting margins are specified this one will be used, since it's
            the most specific. If for example `margin_left` and `margin` are
            both specified, `margin_left` is used for the left side, while the
            other sides use `margin`.

        margin_top: The top margin around this component. If multiple
            conflicting margins are specified this one will be used, since it's
            the most specific. If for example `margin_top` and `margin` are both
            specified, `margin_top` is used for the top side, while the other
            sides use `margin`.

        margin_right: The right margin around this component. If multiple
            conflicting margins are specified this one will be used, since it's
            the most specific. If for example `margin_right` and `margin` are
            both specified, `margin_right` is used for the right side, while the
            other sides use `margin`.

        margin_bottom: The bottom margin around this component. If multiple
            conflicting margins are specified this one will be used, since it's
            the most specific. If for example `margin_bottom` and `margin` are
            both specified, `margin_bottom` is used for the bottom side, while
            the other sides use `margin`.

        width: How much horizontal space this component should request during
            layouting. This can be either a number, or one of the special
            values:

            If `"natural"`, the component will request the minimum amount it
            requires to fit on the screen. For example a `Text` will request
            however much space the characters of that text require. A `Row`
            would request the sum of the widths of its children.

            If `"grow"`, the component will request all the remaining space in
            its parent.

            Please note that the space a `Component` receives during layouting
            may not match the request. As a general rule for example, containers
            try to pass on all available space to children. If you really want a
            `Component` to only take up as much space as requested, consider
            specifying an alignment.

        height: How much vertical space this component should request during
            layouting. This can be either a number, or one of the special
            values:

            If `"natural"`, the component will request the minimum amount it
            requires to fit on the screen. For example a `Text` will request
            however much space the characters of that text require. A `Row`
            would request the height of its tallest child.

            If `"grow"`, the component will request all the remaining space in
            its parent.

            Please note that the space a `Component` receives during layouting
            may not match the request. As a general rule for example, containers
            try to pass on all available space to children. If you really want a
            `Component` to only take up as much space as requested, consider
            specifying an alignment.

        align_x: How this component should be aligned horizontally, if it
            receives more space than it requested. This can be a number between
            0 and 1, where 0 means left-aligned, 0.5 means centered, and 1 means
            right-aligned.

        align_y: How this component should be aligned vertically, if it receives
            more space than it requested. This can be a number between 0 and 1,
            where 0 means top-aligned, 0.5 means centered, and 1 means
            bottom-aligned.
    """

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

    # Weak reference to the component's builder. Used to check if the component is
    # still part of the component tree.
    _weak_builder_: Callable[[], Optional[Component]] = dataclasses.field(
        # Dataclasses seem to unintentionally turn this function into a method.
        # Make sure it works whether or not `self` is passed.
        default=lambda *args: None,
        init=False,
        repr=False,
    )

    # Each time a component is built the build generation in that component's COMPONENT
    # DATA is incremented. If this value no longer matches the value in its
    # builder's COMPONENT DATA, the component is dead.
    _build_generation_: int = dataclasses.field(default=-1, init=False, repr=False)

    # Injected by the session when the component is refreshed
    _session_: Optional["rio.Session"] = dataclasses.field(
        default=None, init=False, repr=False
    )

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: Set[str] = dataclasses.field(
        init=False, default_factory=set, repr=False
    )

    # True if the component is subscribed to either the `on_mount` or
    # `on_unmount` events.
    _watch_tree_mount_and_unmount_: ClassVar[bool] = dataclasses.field(
        default=False, init=False, repr=False
    )

    # This flag indicates whether state bindings for this component have already
    # been initialized. Used by `__getattribute__` to check if it should throw
    # an error.
    _state_bindings_initialized_: bool = dataclasses.field(
        default=False, init=False, repr=False
    )

    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: ClassVar[Dict[str, "StateProperty"]]

    # Maps event tags to the methods that handle them. The methods aren't bound
    # to the instance yet, so make sure to pass `self` when calling them
    #
    # The assigned value is needed so that the `Component` class itself has a
    # valid value. All subclasses override this value in `__init_subclass__`.
    _rio_event_handlers_: ClassVar[
        defaultdict[event.EventTag, Tuple[Callable[..., Any], ...]]
    ] = defaultdict(tuple)

    # Whether this component class is built into Rio, rather than user defined,
    # or from a library.
    _rio_builtin_: ClassVar[bool] = False

    # Whether this instance is internal to Rio, e.g. because the spawning
    # component is a high-level component defined in Rio.
    _rio_internal_: bool = dataclasses.field(default=False, init=False, repr=False)

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

            field: dataclasses.Field[object] = field_or_default

            # If it doesn't have a default value, we can ignore it
            if field.default is dataclasses.MISSING:
                continue

            field.default_factory = make_default_factory_for_value(field.default)
            field.default = dataclasses.MISSING

    @staticmethod
    def _determine_explicitly_set_properties(
        original_init: Callable[Concatenate[Component, P], None],
        self: "Component",
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        # Chain up to the original `__init__`
        original_init(self, *args, **kwargs)

        # Determine which properties were explicitly set
        bound_args = inspect.signature(original_init).bind(self, *args, **kwargs)
        self._explicitly_set_properties_.update(bound_args.arguments)

    @staticmethod
    def _init_component(
        original_init: Callable[Concatenate[Component, P], None],
        self: "Component",
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        # Fetch the session this component is part of
        if global_state.currently_building_session is None:
            raise RuntimeError(
                "Components can only be created inside of `build` methods."
            )

        session = global_state.currently_building_session
        self._session_ = session

        # Create a unique ID for this component
        self._id = session._next_free_component_id
        session._next_free_component_id += 1

        session._register_dirty_component(
            self,
            include_children_recursively=False,
        )

        # Keep track of this component's existence
        #
        # Components must be known by their id, so any messages addressed to
        # them can be passed on correctly.
        session._weak_components_by_id[self._id] = self

        # Some events need attention right after the component is created
        for event_tag, event_handlers in self._rio_event_handlers_.items():
            # Don't register event handlers if there aren't any, since that would slow down the session
            if not event_handlers:
                continue

            # Page changes are handled by the session. Register the handler
            if event_tag == event.EventTag.ON_PAGE_CHANGE:
                session._page_change_callbacks[self] = event_handlers

            # The `periodic` event needs a task to work in
            elif event_tag == event.EventTag.PERIODIC:
                for event_handler in event_handlers:
                    session.create_task(
                        _periodic_event_worker(weakref.ref(self), event_handler),
                        name=f"`rio.event.periodic` event worker for {self}",
                    )

        # Track whether this instance is internal to Rio. This is the case if
        # this component's creator is defined in Rio.
        creator = global_state.currently_building_component
        if creator is None:
            assert type(self).__qualname__ == "HighLevelRootComponent", type(
                self
            ).__qualname__
            self._rio_internal_ = True
        else:
            self._rio_internal_ = creator._rio_builtin_

        # Call the `__init__` created by `@dataclass`
        original_init(self, *args, **kwargs)

        # Initialize the margins. This has to happen after the dataclass
        # `__init__`, because it would overwrite our values.
        def elvis(*param_names: str) -> Any:
            for param_name in param_names:
                value = kwargs.get(param_name)

                if value is not None:
                    return value

            return 0

        self.margin_left = elvis("margin_left", "margin_x", "margin")
        self.margin_top = elvis("margin_top", "margin_y", "margin")
        self.margin_right = elvis("margin_right", "margin_x", "margin")
        self.margin_bottom = elvis("margin_bottom", "margin_y", "margin")

    def _create_state_bindings(self) -> None:
        self._state_bindings_initialized_ = True

        creator = global_state.currently_building_component

        # The creator can be `None` if this component was created by the app's
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
                    owning_component_weak=weakref.ref(creator),
                    owning_property=value,
                    is_root=True,
                    parent=None,
                    value=parent_binding,
                    children=weakref.WeakSet(),
                )
                creator_vars[value.name] = parent_binding

            # Create the child binding
            child_binding = StateBinding(
                owning_component_weak=weakref.ref(self),
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

        # We'll manually take care of calling __post_init__ methods because
        # dataclasses are unreliable. Rename the method so that it won't be
        # called by the dataclass constructor.
        if "__post_init__" in cls_vars:
            cls._rio_post_init = cls.__post_init__  # type: ignore
            del cls.__post_init__  # type: ignore

        # Apply the dataclass transform
        cls._preprocess_dataclass_fields()
        dataclasses.dataclass(eq=False, repr=False)(cls)

        # Keep track of which properties were explicitly set in the constructor.
        introspection.wrap_method(
            cls._determine_explicitly_set_properties,
            cls,
            "__init__",
        )

        # Components need to run custom code in in `__init__`, but dataclass
        # constructors don't chain up. So if this class's `__init__` was created
        # by the `@dataclass` decorator, wrap it with a custom `__init__` that
        # calls our initialization code.
        if not has_custom_init:
            introspection.wrap_method(
                cls._init_component,
                cls,
                "__init__",
            )

        # Replace all properties with custom state properties
        all_parent_state_properties: Dict[str, StateProperty] = {}

        for base in cls.__bases__:
            if not issubclass(base, Component):
                continue

            all_parent_state_properties.update(base._state_properties_)

        cls._initialize_state_properties(all_parent_state_properties)

        # Keep track of all event handlers. By gathering them here, the
        # component constructor doesn't have to re-scan the entire class for
        # each instantiation.
        event_handlers: defaultdict[
            event.EventTag, List[Callable[..., Any]]
        ] = defaultdict(list)

        # Inherit event handlers from base classes
        for base in cls.__bases__:
            if not issubclass(base, Component):
                continue

            for event_tag, handlers in base._rio_event_handlers_.items():
                event_handlers[event_tag].extend(handlers)

        # Add any event handlers added in this class
        for method in vars(cls).values():
            try:
                tag = method._rio_event_tag_
            except AttributeError:
                continue

            event_handlers[tag].append(method)

        # Convert the lists to tuples
        cls._rio_event_handlers_ = defaultdict(
            tuple,
            {
                event_tag: tuple(handlers)
                for event_tag, handlers in event_handlers.items()
            },
        )

        # If the component is subscribed to `on_mount` or `on_unmount`, update
        # the boolean for that
        if (
            event.EventTag.ON_MOUNT in cls._rio_event_handlers_
            or event.EventTag.ON_UNMOUNT in cls._rio_event_handlers_
        ):
            cls._watch_tree_mount_and_unmount_ = True

        # Is this class built into Rio?
        cls._rio_builtin_ = cls.__module__.startswith("rio.")

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

    # When running in development mode, make sure that no component `__init__`
    # tries to read a state property. This would be incorrect because state
    # bindings are not yet initialized at that point.
    if common.RUNNING_IN_DEV_MODE and not TYPE_CHECKING:

        def __getattribute__(self, attr_name: str):
            # fmt: off
            if (
                attr_name in type(self)._state_properties_ and
                not super().__getattribute__("_state_bindings_initialized_")
            ):
                # fmt: on
                raise Exception(
                    "You have attempted to read a state property in a component's"
                    " `__init__` method. This is not allowed because state"
                    " bindings are not yet initialized at that point. Please"
                    " move this code into the `on_create` method."
                )

            return super().__getattribute__(attr_name)

    @property
    def session(self) -> "rio.Session":
        """
        Return the session this component is part of.

        The session is accessible after the build method which constructed this
        component has returned.
        """
        if self._session_ is None:
            raise RuntimeError(
                "The session is only accessible once the build method which"
                " constructed this component has returned."
            )

        return self._session_

    def _custom_serialize(self) -> JsonDoc:
        """
        Return any additional properties to be serialized, which cannot be
        deduced automatically from the type annotations.
        """
        return {}

    @abstractmethod
    def build(self) -> "rio.Component":
        """
        Return a component tree which represents the UI of this component.

        Most components define their appearance and behavior by combining other,
        more basic components. This function's purpose is to do exactly that. It
        returns another component (typically a container) which will be
        displayed on the screen.

        The `build` function should be pure, meaning that it does not modify the
        component's state and returns the same result each time it's invoked.
        """
        raise NotImplementedError()

    def _iter_direct_children(self) -> Iterable["Component"]:
        for name in inspection.get_child_component_containing_attribute_names(
            type(self)
        ):
            try:
                value = getattr(self, name)
            except AttributeError:
                continue

            if isinstance(value, Component):
                yield value

            if isinstance(value, list):
                value = cast(List[object], value)

                for item in value:
                    if isinstance(item, Component):
                        yield item

    def _iter_direct_and_indirect_child_containing_attributes(
        self,
        *,
        include_self: bool,
        recurse_into_high_level_components: bool,
    ) -> Iterable["Component"]:
        # Special case the component itself to handle `include_self`
        if include_self:
            yield self

        if not recurse_into_high_level_components and not isinstance(
            self, FundamentalComponent
        ):
            return

        # Iteratively yield all children
        to_do = list(self._iter_direct_children())
        while to_do:
            cur = to_do.pop()
            yield cur

            if recurse_into_high_level_components or isinstance(
                cur, FundamentalComponent
            ):
                to_do.extend(cur._iter_direct_children())

    def _iter_component_tree(self) -> Iterable["Component"]:
        """
        Iterate over all components in the component tree, with this component as the root.
        """
        yield self

        if isinstance(self, FundamentalComponent):
            for child in self._iter_direct_children():
                yield from child._iter_component_tree()
        else:
            build_result = self.session._weak_component_data_by_component[
                self
            ].build_result
            yield from build_result._iter_component_tree()

    async def _on_message(self, msg: Jsonable, /) -> None:
        raise RuntimeError(f"{type(self).__name__} received unexpected message `{msg}`")

    def _is_in_component_tree(self, cache: Dict[rio.Component, bool]) -> bool:
        """
        Returns whether this component is directly or indirectly connected to the
        component tree of a session.

        This operation is fast, but has to walk up the component tree to make sure
        the component's parent is also connected. Thus, when checking multiple
        components it can easily happen that the same components are checked over and
        over, resulting on O(n log n) runtime. To avoid this, pass a cache
        dictionary to this function, which will be used to memoize the result.

        Be careful not to reuse the cache if the component hierarchy might have
        changed (for example after an async yield).
        """

        # Already cached?
        try:
            return cache[self]
        except KeyError:
            pass

        # Root component?
        if self is self.session._root_component:
            result = True

        # Has the builder has been garbage collected?
        else:
            builder = self._weak_builder_()
            if builder is None:
                result = False

            # Has the builder since created new build output, and this component
            # isn't part of it anymore?
            else:
                parent_data = self.session._weak_component_data_by_component[builder]
                result = (
                    parent_data.build_generation == self._build_generation_
                    and builder._is_in_component_tree(cache)
                )

        # Cache the result and return
        cache[self] = result
        return result

    @overload
    async def call_event_handler(
        self,
        handler: rio.EventHandler[[]],
    ) -> None:
        ...

    @overload
    async def call_event_handler(
        self,
        handler: rio.EventHandler[[T]],
        event_data: T,
        /,
    ) -> None:
        ...

    async def call_event_handler(
        self,
        handler: rio.EventHandler[...],
        *event_data: object,
    ) -> None:
        """
        Calls an even handler, awaiting it if necessary.

        Call an event handler, if one is present. Await it if necessary. Log and
        discard any exceptions. If `event_data` is present, it will be passed to
        the event handler.
        """
        await self.session._call_event_handler(handler, *event_data)

    async def force_refresh(self) -> None:
        """
        Force a rebuild of this component.

        Most of the time components update automatically when their state
        changes. However, some state mutations are invisible to `Rio`: For
        example, appending items to a list modifies the list, but since no list
        instance was actually assigned to th component, `Rio` will be unaware of
        this change.

        In these cases, you can force a rebuild of the component by calling
        `force_refresh`. This will trigger a rebuild of the component and
        display the updated version on the screen.

        Another common use case is if you wish to update an component while an
        event handler is still running. `Rio` will automatically detect changes
        after event handlers return, but if you are performing a long-running
        operation, you may wish to update the component while the event handler
        is still running. This allows you to e.g. update a progress bar while
        the operation is still running.
        """
        self.session._register_dirty_component(
            self,
            include_children_recursively=False,
        )

        await self.session._refresh()

    def __repr__(self) -> str:
        result = f"<{type(self).__name__} id:{self._id}"

        child_strings: List[str] = []
        for child in self._iter_direct_children():
            child_strings.append(f" {type(child).__name__}:{child._id}")

        if child_strings:
            result += " -" + "".join(child_strings)

        return result + ">"


# Most classes have their state properties initialized in
# `Component.__init_subclass__`. However, since `Component` isn't a subclass of
# itself this needs to be done manually.
Component._initialize_state_properties({})
introspection.wrap_method(
    Component._init_component,
    Component,
    "__init__",
)


class FundamentalComponent(Component):
    # Unique id for identifying this class in the frontend. This is initialized
    # in `Component.__init_subclass__`.
    _unique_id: ClassVar[str]

    def build(self) -> "Component":
        raise RuntimeError(
            f"Attempted to call `build` on `FundamentalComponent` {self}"
        )

    @classmethod
    def build_javascript_source(cls, sess: rio.Session) -> str:
        return ""

    @classmethod
    def build_css_source(cls, sess: rio.Session) -> str:
        return ""

    def __init_subclass__(cls):
        # Assign a unique id to this class. This allows the frontend to identify
        # components.
        hash_ = common.secure_string_hash(
            cls.__module__,
            cls.__qualname__,
            hash_length=12,
        )

        cls._unique_id = f"{cls.__name__}-{hash_}"

        # Chain up
        super().__init_subclass__()

    @classmethod
    async def _initialize_on_client(cls, sess: rio.Session) -> None:
        message_source = ""

        javascript_source = cls.build_javascript_source(sess)
        if javascript_source:
            message_source += JAVASCRIPT_SOURCE_TEMPLATE % {
                "js_source": javascript_source,
                "js_class_name": cls.__name__,
                "cls_unique_id": cls._unique_id,
                "child_attribute_names": json.dumps(
                    inspection.get_child_component_containing_attribute_names(cls)
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
        component.
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

    async def _on_message(self, message: Jsonable, /) -> None:
        """
        This function is called when the frontend sends a message to this component
        via `sendMessage`.
        """
        pass


class KeyboardFocusableFundamentalComponent(FundamentalComponent):
    async def grab_keyboard_focus(self) -> None:
        await self.session._remote_set_keyboard_focus(self._id)
