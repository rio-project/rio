import functools
import inspect
import warnings
from pathlib import Path

import introspection.typing

from ..common import ForwardReference
from ..components.component_base import Component, ComponentMeta, StateProperty

__all__ = ["apply_monkeypatches"]


def apply_monkeypatches() -> None:
    ComponentMeta.__call__ = functools.partialmethod(
        ComponentMeta_call, ComponentMeta.__call__
    )  # type: ignore[wtf]

    Component.__getattribute__ = Component_getattribute

    StateProperty.__set__ = functools.partialmethod(
        StateProperty_set, StateProperty.__set__
    )  # type: ignore[wtf]


def ComponentMeta_call(cls, wrapped_method, *args, **kwargs):
    component: Component = wrapped_method(cls, *args, **kwargs)

    # Keep track of who created this component
    caller = inspect.stack()[1]
    component._creator_stackframe_ = (Path(caller.filename), caller.lineno)

    return component


def Component_getattribute(self, attr_name: str):
    # Make sure that no component `__init__` tries to read a state property.
    # This would be incorrect because state bindings are not yet initialized at
    # that point.

    # fmt: off
    if (
        attr_name in type(self)._state_properties_ and
        not object.__getattribute__(self, "_state_bindings_initialized_")
    ):
        # fmt: on
        raise Exception(
            "You have attempted to read a state property in a component's"
            " `__init__` method. This is not allowed because state"
            " bindings are not yet initialized at that point. Please"
            " move this code into the `__post_init__` method."
        )

    return object.__getattribute__(self, attr_name)


def StateProperty_set(
    self: StateProperty,
    wrapped_method,
    instance: Component,
    value: object,
):
    # Type check the value
    if not isinstance(value, StateProperty):
        try:
            evaluated_annotation = self._evaluated_annotation
        except AttributeError:
            if isinstance(self.annotation, ForwardReference):
                evaluated_annotation = (
                    self._evaluated_annotation
                ) = self.annotation.evaluate()
            else:
                evaluated_annotation = self._evaluated_annotation = self.annotation

        try:
            valid = introspection.typing.is_instance(value, evaluated_annotation)
        except NotImplementedError:
            warnings.warn(
                f"Unable to verify assignment to"
                f" {type(instance).__qualname__}.{self.name} (annotated as"
                f" {introspection.typing.annotation_to_string(evaluated_annotation)})"
            )
        else:
            if not valid:
                raise TypeError(
                    f"The value {value!r} can't be assigned to"
                    f" {type(instance).__qualname__}.{self.name}, which is"
                    f" annotated as"
                    f" {introspection.typing.annotation_to_string(evaluated_annotation)}"
                )

    wrapped_method(self, instance, value)
