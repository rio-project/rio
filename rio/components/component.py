from __future__ import annotations

import asyncio
import inspect
import sys
import typing
import weakref
from abc import abstractmethod
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import KW_ONLY, field
from pathlib import Path
from typing import Any, ClassVar, Literal, TypeVar, cast, overload

from typing_extensions import dataclass_transform
from uniserde import Jsonable, JsonDoc

import rio

from .. import debug, event, global_state, inspection
from ..dataclass import RioDataclassMeta, class_local_fields, internal_field
from ..state_properties import StateBinding, StateProperty
from . import fundamental_component

__all__ = ["Component"]


T = TypeVar("T")


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
    period: float,
) -> None:
    try:
        sess = weak_component().session  # type: ignore
    except AttributeError:
        return

    while True:
        # Wait for the next tick
        await asyncio.sleep(period)

        # Wait until there's an active connection to the client. We won't run
        # code periodically if we aren't sure whether the client will come back.
        await sess._is_active_event.wait()

        # Call the handler
        await call_component_handler_once(weak_component, handler)


def _determine_explicitly_set_properties(
    component: Component, args: tuple, kwargs: dict
) -> set[str]:
    # Determine which properties were explicitly set. This includes
    # parameters that received an argument, and also varargs (`*args`)
    signature = inspect.signature(component.__init__)
    bound_args = signature.bind(*args, **kwargs)

    explicitly_set_properties = set(bound_args.arguments)

    # fmt: off
    explicitly_set_properties.update(
        param.name
        for param in signature.parameters.values()
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
    )
    # fmt: on

    return explicitly_set_properties


C = typing.TypeVar("C", bound="Component")


