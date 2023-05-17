from __future__ import annotations

import logging
import typing
import weakref
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Literal, Tuple, Type, Union

from fastapi import WebSocket

import web_gui as wg

from . import messages
from .common import Jsonable
from .styling import *
from .widgets import fundamentals


@dataclass
class WidgetData:
    previous_build_result: wg.Widget


class WontSerialize(Exception):
    pass


class Session:
    def __init__(self, root_widget: wg.Widget, websocket: WebSocket):
        self.root_widget = root_widget
        self.websocket = websocket

        # Weak dictionaries to hold additional information about widgets. These
        # are split in two to avoid the dictionaries keeping the widgets alive.
        # Notice how both dictionaries are weak on the actual widget.
        #
        # Never access these directly. Instead, use helper functions
        # - `lookup_widget`
        # - `lookup_widget_id`
        self._weak_widgets_by_id: weakref.WeakValueDictionary[
            int, wg.Widget
        ] = weakref.WeakValueDictionary()

        self._weak_widget_data_by_widget: weakref.WeakKeyDictionary[
            wg.Widget, WidgetData
        ] = weakref.WeakKeyDictionary()

        # Keep track of all dirty widgets, once again, weakly
        self._dirty_widgets: weakref.WeakSet[wg.Widget] = weakref.WeakSet()

    def lookup_widget_data(self, widget: wg.Widget) -> WidgetData:
        """
        Returns the widget data for the given widget. Raises `KeyError` if no
        data is present for the widget.
        """
        try:
            return self._weak_widget_data_by_widget[widget]
        except KeyError:
            raise KeyError(widget) from None

    def lookup_widget(self, widget_id: int) -> wg.Widget:
        """
        Returns the widget and its data for the given widget ID. Raises
        `KeyError` if no widget is present for the ID.
        """
        return self._weak_widgets_by_id[widget_id]

    def register_dirty_widget(self, widget: wg.Widget) -> None:
        self._dirty_widgets.add(widget)

    async def refresh(self) -> None:
        """
        Make sure the session state is up to date. Specifically:

        - Call build on all widgets marked as dirty
        - Recursively do this for all freshly spawned widgets
        - mark all widgets as clean

        Thus the session is up to date and ready for display to the user after
        this method returns.
        """
        # If nothing is dirty just return. While the loop below wouldn't do
        # anything anyway, this avoids sending a message to the client.
        if not self._dirty_widgets:
            return

        # Build all dirty widgets
        #
        # TODO: Start this at the root widget and continue recursively, to avoid
        #       building widgets that are about to be replaced by their parents
        #       rebuilding.
        while self._dirty_widgets:
            widget = self._dirty_widgets.pop()

            # Inject the session into the widget
            widget._session = self

            # Keep track of this widget's existance
            self._weak_widgets_by_id[widget._id] = widget

            # Fundamental widgets require little treatment
            if isinstance(widget, fundamentals.FundamentalWidget):
                self._dirty_widgets.update(widget._iter_direct_children())

            # Others need to be built
            else:
                build_result = widget.build()

                # Has this widget been built before?
                try:
                    widget_data = self.lookup_widget_data(widget)

                # No, this is the first time
                except KeyError:
                    widget_data = WidgetData(build_result)
                    self._weak_widget_data_by_widget[widget] = widget_data
                    self._weak_widgets_by_id[widget._id] = widget

                # Yes, rescue state
                else:
                    widget_data.previous_build_result = build_result
                    self.rescue_state(widget_data.previous_build_result, build_result)

                # Inject the building widget into the state bindings of all
                # generated widgets
                for child in build_result._iter_direct_and_indirect_children(True):
                    child_vars = vars(child)

                    for state_property in child._dirty_properties:
                        value = child_vars[state_property.name]

                        if (
                            isinstance(value, fundamentals.StateBinding)
                            and value.widget is None
                        ):
                            value.widget = widget

                # Any freshly spawned widgets are dirty
                self._dirty_widgets.add(build_result)

            # As the widget has just been processed, its properties are no
            # longer dirty
            widget._dirty_properties.clear()

        # Send the new state to the client if necessary
        msg = messages.ReplaceWidgets(self._serialize_widget(self.root_widget))
        await self.send_message(msg)

    def _serialize_value(self, value: Any, type_: Type) -> Jsonable:
        """
        Which values are serialized for state depends on the annotated datatypes.
        There is no point in sending fancy values over to the client which it can't
        interpret.

        This function attempts to serialize the value, or raises a `WontSerialize`
        exception if this value shouldn't be included in the state.
        """
        origin = typing.get_origin(type_)
        args = typing.get_args(type_)

        # Explicit check for some types. These don't play nice with `isinstance` and
        # similar methods
        if value is Callable:
            raise WontSerialize()

        # Basic JSON values
        if type_ in (bool, int, float, str):
            return value

        # Tuples or lists of serializable values
        if origin is tuple or origin is list:
            return [self._serialize_value(v, args[0]) for v in value]

        # Special case: `FillLike`
        #
        # TODO: Is there a nicer way to detect these?
        if (
            origin is Union
            and len(args) == 2
            and (args[0] is Fill or args[1] is Fill)
            and (args[0] is Color or args[1] is Color)
        ):
            value = Fill._try_from(value)
            return value._serialize()

        # Colors
        if type_ is Color:
            return value.rgba

        # Optional / Union
        if origin is Union:
            if value is None:
                return None

            for arg in args:
                # Callable doesn't play nice with `isinstance`
                if isinstance(arg, Callable) and callable(value):
                    raise WontSerialize()

                if arg is float and isinstance(value, int):
                    return value

                if isinstance(value, arg):  # type: ignore
                    return self._serialize_value(value, arg)

            assert False, f'Value "{value}" is not of any of the union types {args}'

        # Literal
        if origin is Literal:
            return self._serialize_value(value, type(value))

        # Widgets
        if fundamentals.is_widget_class(type_):
            return self._serialize_widget(value)

        # Invalid type
        raise WontSerialize()

    def _serialize_widget(self, widget: wg.Widget) -> Jsonable:
        """
        Recursively serialize a widget and all of its children.

        Fundamental widgets are serialized as expected. Non-fundamental widgets
        must be built, and thus be present in the session's dictionary caches.
        They are serialized as the fundamental widgets that result when built.
        """

        # Get the effective fundamental widget to serialize
        fundamental_widget = widget

        while not isinstance(fundamental_widget, fundamentals.FundamentalWidget):
            widget_data = self.lookup_widget_data(fundamental_widget)
            fundamental_widget = widget_data.previous_build_result

        # Serialize the obtained fundamental widget
        type_name = type(fundamental_widget).__name__
        type_name_camel_case = type_name[0].lower() + type_name[1:]

        result = {
            "id": fundamental_widget._id,  # TODO: Avoid name clashes
            "type": type_name_camel_case,  # TODO: Avoid name clashes
        }

        result.update(fundamental_widget._custom_serialize())

        for name, type_ in typing.get_type_hints(type(fundamental_widget)).items():
            # Skip some values
            if name in ("_",):  # Used to mark keyword-only arguments in dataclasses
                continue

            # Let the serialization function handle the value
            try:
                result[name] = self._serialize_value(
                    getattr(fundamental_widget, name), type_
                )
            except WontSerialize:
                pass

        return result

    async def handle_message(self, msg: messages.IncomingMessage) -> None:
        """
        Handle a message from the client. This is the main entry point for
        messages from the client.
        """
        try:
            widget_id = msg.widget_id  # type: ignore
        except AttributeError:
            raise NotImplementedError("Encountered message without widget ID")

        try:
            widget = self.lookup_widget(widget_id)
        except KeyError:
            logging.warn(
                f"Encountered message for unknown widget {widget_id}. (The widget might have been deleted in the meantime.)"
            )
            return

        await widget._handle_message(msg)

    async def send_message(self, msg: messages.OutgoingMessage) -> None:
        """
        Send a message to the client. This is the main entry point for messages
        to the client.
        """
        await self.websocket.send_json(msg.as_json())

    def rescue_state(self, old_build: wg.Widget, new_build: wg.Widget) -> None:
        # for old_widget, new_widget in self.find_widget_pairs_to_rescue(old_build, new_build):

        pass

    def find_widget_pairs_to_rescue_state(
        self, old_build: wg.Widget, new_build: wg.Widget
    ) -> Iterable[Tuple[wg.Widget, wg.Widget]]:
        old_widgets_by_key: Dict[str, wg.Widget] = {}
        new_widgets_by_key: Dict[str, wg.Widget] = {}

        matches_by_topology: List[Tuple[wg.Widget, wg.Widget]] = []

        # First scan all widgets for topological matches, and also keep track of
        # each widget by its key
        def key_scan(
            widgets_by_key: Dict[str, wg.Widget],
            widget: wg.Widget,
        ) -> None:
            if widget.key is not None:
                if widget.key in widgets_by_key:
                    raise RuntimeError(
                        f'Multiple widgets share the key "{widget.key}": {widgets_by_key[widget.key]} and {widget}'
                    )

                widgets_by_key[widget.key] = widget

            for child in widget._iter_direct_children():
                key_scan(widgets_by_key, child)

        def chain_to_children(
            old_widget: wg.Widget,
            new_widget: wg.Widget,
        ) -> None:
            for name, typ in typing.get_type_hints(self.__class__).items():
                origin, args = typing.get_origin(typ), typing.get_args(typ)

                # Remap directly contained widgets
                if fundamentals.is_widget_class(origin):
                    worker(
                        getattr(old_widget, name),
                        getattr(new_widget, name),
                    )

                # Iterate over lists of widgets, remapping their values
                elif origin is list and fundamentals.is_widget_class(args[0]):
                    old_children = getattr(old_widget, name)
                    new_children = getattr(new_widget, name)

                    common = min(len(old_children), len(new_children))
                    for old_child, new_child in zip(old_children, new_children):
                        worker(old_child, new_child)

                    for old_child in old_children[common:]:
                        key_scan(old_widgets_by_key, old_child)

                    for new_child in new_children[common:]:
                        key_scan(new_widgets_by_key, new_child)

                # TODO: What about other containers

        def worker(old_widget: wg.Widget, new_widget: wg.Widget) -> None:
            # Do the widget types match?
            if type(old_widget) is type(new_widget):
                matches_by_topology.append((old_widget, new_widget))

                # If the widget is fundamental, chain down
                if isinstance(old_widget, fundamentals.FundamentalWidget):
                    chain_to_children(old_widget, new_widget)
                    return

            # Otherwise neither they, nor their children can be topological
            # matches.  Just keep track of the children's keys.
            key_scan(old_widgets_by_key, old_widget)
            key_scan(new_widgets_by_key, new_widget)

        worker(old_build, new_build)

        # Find matches by key. These take priority over topological matches.
        key_matches = old_widgets_by_key.keys() & new_widgets_by_key.keys()

        for key in key_matches:
            yield old_widgets_by_key[key], new_widgets_by_key[key]

        # Yield topological matches, taking care to not those matches which were
        # already matched by key.
        for old_widget, new_widget in matches_by_topology:
            if old_widget.key in key_matches or new_widget.key in key_matches:
                continue

            yield old_widget, new_widget
