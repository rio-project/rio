from __future__ import annotations

import asyncio
import collections
import copy
import enum
import inspect
import json
import logging
import secrets
import shutil
import time
import traceback
import typing
import weakref
from dataclasses import dataclass
from datetime import tzinfo
from pathlib import Path
from typing import *  # type: ignore

import aiofiles
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
from .components import component_base

__all__ = ["Session"]


T = typing.TypeVar("T")


@dataclass
class ComponentData:
    build_result: rio.Component

    # Keep track of how often this component has been built. This is used by
    # components to determine whether they are still part of their parent's current
    # build output.
    build_generation: int


class WontSerialize(Exception):
    pass


async def dummy_send_message(message: Jsonable) -> None:
    raise NotImplementedError()


async def dummy_receive_message() -> JsonDoc:
    raise NotImplementedError()


def _host_and_get_fill_as_css_variables(
    fill: rio.FillLike,
    sess: "Session",
) -> Dict[str, str]:
    # Convert the fill
    fill = rio.Fill._try_from(fill)

    if isinstance(fill, rio.SolidFill):
        return {
            "color": f"#{fill.color.hex}",
            "background": "none",
            "background-clip": "unset",
            "fill-color": "unset",
        }

    assert isinstance(fill, (rio.LinearGradientFill, rio.ImageFill)), fill
    return {
        "color": "var(--rio-local-text-color)",
        "background": fill._as_css_background(sess),
        "background-clip": "text",
        "fill-color": "transparent",
    }


