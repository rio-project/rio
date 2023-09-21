from __future__ import annotations

from dataclasses import dataclass
from typing import *  # type: ignore

import uniserde
from uniserde import Jsonable

import reflex as rx
import reflex.inspection
from reflex.widgets.widget_base import FundamentalWidget

DUMP_PATH = rx.common.PROJECT_ROOT_DIR / "tree-dump.json"


__all__ = [
    "Attribute",
    "Widget",
    "dump_tree",
    "TreeDump",
]


@uniserde.as_child
@dataclass
class Attribute:
    name: str
    type: str
    value: str | List[int]
    bound_to: Optional[Tuple[str, str]]


@dataclass
class Widget(uniserde.Serde):
    id: int
    type: str
    parent: Optional[int]
    builder: Optional[int]
    attributes: List[Attribute]


@dataclass
class TreeDump(uniserde.Serde):
    widgets: List[Widget]


# def _get_attr_value(attr_value: Any) -> Union[str, List[int]]:
#     if prop.name in child_containing_attribute_names:
#         if attr_value is None:
#             attr_children = []
#         elif isinstance(attr_value, rx.Widget):
#             attr_children = [attr_value]
#         elif isinstance(attr_value, (list, tuple)):
#             attr_children = attr_value
#         elif isinstance(attr_value, dict):
#             attr_children = attr_value.values()
#         else:
#             raise NotImplementedError(
#                 f"Unsupported type for attribute {prop.name}: {type(attr_value)}"
#             )

#         attr_value = [child._id for child in attr_children]
#     else:
#         attr_value = str(attr_value)


def _dump_worker(
    sess: rx.Session,
    widget: rx.Widget,
    parent: Optional[int],
    builder: Optional[int],
) -> Iterable[Widget]:
    # Fetch all of the widget's attributes
    attributes: List[Attribute] = []
    # child_containing_attribute_names = (
    #     reflex.inspection.get_child_widget_containing_attribute_names(type(widget))
    # )

    for prop in type(widget)._state_properties_.values():
        raw_attr_value = prop.__get__(widget, None)

        attributes.append(
            Attribute(
                name=prop.name,
                type="TODO-type",
                # value=_get_attr_value(raw_attr_value),
                value=str(raw_attr_value),
                bound_to=None,  # TODO
            )
        )

    # For fundamental widgets, all children are in the tree and need to be
    # processed. For non-fundamental widgets, fetch the build result
    if isinstance(widget, FundamentalWidget):
        children = list(widget._iter_direct_children())
        child_builder = builder
    else:
        widget_data = sess._lookup_widget_data(widget)
        children = [widget_data.build_result]
        child_builder = widget._id

    # Process all children recursively
    for child in children:
        yield from _dump_worker(
            sess=sess,
            widget=child,
            parent=widget._id,
            builder=child_builder,
        )

    # Instantiate the result
    yield Widget(
        id=widget._id,
        type=type(widget).__name__,
        parent=parent,
        builder=builder,
        attributes=attributes,
    )


def dump_tree(sess: rx.Session) -> TreeDump:
    # Make sure there are no pending changes
    sess._refresh_sync()

    # Dump all widgets
    widgets = list(
        _dump_worker(
            sess=sess,
            widget=sess._root_widget,
            parent=None,
            builder=None,
        )
    )

    # Instantiate the result
    return TreeDump(
        widgets=widgets,
    )
