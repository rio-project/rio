from __future__ import annotations

import enum
import functools
import inspect
import json
from typing import *  # type: ignore

import uniserde
from uniserde import Jsonable, JsonDoc

import rio

from . import color, inspection, maybes, session
from .components import component_base
from .self_serializing import SelfSerializing

__all__ = ["serialize_json", "serialize_and_host_component"]


T = TypeVar("T")
Serializer = Callable[["session.Session", T], Jsonable]


def _serialize_special_types(obj: object) -> Jsonable:
    try:
        func = maybes.TYPE_NORMALIZERS[type(obj)]
    except KeyError:
        raise TypeError(f"Can't serialize {obj!r} as JSON") from None

    return func(obj)  # type: ignore


def serialize_json(data: Jsonable) -> str:
    """
    Like `json.dumps`, but can also serialize numpy types.
    """
    return json.dumps(data, default=_serialize_special_types)


def serialize_and_host_component(component: rio.Component) -> JsonDoc:
    """
    Serializes the component, non-recursively. Children are serialized just by
    their `_id`.

    Non-fundamental components must have been built, and their output cached in
    the session.
    """
    result: JsonDoc = {
        "_python_type_": type(component).__name__,
        "_key_": component.key,
        "_rio_internal_": False,  # TODO
    }

    # Add layout properties, in a more succinct way than sending them
    # separately
    result["_margin_"] = (
        component.margin_left,
        component.margin_top,
        component.margin_right,
        component.margin_bottom,
    )
    result["_size_"] = (
        None if isinstance(component.width, maybes.STR_TYPES) else component.width,
        None if isinstance(component.height, maybes.STR_TYPES) else component.height,
    )
    result["_align_"] = (
        component.align_x,
        component.align_y,
    )
    result["_grow_"] = (
        component.width == "grow",
        component.height == "grow",
    )

    # If it's a fundamental component, serialize its state because JS needs it.
    # For non-fundamental components, there's no reason to send the state to
    # the frontend.
    if isinstance(component, component_base.FundamentalComponent):
        sess = component.session

        for name, serializer in get_attribute_serializers(type(component)).items():
            result[name] = serializer(sess, getattr(component, name))

        # Encode any internal additional state. Doing it this late allows the custom
        # serialization to overwrite automatically generated values.
        result["_type_"] = component._unique_id
        result.update(component._custom_serialize())

    else:
        # Take care to add underscores to any properties here, as the
        # user-defined state is also added and could clash
        result["_type_"] = "Placeholder"
        result["_child_"] = component.session._weak_component_data_by_component[
            component
        ].build_result._id

    return result


@functools.lru_cache(maxsize=None)
def get_attribute_serializers(
    cls: Type[component_base.Component],
) -> Mapping[str, Serializer]:
    """
    Returns a dictionary of attribute names to their types that should be
    serialized for the given component class.
    """
    serializers: Dict[str, Serializer] = {}

    for attr_name, annotation in inspection.get_type_annotations_raw(cls).items():
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
            "_rio_builtin_",
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

        # Annotation couldn't be eval'd? Then we can't serialize it.
        if isinstance(annotation, str):
            continue

        serializer = _get_serializer_for_annotation(annotation)
        if serializer is None:
            continue

        serializers[attr_name] = serializer

    return serializers


def _serialize_basic_json_value(sess: session.Session, value: Jsonable) -> Jsonable:
    return value


def _serialize_self_serializing(
    sess: session.Session, obj: SelfSerializing
) -> Jsonable:
    return obj._serialize(sess)


def _serialize_child_component(
    sess: session.Session, component: component_base.Component
) -> Jsonable:
    return component._id


def _serialize_list(
    sess: session.Session, list_: list[T], item_serializer: Serializer[T]
) -> Jsonable:
    return [item_serializer(sess, item) for item in list_]


def _serialize_enum(
    sess: session.Session, value: object, as_type: Type[enum.Enum]
) -> Jsonable:
    return uniserde.as_json(value, as_type=as_type)


def _serialize_colorset(sess: session.Session, colorset: color.ColorSet) -> Jsonable:
    return sess.theme._serialize_colorset(colorset)


def _serialize_optional(
    sess: session.Session, value: Optional[T], serializer: Serializer[T]
) -> Jsonable:
    if value is None:
        return None

    return serializer(sess, value)


def _get_serializer_for_annotation(annotation: type) -> Serializer | None:
    """
    Which values are serialized for state depends on the annotated
    datatypes. There is no point in sending fancy values over to the client
    which it can't interpret.

    This function looks at the annotation and returns a suitable serialization
    function, or `None` if this attribute shouldn't be serialized.
    """
    # Basic JSON values
    if annotation in (int, float, str, bool, None):
        return _serialize_basic_json_value

    if inspect.isclass(annotation):
        # Self-Serializing
        if issubclass(annotation, SelfSerializing):
            return _serialize_self_serializing

        # Components
        if issubclass(annotation, rio.Component):
            return _serialize_child_component

        # Enums
        if issubclass(annotation, enum.Enum):
            return functools.partial(_serialize_enum, as_type=annotation)

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Sequences of serializable values
    if origin is list:
        item_serializer = _get_serializer_for_annotation(args[0])
        if item_serializer is None:
            return None
        return functools.partial(_serialize_list, item_serializer=item_serializer)

    # Literal
    if origin is Literal:
        return _serialize_basic_json_value

    # ColorSet
    if origin is Union and set(args) == color._color_set_args:
        return _serialize_colorset

    # Optional
    if origin is Union and len(args) == 2 and type(None) in args:
        type_ = next(type_ for type_ in args if type_ is not type(None))
        serializer = _get_serializer_for_annotation(type_)
        if serializer is None:
            return None
        return functools.partial(_serialize_optional, serializer=serializer)

    return None
