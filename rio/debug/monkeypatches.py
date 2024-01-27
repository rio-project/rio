import functools
import inspect
import warnings
from pathlib import Path

import introspection.typing

from .. import global_state
from ..components.component import Component, ComponentMeta, StateProperty

__all__ = [
    "apply_monkeypatches",
]


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

    # Track whether this instance is internal to Rio. This is the case if
    # this component's creator is defined in Rio.
    creator = global_state.currently_building_component
    if creator is None:
        assert type(component).__qualname__ == "HighLevelRootComponent", type(
            component
        ).__qualname__
        component._rio_internal_ = True
    else:
        component._rio_internal_ = creator._rio_builtin_

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
            annotation = self._resolved_annotation
        except AttributeError:
            annotation = introspection.typing.resolve_forward_refs(
                self._raw_annotation,
                self._module,
                mode="ast",
                strict=False,
                treat_name_errors_as_imports=True,
            )
            self._resolved_annotation = annotation

        try:
            valid = introspection.typing.is_instance(
                value, annotation, forward_ref_context=self._module
            )
        except NotImplementedError:
            warnings.warn(
                f"Unable to verify assignment to"
                f" {type(instance).__qualname__}.{self.name} (annotated as"
                f" {self._annotation_as_string()})"
            )
        else:
            if not valid:
                raise TypeError(
                    f"The value {value!r} can't be assigned to"
                    f" {type(instance).__qualname__}.{self.name}, which is"
                    f" annotated as {self._annotation_as_string()}"
                )

    wrapped_method(self, instance, value)
