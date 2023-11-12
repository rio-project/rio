from __future__ import annotations

import functools
import sys
import types
from typing import *  # type: ignore

from introspection import iter_subclasses, safe_is_subclass

from .components import component_base


@functools.lru_cache(maxsize=None)
def get_type_annotations_raw(cls: type) -> Mapping[str, Union[type, str]]:
    """
    Reimplementation of `typing.get_type_hints` because it has a stupid bug in
    python 3.10 where it dies if something is annotated as `dataclasses.KW_ONLY`.
    """
    type_hints: Dict[str, Union[type, str]] = {}

    for cls in cls.__mro__:
        for attr_name, annotation in vars(cls).get("__annotations__", {}).items():
            if attr_name in type_hints:
                continue

            if isinstance(annotation, ForwardRef):
                annotation = annotation.__forward_arg__

            if isinstance(annotation, (str, types.CodeType)):
                globs = vars(sys.modules[cls.__module__])
                try:
                    annotation = eval(annotation, globs)
                except NameError:
                    pass

            type_hints[attr_name] = annotation

    return type_hints


@functools.lru_cache(maxsize=None)
def get_type_annotations(cls: type) -> Mapping[str, type]:
    """
    Returns a dictionary of attribute names to their types for the given class.
    """
    annotations = get_type_annotations_raw(cls)

    for attr_name, annotation in annotations.items():
        if isinstance(annotation, str):
            raise ValueError(
                f"Failed to eval annotation for attribute {attr_name!r}: {annotation}"
            )

    return annotations  # type: ignore


@functools.lru_cache(maxsize=None)
def get_attributes_to_serialize(
    cls: Type[component_base.Component],
) -> Mapping[str, type]:
    """
    Returns a dictionary of attribute names to their types that should be
    serialized for the given component class.
    """
    result: Dict[str, type] = {}

    for attr_name, annotation in get_type_annotations_raw(cls).items():
        if attr_name in {
            "_",
            "_build_generation_",
            "_explicitly_set_properties_",
            "_id",
            "_init_signature_",
            "_session_",
            "_state_properties_",
            "_weak_builder_",
            "_state_bindings_initialized_",
            "align_x",
            "align_y",
            "grow_x",
            "grow_y",
            "height",
            "margin_bottom",
            "margin_left",
            "margin_right",
            "margin_top",
            "margin_x",
            "margin_y",
            "margin",
            "width",
        }:
            continue

        # Annotation couldn't be eval'd? Then we probably can't serialize it.
        if isinstance(annotation, str):
            continue

        result[attr_name] = annotation

    return result


@functools.lru_cache(maxsize=None)
def get_child_component_containing_attribute_names(
    cls: Type[component_base.Component],
) -> Collection[str]:
    attr_names: List[str] = []

    for attr_name, annotation in get_attributes_to_serialize(cls).items():
        origin = get_origin(annotation)
        if origin is None:
            origin = annotation

        args = get_args(annotation)

        if safe_is_subclass(origin, component_base.Component):
            attr_names.append(attr_name)
        elif origin is Union:
            if any(safe_is_subclass(arg, component_base.Component) for arg in args):
                attr_names.append(attr_name)
        elif origin is list:
            if any(safe_is_subclass(arg, component_base.Component) for arg in args):
                attr_names.append(attr_name)

    return tuple(attr_names)


@functools.lru_cache(maxsize=None)
def get_child_component_containing_attribute_names_for_builtin_components() -> (
    Mapping[str, Collection[str]]
):
    result = {
        cls._unique_id: get_child_component_containing_attribute_names(cls)  # type: ignore
        for cls in iter_subclasses(component_base.FundamentalComponent)  # type: ignore
        if cls._unique_id.endswith("-builtin")  # type: ignore
    }

    result.update(
        {
            "Placeholder": ["_child_"],
            "Align-builtin": ["child"],
            "Margin-builtin": ["child"],
        }
    )
    return result
