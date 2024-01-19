from __future__ import annotations

import dataclasses
import types
import weakref
from collections.abc import Callable
from typing import TYPE_CHECKING

import introspection.typing

if TYPE_CHECKING:
    from .components import Component


__all__ = ["StateProperty", "StateBinding"]


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

    def __init__(
        self,
        name: str,
        readonly: bool,
        raw_annotation: introspection.types.TypeAnnotation,
        module: types.ModuleType,
    ):
        self.name = name
        self.readonly = readonly

        self._module = module
        self._raw_annotation = raw_annotation
        self._resolved_annotation: introspection.types.TypeAnnotation

    def _annotation_as_string(self) -> str:
        if isinstance(self._raw_annotation, str):
            return self._raw_annotation

        return introspection.typing.annotation_to_string(self._raw_annotation)

    def __get__(
        self,
        instance: Component | None,
        owner: type | None = None,
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

        instance._session_._register_dirty_component(
            instance,
            include_children_recursively=False,
        )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name}>"


@dataclasses.dataclass(eq=False)
class StateBinding:
    # Weak reference to the component containing this binding
    owning_component_weak: Callable[[], Component | None]

    # The state property whose value this binding is
    owning_property: StateProperty

    # Each binding is either the root-most binding, or a child of another
    # binding. This value is True if this binding is the root.
    is_root: bool

    parent: StateBinding | None
    value: object | None

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
        to_do: list[StateBinding] = [self]

        while to_do:
            cur = to_do.pop()
            owning_component = cur.owning_component_weak()

            if owning_component is not None:
                owning_component._session_._register_dirty_component(
                    owning_component,
                    include_children_recursively=False,
                )

            to_do.extend(cur.children)
