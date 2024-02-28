import inspect
import warnings
from pathlib import Path

import introspection.typing

from .. import components, global_state
from ..components.component import Component, ComponentMeta
from ..state_properties import PleaseTurnThisIntoAStateBinding, StateProperty

__all__ = [
    "apply_monkeypatches",
]


def apply_monkeypatches() -> None:
    introspection.wrap_method(ComponentMeta_call, ComponentMeta, "__call__")
    introspection.wrap_method(StateProperty_get, StateProperty, "__get__")
    introspection.wrap_method(StateProperty_set, StateProperty, "__set__")
    introspection.wrap_method(ListView_init, components.ListView, "__init__")


def ComponentMeta_call(wrapped_method, cls, *args, **kwargs):
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


def StateProperty_get(
    wrapped_method,
    self: StateProperty,
    instance: Component | None,
    owner=None,
):
    if instance is None:
        return self

    if not instance._init_called_:
        raise RuntimeError(
            f"The `__init__` method of {instance} attempted to access the state"
            f" property {self.name!r}. This is not allowed. `__init__` methods"
            f" must only *set* properties, not *read* them. Move the code that"
            f" needs to read a state property into the `__post_init__` method."
        )

    return wrapped_method(self, instance, owner)


def StateProperty_set(
    wrapped_method,
    self: StateProperty,
    instance: Component,
    value: object,
):
    # Type check the value
    if not isinstance(value, PleaseTurnThisIntoAStateBinding):
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

    # Chain to the original method
    wrapped_method(self, instance, value)


def ListView_init(
    wrapped_method,
    self: components.ListView,
    *children,
    **kwargs,
):
    # Make sure all children have a key set
    assert isinstance(children, tuple), children

    for child in children:
        if child.key != None or isinstance(child, components.SeparatorListItem):
            continue

        raise ValueError(
            f"ListView child {child!r} has no key set. List items change frequently, and are often reshuffled. This can lead to unexpected reconciliations, and slow down the UI."
        )

    # Chain to the original method
    wrapped_method(self, *children, **kwargs)