# For some reason vscode doesn't understand that this class is a
# `@dataclass_transform`, so we'll annotate it again...
@dataclass_transform(
    eq_default=False,
    field_specifiers=(internal_field, field),
)
class ComponentMeta(RioDataclassMeta):
    # Cache for the set of all `StateProperty` instances in this class
    _state_properties_: dict[str, StateProperty]

    # Maps event tags to the methods that handle them. The methods aren't bound
    # to the instance yet, so make sure to pass `self` when calling them
    #
    # The assigned value is needed so that the `Component` class itself has a
    # valid value. All subclasses override this value in `__init_subclass__`.
    _rio_event_handlers_: defaultdict[event.EventTag, list[tuple[Callable, Any]]]

    # Whether this component class is built into Rio, rather than user defined,
    # or from a library.
    _rio_builtin_: bool

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Replace all properties with custom state properties
        cls._initialize_state_properties()

        # Inherit event handlers from parents
        cls._rio_event_handlers_ = defaultdict(list)

        for base in cls.__bases__:
            if not isinstance(base, ComponentMeta):
                continue

            for event_tag, handlers in base._rio_event_handlers_.items():  # type: ignore[wtf]
                cls._rio_event_handlers_[event_tag].extend(handlers)

        # Add events from this class itself
        for member in vars(cls).values():
            if not callable(member):
                continue

            try:
                events = member._rio_events_
            except AttributeError:
                continue

            for event_tag, args in events.items():
                for arg in args:
                    cls._rio_event_handlers_[event_tag].append((member, arg))

        # Is this class built into Rio?
        cls._rio_builtin_ = cls.__module__.startswith("rio.")

    def _initialize_state_properties(cls) -> None:
        """
        Spawn `StateProperty` instances for all annotated properties in this
        class.
        """
        all_parent_state_properties: dict[str, StateProperty] = {}

        for base in reversed(cls.__bases__):
            if isinstance(base, ComponentMeta):
                all_parent_state_properties.update(base._state_properties_)  # type: ignore[wtf]

        cls._state_properties_ = all_parent_state_properties

        annotations: dict = vars(cls).get("__annotations__", {})
        module = sys.modules[cls.__module__]

        for field_name, field in class_local_fields(cls).items():
            # Skip internal fields
            if not field.state_property:
                continue

            # Create the StateProperty
            # readonly = introspection.typing.has_annotation(annotation, Readonly
            readonly = False  # TODO

            state_property = StateProperty(
                field_name, readonly, annotations[field_name], module
            )
            setattr(cls, field_name, state_property)

            # Add it to the set of all state properties for rapid lookup
            cls._state_properties_[field_name] = state_property

    def __call__(cls: type[C], *args: object, **kwargs: object) -> C:
        component: C = object.__new__(cls)  # type: ignore[wtf]

        # Inject the session before calling the constructor
        # Fetch the session this component is part of
        if global_state.currently_building_session is None:
            raise RuntimeError(
                "Components can only be created inside of `build` methods."
            )

        session = global_state.currently_building_session
        component._session_ = session

        # Create a unique ID for this component
        component._id = session._next_free_component_id
        session._next_free_component_id += 1

        component._explicitly_set_properties_ = _determine_explicitly_set_properties(
            component, args, kwargs
        )

        # Call `__init__`
        component.__init__(*args, **kwargs)

        component._create_state_bindings()

        # Keep track of this component's existence
        #
        # Components must be known by their id, so any messages addressed to
        # them can be passed on correctly.
        session._weak_components_by_id[component._id] = component

        session._register_dirty_component(
            component,
            include_children_recursively=False,
        )

        # Some events need attention right after the component is created
        for event_tag, event_handlers in component._rio_event_handlers_.items():
            # Don't register an empty list of handlers, since that would
            # still slow down the session
            if not event_handlers:
                continue

            # Page changes are handled by the session. Register the handler
            if event_tag == event.EventTag.ON_PAGE_CHANGE:
                callbacks = tuple(handler for handler, unused in event_handlers)
                session._page_change_callbacks[component] = callbacks

            # The `periodic` event needs a task to work in
            elif event_tag == event.EventTag.PERIODIC:
                for callback, period in event_handlers:
                    session.create_task(
                        _periodic_event_worker(
                            weakref.ref(component), callback, period
                        ),
                        name=f"`rio.event.periodic` event worker for {component}",
                    )

        # Call `_rio_post_init` for every class in the MRO
        for base in reversed(type(component).__mro__):
            try:
                post_init = vars(base)["_rio_post_init"]
            except KeyError:
                continue

            post_init(component)

        return component


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
    key: str | None = internal_field(default=None, init=True)

    width: float | Literal["natural", "grow"] = "natural"
    height: float | Literal["natural", "grow"] = "natural"

    align_x: float | None = None
    align_y: float | None = None

    margin_left: float | None = None
    margin_top: float | None = None
    margin_right: float | None = None
    margin_bottom: float | None = None

    margin_x: float | None = None
    margin_y: float | None = None
    margin: float | None = None

    # TODO: Figure out why `internal_field` isn't working and use it instead
    _id: int = internal_field(init=False)

    # Weak reference to the component's builder. Used to check if the component
    # is still part of the component tree.
    _weak_builder_: Callable[[], Component | None] = internal_field(
        # Dataclasses seem to unintentionally turn this function into a method.
        # Make sure it works whether or not `self` is passed.
        default=lambda *args: None,
        init=False,
    )

    # Each time a component is built the build generation in that component's
    # COMPONENT DATA is incremented. If this value no longer matches the value
    # in its builder's COMPONENT DATA, the component is dead.
    _build_generation_: int = internal_field(default=-1, init=False)

    _session_: rio.Session = internal_field(init=False)

    # Remember which properties were explicitly set in the constructor. This is
    # filled in by `__new__`
    _explicitly_set_properties_: set[str] = internal_field(init=False)

    # Whether the `on_populate` event has already been triggered for this
    # component
    _on_populate_triggered_: bool = internal_field(default=False, init=False)

    # This flag indicates whether state bindings for this component have already
    # been initialized. Used by `__getattribute__` to check if it should throw
    # an error.
    _state_bindings_initialized_: bool = internal_field(default=False, init=False)

    # Whether this instance is internal to Rio, e.g. because the spawning
    # component is a high-level component defined in Rio.
    _rio_internal_: bool = internal_field(init=False)

    # The stackframe which has created this component. Used by the debugger.
    # Only initialized if in debugging mode.
    _creator_stackframe_: tuple[Path, int] = internal_field(init=False)

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

    @property
    def session(self) -> rio.Session:
        """
        Return the session this component is part of.
        """
        return self._session_

    def _custom_serialize(self) -> JsonDoc:
        """
        Return any additional properties to be serialized, which cannot be
        deduced automatically from the type annotations.
        """
        return {}

    @abstractmethod
    def build(self) -> rio.Component:
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

    def _iter_direct_children(self) -> Iterable[Component]:
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
                value = cast(list[object], value)

                for item in value:
                    if isinstance(item, Component):
                        yield item

    def _iter_direct_and_indirect_child_containing_attributes(
        self,
        *,
        include_self: bool,
        recurse_into_high_level_components: bool,
    ) -> Iterable[Component]:
        # Special case the component itself to handle `include_self`
        if include_self:
            yield self

        if not recurse_into_high_level_components and not isinstance(
            self, fundamental_component.FundamentalComponent
        ):
            return

        # Iteratively yield all children
        to_do = list(self._iter_direct_children())
        while to_do:
            cur = to_do.pop()
            yield cur

            if recurse_into_high_level_components or isinstance(
                cur, fundamental_component.FundamentalComponent
            ):
                to_do.extend(cur._iter_direct_children())

    def _iter_component_tree(self) -> Iterable[Component]:
        """
        Iterate over all components in the component tree, with this component as the root.
        """
        yield self

        if isinstance(self, fundamental_component.FundamentalComponent):
            for child in self._iter_direct_children():
                yield from child._iter_component_tree()
        else:
            build_result = self.session._weak_component_data_by_component[
                self
            ].build_result
            yield from build_result._iter_component_tree()

    async def _on_message(self, msg: Jsonable, /) -> None:
        raise RuntimeError(f"{type(self).__name__} received unexpected message `{msg}`")

    def _is_in_component_tree(self, cache: dict[rio.Component, bool]) -> bool:
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

        child_strings: list[str] = []
        for child in self._iter_direct_children():
            child_strings.append(f" {type(child).__name__}:{child._id}")

        if child_strings:
            result += " -" + "".join(child_strings)

        return result + ">"