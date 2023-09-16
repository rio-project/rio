from __future__ import annotations

import asyncio
import collections
import enum
import inspect
import json
import logging
import secrets
import traceback
import typing
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import *  # type: ignore

import babel
import introspection
import unicall
import uniserde
from uniserde import Jsonable, JsonDoc

import reflex as rx

from . import (
    app_server,
    assets,
    color,
    common,
    errors,
    global_state,
    inspection,
    self_serializing,
    theme,
    user_settings_module,
)
from .widgets import widget_base

__all__ = ["Session"]


T = typing.TypeVar("T")


@dataclass
class WidgetData:
    build_result: rx.Widget

    # Keep track of how often this widget has been built. This is used by
    # widgets to determine whether they are still part of their parent's current
    # build output.
    build_generation: int


class WontSerialize(Exception):
    pass


class SessionAttachments:
    def __init__(self, sess: Session):
        self._session = sess
        self._attachments = {}

    def __contains__(self, typ: type) -> bool:
        return typ in self._attachments

    def __getitem__(self, typ: Type[T]) -> T:
        """
        Retrieves an attachment from this session.

        Attached values are:
        - the session's user settings
        - any value that was previously attached using `Session.attach`
        """
        try:
            return self._attachments[typ]  # type: ignore
        except KeyError:
            raise KeyError(typ) from None

    def _add(self, value: Any, synchronize: bool) -> None:
        # User settings need special care
        if isinstance(value, user_settings_module.UserSettings):
            # Get the previously attached value, and unlink it from the session
            try:
                old_value = self[type(value)]
            except KeyError:
                pass
            else:
                old_value._reflex_session_ = None

            # Link the new value to the session
            value._reflex_session_ = self._session

            # Trigger a resync
            if synchronize:
                asyncio.create_task(
                    value._synchronize_now(self._session),
                    name="write back user settings (entire settings instance changed)",
                )

        # Save it with the rest of the attachments
        self._attachments[type(value)] = value

    def add(self, value: Any) -> None:
        """
        Attaches the given value to the `Session`. It can be retrieved later
        using `session.attachments[...]`.
        """
        self._add(value, synchronize=True)


