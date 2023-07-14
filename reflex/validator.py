import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Union

import reflex.widgets.metadata

from . import messages, session
from .common import Jsonable

__all__ = [
    "ClientWidget",
    "ValidationError",
    "Validator",
]


@dataclass
class ClientWidget:
    id: int
    type: str
    state: Dict[str, Jsonable]

    @classmethod
    def from_json(
        cls,
        id: int,
        delta_state: Dict[str, Jsonable],
        registered_html_widgets: Set[str],
    ) -> "ClientWidget":
        # Don't modify the original dict
        delta_state = copy.deepcopy(delta_state)

        # Get the widget type
        try:
            type = delta_state.pop("_type_")
        except KeyError:
            raise ValidationError(f"Widget with id `{id}` is missing `_type_` field")

        if not isinstance(type, str):
            raise ValidationError(f"Widget with id `{id}` has non-string type `{type}`")

        if (
            type not in reflex.widgets.metadata.CHILD_ATTRIBUTE_NAMES
            and type not in registered_html_widgets
        ):
            raise ValidationError(f"Widget with id `{id}` has unknown type `{type}`")

        # Construct the result
        return cls(
            id=id,
            type=type,
            state=delta_state,
        )

    def _get_child_attribute_names(self) -> Iterable[str]:
        try:
            return reflex.widgets.metadata.CHILD_ATTRIBUTE_NAMES[self.type]
        except KeyError:
            return tuple()  # TODO: How to get the children of HTML widgets?

    @property
    def non_child_containing_properties(
        self,
    ) -> Dict[str, Jsonable]:
        child_attribute_names = self._get_child_attribute_names()

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
        child_attribute_names = self._get_child_attribute_names()

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
    def __init__(
        self,
        session_: session.Session,
        *,
        dump_directory_path: Optional[Path] = None,
    ):
        self.session = session_

        if dump_directory_path is not None:
            assert dump_directory_path.exists(), dump_directory_path
            assert dump_directory_path.is_dir(), dump_directory_path

        self.dump_directory_path = dump_directory_path

        self.root_widget: Optional[ClientWidget] = None
        self.widgets_by_id: Dict[int, ClientWidget] = {}

        # HTML widgets must be registered with the frontend before use. This set
        # contains the ids (`HtmlWidget._unique_id`) of all registered widgets.
        self.registered_html_widgets: Set[str] = set(
            reflex.widgets.metadata.CHILD_ATTRIBUTE_NAMES.keys()
        )

    def dump_message(
        self,
        msg: Union[messages.IncomingMessage, messages.OutgoingMessage],
    ):
        """
        Dump the message to a JSON file.

        If no path is set in the validator, this function does nothing.
        """
        if self.dump_directory_path is None:
            return

        direction = (
            "incoming" if isinstance(msg, messages.IncomingMessage) else "outgoing"
        )
        path = self.dump_directory_path / f"message-{direction}.json"

        with open(path, "w") as f:
            json.dump(
                msg.as_json(),
                f,
                indent=4,
            )

    def dump_client_state(
        self,
        widget: Optional[ClientWidget] = None,
        path: Optional[Path] = None,
    ) -> None:
        """
        Dump the client state to a JSON file.

        If no widget is specified, the root widget is used.

        If no path is used the Validator's `dump_client_state_path` is used. If
        no path is used and no path set in the validator, this function does
        nothing.
        """
        if path is None and self.dump_directory_path is not None:
            path = self.dump_directory_path / "client-state.json"

        if path is None:
            return

        if widget is None:
            assert self.root_widget is not None
            widget = self.root_widget

        with open(path, "w") as f:
            json.dump(
                self.as_json(widget),
                f,
                indent=4,
                # The keys are intentionally in a legible order. Don't destroy
                # that.
                sort_keys=False,
            )

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
        """
        Return a JSON-serializable representation of the client state.
        """

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

    def handle_incoming_message(self, msg: messages.IncomingMessage) -> None:
        """
        Process a message passed from Client -> Server.

        This will update the `Validator`'s internal client state and validate
        the message, raising a `ValidationError` if any issues are detected.
        """

        # Delegate to the appropriate handler
        handler_name = f"_handle_incoming_{type(msg).__name__}"

        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            return

        handler(msg)

    def handle_outgoing_message(self, msg: messages.OutgoingMessage) -> None:
        """
        Process a message passed from Server -> Client.

        This will update the `Validator`'s internal client state and validate
        the message, raising a `ValidationError` if any issues are detected.
        """

        # Delegate to the appropriate handler
        handler_name = f"_handle_outgoing_{type(msg).__name__}"

        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            return

        handler(msg)

    def _handle_outgoing_UpdateWidgetStates(
        self,
        msg: messages.UpdateWidgetStates,
    ) -> None:
        # Dump the message, if requested
        self.dump_message(msg)

        # Update the individual widget states
        for widget_id, delta_state in msg.delta_states.items():
            # Get the widget's existing state
            try:
                widget = self.widgets_by_id[widget_id]
            except KeyError:
                widget = ClientWidget.from_json(
                    widget_id,
                    delta_state,
                    self.registered_html_widgets,
                )
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
        invalid_references = {}
        for widget in self.widgets_by_id.values():
            for child_id in widget.referenced_child_ids:
                if child_id not in self.widgets_by_id:
                    invalid_references.setdefault(widget.id, []).append(child_id)

        if invalid_references:
            raise ValidationError(
                f"Invalid widget references detected: {invalid_references}"
            )

        # Make sure all widgets in the session have had their session injected
        for widget in self.session.root_widget._iter_direct_and_indirect_children(
            include_self=True
        ):
            if widget._session_ is None:
                raise ValidationError(
                    f"Widget `{widget}` has not had its session injected"
                )

        # Prune the widget tree
        self.prune_widgets()

        # Look for any widgets which were sent in the message, but are not
        # actually used in the widget tree
        ids_sent = set(msg.delta_states.keys())
        ids_existing = set(self.widgets_by_id.keys())
        ids_superfluous = sorted(ids_sent - ids_existing)

        if ids_superfluous:
            print(
                f"Validator Warning: Message contained superfluous widget ids: {ids_superfluous}"
            )

        # Dump the client state if requested
        self.dump_client_state()

    def _handle_outgoing_EvaluateJavascript(self, msg: messages.EvaluateJavascript):
        # Is this message registering a new widget class?
        match = re.search(r"window.widgetClasses\['(.*)'\]", msg.javascript_source)

        if match is None:
            return

        # Remember the widget class as registered
        self.registered_html_widgets.add(match.group(1))
