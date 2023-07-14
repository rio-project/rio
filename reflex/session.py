from __future__ import annotations

import asyncio
import enum
import inspect
import json
import logging
import secrets
import sys
import typing
import weakref
from dataclasses import dataclass
from typing import *  # type: ignore

import uniserde

import reflex as rx

from . import app_server, assets, common, errors, messages, styling
from .common import Jsonable
from .widgets import widget_base

__all__ = ["Session"]


T = typing.TypeVar("T")


def _get_type_hints(cls: type) -> Dict[str, type]:
    """
    Reimplementation of `typing.get_type_hints` because it has a stupid bug in
    python 3.10 where it dies if something is annotated as `dataclasses.KW_ONLY`.
    """
    type_hints = {}

    for cls in cls.__mro__:
        for attr_name, annotation in vars(cls).get("__annotations__", {}).items():
            if attr_name in type_hints:
                continue

            if isinstance(annotation, typing.ForwardRef):
                annotation = annotation.__forward_code__

            if isinstance(annotation, str):
                globs = vars(sys.modules[cls.__module__])
                annotation = eval(annotation, globs)

            type_hints[attr_name] = annotation

    return type_hints


@dataclass
class WidgetData:
    build_result: rx.Widget

    # Keep track of how often this widget has been built. This is used by
    # widgets to determine whether they are still part of their parent's current
    # build output.
    build_generation: int

    # The ids of all widgets contained in this build output. This does not
    # include the children of non-fundamental widgets, since they have their own
    # build output.
    contained_widget_ids: Set[int]


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

        # HTML widgets have source code which must be evaluated by the client
        # exactly once. Keep track of which widgets have already sent their
        # source code.
        self._initialized_html_widgets: Set[Type[rx.HtmlWidget]] = set()

        # This lock is used to order state updates that are sent to the client.
        # Without it a message which was generated later might be sent to the
        # client before an earlier message, leading to invalid widget
        # references.
        self._refresh_lock = asyncio.Lock()

        # Attachments. These are arbitrary values which are passed around inside
        # of the app. They can be looked up by their type.
        self._attachments: Dict[Type[Any], Any] = {}

    def _lookup_widget_data(self, widget: rx.Widget) -> WidgetData:
        """
        Returns the widget data for the given widget. Raises `KeyError` if no
        data is present for the widget.
        """
        try:
            return self._weak_widget_data_by_widget[widget]
        except KeyError:
            raise KeyError(widget) from None

    def _lookup_widget(self, widget_id: int) -> rx.Widget:
        """
        Returns the widget and its data for the given widget ID. Raises
        `KeyError` if no widget is present for the ID.
        """
        return self._weak_widgets_by_id[widget_id]

    def _register_dirty_widget(
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
            widget, widget_base.HtmlWidget
        ):
            return

        for child in widget._iter_direct_children():
            self._register_dirty_widget(
                child,
                include_fundamental_children_recursively=True,
            )

    def _refresh_sync(self) -> Set[rx.Widget]:
        """
        See `refresh` for details on what this function does.

        The refresh process must be performed atomically, without ever yielding
        control flow to the async event loop. TODO WHY

        To make sure async isn't used unintentionally this part of the refresh
        function is split into a separate, synchronous function.

        The session keeps track of widgets which are no longer referenced in its
        widget tree. Those widgets are NOT included in the function's result.
        """

        # If nothing is dirty just return. While the loop below wouldn't do
        # anything anyway, this avoids sending a message to the client.
        if not self._dirty_widgets:
            return set()

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
            if isinstance(widget, widget_base.HtmlWidget):
                continue

            # Others need to be built
            build_result = widget.build()

            # Inject the building widget into the state bindings of all
            # generated widgets.
            #
            # Take care to do this before reconciliation, because reconciliation
            # needs to access state bindings, which is only possible once the
            # bindings are aware of their widget.
            widget_vars = vars(widget)

            for child in build_result._iter_direct_and_indirect_children(True):
                child_vars = vars(child)

                for state_property in child._state_properties_:
                    value = child_vars[state_property.name]

                    # Create a StateBinding, if requested
                    if isinstance(value, widget_base.StateProperty):
                        # In order to create a `StateBinding`, the parent's
                        # attribute must also be a binding
                        parent_binding = widget_vars[value.name]

                        if not isinstance(parent_binding, widget_base.StateBinding):
                            parent_binding = widget_base.StateBinding(
                                owning_widget_weak=weakref.ref(widget),
                                owning_property=value,
                                is_root=True,
                                parent=None,
                                value=parent_binding,
                                children=weakref.WeakSet(),
                            )
                            widget_vars[value.name] = parent_binding

                        # Create the child binding
                        child_binding = widget_base.StateBinding(
                            owning_widget_weak=weakref.ref(child),
                            owning_property=state_property,
                            is_root=False,
                            parent=parent_binding,
                            value=None,
                            children=weakref.WeakSet(),
                        )
                        parent_binding.children.add(child_binding)
                        child_vars[state_property.name] = child_binding

            # Has this widget been built before?
            try:
                widget_data = self._lookup_widget_data(widget)

            # No, this is the first time
            except KeyError:
                # Create the widget data and cache it
                widget_data = WidgetData(build_result, 0, set())
                self._weak_widget_data_by_widget[widget] = widget_data

                # Mark all fresh widgets as dirty
                self._register_dirty_widget(
                    build_result, include_fundamental_children_recursively=True
                )

            # Yes, rescue state. This will:
            #
            # - Look for widgets in the build output which correspond to widgets
            #   in the previous build output, and transfers state from the new
            #   to the old widget ("reconciliation")
            #
            # - Replace any references to new, reconciled widgets in the build
            #   output with the old widgets instead
            #
            # - Add any dirty widgets from the build output (new, or old but
            #   changed) to the dirty set.
            #
            # - Update the widget data with the build output resulting from the
            #   operations above
            else:
                self._reconcile_tree(widget_data, build_result)

                # Increment the build generation
                widget_data.build_generation += 1

                # Reconciliation can change the build result. Make sure nobody
                # uses `build_result` instead of `widget_data.build_result` from
                # now on.
                del build_result

            # Inject the builder and build generation
            to_do = {widget_data.build_result}
            weak_builder_ref = weakref.ref(widget)

            while to_do:
                cur = to_do.pop()
                cur._weak_builder_ = weak_builder_ref
                cur._build_generation_ = widget_data.build_generation

                if isinstance(cur, widget_base.HtmlWidget):
                    to_do.update(cur._iter_direct_children())

        # Determine which widgets are alive, to avoid sending references to dead
        # widgets to the frontend.
        alive_cache: Dict[rx.Widget, bool] = {
            self.root_widget: True,
        }

        def is_alive(widget: widget_base.Widget) -> bool:
            # Already cached?
            try:
                return alive_cache[widget]
            except KeyError:
                pass

            # Parent has been garbage collected?
            parent = widget._weak_builder_()
            if parent is None:
                result = False

            else:
                parent_data = self._lookup_widget_data(parent)
                result = (
                    parent_data.build_generation == widget._build_generation_
                    and is_alive(parent)
                )

            # Cache and return
            alive_cache[widget] = result
            return result

        return {widget for widget in visited_widgets if is_alive(widget)}

    async def _refresh(self) -> None:
        """
        Make sure the session state is up to date. Specifically:

        - Call build on all widgets marked as dirty
        - Recursively do this for all freshly spawned widgets
        - mark all widgets as clean

        Afterwards, the client is also informed of any changes, meaning that
        after this method returns there are no more dirty widgets in the
        session, and Python's state and the client's state are in sync.
        """

        # For why this lock is here see its creation in `__init__`
        async with self._refresh_lock:
            # Refresh and get a set of all widgets which have been visited
            visited_widgets = self._refresh_sync()

            # Avoid sending empty messages
            if not visited_widgets:
                return

            # Initialize all HTML widgets
            for widget in visited_widgets:
                if (
                    not isinstance(widget, rx.HtmlWidget)
                    or type(widget) in self._initialized_html_widgets
                ):
                    continue

                for msg in widget._build_initialization_messages(self):
                    await self.send_message(msg)

                self._initialized_html_widgets.add(type(widget))

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
        if origin is Callable:
            raise WontSerialize()

        if isinstance(type_, typing.TypeVar):
            raise WontSerialize()

        # Basic JSON values
        if type_ in (bool, int, float, str, None):
            return value

        # Enums
        if inspect.isclass(type_) and issubclass(type_, enum.Enum):
            return uniserde.as_json(value, as_type=type_)

        # Tuples or lists of serializable values
        if origin is tuple or origin is list:
            return [self._serialize_and_host_value(v, args[0]) for v in value]

        # Special case: `FillLike`
        #
        # TODO: Is there a nicer way to detect these?
        if origin is Union and set(args) == {styling.Fill, styling.Color}:
            as_fill = styling.Fill._try_from(value)

            # Image fills may contain an image source which needs to be hosted
            # by the server so the client can access it
            if (
                isinstance(as_fill, styling.ImageFill)
                and as_fill._image._asset is not None
            ):
                self.app_server.weakly_host_asset(as_fill._image._asset)

            return as_fill._serialize()

        # Colors
        if type_ is styling.Color:
            return value.rgba

        # TextStyle
        if type_ is styling.TextStyle:
            return value._serialize()

        # BoxStyle
        if type_ is styling.BoxStyle:
            assert isinstance(value, styling.BoxStyle), value

            # Image fills may contain an image source which needs to be hosted
            # by the server so the client can access it
            if (
                isinstance(value.fill, styling.ImageFill)
                and value.fill._image._asset is not None
            ):
                self.app_server.weakly_host_asset(value.fill._image._asset)

            return value._serialize()

        # MarkdownStyle
        if type_ is styling.MarkdownStyle:
            return value._serialize()

        # Optional
        if origin is Union and len(args) == 2 and type(None) in args:
            if value is None:
                return None

            type_ = next(type_ for type_ in args if type_ is not type(None))
            return self._serialize_and_host_value(value, type_)

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
        if isinstance(widget, widget_base.HtmlWidget):
            result = {
                "_type_": widget._unique_id,
                "_python_type_": type(widget).__name__,
            }
            result.update(widget._custom_serialize())

        else:
            # Take care to add underscores to any properties here, as the
            # user-defined state is also added and could clash
            result = {
                "_type_": "Placeholder",
                "_python_type_": type(widget).__name__,
                "_child_": self._lookup_widget_data(widget).build_result._id,
            }

        # Add layout properties, in a more succinct way than sending them
        # separately
        result["_margin_"] = (
            widget.margin_left,
            widget.margin_top,
            widget.margin_right,
            widget.margin_bottom,
        )
        result["_size_"] = (
            widget.width if isinstance(widget.width, (int, float)) else None,
            widget.height if isinstance(widget.height, (int, float)) else None,
        )
        result["_align_"] = (
            widget.align_x,
            widget.align_y,
        )
        result["_grow_"] = (
            widget.width == "grow",
            widget.height == "grow",
        )

        # Add user-defined state
        for name, type_ in _get_type_hints(type(widget)).items():
            # Skip some values
            if name in (
                "_",
                "_build_generation_",
                "_explicitly_set_properties_",
                "_init_signature_",
                "_session_",
                "_state_properties_",
                "_weak_builder_",
                "align_x",
                "align_y",
                "height",
                "margin_bottom",
                "margin_left",
                "margin_right",
                "margin_top",
                "margin_x",
                "margin_y",
                "margin",
                "width",
                "grow_x",
                "grow_y",
            ):
                continue

            # Let the serialization function handle the value
            try:
                result[name] = self._serialize_and_host_value(
                    getattr(widget, name), type_
                )
            except WontSerialize:
                pass

        return result

    async def _handle_message(self, msg: messages.IncomingMessage) -> None:
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
            widget = self._lookup_widget(widget_id)
        except KeyError:
            logging.warn(
                f"Encountered message for unknown widget {widget_id}. (The widget might have been deleted in the meantime.)"
            )
            return

        await widget._handle_message(msg)

    def _reconcile_tree(self, old_build_data: WidgetData, new_build: rx.Widget) -> None:
        # Find all pairs of widgets which should be reconciled
        matched_pairs = list(
            self._find_widgets_for_reconciliation(
                old_build_data.build_result, new_build
            )
        )

        # Reconciliating individual widgets requires knowledge of which other
        # widgets are being reconciled.
        #
        # -> Collect them into a set first.
        reconciled_widgets_new_to_old: Dict[rx.Widget, rx.Widget] = {
            new_widget: old_widget for old_widget, new_widget in matched_pairs
        }

        # Reconcile all matched pairs
        for new_widget, old_widget in reconciled_widgets_new_to_old.items():
            self._reconcile_widget(
                old_widget,
                new_widget,
                reconciled_widgets_new_to_old,
            )

        # Update the widget data. If the root widget was not reconciled, the new
        # widget is the new build result.
        try:
            reconciled_build_result = reconciled_widgets_new_to_old[new_build]
        except KeyError:
            reconciled_build_result = new_build
            old_build_data.build_result = new_build

        # Replace any references to new reconciled widgets to old ones instead
        def remap_widgets(parent: rx.Widget) -> None:
            parent_vars = vars(parent)

            for attr_name, attr_value in parent_vars.items():
                # Just a widget
                if isinstance(attr_value, rx.Widget):
                    try:
                        attr_value = reconciled_widgets_new_to_old[attr_value]
                    except KeyError:
                        pass
                    else:
                        parent_vars[attr_name] = attr_value

                    remap_widgets(attr_value)

                # List
                elif isinstance(attr_value, list):
                    for ii, item in enumerate(attr_value):
                        if isinstance(item, rx.Widget):
                            try:
                                attr_value[ii] = reconciled_widgets_new_to_old[item]
                            except KeyError:
                                pass

                            remap_widgets(item)

        remap_widgets(reconciled_build_result)

        # Any new widgets which haven't found a match are new and must be
        # processed by the session
        #
        # Note that new widgets cannot possibly have been reconciled, as
        # reconciliation replaces new instances with their old counterparts.
        # Thus, only look up the widgets in a set of old widgets.
        reconciled_widgets_old = set(reconciled_widgets_new_to_old.values())

        for widget in reconciled_build_result._iter_direct_and_indirect_children(
            include_self=True
        ):
            if widget in reconciled_widgets_old:
                continue

            self._register_dirty_widget(
                widget, include_fundamental_children_recursively=False
            )

    def _reconcile_widget(
        self,
        old_widget: rx.Widget,
        new_widget: rx.Widget,
        reconciled_widgets_new_to_old: Dict[rx.Widget, rx.Widget],
    ) -> None:
        """
        Given two widgets of the same type, reconcile them. Specifically:

        - Any state which was explicitly set by the user in the new widget's
          constructor is considered explicitly set, and will be copied into the
          old widget
        - If any values were changed, the widget is registered as dirty with the
          session

        This function also handles `StateBinding`s, for details see comments.
        """
        assert type(old_widget) is type(new_widget), (old_widget, new_widget)

        # Let any following code assume that the two widgets aren't the same
        # instance
        if old_widget is new_widget:
            return

        # Determine which properties will be taken from the new widget
        overridden_values = {}
        old_widget_dict = vars(old_widget)
        new_widget_dict = vars(new_widget)

        for prop in new_widget._state_properties_:
            # Should the value be overridden?
            if prop.name not in new_widget._explicitly_set_properties_:
                continue

            # Take care to keep state bindings up to date
            old_value = old_widget_dict[prop.name]
            new_value = new_widget_dict[prop.name]
            old_is_binding = isinstance(old_value, widget_base.StateBinding)
            new_is_binding = isinstance(new_value, widget_base.StateBinding)

            # If the old value was a binding, and the new one isn't, split the
            # tree of bindings. All children are now roots.
            if old_is_binding and not new_is_binding:
                binding_value = old_value.get_value()
                old_value.owning_widget_weak = lambda: None

                for child_binding in old_value.children:
                    child_binding.is_root = True
                    child_binding.parent = None
                    child_binding.value = binding_value

            # If both values are bindings transfer the children to the new
            # binding
            elif old_is_binding and new_is_binding:
                new_value.owning_widget_weak = old_value.owning_widget_weak
                new_value.children = old_value.children

                for child in old_value.children:
                    child.parent = new_value

                # Save the binding's value in case this is the root binding
                new_value.value = old_value.value

            overridden_values[prop.name] = new_value

        # If the widget has changed mark it as dirty
        def values_equal(old: object, new: object) -> bool:
            """
            Used to compare the old and new values of a property. Returns `True`
            if the values are considered equal, `False` otherwise.
            """
            # Widgets are a special case. Widget attributes are dirty iff the
            # widget isn't reconciled, i.e. it is a new widget
            if isinstance(new, rx.Widget):
                return old is reconciled_widgets_new_to_old.get(new, None)

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

        # Determine which properties will be taken from the new widget
        for prop_name in overridden_values:
            old_value = getattr(old_widget, prop_name)
            new_value = getattr(new_widget, prop_name)

            if not values_equal(old_value, new_value):
                self._register_dirty_widget(
                    old_widget,
                    include_fundamental_children_recursively=False,
                )

                # TODO / FIXME
                #
                # Overriding an attribute can cause the widget to contain
                # widgets which have never had their builder or state properties
                # injected. This code avoids this by marking their builder as
                # dirty. This makes tons of widgets pass through building
                # multiple times though, for no reason at all.
                if isinstance(old_widget, rx.HtmlWidget):
                    builder = old_widget._weak_builder_()
                    assert builder is not None, old_widget
                    self._register_dirty_widget(
                        builder,
                        include_fundamental_children_recursively=False,
                    )

                break

        # Override the key now. It should never be preserved, but doesn't make
        # the widget dirty
        overridden_values["key"] = new_widget.key

        # Now combine the old and new dictionaries
        old_widget_dict.update(overridden_values)

    def _find_widgets_for_reconciliation(
        self,
        old_build: rx.Widget,
        new_build: rx.Widget,
    ) -> Iterable[Tuple[rx.Widget, rx.Widget]]:
        """
        Given two widget trees, find pairs of widgets which can be
        reconciled, i.e. which represent the "same" widget. When exactly
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
            for name, typ in _get_type_hints(type(new_widget)).items():
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
                        [old_child] if isinstance(old_child, rx.Widget) else []
                    )
                    new_widgets = (
                        [new_child] if isinstance(new_child, rx.Widget) else []
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
            new_widget = new_widgets_by_key[key]
            yield (
                old_widgets_by_key[key],
                new_widget,
            )

        # Yield topological matches, taking care to not those matches which were
        # already matched by key.
        for old_widget, new_widget in matches_by_topology:
            if old_widget.key in key_matches or new_widget.key in key_matches:
                continue

            yield old_widget, new_widget

    @overload
    async def file_chooser(
        self,
        *,
        file_extensions: Optional[Iterable[str]] = None,
        multiple: Literal[False] = False,
    ) -> common.FileInfo:
        ...

    @overload
    async def file_chooser(
        self,
        *,
        file_extensions: Optional[Iterable[str]] = None,
        multiple: Literal[True],
    ) -> Tuple[common.FileInfo]:
        ...

    async def file_chooser(
        self,
        *,
        file_extensions: Optional[Iterable[str]] = None,
        multiple: bool = False,
    ) -> Union[common.FileInfo, Tuple[common.FileInfo]]:
        """
        Open a file chooser dialog.
        """
        # Create a secret id and register the file upload with the app server
        upload_id = secrets.token_urlsafe()
        future = asyncio.Future()

        self.app_server._pending_file_uploads[upload_id] = future

        # Allow the user to specify both `jpg` and `.jpg`
        if file_extensions is not None:
            file_extensions = [
                ext if ext.startswith(".") else f".{ext}" for ext in file_extensions
            ]

        # Tell the frontend to upload a file
        await self.send_message(
            messages.RequestFileUpload(
                upload_url=f"{self.app_server.external_url}/reflex/upload/{upload_id}",
                file_extensions=file_extensions,
                multiple=multiple,
            )
        )

        # Wait for the user to upload files
        files = await future

        # Raise an exception if no files were uploaded
        if not files:
            raise errors.NoFileSelectedError()

        # Ensure only one file was provided if `multiple` is False
        if not multiple and len(files) != 1:
            logging.warning(
                "Client attempted to upload multiple files when `multiple` was False."
            )
            raise errors.NoFileSelectedError()

        # Return the file info
        if multiple:
            return tuple(files)
        else:
            return files[0]

    async def save_file(
        self,
        file_name: str,
        file_contents: Union[str, bytes],
        *,
        media_type: Optional[str] = None,
    ) -> None:
        # Convert the file contents to bytes
        if isinstance(file_contents, str):
            file_contents = file_contents.encode("utf-8")

            if media_type is None:
                media_type = "text/plain"

        elif media_type is None:
            media_type = "application/octet-stream"

        # Host the file as asset
        as_asset = assets.HostedAsset(media_type, file_contents)
        self.app_server.weakly_host_asset(as_asset)

        # Tell the frontend to download the file
        await self.send_message(
            messages.EvaluateJavascript(
                f"""
const a = document.createElement('a')
a.href = {json.dumps(as_asset.url(None))}
a.download = {json.dumps(file_name)}
a.target = "_blank"
document.body.appendChild(a)
a.click()
document.body.removeChild(a)
"""
            )
        )

        # Keep the asset alive for some time
        #
        # TODO: Is there a better way to do this
        async def keepaliver() -> None:
            temp = as_asset
            await asyncio.sleep(60)

        asyncio.create_task(keepaliver())

    def attach(self, value: Any) -> None:
        """
        Attaches the given value to the `Session`. It can be retrieved later
        using `get_attachment`.
        """
        self._attachments[type(value)] = value

    def get_attachment(self, typ: Type[T]) -> T:
        """
        Retrieves an attachment that was previously attached using `attach`.
        """
        try:
            return self._attachments[typ]
        except KeyError:
            raise KeyError(typ)