class SessionAttachments:
    def __init__(self, sess: Session):
        self._session = sess
        self._attachments: Dict[type, object] = {}

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
                self._session.create_task(
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
    Represents a single client connection to the app.

    A session corresponds to a single connection to a client. It maintains all
    state related to this client including local settings, the currently active
    page, and others.

    Sessions are created automatically by the app and should not be created
    manually.
    """

    def __init__(
        self,
        app_server_: app_server.AppServer,
        base_url: rio.URL,
        initial_page: rio.URL,
    ):
        super().__init__(
            send_message=dummy_send_message,
            receive_message=dummy_receive_message,
        )

        self._app_server = app_server_

        # Components need unique ids, but we don't want them to be globally unique
        # because then people could guesstimate the approximate number of
        # visitors on a server based on how quickly the component ids go up. So
        # each session will assign its components ids starting from 0.
        self._next_free_component_id: int = 0

        # Keep track of the last time we successfully communicated with the
        # client. After a while with no communication we close the session.
        self._last_interaction_timestamp = time.monotonic()

        # The URL to the app's root/index page. The current page url will always
        # start with this.
        assert base_url.is_absolute(), base_url
        self._base_url = base_url

        # The current page. This is publicly accessible as property
        assert initial_page.is_absolute(), initial_page
        self._active_page_url: rio.URL = initial_page

        # Also the current page url, but as stack of the actual page instances
        self._active_page_instances: Tuple[rio.Page, ...] = ()

        # Keeps track of running asyncio tasks. This is used to make sure that
        # the tasks are cancelled when the session is closed.
        self._running_tasks: Set[asyncio.Task[object]] = set()

        # Maps all PageViews to the id of the PageView one higher up in the component
        # tree. Root PageViews are mapped to None. This map is kept up to date by
        # PageViews themselves.
        self._page_views: weakref.WeakKeyDictionary[
            rio.PageView, Optional[int]
        ] = weakref.WeakKeyDictionary()

        # All components / methods which should be called when the session's
        # page has changed.
        #
        # The methods don't have the component bound yet, so they don't unduly
        # prevent the component from being garbage collected.
        self._page_change_callbacks: weakref.WeakKeyDictionary[
            rio.Component, Callable[[rio.Component], None]
        ] = weakref.WeakKeyDictionary()

        # All components / methods which should be called when the session's window
        # size has changed.
        self._on_window_resize_callbacks: weakref.WeakKeyDictionary[
            rio.Component, Callable[[rio.Component], None]
        ] = weakref.WeakKeyDictionary()

        # All fonts which have been registered with the session. This maps the
        # name of the font to the font's assets, which ensures that the assets
        # are kept alive until the session is closed.
        self._registered_font_assets: Dict[str, List[assets.Asset]] = {
            font.ROBOTO.name: [],
            font.ROBOTO_MONO.name: [],
        }

        # These are injected by the app server after the session has already been created
        self._root_component: rio.Component
        self.external_url: Optional[str]  # None if running in a window
        self.preferred_locales: Tuple[
            babel.Locale, ...
        ]  # Always has at least one member
        self.timezone: tzinfo

        self.window_width: float
        self.window_height: float

        # Must be acquired while synchronizing the user's settings
        self._settings_sync_lock = asyncio.Lock()

        # If `running_in_window`, this contains all the settings loaded from the
        # json file. We need to keep this around so that we can update the
        # settings that have changed and write everything back to the file.
        self._settings_json: Dict[str, object] = {}

        # Weak dictionaries to hold additional information about components.
        # These are split in two to avoid the dictionaries keeping the
        # components alive. Notice how both dictionaries are weak on the actual
        # component.
        #
        # Never access these directly. Instead, use helper functions
        # - `lookup_component`
        # - `lookup_component_data`
        self._weak_components_by_id: weakref.WeakValueDictionary[
            int, rio.Component
        ] = weakref.WeakValueDictionary()

        self._weak_component_data_by_component: weakref.WeakKeyDictionary[
            rio.Component, ComponentData
        ] = weakref.WeakKeyDictionary()

        # Keep track of all dirty components, once again, weakly.
        #
        # Components are dirty if any of their properties have changed since the
        # last time they were built. Newly created components are also considered
        # dirty.
        #
        # Use `register_dirty_component` to add a component to this set.
        self._dirty_components: weakref.WeakSet[rio.Component] = weakref.WeakSet()

        # HTML components have source code which must be evaluated by the client
        # exactly once. Keep track of which components have already sent their
        # source code.
        self._initialized_html_components: Set[str] = set(
            inspection.get_child_component_containing_attribute_names_for_builtin_components()
        )

        # This lock is used to order state updates that are sent to the client.
        # Without it a message which was generated later might be sent to the
        # client before an earlier message, leading to invalid component
        # references.
        self._refresh_lock = asyncio.Lock()

        # Attachments. These are arbitrary values which are passed around inside
        # of the app. They can be looked up by their type.
        # Note: These are initialized by the AppServer.
        self.attachments = SessionAttachments(self)

        # This allows easy access to the app's assets. Users can simply write
        # `component.session.assets / "my_asset.png"`.
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
    def active_page_url(self) -> rio.URL:
        """
        Returns the current page as a tuple of strings.

        This property is read-only. To change the page, use `Session.navigate_to`.
        """
        return self._active_page_url

    @property
    def active_page_instances(self) -> Tuple[rio.Page, ...]:
        """
        Returns the current page as a tuple of `Page` instances.

        This property is read-only. To change the page, use `Session.navigate_to`.
        """
        return self._active_page_instances

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

    async def _call_event_handler(
        self,
        handler: common.EventHandler[...],
        *event_data: object,
    ) -> None:
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

    def create_task(
        self,
        coro: Coroutine[Any, Any, T],
        *,
        name: Optional[str] = None,
    ) -> asyncio.Task[T]:
        """
        Creates an `asyncio.Task` that is cancelled when the session is closed.

        This is identical to `asyncio.create_task`, except that any tasks are
        automatically cancelled when the session is closed. This makes sure that
        old tasks don't keep piling up long after they are no longer needed.

        Args:
            coro: The coroutine to run.

            name: An optional name for the task. Assigning descriptive names can
                be helpful when debugging.
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
        Switches the app to display the given page URL.

        Switches the app to display the given page URL. If `replace` is `True`,
        the browser's most recent history entry is replaced with the new page.
        This means that the user can't go back to the previous page using the
        browser's back button. If `False`, a new history entry is created,
        allowing the user to go back to the previous page.

        Args:
            target_url: The URL of the page to navigate to.

            replace: If `True`, the browser's most recent history entry is
                replaced with the new page. If `False`, a new history entry is
                created, allowing the user to go back to the previous page.
        """

        # Determine the full page to navigate to
        target_url_absolute = self.active_page_url.join(rio.URL(target_url))

        # Is this a page, or a full URL to another site?
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

            self.create_task(history_worker(), name="history worker")
            return

        # Is any guard opposed to this page?
        active_page_instances, active_page = routing.check_page_guards(
            self,
            target_url_relative,
            target_url_absolute,
        )

        # Update the current page
        self._active_page_url = active_page
        self._active_page_instances = tuple(active_page_instances)

        # Dirty all PageViews to force a rebuild
        for page_view in self._page_views:
            self._register_dirty_component(
                page_view, include_children_recursively=False
            )

        self.create_task(self._refresh())

        # Update the browser's history
        async def history_worker() -> None:
            method = "replaceState" if replace else "pushState"
            await self._evaluate_javascript(
                f"window.history.{method}(null, null, {json.dumps(str(target_url))})",
            )

        self.create_task(history_worker())

        # Trigger the `on_page_change` event
        async def event_worker() -> None:
            for component, callback in self._page_change_callbacks.items():
                self.create_task(
                    self._call_event_handler(callback, component),
                    name="`on_page_change` event handler",
                )

        self.create_task(event_worker())

    def _register_dirty_component(
        self,
        component: rio.Component,
        *,
        include_children_recursively: bool,
    ) -> None:
        """
        Add the component to the set of dirty components. The component is only held
        weakly by the session.

        If `include_children_recursively` is true, all children of the component
        are also added.

        The children of non-fundamental components are not added, since they will
        be added after the parent is built anyway.
        """
        self._dirty_components.add(component)

        if not include_children_recursively or not isinstance(
            component, component_base.FundamentalComponent
        ):
            return

        for child in component._iter_direct_children():
            self._register_dirty_component(
                child,
                include_children_recursively=True,
            )

    def _refresh_sync(self) -> Set[rio.Component]:
        """
        See `refresh` for details on what this function does.

        The refresh process must be performed atomically, without ever yielding
        control flow to the async event loop. TODO WHY

        To make sure async isn't used unintentionally this part of the refresh
        function is split into a separate, synchronous function.

        The session keeps track of components which are no longer referenced in its
        component tree. Those components are NOT included in the function's result.
        """

        # Keep track of all components which are visited. Only they will be sent to
        # the client.
        visited_components: collections.Counter[rio.Component] = collections.Counter()

        # Build all dirty components
        while self._dirty_components:
            component = self._dirty_components.pop()

            # Remember that this component has been visited
            visited_components[component] += 1

            # Catch deep recursions and abort
            build_count = visited_components[component]
            if build_count > 5:
                raise RecursionError(
                    f"The component `{component}` has been rebuilt {build_count} times during a single refresh. This is likely because one of your components' `build` methods is modifying the component's state"
                )

            # Fundamental components require no further treatment
            if isinstance(component, component_base.FundamentalComponent):
                continue

            # Others need to be built
            global_state.currently_building_component = component
            global_state.currently_building_session = self

            try:
                build_result = component.build()
            finally:
                global_state.currently_building_component = None
                global_state.currently_building_session = None

            # Sanity check
            if not isinstance(build_result, rio.Component):  # type: ignore[unnecessary-isinstance]
                raise ValueError(
                    f"The output of `build` methods must be instances of `rio.Component`, but `{component}` returned `{build_result}`"
                )

            # Has this component been built before?
            try:
                component_data = self._weak_component_data_by_component[component]

            # No, this is the first time
            except KeyError:
                # Create the component data and cache it
                component_data = ComponentData(build_result, 0)
                self._weak_component_data_by_component[component] = component_data

            # Yes, rescue state. This will:
            #
            # - Look for components in the build output which correspond to components
            #   in the previous build output, and transfers state from the new
            #   to the old component ("reconciliation")
            #
            # - Replace any references to new, reconciled components in the build
            #   output with the old components instead
            #
            # - Add any dirty components from the build output (new, or old but
            #   changed) to the dirty set.
            #
            # - Update the component data with the build output resulting from the
            #   operations above
            else:
                self._reconcile_tree(component, component_data, build_result)

                # Increment the build generation
                component_data.build_generation = global_state.build_generation
                global_state.build_generation += 1

                # Reconciliation can change the build result. Make sure nobody
                # uses `build_result` instead of `component_data.build_result` from
                # now on.
                del build_result

            # Inject the builder and build generation
            weak_builder = weakref.ref(component)

            children = component_data.build_result._iter_direct_and_indirect_child_containing_attributes(
                include_self=True,
                recurse_into_high_level_components=False,
            )
            for child in children:
                child._weak_builder_ = weak_builder
                child._build_generation_ = component_data.build_generation

        # Determine which components are alive, to avoid sending references to dead
        # components to the frontend.
        alive_cache: Dict[rio.Component, bool] = {
            self._root_component: True,
        }

        return {
            component
            for component in visited_components
            if component._is_in_component_tree(alive_cache)
        }

    async def _refresh(self) -> None:
        """
        Make sure the session state is up to date. Specifically:

        - Call build on all components marked as dirty
        - Recursively do this for all freshly spawned components
        - mark all components as clean

        Afterwards, the client is also informed of any changes, meaning that
        after this method returns there are no more dirty components in the
        session, and Python's state and the client's state are in sync.
        """

        # For why this lock is here see its creation in `__init__`
        async with self._refresh_lock:
            # Refresh and get a set of all components which have been visited
            visited_components = self._refresh_sync()

            # Avoid sending empty messages
            if not visited_components:
                return

            # Serialize all components which have been visited
            delta_states: Dict[int, JsonDoc] = {
                component._id: self._serialize_and_host_component(component)
                for component in visited_components
            }

            await self._update_component_states(visited_components, delta_states)

    async def _update_component_states(
        self, visited_components: Set[rio.Component], delta_states: Dict[int, JsonDoc]
    ) -> None:
        # Initialize all HTML components
        for component in visited_components:
            if (
                not isinstance(component, component_base.FundamentalComponent)
                or type(component)._unique_id in self._initialized_html_components
            ):
                continue

            await component._initialize_on_client(self)
            self._initialized_html_components.add(type(component)._unique_id)

        # Check whether the root component needs replacing
        if self._root_component in visited_components:
            root_component_id = self._root_component._id
        else:
            root_component_id = None

        # Send the new state to the client
        await self._remote_update_component_states(delta_states, root_component_id)

    async def _send_reconnect_message(self) -> None:
        self._initialized_html_components.clear()

        # For why this lock is here see its creation in `__init__`
        async with self._refresh_lock:
            visited_components: Set[component_base.Component] = set()
            delta_states = {}

            for component in self._root_component._iter_component_tree():
                visited_components.add(component)
                delta_states[component._id] = self._serialize_and_host_component(
                    component
                )

            await self._update_component_states(visited_components, delta_states)

    def _serialize_and_host_value(
        self,
        value: Any,
        type_: type,
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
        if origin is Union and set(args) == color._color_set_args:
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

        # Components
        if introspection.safe_is_subclass(type_, rio.Component):
            return value._id

        # Invalid type
        raise WontSerialize()

    def _serialize_and_host_component(
        self,
        component: rio.Component,
    ) -> JsonDoc:
        """
        Serializes the component, non-recursively. Children are serialized just by
        their `_id`.

        Non-fundamental components must have been built, and their output cached in
        the session.
        """
        result: JsonDoc = {
            "_python_type_": type(component).__name__,
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
            component.width if isinstance(component.width, (int, float)) else None,
            component.height if isinstance(component.height, (int, float)) else None,
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
            for name, type_ in inspection.get_attributes_to_serialize(
                type(component)
            ).items():
                try:
                    result[name] = self._serialize_and_host_value(
                        getattr(component, name),
                        type_,
                    )
                except WontSerialize:
                    pass

        # Encode any internal additional state. Doing it this late allows the custom
        # serialization to overwrite automatically generated values.
        if isinstance(component, component_base.FundamentalComponent):
            result["_type_"] = component._unique_id
            result.update(component._custom_serialize())

        else:
            # Take care to add underscores to any properties here, as the
            # user-defined state is also added and could clash
            result["_type_"] = "Placeholder"
            result["_child_"] = self._weak_component_data_by_component[
                component
            ].build_result._id

        return result

    def _reconcile_tree(
        self,
        builder: rio.Component,
        old_build_data: ComponentData,
        new_build: rio.Component,
    ) -> None:
        # Find all pairs of components which should be reconciled
        matched_pairs = list(
            self._find_components_for_reconciliation(
                old_build_data.build_result, new_build
            )
        )

        # Reconciliating individual components requires knowledge of which other
        # components are being reconciled.
        #
        # -> Collect them into a set first.
        reconciled_components_new_to_old: Dict[rio.Component, rio.Component] = {
            new_component: old_component
            for old_component, new_component in matched_pairs
        }

        # Reconcile all matched pairs
        for new_component, old_component in reconciled_components_new_to_old.items():
            self._reconcile_component(
                old_component,
                new_component,
                reconciled_components_new_to_old,
            )

            # Performance optimization: Since the new component has just been
            # reconciled into the old one, it cannot possibly still be part of
            # the component tree. It is thus safe to remove from the set of dirty
            # components to prevent a pointless rebuild.
            self._dirty_components.discard(new_component)

        # Update the component data. If the root component was not reconciled, the new
        # component is the new build result.
        try:
            reconciled_build_result = reconciled_components_new_to_old[new_build]
        except KeyError:
            reconciled_build_result = new_build
            old_build_data.build_result = new_build

        # Replace any references to new reconciled components to old ones instead
        def remap_components(parent: rio.Component) -> None:
            parent_vars = vars(parent)

            for attr_name in inspection.get_child_component_containing_attribute_names(
                type(parent)
            ):
                attr_value = parent_vars[attr_name]

                # Just a component
                if isinstance(attr_value, rio.Component):
                    try:
                        attr_value = reconciled_components_new_to_old[attr_value]
                    except KeyError:
                        # Make sure that any components which are now in the tree
                        # have their builder properly set.
                        if isinstance(parent, component_base.FundamentalComponent):
                            attr_value._weak_builder_ = parent._weak_builder_
                            attr_value._build_generation_ = parent._build_generation_
                    else:
                        parent_vars[attr_name] = attr_value

                    remap_components(attr_value)

                # List / Collection
                elif isinstance(attr_value, list):
                    attr_value = cast(List[object], attr_value)

                    for ii, item in enumerate(attr_value):
                        if isinstance(item, rio.Component):
                            try:
                                item = reconciled_components_new_to_old[item]
                            except KeyError:
                                # Make sure that any components which are now in
                                # the tree have their builder properly set.
                                if isinstance(
                                    parent, component_base.FundamentalComponent
                                ):
                                    item._weak_builder_ = parent._weak_builder_
                                    item._build_generation_ = parent._build_generation_
                            else:
                                attr_value[ii] = item

                            remap_components(item)

        remap_components(reconciled_build_result)

    def _reconcile_component(
        self,
        old_component: rio.Component,
        new_component: rio.Component,
        reconciled_components_new_to_old: Dict[rio.Component, rio.Component],
    ) -> None:
        """
        Given two components of the same type, reconcile them. Specifically:

        - Any state which was explicitly set by the user in the new component's
          constructor is considered explicitly set, and will be copied into the
          old component
        - If any values were changed, the component is registered as dirty with the
          session

        This function also handles `StateBinding`s, for details see comments.
        """
        assert type(old_component) is type(new_component), (
            old_component,
            new_component,
        )

        # Let any following code assume that the two components aren't the same
        # instance
        if old_component is new_component:
            return

        # Determine which properties will be taken from the new component
        overridden_values: Dict[str, object] = {}
        old_component_dict = vars(old_component)
        new_component_dict = vars(new_component)

        for prop_name in new_component._state_properties_:
            # Should the value be overridden?
            if prop_name not in new_component._explicitly_set_properties_:
                continue

            # Take care to keep state bindings up to date
            old_value = old_component_dict[prop_name]
            new_value = new_component_dict[prop_name]
            old_is_binding = isinstance(old_value, component_base.StateBinding)
            new_is_binding = isinstance(new_value, component_base.StateBinding)

            # If the old value was a binding, and the new one isn't, split the
            # tree of bindings. All children are now roots.
            if old_is_binding and not new_is_binding:
                binding_value = old_value.get_value()
                old_value.owning_component_weak = lambda: None

                for child_binding in old_value.children:
                    child_binding.is_root = True
                    child_binding.parent = None
                    child_binding.value = binding_value

            # If both values are bindings transfer the children to the new
            # binding
            elif old_is_binding and new_is_binding:
                new_value.owning_component_weak = old_value.owning_component_weak
                new_value.children = old_value.children

                for child in old_value.children:
                    child.parent = new_value

                # Save the binding's value in case this is the root binding
                new_value.value = old_value.value

            overridden_values[prop_name] = new_value

        # If the component has changed mark it as dirty
        def values_equal(old: object, new: object) -> bool:
            """
            Used to compare the old and new values of a property. Returns `True`
            if the values are considered equal, `False` otherwise.
            """
            # Components are a special case. Component attributes are dirty iff the
            # component isn't reconciled, i.e. it is a new component
            if isinstance(new, rio.Component):
                return old is new or old is reconciled_components_new_to_old.get(
                    new, None
                )

            if isinstance(new, list):
                if not isinstance(old, list):
                    return False

                old = cast(List[object], old)
                new = cast(List[object], new)

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

        # Determine which properties will be taken from the new component
        for prop_name in overridden_values:
            old_value = getattr(old_component, prop_name)
            new_value = getattr(new_component, prop_name)

            if not values_equal(old_value, new_value):
                self._register_dirty_component(
                    old_component,
                    include_children_recursively=False,
                )
                break

        # Override the key now. It should never be preserved, but doesn't make
        # the component dirty
        overridden_values["key"] = new_component.key

        # Now combine the old and new dictionaries
        #
        # Notice that the component's `_weak_builder_` is always preserved. So even
        # components whose position in the tree has changed still have the correct
        # builder set.
        old_component_dict.update(overridden_values)

    def _find_components_for_reconciliation(
        self,
        old_build: rio.Component,
        new_build: rio.Component,
    ) -> Iterable[Tuple[rio.Component, rio.Component]]:
        """
        Given two component trees, find pairs of components which can be
        reconciled, i.e. which represent the "same" component. When exactly
        components are considered to be the same is up to the implementation and
        best-effort.

        Returns an iterable over (old_component, new_component) pairs, as well as a
        list of all components occurring in the new tree, which did not have a match
        in the old tree.
        """

        old_components_by_key: Dict[str, rio.Component] = {}
        new_components_by_key: Dict[str, rio.Component] = {}

        matches_by_topology: List[Tuple[rio.Component, rio.Component]] = []

        # First scan all components for topological matches, and also keep track of
        # each component by its key
        def register_component_by_key(
            components_by_key: Dict[str, rio.Component],
            component: rio.Component,
        ) -> None:
            if component.key is None:
                return

            # It's possible that the same component is registered twice, once
            # from a key_scan caused by a failed structural match, and once from
            # recursing into a successful key match.
            if (
                component.key in components_by_key
                and components_by_key[component.key] is not component
            ):
                raise RuntimeError(
                    f'Multiple components share the key "{component.key}": {components_by_key[component.key]} and {component}'
                )

            components_by_key[component.key] = component

        def key_scan(
            components_by_key: Dict[str, rio.Component],
            component: rio.Component,
            include_self: bool = True,
        ) -> None:
            for (
                child
            ) in component._iter_direct_and_indirect_child_containing_attributes(
                include_self=include_self,
                recurse_into_high_level_components=True,
            ):
                register_component_by_key(components_by_key, child)

        def chain_to_children(
            old_component: rio.Component,
            new_component: rio.Component,
        ) -> None:
            def _extract_components(attr: object) -> List[rio.Component]:
                if isinstance(attr, rio.Component):
                    return [attr]

                if isinstance(attr, list):
                    attr = cast(List[object], attr)

                    return [item for item in attr if isinstance(item, rio.Component)]

                return []

            # Iterate over the children, but make sure to preserve the topology.
            # Can't just use `iter_direct_children` here, since that would
            # discard topological information.
            for attr_name in inspection.get_child_component_containing_attribute_names(
                type(new_component)
            ):
                old_value = getattr(old_component, attr_name, None)
                new_value = getattr(new_component, attr_name, None)

                old_components = _extract_components(old_value)
                new_components = _extract_components(new_value)

                # Chain to the children
                common = min(len(old_components), len(new_components))
                for old_child, new_child in zip(old_components, new_components):
                    worker(old_child, new_child)

                for old_child in old_components[common:]:
                    key_scan(old_components_by_key, old_child, include_self=True)

                for new_child in new_components[common:]:
                    key_scan(new_components_by_key, new_child, include_self=True)

        def worker(old_component: rio.Component, new_component: rio.Component) -> None:
            # Register the component by key
            register_component_by_key(old_components_by_key, old_component)
            register_component_by_key(new_components_by_key, new_component)

            # If the components' types or keys don't match, stop looking for
            # topological matches. Just keep track of the children's keys.
            if (
                type(old_component) is not type(new_component)
                or old_component.key != new_component.key
            ):
                key_scan(old_components_by_key, old_component, include_self=False)
                key_scan(new_components_by_key, new_component, include_self=False)
                return

            # Key matches are handled elsewhere, so if the key is not `None`, do
            # nothing. We'd just end up doing the same work twice.
            if old_component.key is not None:
                return

            matches_by_topology.append((old_component, new_component))
            chain_to_children(old_component, new_component)

        worker(old_build, new_build)

        # Find matches by key and reconcile their children. This can produce new
        # key matches, so we do it in a loop.
        new_key_matches = old_components_by_key.keys() & new_components_by_key.keys()

        while new_key_matches:
            for key in new_key_matches:
                old_component = old_components_by_key[key]
                new_component = new_components_by_key[key]

                # If the components have different types, even the same key
                # can't make them match
                if type(old_component) is not type(new_component):
                    continue

                yield (old_component, new_component)

                # Recurse into these two components
                chain_to_children(old_component, new_component)

            # If any new key matches were found, repeat the process
            new_key_matches = (
                old_components_by_key.keys()
                & new_components_by_key.keys() - new_key_matches
            )

        # Yield topological matches
        for old_component, new_component in matches_by_topology:
            yield old_component, new_component

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

        self.create_task(self._remote_register_font(font.name, urls))  # type: ignore

        self._registered_font_assets[font.name] = font_assets

    def _get_settings_file_path(self) -> Path:
        """
        The path to the settings file. Only used if `running_in_window`.
        """
        import platformdirs

        return (
            Path(
                platformdirs.user_data_dir(
                    appname=self._app_server.app.name,
                    roaming=True,
                    ensure_exists=True,
                )
            )
            / "settings.json"
        )

    async def _load_user_settings(
        self, settings_sent_by_client: Dict[str, object]
    ) -> None:
        # If `running_in_window`, load the settings from the config file.
        # Otherwise, parse the settings sent by the browser.
        #
        # Keys in this dict can be attributes of the "root" section or names of
        # sections. To prevent name clashes, section names are prefixed with
        # "section:".
        settings_json: Dict[str, object]

        if self.running_in_window:
            try:
                async with aiofiles.open(self._get_settings_file_path()) as file:
                    settings_text = await file.read()

                settings_json = json.loads(settings_text)
            except (IOError, json.JSONDecodeError):
                settings_json = {}

            self._settings_json = settings_json
        else:
            # Browsers send us a flat dict where the keys are prefixed with the
            # section name. We will convert each section into a dict.
            settings_json = {}

            for key, value in settings_sent_by_client.items():
                # Find the section name
                section_name, _, key = key.rpartition(":")

                if section_name:
                    section = settings_json.setdefault("section:" + section_name, {})
                    section[key] = value  # type: ignore
                else:
                    settings_json[key] = value

        # If `running_in_window`, we need to store the settings JSON so that
        # we can update the changed keys and write the whole thing to a file.
        if self.running_in_window:
            self._settings_json = settings_json

        # Instantiate and attach the settings
        for default_settings in self._app_server.default_attachments:
            if not isinstance(default_settings, user_settings_module.UserSettings):
                continue

            settings = type(default_settings)._from_json(
                self,
                settings_json,
                default_settings,
            )

            # Attach the instance to the session
            self.attachments._add(settings, synchronize=False)

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

        This function opens a file chooser dialog, allowing the user to select a
        file. The selected file is returned, allowing you to access its
        contents.

        See also `save_file`, if you want to save a file instead of opening one.

        Args:
            file_extensions: A list of file extensions which the user is allowed
                to select. Defaults to `None`, which means that the user may
                select any file.

            multiple: Whether the user should pick a single file, or multiple.

        Raises:
            NoFileSelectedError: If the user did not select a file.
        """
        # Create a secret id and register the file upload with the app server
        upload_id = secrets.token_urlsafe()
        future = asyncio.Future[List[common.FileInfo]]()

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
        file_contents: Union[Path, str, bytes],
        file_name: str = "Unnamed File",
        *,
        media_type: Optional[str] = None,
        directory: Optional[Path] = None,
    ) -> None:
        """
        Save a file to the user's device.

        This function allows you to save a file to the user's device. The user
        will be prompted to select a location to save the file to.

        See also `file_chooser` if you want to open a file instead of saving
        one.

        Args:
            file_contents: The contents of the file to save. This can be a
                string, bytes, or a path to a file on the server.

            file_name: The default file name that will be displayed in the file
                dialog. The user can freely change it.

            media_type: The media type of the file. Defaults to `None`, which
                means that the media type will be guessed from the file name.

            directory: The directory where the file dialog should open. This has
                no effect if the user is visiting the app in a browser.
        """
        if self.running_in_window:
            # FIXME: Find (1) a better way to get the active window and (2) a
            # way to open a file dialog without blocking the event loop.
            import webview  # type: ignore

            active_window = webview.active_window()
            destination = active_window.create_file_dialog(
                webview.SAVE_DIALOG,
                directory=directory,
                save_filename=file_name,
            )

            if isinstance(file_contents, Path):
                await asyncio.to_thread(shutil.copy, file_contents, destination)

            elif isinstance(file_contents, str):
                async with aiofiles.open(destination, "w", encoding="utf8") as file:
                    await file.write(file_contents)

            elif isinstance(file_contents, bytes):  # type: ignore[unnecessary-isinstance]
                async with aiofiles.open(destination, "wb") as file:
                    await file.write(file_contents)

            else:
                raise ValueError(
                    f"The file contents must be a Path, str or bytes, not {file_contents!r}"
                )

            return

        # Create an asset for the file
        if isinstance(file_contents, Path):
            as_asset = assets.PathAsset(file_contents, media_type)

        elif isinstance(file_contents, str):
            as_asset = assets.BytesAsset(
                file_contents.encode("utf-8"),
                "text/plain" if media_type is None else media_type,
            )

        elif isinstance(file_contents, bytes):  # type: ignore[unnecessary-isinstance]
            as_asset = assets.BytesAsset(
                file_contents,
                "application/octet-stream" if media_type is None else media_type,
            )

        else:
            raise ValueError(
                f"The file contents must be a Path, str or bytes, not {file_contents!r}"
            )

        # Host the asset
        url = self._app_server.host_asset_with_timeout(as_asset, 60)

        # Tell the frontend to download the file
        await self._evaluate_javascript(
            f"""
const a = document.createElement('a')
a.href = {json.dumps(str(url))}
a.download = {json.dumps(file_name)}
a.type = {json.dumps(media_type)}
a.target = "_blank"
document.body.appendChild(a)
a.click()
document.body.removeChild(a)
"""
        )

    async def _apply_theme(self, thm: theme.Theme) -> None:
        """
        Updates the client's theme to match the given one.
        """
        # Build the set of all CSS variables that must be set

        # Miscellaneous
        variables: Dict[str, str] = {
            "--rio-global-corner-radius-small": f"{thm.corner_radius_small}rem",
            "--rio-global-corner-radius-medium": f"{thm.corner_radius_medium}rem",
            "--rio-global-corner-radius-large": f"{thm.corner_radius_large}rem",
            "--rio-global-shadow-color": f"#{thm.shadow_color.hex}",
        }

        # Palettes
        palette_names = (
            "primary",
            "secondary",
            "background",
            "neutral",
            "disabled",
            "success",
            "warning",
            "danger",
        )

        for palette_name in palette_names:
            palette = getattr(thm, f"{palette_name}_palette")
            assert isinstance(palette, theme.Palette), palette

            variables[f"--rio-global-{palette_name}-bg"] = f"#{palette.background.hex}"
            variables[
                f"--rio-global-{palette_name}-bg-variant"
            ] = f"#{palette.background_variant.hex}"
            variables[
                f"--rio-global-{palette_name}-bg-active"
            ] = f"#{palette.background_active.hex}"
            variables[f"--rio-global-{palette_name}-fg"] = f"#{palette.foreground.hex}"

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

        # Update the variables client-side
        await self._remote_apply_theme(
            variables,
            "light"
            if thm.neutral_palette.background.perceived_brightness > 0.5
            else "dark",
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
        name="updateComponentStates",
        parameter_format="dict",
        await_response=False,
    )
    async def _remote_update_component_states(
        self,
        # Maps component ids to serialized components. The components may be partial,
        # i.e. any property may be missing.
        delta_states: Dict[int, Any],
        # Tells the client to make the given component the new root component.
        root_component_id: Optional[int],
    ) -> None:
        """
        Replace all components in the UI with the given one.
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

    def _try_get_component_for_message(
        self, component_id: int
    ) -> Optional[rio.Component]:
        """
        Attempts to get the component referenced by `component_id`. Returns `None` if
        there is no such component. This can happen during normal opration, e.g.
        because a component has been deleted while the message was in flight.
        """

        try:
            return self._weak_components_by_id[component_id]
        except KeyError:
            logging.warn(
                f"Encountered message for unknown component {component_id}. (The component might have been deleted in the meantime.)"
            )
            return None

    @unicall.local(name="componentStateUpdate")
    async def _component_state_update(
        self,
        component_id: int,
        delta_state: Any,
    ) -> None:
        # Get the component
        component = self._try_get_component_for_message(component_id)

        if component is None:
            return

        # Update the component's state
        assert isinstance(component, component_base.FundamentalComponent), component
        await component._on_state_update(delta_state)

    @unicall.local(name="componentMessage")
    async def _component_message(
        self,
        component_id: int,
        payload: Any,
    ) -> None:
        # Get the component
        component = self._try_get_component_for_message(component_id)

        if component is None:
            return

        # Let the component handle the message
        await component._on_message(payload)

    @unicall.local(name="ping")
    async def _ping(self, ping: str) -> str:
        return "pong"

    @unicall.local(name="onUrlChange")
    async def _on_url_change(self, new_url: str) -> None:
        """
        Called by the client when the page changes.
        """
        # Try to navigate to the new page
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
        for component, callback in self._on_window_resize_callbacks.items():
            self.create_task(
                self._call_event_handler(callback, component),
                name="`on_window_resize` event handler",
            )
