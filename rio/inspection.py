from __future__ import annotations

import functools
import sys
from typing import *  # type: ignore

from introspection import iter_subclasses, safe_is_subclass

from .widgets import widget_base


@functools.lru_cache(maxsize=None)
def get_type_annotations(cls: type) -> Mapping[str, type]:
    """
    Reimplementation of `typing.get_type_hints` because it has a stupid bug in
    python 3.10 where it dies if something is annotated as `dataclasses.KW_ONLY`.
    """
    type_hints = {}

    for cls in cls.__mro__:
        for attr_name, annotation in vars(cls).get("__annotations__", {}).items():
            if attr_name in type_hints:
                continue

            if isinstance(annotation, ForwardRef):
                annotation = annotation.__forward_code__

            if isinstance(annotation, str):
                globs = vars(sys.modules[cls.__module__])
                annotation = eval(annotation, globs)

            type_hints[attr_name] = annotation

    return type_hints


@functools.lru_cache(maxsize=None)
def get_attributes_to_serialize(cls: Type[widget_base.Widget]) -> Mapping[str, Type]:
    """
    Returns a dictionary of attribute names to their types that should be
    serialized for the given widget class.
    """
    result = {}

    for attr_name, annotation in get_type_annotations(cls).items():
        if attr_name in {
            "_",
            "_build_generation_",
            "_explicitly_set_properties_",
            "_id",
            "_init_signature_",
            "_session_",
            "_state_properties_",
            "_weak_builder_",
            "_state_bindings_initialized",
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

        result[attr_name] = annotation

    return result


@functools.lru_cache(maxsize=None)
def get_child_widget_containing_attribute_names(
    cls: Type[widget_base.Widget],
) -> Collection[str]:
    attr_names = []

    for attr_name, annotation in get_type_annotations(cls).items():
        origin = get_origin(annotation)
        if origin is None:
            origin = annotation

        args = get_args(annotation)

        if safe_is_subclass(origin, widget_base.Widget):
            attr_names.append(attr_name)
        elif origin is Union:
            if any(safe_is_subclass(arg, widget_base.Widget) for arg in args):
                attr_names.append(attr_name)
        elif origin is list:
            if any(safe_is_subclass(arg, widget_base.Widget) for arg in args):
                attr_names.append(attr_name)

    return tuple(attr_names)


@functools.lru_cache(maxsize=None)
def get_child_widget_containing_attribute_names_for_builtin_widgets() -> (
    Mapping[str, Collection[str]]
):
    result = {
        cls._unique_id: get_child_widget_containing_attribute_names(cls)  # type: ignore
        for cls in iter_subclasses(widget_base.FundamentalWidget)
        if cls._unique_id.endswith("-builtin")  # type: ignore
    }

    result["Placeholder"] = ["_child_"]
    return result
