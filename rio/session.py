from __future__ import annotations

import asyncio
import collections
import enum
import inspect
import json
import logging
import secrets
import time
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

import rio

from . import (
    app_server,
    assets,
    color,
    common,
    errors,
    font,
    global_state,
    inspection,
    routing,
    self_serializing,
    text_style,
    theme,
    user_settings_module,
)
from .widgets import widget_base

__all__ = ["Session"]


T = typing.TypeVar("T")


@dataclass
class WidgetData:
    build_result: rio.Widget

    # Keep track of how often this widget has been built. This is used by
    # widgets to determine whether they are still part of their parent's current
    # build output.
    build_generation: int


class WontSerialize(Exception):
    pass


async def dummy_send_message(message: Jsonable) -> None:
    raise NotImplementedError()


async def dummy_receive_message() -> JsonDoc:
    raise NotImplementedError()


def _host_and_get_fill_as_css_variables(
    fill: rio.FillLike, sess: "Session"
) -> Dict[str, str]:
    # Convert the fill
    fill = rio.Fill._try_from(fill)

    if isinstance(fill, rio.SolidFill):
        return {
            "text-color": f"#{fill.color.hex}",
            "text-background": "none",
            "text-background-clip": "border-box",
            "text-fill-color": "transparent",
        }

    assert isinstance(fill, (rio.LinearGradientFill, rio.ImageFill)), fill
    return {
        "text-color": "var(--rio-local-text-color)",
        "text-background": fill._as_css_background(sess),
        "text-background-clip": "text",
        "text-fill-color": "transparent",
    }


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
                old_value._rio_session_ = None

            # Link the new value to the session
            value._rio_session_ = self._session

            # Trigger a resync
            if synchronize:
                self._session._create_task(
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
        app_server_: app_server.AppServer,
        base_url: rio.URL,
        initial_route: rio.URL,
    ):
        super().__init__(
            send_message=dummy_send_message,
            receive_message=dummy_receive_message,
        )

        self._app_server = app_server_

        # Widgets need unique ids, but we don't want them to be globally unique
        # because then people could guesstimate the approximate number of
        # visitors on a server based on how quickly the widget ids go up. So
        # each session will assign its widgets ids starting from 0.
        self._next_free_widget_id: int = 0

        # Keep track of the last time we successfully communicated with the
        # client. After a while with no communication we close the session.
        self._last_interaction_timestamp = time.monotonic()

        # The URL to the app's root directory. The current route will always
        # start with this.
        assert base_url.is_absolute(), base_url
        self._base_url = base_url

        # The current route. This is publicly accessible as property
        assert initial_route.is_absolute(), initial_route
        self._active_route: rio.URL = initial_route

        # Also the current route, but as stack of the actual route instances
        self._active_route_instances: Tuple[rio.Route, ...] = ()

        # Keeps track of running asyncio tasks. This is used to make sure that
        # the tasks are cancelled when the session is closed.
        self._running_tasks: Set[asyncio.Task] = set()

        # Maps all routers to the id of the router one higher up in the widget
        # tree. Root routers are mapped to None. This map is kept up to date by
        # routers themselves.
        self._routers: weakref.WeakKeyDictionary[
            rio.Router, Optional[int]
        ] = weakref.WeakKeyDictionary()

        # All widgets / methods which should be called when the session's route
        # has changed.
        #
        # The methods don't have the widget bound yet, so they don't unduly
        # prevent the widget from being garbage collected.
        self._route_change_callbacks: weakref.WeakKeyDictionary[
            rio.Widget, Callable[[rio.Widget], None]
        ] = weakref.WeakKeyDictionary()

        # All widgets / methods which should be called when the session's window
        # size has changed.
        self._on_window_resize_callbacks: weakref.WeakKeyDictionary[
            rio.Widget, Callable[[rio.Widget], None]
        ] = weakref.WeakKeyDictionary()

        # All fonts which have been registered with the session. This maps the
        # name of the font to the font's assets, which ensures that the assets
        # are kept alive until the session is closed.
        self._registered_font_assets: Dict[str, List[assets.Asset]] = {
            font.ROBOTO.name: [],
            font.ROBOTO_MONO.name: [],
        }

        # These are injected by the app server after the session has already been created
        self._root_widget: rio.Widget
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
            int, rio.Widget
        ] = weakref.WeakValueDictionary()

        self._weak_widget_data_by_widget: weakref.WeakKeyDictionary[
            rio.Widget, WidgetData
        ] = weakref.WeakKeyDictionary()

        # Keep track of all dirty widgets, once again, weakly.
        #
        # Widgets are dirty if any of their properties have changed since the
        # last time they were built. Newly created widgets are also considered
        # dirty.
        #
        # Use `register_dirty_widget` to add a widget to this set.
        self._dirty_widgets: weakref.WeakSet[rio.Widget] = weakref.WeakSet()

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
    def app(self) -> rio.App:
        """
        Returns the app which this session belongs to.
        """
        return self._app_server.app

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
    def base_url(self) -> rio.URL:
        """
        Returns the base URL of the app.

        Only available when running as a website.
        """
        if self._app_server.running_in_window:
            raise RuntimeError(
                f"Cannot get the base URL of an app that is running in a window"
            )

        return self._base_url

    @property
    def active_route(self) -> rio.URL:
        """
        Returns the current route as a tuple of strings.

        This property is read-only. To change the route, use `Session.navigate_to`.
        """
        return self._active_route

    @property
    def active_route_instances(self) -> Tuple[rio.Route, ...]:
        """
        Returns the current route as a tuple of `Route` instances.

        This property is read-only. To change the route, use `Session.navigate_to`.
        """
        return self._active_route_instances

    @overload
    async def _call_event_handler(
        self,
        handler: common.EventHandler[[]],
    ) -> None:
        ...

    @overload
    async def _call_event_handler(
        self,
        handler: common.EventHandler[[T]],
        event_data: T,
        /,
    ) -> None:
        ...

    async def _call_event_handler(self, handler, *event_data) -> None:
        # Event handlers are optional
        if handler is None:
            return

        # If the handler is available, call it and await it if necessary
        try:
            result = handler(*event_data)

            if inspect.isawaitable(result):
                await result

        # Display and discard exceptions
        except Exception:
            print("Exception in event handler:")
            traceback.print_exc()

    def _create_task(self, coro: Coroutine, name: Optional[str] = None) -> asyncio.Task:
        """
        Creates an `asyncio.Task` that is cancelled when the session is closed.
        """
        task = asyncio.create_task(coro, name=name)

        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.remove)

        return task

    def _close(self):
        # Cancel all running tasks
        for task in self._running_tasks:
            task.cancel()

    def navigate_to(
        self,
        target_url: Union[rio.URL, str],
        *,
        replace: bool = False,
    ) -> None:
        """
        Switches the app to display the given route.

        If `replace` is `True`, the browser's most recent history entry is
        replaced with the new route. This means that the user can't go back to
        the previous route using the browser's back button. If `False`, a new
        history entry is created, allowing the user to go back to the previous
        route.
        """

        # Determine the full route to navigate to
        target_url_absolute = self.active_route.join(rio.URL(target_url))

        # Is this a route, or a full URL to another site?
        try:
            target_url_relative = common.make_url_relative(
                self._base_url,
                target_url_absolute,
            )

        # This is an external URL. Navigate to it
        except ValueError:

            async def history_worker() -> None:
                await self._evaluate_javascript(
                    f"window.location.href = {json.dumps(str(target_url))}",
                )

            self._create_task(history_worker(), name="history worker")
            return

        # Is any guard opposed to this route?
        active_route_instances, active_route = routing.check_route_guards(
            self,
            target_url_relative,
            target_url_absolute,
        )

        # Update the current route
        self._active_route = active_route
        self._active_route_instances = tuple(active_route_instances)

        # Dirty all routers to force a rebuild
        for router in self._routers:
            self._register_dirty_widget(router, include_children_recursively=False)

        self._create_task(self._refresh())

        # Update the browser's history
        async def history_worker() -> None:
            method = "replaceState" if replace else "pushState"
            await self._evaluate_javascript(
                f"window.history.{method}(null, null, {json.dumps(str(target_url))})",
            )

        self._create_task(history_worker())

        # Trigger the `on_route_change` event
        async def event_worker() -> None:
            for widget, callback in self._route_change_callbacks.items():
                self._create_task(
                    self._call_event_handler(callback, widget),
                    name="`on_route_change` event handler",
                )

        self._create_task(event_worker())

    def _register_dirty_widget(
        self,
        widget: rio.Widget,
        *,
        include_children_recursively: bool,
    ) -> None:
        """
        Add the widget to the set of dirty widgets. The widget is only held
        weakly by the session.

        If `include_children_recursively` is true, all children of the widget
        are also added.

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

    def _refresh_sync(self) -> Set[rio.Widget]:
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
        visited_widgets: collections.Counter[rio.Widget] = collections.Counter()

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
                widget_data = self._weak_widget_data_by_widget[widget]

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

            children = widget_data.build_result._iter_direct_and_indirect_child_containing_attributes(
                include_self=True,
                recurse_into_high_level_widgets=False,
            )
            for child in children:
                child._weak_builder_ = weak_builder
                child._build_generation_ = widget_data.build_generation

        # Determine which widgets are alive, to avoid sending references to dead
        # widgets to the frontend.
        alive_cache: Dict[rio.Widget, bool] = {
            self._root_widget: True,
        }

        return {
            widget
            for widget in visited_widgets
            if widget._is_in_widget_tree(alive_cache)
        }

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

            # Serialize all widgets which have been visited
            delta_states: Dict[int, JsonDoc] = {
                widget._id: self._serialize_and_host_widget(widget)
                for widget in visited_widgets
            }

            await self._update_widget_states(visited_widgets, delta_states)

    async def _update_widget_states(
        self, visited_widgets: Set[rio.Widget], delta_states: Dict[int, JsonDoc]
    ) -> None:
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
        await self._remote_update_widget_states(delta_states, root_widget_id)

    async def _send_reconnect_message(self) -> None:
        self._initialized_html_widgets.clear()

        # For why this lock is here see its creation in `__init__`
        async with self._refresh_lock:
            visited_widgets = set()
            delta_states = {}

            for widget in self._root_widget._iter_widget_tree():
                visited_widgets.add(widget)
                delta_states[widget._id] = self._serialize_and_host_widget(widget)

            await self._update_widget_states(visited_widgets, delta_states)

    def _serialize_and_host_value(
        self,
        value: Any,
        type_: Type,
    ) -> Jsonable:
        """
        Which values are serialized for state depends on the annotated
        datatypes. There is no point in sending fancy values over to the client
        which it can't interpret.

        This function attempts to serialize the value, or raises a
        `WontSerialize` exception if this value shouldn't be included in the
        state.
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
            return [self._serialize_and_host_value(v, args[0]) for v in value]

        # ColorSet
        # Important: This must happen before the SelfSerializing check, because
        # `value` might be a `Color`
        if origin is Union and set(args) == color._color_spec_args:
            thm = self.attachments[theme.Theme]
            return thm._serialize_colorset(value)

        # Self-Serializing
        if isinstance(value, self_serializing.SelfSerializing):
            return value._serialize(self)

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
        if introspection.safe_is_subclass(type_, rio.Widget):
            return value._id

        # Invalid type
        raise WontSerialize()

    def _serialize_and_host_widget(
        self,
        widget: rio.Widget,
    ) -> JsonDoc:
        """
        Serializes the widget, non-recursively. Children are serialized just by
        their `_id`.

        Non-fundamental widgets must have been built, and their output cached in
        the session.
        """
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

        # If it's a fundamental widget, serialize its state because JS needs it.
        # For non-fundamental widgets, there's no reason to send the state to
        # the frontend.
        if isinstance(widget, widget_base.FundamentalWidget):
            for name, type_ in inspection.get_attributes_to_serialize(
                type(widget)
            ).items():
                try:
                    result[name] = self._serialize_and_host_value(
                        getattr(widget, name),
                        type_,
                    )
                except WontSerialize:
                    pass

        # Encode any internal additional state. Doing it this late allows the custom
        # serialization to overwrite automatically generated values.
        if isinstance(widget, widget_base.FundamentalWidget):
            result["_type_"] = widget._unique_id
            result.update(widget._custom_serialize())

        else:
            # Take care to add underscores to any properties here, as the
            # user-defined state is also added and could clash
            result["_type_"] = "Placeholder"
            result["_child_"] = self._weak_widget_data_by_widget[
                widget
            ].build_result._id

        return result

    def _reconcile_tree(
        self,
        builder: rio.Widget,
        old_build_data: WidgetData,
        new_build: rio.Widget,
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
        reconciled_widgets_new_to_old: Dict[rio.Widget, rio.Widget] = {
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
        def remap_widgets(parent: rio.Widget) -> None:
            parent_vars = vars(parent)

            for attr_name in inspection.get_child_widget_containing_attribute_names(
                type(parent)
            ):
                attr_value = parent_vars[attr_name]

                # Just a widget
                if isinstance(attr_value, rio.Widget):
                    try:
                        attr_value = reconciled_widgets_new_to_old[attr_value]
                    except KeyError:
                        # Make sure that any widgets which are now in the tree
                        # have their builder properly set.
                        if isinstance(parent, widget_base.FundamentalWidget):
                            attr_value._weak_builder_ = parent._weak_builder_
                            attr_value._build_generation_ = parent._build_generation_
                    else:
                        parent_vars[attr_name] = attr_value

                    remap_widgets(attr_value)

                # List / Collection
                elif isinstance(attr_value, list):
                    for ii, item in enumerate(attr_value):
                        if isinstance(item, rio.Widget):
                            try:
                                item = reconciled_widgets_new_to_old[item]
                            except KeyError:
                                # Make sure that any widgets which are now in
                                # the tree have their builder properly set.
                                if isinstance(parent, widget_base.FundamentalWidget):
                                    item._weak_builder_ = parent._weak_builder_
                                    item._build_generation_ = parent._build_generation_
                            else:
                                attr_value[ii] = item

                            remap_widgets(item)

        remap_widgets(reconciled_build_result)

    def _reconcile_widget(
        self,
        old_widget: rio.Widget,
        new_widget: rio.Widget,
        reconciled_widgets_new_to_old: Dict[rio.Widget, rio.Widget],
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

        for prop_name in new_widget._state_properties_:
            # Should the value be overridden?
            if prop_name not in new_widget._explicitly_set_properties_:
                continue

            # Take care to keep state bindings up to date
            old_value = old_widget_dict[prop_name]
            new_value = new_widget_dict[prop_name]
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

            overridden_values[prop_name] = new_value

        # If the widget has changed mark it as dirty
        def values_equal(old: object, new: object) -> bool:
            """
            Used to compare the old and new values of a property. Returns `True`
            if the values are considered equal, `False` otherwise.
            """
            # Widgets are a special case. Widget attributes are dirty iff the
            # widget isn't reconciled, i.e. it is a new widget
            if isinstance(new, rio.Widget):
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
        old_build: rio.Widget,
        new_build: rio.Widget,
    ) -> Iterable[Tuple[rio.Widget, rio.Widget]]:
        """
        Given two widget trees, find pairs of widgets which can be
        reconciled, i.e. which represent the "same" widget. When exactly
        widgets are considered to be the same is up to the implementation and
        best-effort.

        Returns an iterable over (old_widget, new_widget) pairs, as well as a
        list of all widgets occurring in the new tree, which did not have a match
        in the old tree.
        """

        old_widgets_by_key: Dict[str, rio.Widget] = {}
        new_widgets_by_key: Dict[str, rio.Widget] = {}

        matches_by_topology: List[Tuple[rio.Widget, rio.Widget]] = []

        # First scan all widgets for topological matches, and also keep track of
        # each widget by its key
        def register_widget_by_key(
            widgets_by_key: Dict[str, rio.Widget],
            widget: rio.Widget,
        ) -> None:
            if widget.key is None:
                return

            if widget.key in widgets_by_key:
                raise RuntimeError(
                    f'Multiple widgets share the key "{widget.key}": {widgets_by_key[widget.key]} and {widget}'
                )

            widgets_by_key[widget.key] = widget

        def key_scan(
            widgets_by_key: Dict[str, rio.Widget],
            widget: rio.Widget,
            include_self: bool = True,
        ) -> None:
            for child in widget._iter_direct_and_indirect_child_containing_attributes(
                include_self=include_self,
                recurse_into_high_level_widgets=True,
            ):
                register_widget_by_key(widgets_by_key, child)

        def chain_to_children(
            old_widget: rio.Widget,
            new_widget: rio.Widget,
        ) -> None:
            def _extract_widgets(attr: object) -> List[rio.Widget]:
                if isinstance(attr, rio.Widget):
                    return [attr]

                if isinstance(attr, list):
                    return [item for item in attr if isinstance(item, rio.Widget)]

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

        def worker(old_widget: rio.Widget, new_widget: rio.Widget) -> None:
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

    def _register_font(self, font: text_style.Font) -> None:
        # Fonts are different from other assets because they need to be
        # registered under a name, not just a URL. We don't want to re-register
        # the same font multiple times, so we keep track of all registered
        # fonts. Every registered font is associated with all its assets
        # (regular, bold, italic, ...), which will be kept alive until the
        # session is closed.
        if font.name in self._registered_font_assets:
            return

        # It's a new font, register it
        font_assets: List[assets.Asset] = []
        urls: List[Optional[str]] = [None] * 4

        for i, location in enumerate(
            (font.regular, font.bold, font.italic, font.bold_italic)
        ):
            if location is None:
                continue

            # Host the font file as an asset
            asset = assets.Asset.new(location)
            urls[i] = asset._serialize(self)

            font_assets.append(asset)

        self._create_task(self._remote_register_font(font.name, urls))  # type: ignore

        self._registered_font_assets[font.name] = font_assets

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
            upload_url=f"/rio/upload/{upload_id}",
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
        url = as_asset._serialize(self)

        # Tell the frontend to download the file
        await self._evaluate_javascript(
            f"""
const a = document.createElement('a')
a.href = {json.dumps(url)}
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
            holdonewellgethelp = as_asset
            await asyncio.sleep(60)

        self._create_task(keepaliver())

    async def _apply_theme(self, thm: theme.Theme) -> None:
        """
        Updates the client's theme to match the given one.
        """
        # Build the set of all variables

        # Miscellaneous
        variables: Dict[str, str] = {
            "--rio-global-corner-radius-small": f"{thm.corner_radius_small}rem",
            "--rio-global-corner-radius-large": f"{thm.corner_radius_large}rem",
            "--rio-global-shadow-radius": f"{thm.shadow_radius}rem",
        }

        # Theme Colors
        color_names = (
            "primary_color",
            "secondary_color",
            "disabled_color",
            "primary_color_variant",
            "secondary_color_variant",
            "disabled_color_variant",
            "background_color",
            "surface_color",
            "surface_color_variant",
            "surface_active_color",
            "success_color",
            "warning_color",
            "danger_color",
            "success_color_variant",
            "warning_color_variant",
            "danger_color_variant",
            "shadow_color",
            "text_color_on_light",
            "text_color_on_dark",
        )

        for py_color_name in color_names:
            css_color_name = f'--rio-global-{py_color_name.replace("_", "-")}'
            color = getattr(thm, py_color_name)
            assert isinstance(color, rio.Color), color
            variables[css_color_name] = f"#{color.hex}"

        # Text styles
        style_names = (
            "heading1",
            "heading2",
            "heading3",
            "text",
        )

        for style_name in style_names:
            style = getattr(thm, f"{style_name}_style")
            assert isinstance(style, rio.TextStyle), style

            css_prefix = f"--rio-global-{style_name}"
            variables[f"{css_prefix}-font-name"] = style.font._serialize(self)
            variables[f"{css_prefix}-font-size"] = f"{style.font_size}rem"
            variables[f"{css_prefix}-italic"] = "italic" if style.italic else "normal"
            variables[f"{css_prefix}-font-weight"] = style.font_weight
            variables[f"{css_prefix}-underlined"] = (
                "underline" if style.underlined else "unset"
            )
            variables[f"{css_prefix}-all-caps"] = (
                "uppercase" if style.all_caps else "unset"
            )

            # CSS variables for the fill
            fill_variables = _host_and_get_fill_as_css_variables(style.fill, self)

            for var, value in fill_variables.items():
                variables[f"{css_prefix}-{var}"] = value

        # Colors derived from, but not stored in the theme
        derived_colors = {
            "text-on-primary-color": thm.text_color_for(thm.primary_color),
            "text-on-secondary-color": thm.text_color_for(thm.secondary_color),
            "text-on-success-color": thm.text_color_for(thm.success_color),
            "text-on-warning-color": thm.text_color_for(thm.warning_color),
            "text-on-danger-color": thm.text_color_for(thm.danger_color),
        }

        for css_name, color in derived_colors.items():
            variables[f"--rio-global-{css_name}"] = f"#{color.hex}"

        # Update the variables client-side
        await self._remote_apply_theme(
            variables,
            "light" if thm.background_color.perceived_brightness > 0.5 else "dark",
        )

    @unicall.remote(
        name="applyTheme",
        parameter_format="dict",
        await_response=False,
    )
    async def _remote_apply_theme(
        self,
        css_variables: Dict[str, str],
        theme_variant: Literal["light", "dark"],
    ) -> None:
        raise NotImplementedError

    @unicall.remote(
        name="updateWidgetStates",
        parameter_format="dict",
        await_response=False,
    )
    async def _remote_update_widget_states(
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

    @unicall.remote(
        name="evaluateJavaScript",
        parameter_format="dict",
        await_response=True,
    )
    async def _evaluate_javascript(self, java_script_source: str) -> Any:
        """
        Evaluate the given javascript code in the client.
        """
        raise NotImplementedError

    @unicall.remote(
        name="requestFileUpload",
        parameter_format="dict",
        await_response=False,
    )
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

    @unicall.remote(name="setUserSettings", await_response=False)
    async def _set_user_settings(self, delta_settings: Dict[str, Any]) -> None:
        """
        Persistently store the given key-value pairs at the user. The values
        have to be jsonable.

        Any keys not present here are still preserved. Thus the function
        effectively behaves like `dict.update`.
        """
        raise NotImplementedError

    @unicall.remote(name="registerFont", await_response=False)
    async def _remote_register_font(self, name: str, urls: List[Optional[str]]) -> None:
        raise NotImplementedError

    def _try_get_widget_for_message(self, widget_id: int) -> Optional[rio.Widget]:
        """
        Attempts to get the widget referenced by `widget_id`. Returns `None` if
        there is no such widget. This can happen during normal opration, e.g.
        because a widget has been deleted while the message was in flight.
        """

        try:
            return self._weak_widgets_by_id[widget_id]
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
    async def _on_url_change(self, new_url: str) -> None:
        """
        Called by the client when the route changes.
        """
        # Try to navigate to the new route
        self.navigate_to(
            new_url,
            replace=True,
        )

        # Refresh the session
        await self._refresh()

    @unicall.local(name="onWindowResize")
    async def _on_window_resize(self, new_width: float, new_height: float) -> None:
        """
        Called by the client when the window is resized.
        """
        # Update the stored window size
        self._window_width = new_width
        self._window_height = new_height

        # Call any registered callbacks
        for widget, callback in self._on_window_resize_callbacks.items():
            self._create_task(
                self._call_event_handler(callback, widget),
                name="`on_window_resize` event handler",
            )
