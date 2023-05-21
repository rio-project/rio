from __future__ import annotations

import logging
import typing
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from PIL.Image import Image

import reflex as rx

from . import app_server, assets, image_source, messages, validator
from .common import Jsonable
from .styling import *
from .widgets import widget_base


@dataclass
class WidgetData:
    build_result: rx.Widget


class WontSerialize(Exception):
    pass


class Session:
    """
    A session corresponds to a single connection to a client. It maintains all
    state related to this client including the GUI.
    """

    def __init__(
        self,
        root_widget: rx.Widget,
        send_message: Callable[[messages.OutgoingMessage], Awaitable[None]],
        app_server_: app_server.AppServer,
    ):
        self.root_widget = root_widget
        self.send_message = send_message
        self.app_server = app_server_

        # Weak dictionaries to hold additional information about widgets. These
        # are split in two to avoid the dictionaries keeping the widgets alive.
        # Notice how both dictionaries are weak on the actual widget.
        #
        # Never access these directly. Instead, use helper functions
        # - `lookup_widget`
        # - `lookup_widget_data`
        self._weak_widgets_by_id: weakref.WeakValueDictionary[
            int, rx.Widget
        ] = weakref.WeakValueDictionary()

        self._weak_widget_data_by_widget: weakref.WeakKeyDictionary[
            rx.Widget, WidgetData
        ] = weakref.WeakKeyDictionary()

        # Keep track of all dirty widgets, once again, weakly.
        #
        # Widgets are dirty if any of their properties have changed since the
        # last time they were built. Newly created widgets are also considered
        # dirty.
        #
        # Use `register_dirty_widget` to add a widget to this set.
        self._dirty_widgets: weakref.WeakSet[rx.Widget] = weakref.WeakSet()

    def lookup_widget_data(self, widget: rx.Widget) -> WidgetData:
        """
        Returns the widget data for the given widget. Raises `KeyError` if no
        data is present for the widget.
        """
        try:
            return self._weak_widget_data_by_widget[widget]
        except KeyError:
            raise KeyError(widget) from None

    def lookup_widget(self, widget_id: int) -> rx.Widget:
        """
        Returns the widget and its data for the given widget ID. Raises
        `KeyError` if no widget is present for the ID.
        """
        return self._weak_widgets_by_id[widget_id]

    def register_dirty_widget(
        self,
        widget: rx.Widget,
        *,
        include_fundamental_children_recursively: bool,
    ) -> None:
        """
        Add the widget to the set of dirty widgets. The widget is only held
        weakly by the session.

        If `include_fundamental_children_recursively` is true, all children of
        the widget that are fundamental widgets are also added.

        The children of non-fundamental widgets are not added, since they will
        be added after the parent is built anyway.
        """
        self._dirty_widgets.add(widget)

        if not include_fundamental_children_recursively or not isinstance(
            widget, widget_base.FundamentalWidget
        ):
            return

        for child in widget._iter_direct_children():
            self.register_dirty_widget(
                child,
                include_fundamental_children_recursively=True,
            )

    async def refresh(self) -> None:
        """
        Make sure the session state is up to date. Specifically:

        - Call build on all widgets marked as dirty
        - Recursively do this for all freshly spawned widgets
        - mark all widgets as clean

        Afterwards, the client is also informed of any changes, meaning that
        after this method returns there are no more dirty widgets in the
        session, and Python's state and the client's state are in sync.
        """
        # If nothing is dirty just return. While the loop below wouldn't do
        # anything anyway, this avoids sending a message to the client.
        if not self._dirty_widgets:
            return

        # Keep track of all widgets which are visited. Only they will be sent to
        # the client.
        visited_widgets: Set[widget_base.Widget] = set()

        # Build all dirty widgets
        while self._dirty_widgets:
            widget = self._dirty_widgets.pop()

            # Remember that this widget has been visited
            visited_widgets.add(widget)

            # Inject the session into the widget
            #
            # Widgets need to know the session they are part of, so that any
            # contained `StateProperty` instances can inform the session that
            # their widget is dirty, among other things.
            widget._session_ = self

            # Keep track of this widget's existence
            #
            # Widgets must be known by their id, so any messages addressed to
            # them can be passed on correctly.
            self._weak_widgets_by_id[widget._id] = widget

            # Fundamental widgets require no further treatment
            if isinstance(widget, widget_base.FundamentalWidget):
                continue

            # Others need to be built
            build_result = widget.build()

            # Inject the building widget into the state bindings of all
            # generated widgets.
            #
            # Take care to do this before reconciliation, because reconciliation
            # needs to access state bindings, which is only possible once the
            # bindings are aware of their widget.
            for child in build_result._iter_direct_and_indirect_children(True):
                child_vars = vars(child)

                for state_property in child._state_properties_:
                    value = child_vars[state_property.name]

                    if (
                        isinstance(value, widget_base.StateBinding)
                        and value.widget is None
                    ):
                        value.widget = widget

            # Has this widget been built before?
            try:
                widget_data = self.lookup_widget_data(widget)

            # No, this is the first time
            except KeyError:
                # Create the widget data and cache it
                widget_data = WidgetData(build_result)
                self._weak_widget_data_by_widget[widget] = widget_data
                self._weak_widgets_by_id[widget._id] = widget

                # Mark all fresh widgets as dirty
                self.register_dirty_widget(
                    build_result, include_fundamental_children_recursively=True
                )

            # Yes, rescue state
            #
            # This will look for widgets in the build output, which correspond
            # to widgets in the previous build output, and transfers state from
            # the old to the new widget.
            #
            # Furthermore, this adds any dirty widgets from the built output
            # (new, or old but changed) to the dirty set.
            else:
                self.reconciliate_tree(widget_data.build_result, build_result)
                widget_data.build_result = build_result

        # Send the new state to the client if necessary
        delta_states: Dict[int, Any] = {
            widget._id: self._serialize_and_host_widget(widget)
            for widget in visited_widgets
        }

        # Check whether the root widget needs replacing
        if self.root_widget in visited_widgets:
            root_widget_id = self.root_widget._id
        else:
            root_widget_id = None

        await self.send_message(
            messages.UpdateWidgetStates(delta_states, root_widget_id)
        )

    def _serialize_and_host_value(self, value: Any, type_: Type) -> Jsonable:
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
            return [self._serialize_and_host_value(v, args[0]) for v in value]

        # Special case: `FillLike`
        #
        # TODO: Is there a nicer way to detect these?
        if origin is Union and set(args) == {Fill, Color}:
            as_fill = Fill._try_from(value)

            # Image fills may contain an image source which needs to be hosted
            # by the server so the client can access it
            if isinstance(as_fill, ImageFill) and as_fill._image._asset is not None:
                self.app_server.weakly_host_asset(as_fill._image._asset)

            return as_fill._serialize()

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
                    return self._serialize_and_host_value(value, arg)

            assert False, f'Value "{value}" is not of any of the union types {args}'

        # Literal
        if origin is Literal:
            return self._serialize_and_host_value(value, type(value))

        # Widgets
        if widget_base.is_widget_class(type_):
            return value._id

        # Invalid type
        raise WontSerialize()

    def _serialize_and_host_widget(self, widget: rx.Widget) -> Jsonable:
        """
        Serializes the widget, non-recursively. Children are serialized just by
        their `_id`.

        Non-fundamental widgets must have been built, and their output cached in
        the session.
        """
        result: Dict[str, Jsonable]

        # Encode any internal state
        if isinstance(widget, widget_base.FundamentalWidget):
            type_name = type(widget).__name__
            type_name_camel_case = type_name[0].lower() + type_name[1:]

            result = {
                "_type_": type_name_camel_case,
                "_python_type_": type_name,
            }
            result.update(widget._custom_serialize())

        else:
            # Take care to add underscores to any properties here, as the
            # user-defined state is also added and could clash
            result = {
                "_type_": "placeholder",
                "_python_type_": type(widget).__name__,
                "_child_": self.lookup_widget_data(widget).build_result._id,
            }

        # Add user-defined state
        for name, type_ in typing.get_type_hints(type(widget)).items():
            # Skip some values
            if name in ("_",):  # Used to mark keyword-only arguments in dataclasses
                continue

            # Let the serialization function handle the value
            try:
                result[name] = self._serialize_and_host_value(
                    getattr(widget, name), type_
                )
            except WontSerialize:
                pass

        return result

    async def handle_message(self, msg: messages.IncomingMessage) -> None:
        """
        Handle a message from the client. This is the main entry point for
        messages from the client.
        """
        # Get the widget this message is addressed to
        try:
            widget_id = msg.widget_id  # type: ignore
        except AttributeError:
            raise NotImplementedError("Encountered message without widget ID")

        # Let the widget handle the message
        try:
            widget = self.lookup_widget(widget_id)
        except KeyError:
            logging.warn(
                f"Encountered message for unknown widget {widget_id}. (The widget might have been deleted in the meantime.)"
            )
            return

        await widget._handle_message(msg)

    def reconciliate_tree(self, old_build: rx.Widget, new_build: rx.Widget) -> None:
        # Find all pairs of widgets which should be reconciliated
        matched_pairs = list(self.find_widgets_for_reconciliation(old_build, new_build))

        # Reconciliating individual widgets requires knowledge of which other
        # widgets are being reconciliated.
        #
        # -> Collect them into a set first.
        reconciled_widgets: Set[rx.Widget] = set()
        for old_widget, new_widget in matched_pairs:
            reconciled_widgets.add(new_widget)

        # Reconciliate all matched pairs
        for old_widget, new_widget in matched_pairs:
            self.reconciliate_widget(
                old_widget,
                new_widget,
                reconciled_widgets,
            )

        # Any new widgets which haven't found a match are new and must be
        # processed by the session
        for widget in new_build._iter_direct_and_indirect_children(include_self=True):
            if widget in reconciled_widgets:
                continue

            self.register_dirty_widget(
                widget, include_fundamental_children_recursively=False
            )

    def reconciliate_widget(
        self,
        old_widget: rx.Widget,
        new_widget: rx.Widget,
        reconciliated_widgets: Set[rx.Widget],
    ) -> None:
        """
        Given two widgets of the same type, copy relevant state from the old one
        to the new one.

        Specifically:

        - Any state which was explicitly set by the user in the new widget's
          constructor is considered explicitly set, and will not be overwritten
        - Any other values are copied from the old widget to the new one
        - If any values were changed, the new widget is registered as dirty
          with the session

        This function also handles `StateBinding`s, for details see comments.
        """
        assert type(old_widget) is type(new_widget), (old_widget, new_widget)

        # First, determine which properties will be taken from the new widget
        overridden_values = {}
        new_widget_dict = vars(new_widget)
        old_widget_dict = vars(old_widget)

        for prop in new_widget._state_properties_:
            if prop.name not in new_widget._explicitly_set_properties_:
                continue

            overridden_values[prop.name] = new_widget_dict[prop.name]

        # Check if any of the widget's values have changed. If so, it is
        # considered dirty
        def values_equal(old: object, new: object) -> bool:
            # Widgets are a special case. Widget attributes are dirty iff the
            # widget isn't reconciliated, i.e. it is a new widget
            if isinstance(new, rx.Widget):
                return new in reconciliated_widgets

            if isinstance(new, list):
                if not isinstance(old, list):
                    return False

                if len(old) != len(new):
                    return False

                for old_item, new_item in zip(old, new):
                    if not values_equal(old_item, new_item):
                        return False

                return True

            # Otherwise attempt to compare the values
            try:
                return old == new
            except Exception:
                return old is new

        for prop_name in overridden_values:
            old_value = getattr(old_widget, prop_name)
            new_value = getattr(new_widget, prop_name)

            if not values_equal(old_value, new_value):
                self.register_dirty_widget(
                    new_widget, include_fundamental_children_recursively=False
                )
                break

        # Override the key now. It should never be preserved, but doesn't make
        # the widget dirty
        overridden_values["key"] = new_widget.key

        # Now combine the old and new dictionaries
        old_widget_dict.update(overridden_values)
        new_widget.__dict__ = old_widget_dict

        # The new widget is supposed to take the old widget's place. Part of
        # this is, that the old widget's `WidgetData` is now associated with the
        # new widget
        #
        # (Only do this if the widget isn't fundamental, as those aren't in the
        # cache.)
        try:
            self._weak_widget_data_by_widget[
                new_widget
            ] = self._weak_widget_data_by_widget.pop(old_widget)
        except KeyError:
            assert isinstance(new_widget, widget_base.FundamentalWidget), new_widget

    def find_widgets_for_reconciliation(
        self,
        old_build: rx.Widget,
        new_build: rx.Widget,
    ) -> Iterable[Tuple[rx.Widget, rx.Widget]]:
        """
        Given two widget trees, find pairs of widgets which can be
        reconciliated, i.e. which represent the "same" widget. When exactly
        widgets are considered to be the same is up to the implementation and
        best-effort.

        Returns an iterable over (old_widget, new_widget) pairs, as well as a
        list of all widgets occurring in the new tree, which did not have a match
        in the old tree.
        """

        old_widgets_by_key: Dict[str, rx.Widget] = {}
        new_widgets_by_key: Dict[str, rx.Widget] = {}

        matches_by_topology: List[Tuple[rx.Widget, rx.Widget]] = []

        # First scan all widgets for topological matches, and also keep track of
        # each widget by its key
        def register_widget_by_key(
            widgets_by_key: Dict[str, rx.Widget],
            widget: rx.Widget,
        ) -> None:
            if widget.key is None:
                return

            if widget.key in widgets_by_key:
                raise RuntimeError(
                    f'Multiple widgets share the key "{widget.key}": {widgets_by_key[widget.key]} and {widget}'
                )

            widgets_by_key[widget.key] = widget

        def key_scan(
            widgets_by_key: Dict[str, rx.Widget],
            widget: rx.Widget,
            include_self: bool = True,
        ) -> None:
            for child in widget._iter_direct_and_indirect_children(
                include_self=include_self
            ):
                register_widget_by_key(widgets_by_key, child)

        def chain_to_children(
            old_widget: rx.Widget,
            new_widget: rx.Widget,
        ) -> None:
            # Iterate over the children, but make sure to preserve the topology.
            # Can't just use `iter_direct_children` here, since that would
            # discard topological information.
            for name, typ in typing.get_type_hints(type(new_widget)).items():
                origin, args = typing.get_origin(typ), typing.get_args(typ)

                old_widgets: List[rx.Widget]
                new_widgets: List[rx.Widget]

                # Widget
                if widget_base.is_widget_class(typ):
                    old_widgets = [getattr(old_widget, name)]
                    new_widgets = [getattr(new_widget, name)]

                # Union[Widget, ...]
                elif origin is typing.Union and any(
                    widget_base.is_widget_class(arg) for arg in args
                ):
                    old_child = getattr(old_widget, name)
                    new_child = getattr(new_widget, name)

                    old_widgets = (
                        [old_child] if widget_base.is_widget_class(old_child) else []
                    )
                    new_widgets = (
                        [new_child] if widget_base.is_widget_class(new_child) else []
                    )

                # List[Widget]
                elif origin is list and widget_base.is_widget_class(args[0]):
                    old_widgets = getattr(old_widget, name)
                    new_widgets = getattr(new_widget, name)

                # Anything else
                #
                # TODO: What about other containers?
                else:
                    continue

                # Chain to the children
                common = min(len(old_widgets), len(new_widgets))
                for old_child, new_child in zip(old_widgets, new_widgets):
                    worker(old_child, new_child)

                for old_child in old_widgets[common:]:
                    key_scan(old_widgets_by_key, old_child, include_self=True)

                for new_child in new_widgets[common:]:
                    key_scan(new_widgets_by_key, new_child, include_self=True)

        def worker(old_widget: rx.Widget, new_widget: rx.Widget) -> None:
            # Register the widget by key
            register_widget_by_key(old_widgets_by_key, old_widget)
            register_widget_by_key(new_widgets_by_key, new_widget)

            # Do the widget types match?
            if type(old_widget) is type(new_widget):
                matches_by_topology.append((old_widget, new_widget))
                chain_to_children(old_widget, new_widget)
                return

            # Otherwise neither they, nor their children can be topological
            # matches.  Just keep track of the children's keys.
            key_scan(old_widgets_by_key, old_widget, include_self=False)
            key_scan(new_widgets_by_key, new_widget, include_self=False)

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