class Session(unicall.Unicall):
    """
    A session corresponds to a single connection to a client. It maintains all
    state related to this client including the GUI.
    """

    def __init__(
        self,
        initial_route: Iterable[str],
        send_message: Callable[[Jsonable], Awaitable[None]],
        receive_message: Callable[[], Awaitable[Jsonable]],
        app_server_: app_server.AppServer,
    ):
        super().__init__(send_message=send_message, receive_message=receive_message)

        self._app_server = app_server_

        # The current route. This isn't used by the session itself, but routers
        # can use it to agree on what to display.
        self._current_route: Tuple[str, ...] = tuple(initial_route)

        # Maps all routers to the id of the router one higher up in the widget
        # tree. Root routers are mapped to None. This map is kept up to date by
        # routers themselves.
        self._routers: weakref.WeakKeyDictionary[
            rx.Router, Optional[int]
        ] = weakref.WeakKeyDictionary()

        # All widgets / methods which should be called when the session's route
        # has changed.
        #
        # The methods don't have the widget bound yet, so they don't unduly
        # prevent the widget from being garbage collected.
        self._route_change_callbacks: weakref.WeakKeyDictionary[
            rx.Widget, Callable[[rx.Widget], None]
        ] = weakref.WeakKeyDictionary()

        # These are injected by the app server after the session has already been created
        self._root_widget: rx.Widget
        self.external_url: Optional[str]  # None if running in a window
        self.preferred_locales: Tuple[
            babel.Locale, ...
        ]  # Always has at least one member

        self.window_width: float
        self.window_height: float

        # Must be acquired while synchronizing the user's settings
        self._settings_sync_lock = asyncio.Lock()

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
        self._initialized_html_widgets: Set[str] = set(
            inspection.get_child_widget_containing_attribute_names_for_builtin_widgets()
        )

        # This lock is used to order state updates that are sent to the client.
        # Without it a message which was generated later might be sent to the
        # client before an earlier message, leading to invalid widget
        # references.
        self._refresh_lock = asyncio.Lock()

        # Attachments. These are arbitrary values which are passed around inside
        # of the app. They can be looked up by their type.
        # Note: These are initialized by the AppServer.
        self.attachments = SessionAttachments(self)

        # This allows easy access to the app's assets. Users can simply write
        # `widget.session.assets / "my_asset.png"`.
        self.assets = self._app_server.app.assets_dir

    @property
    def running_in_window(self) -> bool:
        """
        Returns `True` if the app is running in a local window, and `False` if
        it is hosted as a website.
        """
        return self._app_server.running_in_window

    @property
    def running_as_website(self) -> bool:
        """
        Returns `True` if the app is running as a website, and `False` if it is
        running in a local window.
        """
        return self._app_server.running_in_window

    @property
    def current_route(self) -> Tuple[str, ...]:
        """
        Returns the current route as a tuple of strings.

        This property is read-only. To change the route, use `Session.navigate_to`.
        """
        return self._current_route

    def navigate_to(
        self,
        route: str,
        *,
        replace: bool = False,
    ) -> None:
        """
        If `route` starts with `/`, `./` o `../`, switch to the given route,
        without reloading the website. If it starts with `/` the route is taken
        as absolute, completely superseeding the current route. Otherwise the
        route is taken as relative to the current route. Any `./` are ignored.
        `../` are interpreted as "go up one level".

        If `route` doesn't start with `/`, `./` o `../`, it is taken to be a
        full URL, and the browser will navigate to it.

        Raises a `ValueError` if so many `../` are used that the route would
        leave the root route.

        If `replace` is `True`, the browser's most recent history entry is
        replaced with the new route. This means that the user can't go back to
        the previous route using the browser's back button. If `False`, a new
        history entry is created, allowing the user to go back to the previous
        route.
        """
        # If this is a full URL, navigate to it
        if not route.startswith(("/", "./", "../")):

            async def history_worker() -> None:
                await self._evaluate_javascript(
                    f"window.location.href = {json.dumps(route)}",
                )

            asyncio.create_task(history_worker())
            return

        # Determine the full route to navigate to
        initial_target_route = common.join_routes(self._current_route, route)

        # Is any guard opposed to this route?
        target_route = initial_target_route
        visited_redirects = {target_route}
        past_redirects = [target_route]

        while True:
            for router in self._routers:
                # Get the route instance
                try:
                    route_segment = target_route[router._level[0]]
                except IndexError:
                    route_segment = ""

                try:
                    route_instance = router.routes[route_segment]
                except KeyError:
                    # If there is no fallback route this can be safely ignored,
                    # since the default fallback doesn't have a guard.
                    if router.fallback_route is None:
                        continue

                    route_instance = router.fallback_route

                # Run the guard
                try:
                    redirect_str = route_instance.guard(self)
                except Exception:
                    print("Ignoring guard, because it has raised an exception:")
                    traceback.print_exc()
                    continue

                # No redirect - check the next router
                if redirect_str is None:
                    continue

                # Honest to god redirect
                target_route = common.join_routes(self._current_route, redirect_str)
                break

            # No guard is opposed to this route. Use it
            else:
                break

            # Detect infinite loops and break them
            if target_route in visited_redirects:
                current_route_str = "/" + "/".join(self._current_route)
                initial_target_route_str = "/" + "/".join(initial_target_route)
                route_strings = ["/" + "/".join(route) for route in past_redirects]
                route_strings_list = " -> " + "\n -> ".join(route_strings)

                logging.warning(
                    f"Rejecting navigation to `{initial_target_route_str}` because route guards have created an infinite loop:\n\n    {current_route_str}\n{route_strings_list}"
                )
                return

            # Remember that this route has been visited before
            visited_redirects.add(target_route)
            past_redirects.append(target_route)

        # Update the current route
        self._current_route = target_route

        # Dirty all routers to force a rebuild
        for router in self._routers:
            self._register_dirty_widget(router, include_children_recursively=True)

        asyncio.create_task(self._refresh())

        # Update the browser's history
        async def history_worker() -> None:
            method = "replaceState" if replace else "pushState"
            await self._evaluate_javascript(
                f"window.history.{method}(null, null, {json.dumps(route)})",
            )

        asyncio.create_task(history_worker())

        # Trigger the `on_route_change` event
        async def event_worker() -> None:
            for widget, callback in self._route_change_callbacks.items():
                await common.call_event_handler(lambda: callback(widget))

        asyncio.create_task(event_worker())

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
        include_children_recursively: bool,
    ) -> None:
        """
        Add the widget to the set of dirty widgets. The widget is only held
        weakly by the session.

        If `include_fundamental_children_recursively` is true, all children of
        the widget are also added.

        The children of non-fundamental widgets are not added, since they will
        be added after the parent is built anyway.
        """
        self._dirty_widgets.add(widget)

        if not include_children_recursively or not isinstance(
            widget, widget_base.FundamentalWidget
        ):
            return

        for child in widget._iter_direct_children():
            self._register_dirty_widget(
                child,
                include_children_recursively=True,
            )

    def _refresh_sync(self) -> Tuple[Set[rx.Widget], Dict[int, JsonDoc]]:
        """
        See `refresh` for details on what this function does.

        The refresh process must be performed atomically, without ever yielding
        control flow to the async event loop. TODO WHY

        To make sure async isn't used unintentionally this part of the refresh
        function is split into a separate, synchronous function.

        The session keeps track of widgets which are no longer referenced in its
        widget tree. Those widgets are NOT included in the function's result.
        """

        # Keep track of all widgets which are visited. Only they will be sent to
        # the client.
        visited_widgets: collections.Counter[rx.Widget] = collections.Counter()

        # Build all dirty widgets
        while self._dirty_widgets:
            widget = self._dirty_widgets.pop()

            # Remember that this widget has been visited
            visited_widgets[widget] += 1

            # Catch deep recursions and abort
            build_count = visited_widgets[widget]
            if build_count > 5:
                raise RecursionError(
                    f"The widget `{widget}` has been rebuilt {build_count} times during a single refresh. This is likely because one of your widgets' `build` methods is modifying the widget's state"
                )

            # Fundamental widgets require no further treatment
            if isinstance(widget, widget_base.FundamentalWidget):
                continue

            # Others need to be built
            global_state.currently_building_widget = widget
            global_state.currently_building_session = self

            try:
                build_result = widget.build()
            finally:
                global_state.currently_building_widget = None
                global_state.currently_building_session = None

            # Has this widget been built before?
            try:
                widget_data = self._lookup_widget_data(widget)

            # No, this is the first time
            except KeyError:
                # Create the widget data and cache it
                widget_data = WidgetData(build_result, 0)
                self._weak_widget_data_by_widget[widget] = widget_data

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
                self._reconcile_tree(widget, widget_data, build_result)

                # Increment the build generation
                widget_data.build_generation = global_state.build_generation
                global_state.build_generation += 1

                # Reconciliation can change the build result. Make sure nobody
                # uses `build_result` instead of `widget_data.build_result` from
                # now on.
                del build_result

            # Inject the builder and build generation
            weak_builder = weakref.ref(widget)

            for child in widget_data.build_result._iter_direct_and_indirect_children(
                include_self=True,
                cross_build_boundaries=False,
            ):
                child._weak_builder_ = weak_builder
                child._build_generation_ = widget_data.build_generation

        # Determine which widgets are alive, to avoid sending references to dead
        # widgets to the frontend.
        alive_cache: Dict[rx.Widget, bool] = {
            self._root_widget: True,
        }

        alive_set = {
            widget
            for widget in visited_widgets
            if widget._is_in_widget_tree(alive_cache)
        }

        # Serialize
        to_serialize = alive_set.copy()
        seralized_widgets: Set[rx.Widget] = set()
        delta_states: Dict[int, JsonDoc] = {}

        while to_serialize:
            cur: rx.Widget = to_serialize.pop()

            # Serialize it. Since this function already has to walk all of the
            # widget's children, it also returns all of them.
            cur_children, cur_serialized = self._serialize_and_host_widget(cur)

            # Add the serialized widget to the result
            seralized_widgets.add(cur)
            delta_states[cur._id] = cur_serialized

            # Any children of this widget are also definitely alive. If they
            # haven't been found to be alive yet, do so now.
            if isinstance(cur, widget_base.FundamentalWidget):
                new_alives = cur_children - alive_set

                to_serialize.update(new_alives)
                alive_set.update(new_alives)

                for child in new_alives:
                    cur_builder = cur._weak_builder_()
                    assert cur_builder is not None

                    child._weak_builder_ = cur._weak_builder_
                    child._build_generation_ = self._lookup_widget_data(
                        cur_builder
                    ).build_generation

        return seralized_widgets, delta_states

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
            visited_widgets, delta_states = self._refresh_sync()

            assert len(visited_widgets) == len(delta_states), (
                visited_widgets,
                delta_states,
            )

            # Avoid sending empty messages
            if not visited_widgets:
                return

            # Initialize all HTML widgets
            for widget in visited_widgets:
                if (
                    not isinstance(widget, widget_base.FundamentalWidget)
                    or type(widget)._unique_id in self._initialized_html_widgets
                ):
                    continue

                await widget._initialize_on_client(self)
                self._initialized_html_widgets.add(type(widget)._unique_id)

            # Check whether the root widget needs replacing
            if self._root_widget in visited_widgets:
                root_widget_id = self._root_widget._id
            else:
                root_widget_id = None

            # Send the new state to the client
            await self._update_widget_states(delta_states, root_widget_id)

    def _serialize_and_host_value(
        self,
        value: Any,
        type_: Type,
        visited: Set[rx.Widget],
    ) -> Jsonable:
        """
        Which values are serialized for state depends on the annotated
        datatypes. There is no point in sending fancy values over to the client
        which it can't interpret.

        This function attempts to serialize the value, or raises a
        `WontSerialize` exception if this value shouldn't be included in the
        state.

        If the result contains any references to widgets, they are added to the
        `visited` set.
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

        # Sequences of serializable values
        if origin is list:
            return [
                self._serialize_and_host_value(
                    v,
                    args[0],
                    visited,
                )
                for v in value
            ]

        # Self-Serializing
        if isinstance(value, self_serializing.SelfSerializing):
            return value._serialize(self._app_server)

        # ColorSet
        if origin is Union and set(args) == color._color_spec_args:
            thm = self.attachments[theme.Theme]
            return thm._serialize_colorset(value)

        # Optional
        if origin is Union and len(args) == 2 and type(None) in args:
            if value is None:
                return None

            type_ = next(type_ for type_ in args if type_ is not type(None))
            return self._serialize_and_host_value(value, type_, visited)

        # Literal
        if origin is Literal:
            return self._serialize_and_host_value(value, type(value), visited)

        # Widgets
        if introspection.safe_is_subclass(type_, rx.Widget):
            visited.add(value)
            return value._id

        # Invalid type
        raise WontSerialize()

    def _serialize_and_host_widget(
        self,
        widget: rx.Widget,
    ) -> Tuple[Set[rx.Widget], JsonDoc]:
        """
        Serializes the widget, non-recursively. Children are serialized just by
        their `_id`.

        Non-fundamental widgets must have been built, and their output cached in
        the session.

        The result is a tuple of:
        - All widgets which were encountered as children of the given `widget`
        - The serialized widget
        """
        visited: Set[rx.Widget] = set()
        result: JsonDoc = {
            "_python_type_": type(widget).__name__,
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
        for name, type_ in inspection.get_attributes_to_serialize(type(widget)).items():
            try:
                result[name] = self._serialize_and_host_value(
                    getattr(widget, name),
                    type_,
                    visited,
                )
            except WontSerialize:
                pass

        # Encode any internal additional state. Doing it this late allows the custom
        # serialization to overwrite automatically generated values.
        if isinstance(widget, widget_base.FundamentalWidget):
            result["_type_"] = widget._unique_id
            result.update(widget._custom_serialize(self._app_server))

        else:
            # Take care to add underscores to any properties here, as the
            # user-defined state is also added and could clash
            result["_type_"] = "Placeholder"
            result["_child_"] = self._lookup_widget_data(widget).build_result._id

        return visited, result

    def _reconcile_tree(
        self,
        builder: rx.Widget,
        old_build_data: WidgetData,
        new_build: rx.Widget,
    ) -> None:
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

            # Performance optimization: Since the new widget has just been
            # reconciled into the old one, it cannot possibly still be part of
            # the widget tree. It is thus safe to remove from the set of dirty
            # widgets to prevent a pointless rebuild.
            self._dirty_widgets.discard(new_widget)

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

            for attr_name in inspection.get_child_widget_containing_attribute_names(
                type(parent)
            ):
                attr_value = parent_vars[attr_name]

                # Just a widget
                if isinstance(attr_value, rx.Widget):
                    try:
                        attr_value = reconciled_widgets_new_to_old[attr_value]
                    except KeyError:
                        pass
                    else:
                        parent_vars[attr_name] = attr_value

                    remap_widgets(attr_value)

                # List / Collection
                elif isinstance(attr_value, list):
                    for ii, item in enumerate(attr_value):
                        if isinstance(item, rx.Widget):
                            try:
                                item = reconciled_widgets_new_to_old[item]
                            except KeyError:
                                pass

                            attr_value[ii] = item
                            remap_widgets(item)

        remap_widgets(reconciled_build_result)

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
                return old is new or old is reconciled_widgets_new_to_old.get(new, None)

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
                    include_children_recursively=False,
                )
                break

        # Override the key now. It should never be preserved, but doesn't make
        # the widget dirty
        overridden_values["key"] = new_widget.key

        # Now combine the old and new dictionaries
        #
        # Notice that the widget's `_weak_builder_` is always preserved. So even
        # widgets whose position in the tree has changed still have the correct
        # builder set.
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
                include_self=include_self,
                cross_build_boundaries=True,
            ):
                register_widget_by_key(widgets_by_key, child)

        def chain_to_children(
            old_widget: rx.Widget,
            new_widget: rx.Widget,
        ) -> None:
            def _extract_widgets(attr: object) -> List[rx.Widget]:
                if isinstance(attr, rx.Widget):
                    return [attr]

                if isinstance(attr, list):
                    return [item for item in attr if isinstance(item, rx.Widget)]

                return []

            # Iterate over the children, but make sure to preserve the topology.
            # Can't just use `iter_direct_children` here, since that would
            # discard topological information.
            for attr_name in inspection.get_child_widget_containing_attribute_names(
                type(new_widget)
            ):
                old_value = getattr(old_widget, attr_name, None)
                new_value = getattr(new_widget, attr_name, None)

                old_widgets = _extract_widgets(old_value)
                new_widgets = _extract_widgets(new_value)

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

        self._app_server._pending_file_uploads[upload_id] = future

        # Allow the user to specify both `jpg` and `.jpg`
        if file_extensions is not None:
            file_extensions = [
                ext if ext.startswith(".") else f".{ext}" for ext in file_extensions
            ]

        # Tell the frontend to upload a file
        await self._request_file_upload(
            upload_url=f"/reflex/upload/{upload_id}",
            file_extensions=file_extensions,
            multiple=multiple,
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
            return tuple(files)  # type: ignore
        else:
            return files[0]

    async def save_file(
        self,
        file_name: str,
        file_contents: Union[Path, str, bytes],
        *,
        media_type: Optional[str] = None,
    ) -> None:
        # Create an asset for the file
        if isinstance(file_contents, Path):
            as_asset = assets.PathAsset(file_contents, media_type)

        elif isinstance(file_contents, str):
            as_asset = assets.BytesAsset(
                file_contents.encode("utf-8"),
                "text/plain" if media_type is None else media_type,
            )

        elif isinstance(file_contents, bytes):
            as_asset = assets.BytesAsset(
                file_contents,
                "application/octet-stream" if media_type is None else media_type,
            )

        else:
            raise ValueError(
                f"The file contents must be a Path, str or bytes, not {file_contents!r}"
            )

        # Host the asset
        self._app_server.weakly_host_asset(as_asset)

        # Tell the frontend to download the file
        await self._evaluate_javascript(
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

        # Keep the asset alive for some time
        #
        # TODO: Is there a better way to do this
        async def keepaliver() -> None:
            await asyncio.sleep(60)

        asyncio.create_task(keepaliver())

    @unicall.remote(name="updateWidgetStates", parameter_format="dict")
    async def _update_widget_states(
        self,
        # Maps widget ids to serialized widgets. The widgets may be partial,
        # i.e. any property may be missing.
        delta_states: Dict[int, Any],
        # Tells the client to make the given widget the new root widget.
        root_widget_id: Optional[int],
    ) -> None:
        """
        Replace all widgets in the UI with the given one.
        """
        raise NotImplementedError

    @unicall.remote(name="evaluateJavaScript", parameter_format="dict")
    async def _evaluate_javascript(self, java_script_source: str) -> Any:
        """
        Evaluate the given javascript code in the client.
        """
        raise NotImplementedError

    @unicall.remote(name="requestFileUpload", parameter_format="dict")
    async def _request_file_upload(
        self,
        upload_url: str,
        file_extensions: Optional[List[str]],
        multiple: bool,
    ) -> None:
        """
        Tell the client to upload a file to the server.
        """
        raise NotImplementedError

    @unicall.remote(name="setUserSettings")
    async def _set_user_settings(self, delta_settings: Dict[str, Any]) -> None:
        """
        Persistently store the given key-value pairs at the user. The values
        have to be jsonable.

        Any keys not present here are still preserved. Thus the function
        effectively behaves like `dict.update`.
        """
        raise NotImplementedError

    def _try_get_widget_for_message(self, widget_id: int) -> Optional[rx.Widget]:
        """
        Attempts to get the widget referenced by `widget_id`. Returns `None` if
        there is no such widget. This can happen during normal opration, e.g.
        because a widget has been deleted while the message was in flight.
        """

        try:
            return self._lookup_widget(widget_id)
        except KeyError:
            logging.warn(
                f"Encountered message for unknown widget {widget_id}. (The widget might have been deleted in the meantime.)"
            )
            return None

    @unicall.local(name="widgetStateUpdate")
    async def _widget_state_update(
        self,
        widget_id: int,
        delta_state: Any,
    ) -> None:
        # Get the widget
        widget = self._try_get_widget_for_message(widget_id)

        if widget is None:
            return

        # Update the widget's state
        assert isinstance(widget, widget_base.FundamentalWidget), widget
        await widget._on_state_update(delta_state)

    @unicall.local(name="widgetMessage")
    async def widget_message(
        self,
        widget_id: int,
        payload: Any,
    ) -> None:
        # Get the widget
        widget = self._try_get_widget_for_message(widget_id)

        if widget is None:
            return

        # Let the widget handle the message
        await widget._on_message(payload)

    @unicall.local(name="ping")
    async def _ping(self, ping: str) -> str:
        return "pong"

    @unicall.local(name="onUrlChange")
    async def _on_url_change(self, new_route: str) -> None:
        """
        Called by the client when the route changes.
        """
        print(f"TODO: The browser has navigated to {new_route}")
