from __future__ import annotations

import functools
import sys
import types
from typing import *  # type: ignore

from introspection import iter_subclasses, safe_is_subclass

from . import serialization
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
def get_child_component_containing_attribute_names(
    cls: Type[component_base.Component],
) -> Collection[str]:
    attr_names: List[str] = []

    for attr_name, serializer in serialization.get_attribute_serializers(cls).items():
        # : Component
        if serializer is serialization._serialize_child_component:
            attr_names.append(attr_name)
        elif isinstance(serializer, functools.partial):
            # : Optional[Component]
            if (
                serializer.func is serialization._serialize_optional
                and serializer.keywords["serializer"]
                is serialization._serialize_child_component
            ):
                attr_names.append(attr_name)
            # : List[Component]
            elif (
                serializer.func is serialization._serialize_list
                and serializer.keywords["item_serializer"]
                is serialization._serialize_child_component
            ):
                attr_names.append(attr_name)

    return tuple(attr_names)


@functools.lru_cache(maxsize=None)
def get_child_component_containing_attribute_names_for_builtin_components() -> (
    Mapping[str, Collection[str]]
):
    result = {
        cls._unique_id: get_child_component_containing_attribute_names(cls)
        for cls in iter_subclasses(component_base.FundamentalComponent)
        if cls._unique_id.endswith("-builtin")
    }

    result.update(
        {
            "Placeholder": ["_child_"],
            "Align-builtin": ["child"],
            "Margin-builtin": ["child"],
        }
    )
    return result
