import inspect
import logging
import pprint
import typing
import weakref
from dataclasses import dataclass
from typing import Any, Callable, Tuple, Type, Union

from fastapi import WebSocket

from . import messages, widgets
from .common import Jsonable
from .styling import *


@dataclass
class WidgetData:
    previous_build_result: widgets.Widget


class WontSerialize(Exception):
    pass


class Session:
    def __init__(self, root_widget: widgets.Widget, websocket: WebSocket):
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
            int, widgets.Widget
        ] = weakref.WeakValueDictionary()

        self._weak_widget_data_by_widget: weakref.WeakKeyDictionary[
            widgets.Widget, WidgetData
        ] = weakref.WeakKeyDictionary()

        # Keep track of all dirty widgets, once again, weakly
        self._dirty_widgets: weakref.WeakSet[widgets.Widget] = weakref.WeakSet()

    def lookup_widget_data(self, widget: widgets.Widget) -> WidgetData:
        """
        Returns the widget data for the given widget. Raises `KeyError` if no
        data is present for the widget.
        """
        return self._weak_widget_data_by_widget[widget]

    def lookup_widget(self, widget_id: int) -> widgets.Widget:
        """
        Returns the widget and its data for the given widget ID. Raises
        `KeyError` if no widget is present for the ID.
        """
        return self._weak_widgets_by_id[widget_id]

    def register_dirty_widget(self, widget: widgets.Widget) -> None:
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

            # Fundamental widgets just need their children looked at
            if isinstance(widget, widgets.FundamentalWidget):
                self._dirty_widgets.update(widget._iter_direct_children())
                continue

            # Other children need to be built
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
                pass  # TODO: Rescue state

            # Any freshly spawned widgets are dirty
            self._dirty_widgets.add(build_result)

        # Send the new state to the client if necessary
        foo = messages.ReplaceWidgets(self._serialize_widget(self.root_widget))
        await self.send_message(foo)

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

                if isinstance(value, arg):  # type: ignore
                    return self._serialize_value(value, arg)

            assert False, f'Value "{value}" is not of any of the union types {args}'

        # Literal
        if origin is Literal:
            return self._serialize_value(value, type(value))

        # Widgets
        if inspect.isclass(type_) and issubclass(type_, widgets.Widget):
            return self._serialize_widget(value)

        # Invalid type
        raise WontSerialize()

    def _serialize_widget(self, widget: widgets.Widget) -> Jsonable:
        """
        Recursively serialize a widget and all of its children.

        Fundamental widgets are serialized as expected. Non-fundamental widgets
        must be built, and thus be present in the session's dictionary caches.
        They are serialized as the fundamental widgets that result when built.
        """

        # Get the effective fundamental widget to serialize
        fundamental_widget = widget

        while not isinstance(fundamental_widget, widgets.FundamentalWidget):
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
