
from __future__ import annotations

import functools
import sys
from collections.abc import Collection, Sequence, Mapping
from typing import ForwardRef, Type, Union, get_origin, get_args

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
def get_child_widget_containing_attribute_names(cls: Type[widget_base.Widget]) -> Collection[str]:
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
        elif origin in (list, set, tuple, Sequence, Collection):
            if any(safe_is_subclass(arg, widget_base.Widget) for arg in args):
                attr_names.append(attr_name)
    
    return attr_names


@functools.lru_cache(maxsize=None)
def get_child_widget_containing_attribute_names_for_builtin_widgets() -> Mapping[str, Collection[str]]:
    result = {
        cls._unique_id: get_child_widget_containing_attribute_names(cls)
        for cls in iter_subclasses(widget_base.HtmlWidget)
        if cls._unique_id.endswith("-builtin")
    }

    result['Placeholder'] = ['_child_']
    return result
