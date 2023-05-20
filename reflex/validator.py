import copy
from dataclasses import dataclass
from pprint import pprint
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union

import reflex as rx

from . import messages
from .common import Jsonable

# Given a widget type, this dict contains the attribute names which contain
# children / child ids
_CHILD_ATTRIBUTE_NAMES: Dict[str, Set[str]] = {
    "text": set(),
    "row": {"children"},
    "column": {"children"},
    "rectangle": {"child"},
    "stack": {"children"},
    "margin": {"child"},
    "align": {"child"},
    "mouseEventListener": {"child"},
    "textInput": set(),
    "override": {"child"},
    "placeholder": {"_child_"},
}


@dataclass
class ClientWidget:
    id: int
    type: str
    state: Dict[str, Jsonable]

    @classmethod
    def from_json(cls, id: int, delta_state: Dict[str, Jsonable]) -> "ClientWidget":
        # Don't modify the original dict
        delta_state = copy.deepcopy(delta_state)

        # Get the widget type
        try:
            type = delta_state.pop("_type_")
        except KeyError:
            raise ValidationError(f"Widget with id `{id}` is missing `_type_` field")

        if not isinstance(type, str):
            raise ValidationError(f"Widget with id `{id}` has non-string type `{type}`")

        if type not in _CHILD_ATTRIBUTE_NAMES:
            raise ValidationError(f"Widget with id `{id}` has unknown type `{type}`")

        # Construct the result
        return cls(
            id=id,
            type=type,
            state=delta_state,
        )

    @property
    def non_child_containing_properties(
        self,
    ) -> Dict[str, Jsonable]:
        child_attribute_names = _CHILD_ATTRIBUTE_NAMES[self.type]

        result = {}
        for name, value in self.state.items():
            if name in child_attribute_names:
                continue

            result[name] = value

        return result

    @property
    def child_containing_properties(
        self,
    ) -> Dict[str, Union[None, int, List[int]]]:
        child_attribute_names = _CHILD_ATTRIBUTE_NAMES[self.type]

        result = {}
        for name, value in self.state.items():
            if name not in child_attribute_names:
                continue

            result[name] = value

        return result

    @property
    def referenced_child_ids(self) -> Iterable[int]:
        for property_value in self.child_containing_properties.values():
            if property_value is None:
                continue

            if isinstance(property_value, int):
                yield property_value
                continue

            assert isinstance(property_value, list), property_value
            yield from property_value


class ValidationError(Exception):
    pass


class Validator:
    def __init__(self):
        self.root_widget: Optional[ClientWidget] = None
        self.widgets_by_id: Dict[int, ClientWidget] = {}

    def prune_widgets(self) -> None:
        """
        Remove all widgets which are not referenced directly or indirectly by
        the root widget.
        """
        # If there is no root widget, everybody is an orphan
        if self.root_widget is None:
            self.widgets_by_id.clear()
            return

        # Find all widgets which are referenced directly or indirectly by the
        # root widget
        visited_ids: Set[int] = set()

        to_do = [self.root_widget]

        while to_do:
            current = to_do.pop()

            # TODO Use this opportunity to detect cycles?
            if current.id in visited_ids:
                print(
                    f"Warning: Validator found a cycle in the widget tree involving widget with id `{current.id}`"
                )
                continue

            # Mark the current widget as visited
            visited_ids.add(current.id)

            # Chain to its children
            for child_id in current.referenced_child_ids:
                to_do.append(self.widgets_by_id[child_id])

        # Remove all superfluous widgets
        self.widgets_by_id = {
            id: widget for id, widget in self.widgets_by_id.items() if id in visited_ids
        }

    def as_json(self, widget: Optional[ClientWidget] = None) -> Dict[str, Jsonable]:
        if widget is None:
            assert self.root_widget is not None
            widget = self.root_widget

        result = {
            "_type_": widget.type,
            "_id_": widget.id,
        }

        for name, value in widget.non_child_containing_properties.items():
            result[name] = value

        for name, value in widget.child_containing_properties.items():
            if value is None:
                result[name] = None
                continue

            if isinstance(value, int):
                result[name] = self.as_json(self.widgets_by_id[value])
                continue

            assert isinstance(value, list), value
            result[name] = [self.as_json(self.widgets_by_id[id]) for id in value]

        return result

    async def handle_incoming_message(self, msg: messages.IncomingMessage) -> None:
        # Delegate to the appropriate handler
        handler_name = f"_handle_incoming_{type(msg).__name__}"

        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            return

        await handler(msg)

    async def handle_outgoing_message(self, msg: messages.OutgoingMessage) -> None:
        # Delegate to the appropriate handler
        handler_name = f"_handle_outgoing_{type(msg).__name__}"

        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            return

        await handler(msg)

    async def _handle_outgoing_UpdateWidgetStates(
        self,
        msg: messages.UpdateWidgetStates,
    ) -> None:
        # Update the individual widget states
        for widget_id, delta_state in msg.delta_states.items():
            # Get the widget's existing state
            try:
                widget = self.widgets_by_id[widget_id]
            except KeyError:
                widget = ClientWidget.from_json(widget_id, delta_state)
                self.widgets_by_id[widget_id] = widget
            else:
                delta_state = delta_state.copy()

                # A widget's `_type_` cannot be modified. This value is also
                # stored separately by `ClientWidget`, so make sure it never
                # makes it into the widget's state.
                try:
                    new_type = delta_state.pop("_type_")
                except KeyError:
                    pass
                else:
                    if new_type != widget.type:
                        raise ValidationError(
                            f"Attempted to modify the `_type_` for widget with id `{widget_id}` from `{widget.type}` to `{new_type}`"
                        ) from None

                # Update the widget's state
                widget.state.update(delta_state)

        # Update the root widget if requested
        if msg.root_widget_id is not None:
            try:
                self.root_widget = self.widgets_by_id[msg.root_widget_id]
            except KeyError:
                raise ValidationError(
                    f"Attempted to set root widget to unknown widget with id `{msg.root_widget_id}`"
                ) from None

        # If no root widget is known yet, this message has to contain one
        if self.root_widget is None:
            raise ValidationError(
                "Despite no root widget being known yet, an `UpdateWidgetStates` message was sent without a `root_widget_id`",
            )

        # Make sure no invalid widget references are present
        for widget in self.widgets_by_id.values():
            for child_id in widget.referenced_child_ids:
                if child_id not in self.widgets_by_id:
                    raise ValidationError(
                        f"Widget with id `{widget.id}` references unknown widget with id `{child_id}`"
                    )

        # Prune the widget tree
        self.prune_widgets()
