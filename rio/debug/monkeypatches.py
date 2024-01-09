import functools
import inspect
from pathlib import Path

from ..components.component_base import Component, ComponentMeta

__all__ = ["apply_monkeypatches"]


def apply_monkeypatches() -> None:
    ComponentMeta.__call__ = functools.partialmethod(
        ComponentMeta_call, ComponentMeta.__call__
    )  # type: ignore

    Component.__getattribute__ = Component_getattribute


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
